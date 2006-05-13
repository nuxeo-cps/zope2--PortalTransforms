from Products.PortalTransforms.interfaces import itransform
from docutils.core import publish_string
from Products.PortalTransforms.libtransforms.html4zope import Writer
import sys
if sys.version_info < (2,2):
    # fix the types module to make it docutils working with py2.1
    import types
    types.StringTypes = (types.UnicodeType, types.StringType)

class warnings:
    def __init__(self):
        self.messages = []

    def write(self, message):
        self.messages.append(message)


class rest:
    __implements__ = itransform

    __name__ = "rest_to_html"
    inputs  = ("text/x-rst", "text/restructured",)
    output = "text/html"

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        settings_overrides = {'report_level': 1,
                              'halt_level': 6,
                              'warning_stream': warnings(),
                              'documentclass': '',
                              'traceback': 1,
                              }

        # do the format
        html = publish_string(writer=Writer(), source=orig, settings_overrides=settings_overrides)
        #warnings = ''.join(pub.settings.warning_stream.messages) #XXX what todo with this?
        html = html.replace(' class="document"', '', 1)
        data.setData(html)
        return data

def register():
    return rest()
