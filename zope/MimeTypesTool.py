from OFS.Folder import Folder
try:
    from Products.CMFCore.permissions import ManagePortal
except ImportError: # BBB: CMF 1.4
    from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.TypesTool import  FactoryTypeInformation
from Products.CMFCore.utils import UniqueObject
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from Acquisition import aq_parent
from AccessControl import ClassSecurityInfo

from Products.PortalTransforms.interfaces import isourceAdapter, imimetypes_registry
from Products.PortalTransforms.utils import log, _www
from Products.PortalTransforms.MimeTypesRegistry import MimeTypesRegistry
from Products.PortalTransforms.zope.MimeTypeItem import MimeTypeItem

__revision__ = '$Id$'

class MimeTypesTool(UniqueObject, ActionProviderBase, Folder, MimeTypesRegistry):
    """extend the MimeTypesRegistry of CMF compliance
    """

    __implements__ = (imimetypes_registry, isourceAdapter)

    id        = 'mimetypes_registry'
    meta_type = 'MimeTypes Registry'
    isPrincipiaFolderish = 1 # Show up in the ZMI

    meta_types = all_meta_types = (
        { 'name'   : 'MimeType',
          'action' : 'manage_addMimeTypeForm'},
        )

    manage_options = (
        ( { 'label'   : 'MimeTypes',
            'action' : 'manage_main'},) +
        Folder.manage_options[2:]
        )

    manage_addMimeTypeForm = PageTemplateFile('addMimeType', _www)
    manage_main = PageTemplateFile('listMimeTypes', _www)
    manage_editMimeTypeForm = PageTemplateFile('editMimeType', _www)

    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'register')
    security.declareProtected(ManagePortal, 'unregister')
    security.declarePublic('mimetypes')
    security.declarePublic('list_mimetypes')
    security.declarePublic('lookup')
    security.declarePublic('lookupExtension')
    security.declarePublic('classify')

    # FIXME
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, fill=1):
        MimeTypesRegistry.__init__(self, fill=1)
        del self.defaultMimetype
        self.manage_addProperty('defaultMimetype', 'text/plain', 'string')
        del self.unicodePolicy
        self.manage_addProperty('unicodePolicies', 'strict ignore replace', 'tokens')
        self.manage_addProperty('unicodePolicy', 'unicodePolicies', 'selection')

    def lookup(self, mimetypestring):
        result = MimeTypesRegistry.lookup(self, mimetypestring)
        return tuple([m.__of__(self) for m in result])

    security.declareProtected(ManagePortal, 'manage_delObjects')
    def manage_delObjects(self, ids, REQUEST=None):
        """ delete the selected mime types """
        for id in ids:
            self.unregister(self.lookup(id)[0])
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

    security.declareProtected(ManagePortal, 'manage_addMimeType')
    def manage_addMimeType(self, id, mimetypes, extensions, icon_path, binary=0,
                           REQUEST=None):
        """add a mime type to the tool"""
        mt = MimeTypeItem(id, mimetypes, extensions, binary, icon_path)
        self.register(mt)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


    security.declareProtected(ManagePortal, 'manage_editMimeType')
    def manage_editMimeType(self, name, new_name, mimetypes, extensions, icon_path, binary=0,
                            REQUEST=None):
        """edit a mime type by name"""
        mt = self.lookup(name)[0]
        self.unregister(mt)
        mt.edit(new_name, mimetypes, extensions, icon_path, binary)
        self.register(mt)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


InitializeClass(MimeTypesTool)
