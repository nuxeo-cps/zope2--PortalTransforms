from Acquisition import Implicit
from OFS.SimpleItem import Item
from AccessControl import ClassSecurityInfo
from Globals import Persistent, InitializeClass
try:
    from Products.CMFCore.permissions import ManagePortal
except ImportError: # BBB: CMF 1.4
    from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.PortalTransforms.interfaces import imimetype
from Products.PortalTransforms.MimeTypeItem import mimetype

__revision__ = '$Id$'

class MimeTypeItem(mimetype, Persistent, Implicit, Item):
    """ A mimetype object to be managed inside the mimetypes tool """

    security = ClassSecurityInfo()
    __implements__ = (imimetype,)

    security.declarePublic('name')
    security.declarePublic('major')
    security.declarePublic('minor')
    security.declarePublic('normalized')

    security.declareProtected(ManagePortal, 'edit')
    def edit(self, name, mimetypes, extensions, icon_path, binary=0,
             REQUEST=None):
        """edit this mime type"""
        # if mimetypes and extensions are string instead of lists, split them on new lines
        if type(mimetypes) in (type(''), type(u'')):
            mimetypes = [mts.strip() for mts in mimetypes.split('\n') if mts.strip()]
        if type(extensions) in (type(''), type(u'')):
            extensions = [mts.strip() for mts in extensions.split('\n') if mts.strip()]
        self.__name__ = self.id = name
        self.mimetypes = mimetypes
        self.extensions = extensions
        self.binary = binary
        self.icon_path = icon_path
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

InitializeClass(MimeTypeItem)
