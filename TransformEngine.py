from Products.PortalTransforms.interfaces import iengine, idatastream, itransform
from Products.PortalTransforms.data import datastream
from Products.PortalTransforms.chain import chain
from Products.PortalTransforms.utils import log, TransformException, DictClass, \
     ListClass, getToolByName, implements, Base, Cache, HAS_ZOPE
from Products.PortalTransforms.libtransforms.utils import MissingBinary

__revision__ = '$Id$'

class TransformEngine(Base):

    __implements__ = iengine

    def __init__(self, policies=None, max_sec_in_cache=3600):
        self._mtmap = DictClass()
        self._policies = policies or DictClass()
        self.max_sec_in_cache = max_sec_in_cache

    # mimetype oriented conversions (iengine interface) ########################

    def registerTransform(self, transform):
        """register a transform

        transform must implements itransform
        """
        if not implements(transform, itransform):
            raise TransformException('%s does not implement itransform' % transform)
        name = transform.name()
        __traceback_info__ = (name, transform)
        self._setObject(name, transform)
        self._mapTransform(transform)

    def unregisterTransform(self, name):
        """ unregister a transform
        name is the name of a registered transform
        """
        self._unmapTransform(getattr(self, name))


    def convertTo(self, target_mimetype, orig, data=None, object=None, usedby=None,
                  **kwargs):
        """Convert orig to a given mimetype

        * orig is an encoded string

        * data an optional idatastream object. If None a new datastream will be
        created and returned

        * optional object argument is the object on which is bound the data.
        If present that object will be used by the engine to bound cached data.

        * additional arguments (kwargs) will be passed to the transformations.
        Some usual arguments are : filename, mimetype, encoding

        return an object implementing idatastream or None if no path has been
        found.
        """
        target_mimetype = str(target_mimetype)

        if object is not None:
            cache = Cache(object)
            data = cache.getCache(target_mimetype)
            if data is not None:
                time, data = data
                if self.max_sec_in_cache == 0 or time < self.max_sec_in_cache:
                    return data

        if data is None:
            data = self._wrap(target_mimetype)

        registry = getToolByName(self, 'mimetypes_registry')
        orig_mt = registry.classify(orig,
                                    mimetype=kwargs.get('mimetype'),
                                    filename=kwargs.get('filename'))
        if not orig_mt:
            log('Unable to guess input mime type (filename=%s, mimetype=%s)' %(
                kwargs.get('mimetype'), kwargs.get('filename')))
            return None

        target_mt = registry.lookup(target_mimetype)
        if target_mt:
            target_mt = target_mt[0]
        else:
            log('Unable to match target mime type %s'% str(target_mimetype))
            return None

        ## fastpath
        if orig_mt == target_mt:
            data.setData(orig)
            md = data.getMetadata()
            md['mimetype'] = str(orig_mt)
            if object is not None:
                cache.setCache(str(target_mimetype), data)
            return data

        ## get a path to output mime type
        requirements = self._policies.get(target_mt, [])
        path = self._findPath(orig_mt, target_mt, list(requirements))
        if not path and requirements:
            log('Unable to satisfy requirements %s' % ', '.join(requirements))
            path = self._findPath(orig_mt, target_mt)

        if not path:
            log('NO PATH FROM %s TO %s : %s' % (orig_mt, target_mimetype, path))
            return None #XXX raise TransformError

        log('PATH FROM %s TO %s : %s' % (orig_mt, target_mimetype, path))
        if len(path) > 1:
            ## create a chain on the fly (sly)
            transform = chain()
            for t in path:
                transform.registerTransform(t)
        else:
            transform = path[0]

        result = transform.convert(orig, data, **kwargs)
        self._setMetaData(result, transform)

        # set cache if possible
        if object is not None:
            cache.setCache(str(target_mimetype), result)

        # return idatastream object
        return result


    def convert(self, name, orig, data=None, **kwargs):
        """run a tranform of a given name on data

        * name is the name of a registered transform

        see convertTo docstring for more info
        """
        if not data:
            data = self._wrap(name)
        try:
            transform = getattr(self, name)
        except AttributeError:
            raise Exception('No such transform "%s"' % name)
        data = transform.convert(orig, data, **kwargs)
        self._setMetaData(data, transform)
        return data


    def __call__(self, name, orig, data=None, **kwargs):
        """run a transform by its name, returning the raw data product

        * name is the name of a registered transform.

        return an encoded string.
        see convert docstring for more info on additional arguments.
        """
        data = self.convert(name, orig, data, **kwargs)
        return data.getData()


    # utilities ###############################################################

    def _setMetaData(self, datastream, transform):
        """set metadata on datastream according to the given transform
        (mime type and optionaly encoding)
        """
        md = datastream.getMetadata()
        if hasattr(transform, 'output_encoding'):
            md['encoding'] = transform.output_encoding
        md['mimetype'] = transform.output

    def _wrap(self, name):
        """wrap a data object in an icache"""
        return datastream(name)

    def _unwrap(self, data):
        """unwrap data from an icache"""
        if implements(data, idatastream):
            data = data.getData()
        return data

    def _mapTransform(self, transform):
        """map transform to internal structures"""
        registry = getToolByName(self, 'mimetypes_registry')
        inputs = getattr(transform, 'inputs', None)
        if not inputs:
            raise TransformException('Bad transform %s : no input MIME type' %
                                     (transform))
        for i in inputs:
            mts = registry.lookup(i)
            if not mts:
                msg = 'Input MIME type %r for transform %s is not registered \
in the MIME types registry' % (i, transform.name())
                raise TransformException(msg)
            for mti in mts:
                for mt in mti.mimetypes:
                    mt_in = self._mtmap.setdefault(mt, DictClass())
                    output = getattr(transform, 'output', None)
                    if not output:
                        msg = 'Bad transform %s : no output MIME type'
                        raise TransformException(msg % transform.name())
                    mto = registry.lookup(output)
                    if not mto:
                        msg = 'Output MIME type %r for transform %s is not \
registered in the MIME types registry' % (output, transform.name())
                        raise TransformException(msg)
                    if len(mto) > 1:
                        msg = 'Wildcarding not allowed in transform\'s output \
MIME type'
                        raise TransformException(msg)

                    for mt2 in mto[0].mimetypes:
                        try:
                            if not transform in mt_in[mt2]:
                                mt_in[mt2].append(transform)
                        except KeyError:
                            mt_in[mt2] = ListClass([transform])

    def _unmapTransform(self, transform):
        """unmap transform from internal structures"""
        registry = getToolByName(self, 'mimetypes_registry')
        for i in transform.inputs:
            for mti in registry.lookup(i):
                for mt in mti.mimetypes:
                    mt_in = self._mtmap.get(mt, {})
                    output = transform.output
                    mto = registry.lookup(output)
                    for mt2 in mto[0].mimetypes:
                        l = mt_in[mt2]
                        for i in range(len(l)):
                            if transform.name() == l[i].name():
                                l.pop(i)
                                break
                        else:
                            log('Can\'t find transform %s from %s to %s' % (
                                transform.name(), mti, mt))

    def _findPath(self, orig, target, required_transforms=()):
        """return the shortest path for transformation from orig mimetype to
        target mimetype
        """
        path = []

        if not self._mtmap:
            return None

        # naive algorithm :
        #  find all possible paths with required transforms
        #  take the shortest
        #
        # it should be enough since we should not have so much possible paths
        shortest, winner = 9999, None
        for path in self._getPaths(str(orig), str(target), required_transforms):
            if len(path) < shortest:
                winner = path
                shortest = len(path)

        return winner

    def _getPaths(self, orig, target, requirements, path=None, result=None):
        """return a all path for transformation from orig mimetype to
        target mimetype
        """
        if path is None:
            result = []
            path = []
            requirements = list(requirements)
        outputs = self._mtmap.get(orig)
        if outputs is None:
            return result
        path.append(None)
        for o_mt, transforms in outputs.items():
            for transform in transforms:
                required = 0
                try:
                    name = transform.name()
                except MissingBinary, err:
                    log('MissingBinary %s' % (err,))
                    continue
                if name in requirements:
                    requirements.remove(name)
                    required = 1
                if transform in path:
                    # avoid infinite loop...
                    continue
                path[-1] = transform
                if o_mt == target:
                    if not requirements:
                        result.append(path[:])
                else:
                    self._getPaths(o_mt, target, requirements, path, result)
                if required:
                    requirements.append(name)
        path.pop()

        return result
