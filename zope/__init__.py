__revision__ = '$Id$'

from Products.CMFCore.DirectoryView import registerDirectory
import TransformTool
import MimeTypesTool

PKG_NAME = 'PortalTransforms'

pt_globals = globals()

tools = (
    TransformTool.TransformTool,
    MimeTypesTool.MimeTypesTool,
    )

from Products.PortalTransforms.utils import skins_dir

registerDirectory(skins_dir, pt_globals)

def initialize(context):
    from Products.CMFCore import utils
    utils.ToolInit("%s Tool" % PKG_NAME, tools=tools,
                   icon="tool.png",
                   ).initialize(context)
