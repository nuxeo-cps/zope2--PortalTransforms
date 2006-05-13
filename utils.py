"""some common utilities
"""


__revision__ = '$Id$'

from time import time

class TransformException(Exception) : pass

FB_REGISTRY = None

try:
    try:
        import Zope2
    except ImportError: # BBB: for Zope 2.7
        import Zope as Zope2
except ImportError:
    HAS_ZOPE = 0

    # no Zope specific... #####################################################

    # base class
    class Base : pass

    # logging function
    from sys import stderr
    def log(msg, severity=None, id=None):
        print >>stderr, msg

    # list and dict classes to use
    from UserDict import UserDict as DictClass
    from UserList import UserList as ListClass

    # getToolByName should only have to return the mime types registry in this
    # mode
    _MTR = None
    def getToolByName(self, name):
        assert name == 'mimetypes_registry'
        global _MTR
        if _MTR is None:
            from Products.PortalTransforms.MimeTypesTool import MimeTypesTool
            _MTR = MimeTypesTool(fill=1)
        return _MTR

    # interfaces
    class Interface : pass

    from types import ListType, TupleType
    def implements(object, interface):
        if hasattr(object, "__implements__") and \
               (interface == object.__implements__ or \
                (type(object.__implements__) in (ListType, TupleType) and \
                 interface in object.__implements__)):
            return 1
        return 0
else:
    HAS_ZOPE = 1

    # base class
    from ExtensionClass import Base

    # logging function
    from zLOG import LOG, INFO
    def log(msg, severity=INFO, id='PortalTransforms'):
        LOG(id, severity, msg)

    # directory where template for the ZMI are located
    import os.path
    _www = os.path.join(os.path.dirname(__file__), 'www')
    skins_dir = os.path.join(os.path.dirname(__file__), 'skins')

    # list and dict classes to use
    from Globals import PersistentMapping as DictClass
    try:
        from ZODB.PersistentList import PersistentList as ListClass
    except ImportError:
        from persistent.list import PersistentList as ListClass

    # interfaces
    try:
        # Zope >= 2.6
        from Interface import Interface
    except ImportError:
        # Zope < 2.6
        from Interface import Base as Interface

    def implements(object, interface):
        return interface.isImplementedBy(object)

    # getToolByName
    from Products.CMFCore.utils import getToolByName as _getToolByName
    _marker = []

    def getToolByName(context, name, default=_marker):
        global FB_REGISTRY
        tool = _getToolByName(context, name, default)
        if name == 'mimetypes_registry' and tool is default:
            if FB_REGISTRY is None:
                from Products.PortalTransforms.MimeTypesRegistry \
                     import MimeTypesRegistry
                FB_REGISTRY = MimeTypesRegistry()
            tool = FB_REGISTRY
        return tool

# common ######################################################################

class Cache:

    def __init__(self, context, _id='_v_transform_cache'):
        self.context = context
        self._id =_id

    def _genCacheKey(self, identifier, *args):
        key = identifier
        for arg in args:
            key = '%s_%s' % (key, arg)
        key = key.replace('/', '_')
        key = key.replace('+', '_')
        key = key.replace('-', '_')
        key = key.replace(' ', '_')
        return key

    def setCache(self, key, value):
        """cache a value indexed by key"""
        context = self.context
        key = self._genCacheKey(key)
        if not hasattr(context, self._id):
            setattr(context, self._id, {})
        getattr(context, self._id)[key] = (time(), value)
        return key

    def getCache(self, key):
        """try to get a cached value for key

        return None if not present
        else return a tuple (time spent in cache, value)
        """
        context = self.context
        key = self._genCacheKey(key)
        dict = getattr(context, self._id, None)
        if dict is None :
            return None
        try:
            orig_time, value = dict.get(key, None)
            return time() - orig_time, value
        except TypeError:
            return None
