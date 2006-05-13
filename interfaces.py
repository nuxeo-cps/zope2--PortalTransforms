from utils import Interface

## Transforms related interfaces ##############################################

class idatastream(Interface):
    """data stream, is the result of a transform"""

    def setData(self, value):
        """set the main data produced by a transform, i.e. usually a string"""

    def getData():
        """provide access to the transformed data object, i.e. usually a string.
        This data may references subobjects.
        """

    def setSubObjects(self, objects):
        """set a dict-like object containing subobjects.
        keys should be object's identifier (e.g. usually a filename) and
        values object's content.
        """

    def getSubObjects(self):
        """return a dict-like object with any optional subobjects associated
        with the data"""

    def getMetadata():
        """return a dict-like object with any optional metadata from
        the transform
        You can modify the returned dictionnary to add/change metadata
        """

class itransform(Interface):
    """A transformation plugin -- tranform data somehow
    must be threadsafe and stateless"""

#     inputs = Attribute("""list of imimetypes (or registered rfc-2046
#     names) this transform accepts as inputs.""")

#     output = Attribute("""output imimetype as instance or rfc-2046
#     name""")

#     output_encoding = Attribute("""output encoding of this transform.
#     If not specified, the transform should output the same encoding as received data
#     """)

    def name(self):
        """return the name of the transform instance"""

    def convert(data, idata, filename=None, **kwargs):
        """convert the data, store the result in idata and return that

        optional argument filename may give the original file name of received data

        additional arguments given to engine's convert, convertTo or __call__ are
        passed back to the transform
        """


class ichain(itransform):

    def registerTransform(transform, condition=None):
        """Append a transform to the chain"""


class iengine(Interface):

    def registerTransform(transform):
        """register a transform

        transform must implements itransform
        """

    def unregisterTransform(name):
        """ unregister a transform
        name is the name of a registered transform
        """

    def convertTo(mimetype, orig, data=None, object=None, **kwargs):
        """Convert orig to a given mimetype

        * orig is an encoded string

        * data an optional idatastream object. If None a new datastream will be
        created and returned

        * optional object argument is the object on which is bound the data.
        If present that object will be used by the engine to bound cached data.

        * additional arguments (kwargs) will be passed to the transformations.

        return an object implementing idatastream or None if no path has been
        found.
        """

    def convert(name, orig, data=None, **kwargs):
        """run a tranform of a given name on data

        * name is the name of a registered transform

        see convertTo docstring for more info
        """

    def __call__(name, orig, data=None, **kwargs):
        """run a transform by its name, returning the raw data product

        * name is the name of a registered transform.

        return an encoded string.
        see convert docstring for more info on additional arguments.
        """

## MIME types related interfaces ##############################################

class imimetype(Interface):
    """Specification for dealing with mimetypes RFC-2046 style"""

#     mimetypes = Attribute("List of mimetypes in the RFC-2046 format")
#     extensions = Attribute("""List of extensions mapped to this
#     mimetype w/o the leading .""")

#     binary = Attribute("""Boolean indicating if the mimetype should be
#     treated as binary (and not human readable)""")

    def name(self):
        """return the Human readable name of the mimetype"""

    def major(self):
        """ return the major part of the RFC-2046 name for this mime type """

    def minor(self):
        """ return the minor part of the RFC-2046 name for this mime type """

    def normalized(self):
        """ return the main RFC-2046 name for this mime type

        e.g. if this object has names ('text/restructured', 'text-x-rst')
        then self.normalized() will always return the first form.
        """

class iclassifier(Interface):
    """Optional mixin interface for imimetype, code to test if the
    mimetype is present in data
    """
    def classify(data):
        """ boolean indicating if the data fits the mimetype"""


class isourceAdapter(Interface):

    def __call__(data, **kwargs):
        """convert data to unicode, may take optional kwargs to aid in
        conversion"""


class imimetypes_registry(Interface):

    def classify(data, mimetype=None, filename=None):
        """return a content type for this data or None
        None should rarely be returned as application/octet can be
        used to represent most types
        """

    def lookup(mimetypestring):
        """Lookup for imimetypes object matching mimetypestring

        mimetypestring may have an empty minor part or containing a wildcard (*)
        mimetypestring may be an imimetype object (in this case it will be
        returned unchanged, else it should be a RFC-2046 name

        return a list of mimetypes objects associated with the RFC-2046 name
        return an empty list if no one is known.
        """

    def lookupExtension(filename):
        """ return the mimetypes object associated with the file's extension
        return None if it is not known.

        filename maybe a file name like 'content.txt' or an extension like 'rest'
        """

    def mimetypes():
        """return all defined mime types, each one implements at least imimetype
        """

    def list_mimetypes():
        """return all defined mime types, as string"""
