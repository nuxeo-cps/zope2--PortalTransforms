from Products.PortalTransforms.interfaces import itransform
from StructuredText.StructuredText import HTML

class st:
    __implements__ = itransform

    __name__ = "st_to_html"
    inputs   = ("text/structured",)
    output   = "text/html"

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        data.setData(HTML(text=orig, level=1))
        return data

def register():
    return st()
