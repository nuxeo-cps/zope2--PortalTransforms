"""this file act as a redirector to provide the correct class if we are running
zope or not
"""
__revision__ = '$Id$'

from Products.PortalTransforms.utils import HAS_ZOPE

if HAS_ZOPE:
    from zope.MimeTypesTool import MimeTypesTool
else:
    from MimeTypesRegistry import MimeTypesRegistry as MimeTypesTool
