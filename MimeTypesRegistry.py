from os.path import splitext, basename
from types import UnicodeType, StringType

from Acquisition import aq_base
from Products.PortalTransforms.interfaces import imimetype, isourceAdapter, \
     iclassifier, imimetypes_registry
from Products.PortalTransforms.MimeTypeItem import MimeTypeItem, \
     MimeTypeException
from Products.PortalTransforms.mime_types import initialize, magic
from Products.PortalTransforms.utils import log, implements, DictClass, Base
from cPickle import loads, dumps
from encoding import guess_encoding

__revision__ = '$Id$'

STRING_TYPES = (UnicodeType, StringType)

suffix_map = {
    'tgz': '.tar.gz',
    'taz': '.tar.gz',
    'tz': '.tar.gz',
    }

# XXX Added by Nuxeo for the sake of .tar.gz files.
# Mapping of suffixes generally used after the suffix in value.
cps_suffix_map = {
    'gz': ('tar',),
    'bz2': ('tar',),
    'Z': ('pcf',),
    'xml': ('doc', 'docb'),
}

# XXX Unused after Nuxeo cleaning but also in PortalTransform 1.0.4 and above
encodings_map = {
    'gz': 'gzip',
    'Z': 'compress',
    }

class MimeTypesRegistry(Base):
    """Mimetype registry that deals with
    a) registering types
    b) wildcarding of rfc-2046 types
    c) classifying data into a given type
    """

    __implements__ = (imimetypes_registry, isourceAdapter)

    def __init__(self, fill=1):
        self.encodings_map = encodings_map.copy()
        self.suffix_map = suffix_map.copy()
        # Major key -> minor imimetype objects
        self._mimetypes  = DictClass()
        # ext -> imimetype mapping
        self.extensions = DictClass()
        self.defaultMimetype = 'text/plain'
        self.unicodePolicy = 'replace'
        if fill:
            # initialize mime types
            initialize(self)

    def register(self, mimetype):
        """ Register a new mimetype

        mimetype must implement imimetype
        """
        mimetype = aq_base(mimetype)
        assert implements(mimetype, imimetype)
        for t in mimetype.mimetypes:
            major, minor = split(t)
            if not major or not minor or minor == '*':
                raise MimeTypeException('Can\'t register mime type %s' % t)
            group = self._mimetypes.setdefault(major, DictClass())
            if group.has_key(minor):
                log('Warning: redefining mime type %s (%s)' % (t, mimetype.__class__))
            group[minor] = mimetype
        for extension in mimetype.extensions:
            self.register_extension(extension, mimetype)

    def register_extension(self, extension, mimetype):
        """ Associate a file's extension to a imimetype

        extension is a string representing a file extension (not
        prefixed by a dot) mimetype must implement imimetype
        """
        mimetype = aq_base(mimetype)
        if self.extensions.has_key(extension):
            log('Warning: redefining extension %s from %s to %s' % (
                extension, self.extensions[extension], mimetype))
        #we don't validate fmt yet, but its ["txt", "html"]
        self.extensions[extension] = mimetype


    def unregister(self, mimetype):
        """ Unregister a new mimetype

        mimetype must implement imimetype
        """
        assert implements(mimetype, imimetype)
        for t in mimetype.mimetypes:
            major, minor = split(t)
            group = self._mimetypes.get(major, {})
            if group.get(minor) == mimetype:
                del group[minor]
        for e in mimetype.extensions:
            if self.extensions.get(e) == mimetype:
                del self.extensions[e]


    def mimetypes(self):
        """Return all defined mime types, each one implements at least
        imimetype
        """
        res = {}
        for g in self._mimetypes.values():
            for mt in g.values():
                res[mt] =1
        return res.keys()

    def list_mimetypes(self):
        """Return all defined mime types, as string"""
        return [str(mt) for mt in self.mimetypes()]

    def lookup(self, mimetypestring):
        """Lookup for imimetypes object matching mimetypestring

        mimetypestring may have an empty minor part or containing a
        wildcard (*) mimetypestring may and imimetype object (in this
        case it will be returned unchanged

        Return a list of mimetypes objects associated with the
        RFC-2046 name return an empty list if no one is known.
        """
        if implements(mimetypestring, imimetype):
            return (mimetypestring, )
        __traceback_info__ = (repr(mimetypestring), str(mimetypestring))
        major, minor = split(str(mimetypestring))
        group = self._mimetypes.get(major, {})
        if not minor or minor == '*':
            v = group.values()
        else:
            v = group.get(minor)
            if v:
                v = (v,)
            else:
                return ()
        return v

    def lookupExtension(self, filename):
        """Lookup for imimetypes object matching filename

        Filename maybe a file name like 'content.txt' or an extension
        like 'rest'

        Return an imimetype object associated with the file's
        extension or None

        XXX Changed by Nuxeo for types like tar.gz, which is different from a
        plain tar file and is not just a gzip'ed file; even the Mimetype tool
        makes a difference between x-tar files and x-gtar files.
        Combinations not in 'cps_suffix_map' are considered to be nothing but
        gzip'ed files (for instance) using the same mimetype.
        """
        if filename.rfind('.') != -1:
            base, ext = splitext(filename)
            ext = ext[1:] # remove the dot
            while cps_suffix_map.has_key(ext):
                base, prevext = splitext(base)
                if not prevext:
                    break
                prevext = prevext[1:] # remove the dot
                if prevext in cps_suffix_map[ext]:
                    # both extensions mean something else than a single one
                    ext = '%s.%s' % (prevext, ext)
                else:
                    # this previous suffix don't map to a different mimetype
                    # but this is supposed to be more specific.
                    ext = prevext
        else:
            ext = filename
        # XXX Nuxeo: the rest of that method was removed in version 1.0.4
        # and above
        return self.extensions.get(ext)

    def _classifiers(self):
        return [mt for mt in self.mimetypes() if implements(mt, iclassifier)]

    def classify(self, data, mimetype=None, filename=None):
        """Classify works as follows:
        1) you tell me the rfc-2046 name and I give you an imimetype
           object
        2) the filename includes an extension from which we can guess
           the mimetype
        3) we can optionally introspect the data
        4) default to self.defaultMimetype if no data was provided
           else to application/octet-stream if no filename was provided,
           else to None

        Return an imimetype object
        """
        mt = None
        if mimetype:
            mt = self.lookup(mimetype)
            if mt:
                mt = mt[0]
        elif filename:
            mt = self.lookupExtension(filename)
        if data and not mt:
            for c in self._classifiers():
                if c.classify(data):
                    mt = c
                    break
            if not mt:
                mstr = magic.guessMime(data)
                if mstr:
                    mt = self.lookup(mstr)
                    if mt:
                        mt = mt[0]
        if not mt:
            if not data:
                mt = self.lookup(self.defaultMimetype)[0]
            elif filename:
                mt = self.lookup('application/octet-stream')[0]
            else:
                mt = None
        if mt:
            # Remove acquisition wrappers
            mt = aq_base(mt)
            # Copy by pickle, to remove connection references
            mt = loads(dumps(mt))
        return mt

    def __call__(self, data, **kwargs):
        """ Return a triple (data, filename, mimetypeobject) given
        some raw data and optional paramters

        method from the isourceAdapter interface
        """
        mimetype = kwargs.get('mimetype', None)
        filename = kwargs.get('filename', None)
        encoding = kwargs.get('encoding', None)
        mt = None
        if hasattr(data, 'filename'):
            filename = basename(data.filename)
        elif hasattr(data, 'name'):
            filename = basename(data.name)

        if hasattr(data, 'read'):
            _data = data.read()
            if hasattr(data, 'seek'):
                data.seek(0)
            data = _data

        # We need to figure out if data is binary and skip encoding if
        # it is
        mt = self.classify(data, mimetype=mimetype, filename=filename)

        if mt and not mt.binary and not type(data) is UnicodeType:
            # if no encoding specified, try to guess it from data
            if encoding is None:
                encoding = self.guess_encoding(data)
            try:
                data = unicode(data, encoding, self.unicodePolicy)
            except (ValueError, LookupError):
                # wrong unicodePolicy
                data = unicode(data, encoding)

        return (data, filename, mt)

    def guess_encoding(self, data):
        """ Try to guess encoding from a text value if no encoding
        guessed, used the default charset from site properties (Zope)
        with a fallback to UTF-8 (should never happen with correct
        site_properties, but always raise Attribute error without
        Zope)
        """
        if type(data) is type(u''):
            # data maybe unicode but with another encoding specified
            data = data.encode('UTF-8')
        encoding = guess_encoding(data)
        if encoding is None:
            try:
                site_props = self.portal_properties.site_properties
                encoding = site_props.getProperty('default_charset', 'UTF-8')
            except:
                encoding = 'UTF-8'
        return encoding

def split(name):
    """ split a mime type in a (major / minor) 2-uple """
    try:
        major, minor = name.split('/', 1)
    except:
        raise MimeTypeException('Malformed MIME type (%s)' % name)
    return major, minor
