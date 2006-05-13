import os
from Products.CMFCore.DirectoryView import addDirectoryViews, registerDirectory, \
     createDirectoryView, manage_listAvailableDirectories
from Products.CMFCore.utils import getToolByName, minimalpath
from Globals import package_home
from OFS.ObjectManager import BadRequestException

from Products.PortalTransforms import pt_globals, skins_dir
from Products.PortalTransforms.MimeTypeItem import MimeTypeItem


def install(self):
    if not hasattr(self, "mimetypes_registry"):
        addTool = self.manage_addProduct['PortalTransforms'].manage_addTool
        addTool('MimeTypes Registry')

    if not hasattr(self, "portal_transforms"):
        addTool = self.manage_addProduct['PortalTransforms'].manage_addTool
        addTool('Portal Transforms')

    skinstool=getToolByName(self, 'portal_skins')

    fullProductSkinsPath = os.path.join(package_home(pt_globals), skins_dir)
    productSkinsPath = minimalpath(fullProductSkinsPath)
    registered_directories = manage_listAvailableDirectories()
    if productSkinsPath not in registered_directories:
        registerDirectory(skins_dir, pt_globals)
    try:
        addDirectoryViews(skinstool, skins_dir, pt_globals)
    except BadRequestException, e:
        pass  # directory view has already been added

    files = os.listdir(fullProductSkinsPath)
    for productSkinName in files:
        if os.path.isdir(os.path.join(fullProductSkinsPath, productSkinName)) \
               and productSkinName != 'CVS':
            for skinName in skinstool.getSkinSelections():
                path = skinstool.getSkinPath(skinName)
                path = [i.strip() for i in  path.split(',')]
                try:
                    if productSkinName not in path:
                        path.insert(path.index('custom') +1, productSkinName)
                except ValueError:
                    if productSkinName not in path:
                        path.append(productSkinName)
                path = ','.join(path)
                skinstool.addSkinSelection(skinName, path)

    # application/excel   	application/excel  	xls
    registry = getToolByName(self, 'mimetypes_registry')
    registry.unregister(MimeTypeItem("Erroneous mimetype",
                                     ('application/excel',),
                                     ('xls',)),
                        )
