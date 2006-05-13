__revision__ = '$Id$'

from utils import HAS_ZOPE

if HAS_ZOPE:
    from Products.PortalTransforms.zope import *
