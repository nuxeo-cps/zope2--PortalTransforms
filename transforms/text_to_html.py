from Products.PortalTransforms.interfaces import itransform
from DocumentTemplate.DT_Util import html_quote

__revision__ = '$Id$'

class TextToHTML:
    """simple transform which wrap raw text in a verbatim environment"""

    __implements__ = itransform

    __name__ = "text_to_html"
    output = "text/html"

    def __init__(self, name=None, inputs=('text/plain',)):
        self.config = { 'inputs' : inputs, }
        self.config_metadata = {
            'inputs' : ('list', 'Inputs', 'Input(s) MIME type. Change with care.'),
            }
        if name:
            self.__name__ = name

    def name(self):
        return self.__name__

    def __getattr__(self, attr):
        if attr == 'inputs':
            return self.config['inputs']
        if attr == 'output':
            return self.config['output']
        raise AttributeError(attr)

    def convert(self, orig, data, **kwargs):
        #data.setData('<pre class="data">%s</pre>' % orig)
        data.setData(html_quote(orig.strip()).replace('\n', '<br/>'))
        return data

def register():
    return TextToHTML()
