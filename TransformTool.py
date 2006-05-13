"""this file act as a redirector to provide the correct class if we are running
zope or not
"""
__revision__ = '$Id$'

from Products.PortalTransforms.utils import HAS_ZOPE

if HAS_ZOPE:
    from zope.TransformTool import TransformTool
else:
    from TransformEngine import TransformEngine

    class TransformTool(TransformEngine):

        def __init__(self):
            TransformEngine.__init__(self)
            self._transforms = {}

        def _setObject(self, id, transform):
            self._transforms[id] = transform

        def __getattr__(self, attr):
            try:
                return self._transforms[attr]
            except KeyError:
                raise AttributeError(attr)
