from OFS.Folder import Folder
try:
    from Products.CMFCore.permissions import ManagePortal
except ImportError: # BBB: CMF 1.4
    from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import Persistent, InitializeClass

from Acquisition import Implicit, aq_parent
from OFS.SimpleItem import Item
from AccessControl.Role import RoleManager
from AccessControl import ClassSecurityInfo

from Products.PortalTransforms.zope.Transform import Transform
from Products.PortalTransforms.zope.TransformsChain import TransformsChain
from Products.PortalTransforms.interfaces import iengine
from Products.PortalTransforms.utils import log, _www, TransformException,\
     DictClass, getToolByName, implements
from Products.PortalTransforms.TransformEngine import TransformEngine

__revision__ = '$Id$'

class TransformTool(TransformEngine, UniqueObject, ActionProviderBase, Folder):
    """ Transform tool, manage mime type oriented content transformation """

    id        = 'portal_transforms'
    meta_type = id.title().replace('_', ' ')
    isPrincipiaFolderish = 1 # Show up in the ZMI

    __implements__ = iengine

    meta_types = all_meta_types = (
        { 'name'   : 'Transform',
          'action' : 'manage_addTransformForm'},
        { 'name'   : 'TransformsChain',
          'action' : 'manage_addTransformsChainForm'},
        )

    manage_addTransformForm = PageTemplateFile('addTransform', _www)
    manage_addTransformsChainForm = PageTemplateFile('addTransformsChain', _www)
    manage_cacheForm = PageTemplateFile('setCacheTime', _www)
    manage_editTransformationPolicyForm = PageTemplateFile('editTransformationPolicy', _www)
    manage_reloadAllTransforms = PageTemplateFile('reloadAllTransforms', _www)

    manage_options = ((Folder.manage_options[0],) + Folder.manage_options[2:] +
                      (
        { 'label'   : 'Caches',
          'action' : 'manage_cacheForm'},
        { 'label'   : 'Policy',
          'action' : 'manage_editTransformationPolicyForm'},
        { 'label'   : 'Reload transforms',
          'action' : 'manage_reloadAllTransforms'},
        )
                      )

    security = ClassSecurityInfo()

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        """ overload manage_afterAdd to finish initialization when the
        transform tool is added
        """
        Folder.manage_afterAdd(self, item, container)
        from Products.PortalTransforms import transforms
        try:
            # first initialization
            transforms.initialize(self)
        except:
            # may fail on copy
            pass

    security.declareProtected(ManagePortal, 'manage_addTransform')
    def manage_addTransform(self, id, module, REQUEST=None):
        """ add a new transform to the tool """
        transform = Transform(id, module)
        self._setObject(id, transform)
        self._mapTransform(transform)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

    security.declareProtected(ManagePortal, 'manage_addTransform')
    def manage_addTransformsChain(self, id, description, REQUEST=None):
        """ add a new transform to the tool """
        transform = TransformsChain(id, description)
        self._setObject(id, transform)
        self._mapTransform(transform)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

    security.declareProtected(ManagePortal, 'manage_addTransform')
    def manage_setCacheValidityTime(self, seconds, REQUEST=None):
        """set  the lifetime of cached data in seconds"""
        self.max_sec_in_cache = int(seconds)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

    security.declareProtected(ManagePortal, 'reloadTransforms')
    def reloadTransforms(self, ids=()):
        """ reload transforms with the given ids
        if no ids, reload all registered transforms

        return a list of (transform_id, transform_module) describing reloaded
        transforms
        """
        if not ids:
            ids = self.objectIds()
        reloaded = []
        for id in ids:
            o = getattr(self, id)
            o.reload()
            reloaded.append((id, o.module))
        return reloaded

    # Policy handling methods #################################################

    def manage_addPolicy(self, output_mimetype, required_transforms, REQUEST=None):
        """ add a policy for a given output mime types"""
        registry = getToolByName(self, 'mimetypes_registry')
        if not registry.lookup(output_mimetype):
            raise TransformException('Unknown MIME type')
        if self._policies.has_key(output_mimetype):
            msg = 'A policy for output %s is yet defined' % output_mimetype
            raise TransformException(msg)

        required_transforms = tuple(required_transforms)
        self._policies[output_mimetype] = required_transforms
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_editTransformationPolicyForm')

    def manage_delPolicies(self, outputs, REQUEST=None):
        """ remove policies for given output mime types"""
        for mimetype in outputs:
            del self._policies[mimetype]
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_editTransformationPolicyForm')

    def listPolicies(self):
        """ return the list of defined policies

        a policy is a 2-uple (output_mime_type, [list of required transforms])
        """
        # XXXFIXME: backward compat, should be removed latter
        if not hasattr(self, '_policies'):
            self._policies = DictClass()
        return self._policies.items()

    # mimetype oriented conversions (iengine interface) ########################

    def registerTransform(self, transform):
        """register a new transform

        transform isn't a Zope Transform (the wrapper) but the wrapped transform
        the persistence wrapper will be created here
        """
        # needed when call from transform.transforms.initialize which
        # register non zope transform
        module = str(transform.__module__)
        transform = Transform(transform.name(), module, transform)
        TransformEngine.registerTransform(self, transform)


    security.declarePublic('classify')
    security.declarePublic('convert')

InitializeClass(TransformTool)
