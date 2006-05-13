import os
import sys
from Products.PortalTransforms.libtransforms.utils \
    import bodyfinder, scrubHTML
from Products.PortalTransforms.libtransforms.commandtransform \
    import commandtransform

ENCODING = "iso-8859-15"

class document(commandtransform):

    def __init__(self, name, data):
        """ Initialization: create tmp work directory and copy the
        document into a file"""
        binary = 'wvHtml'
        if sys.platform == 'win32':
            binary = 'wvWare'
        commandtransform.__init__(self, name, binary=binary)
        name = self.name()
        if not name.endswith('.doc'):
            name = name + ".doc"
        self.tmpdir, self.fullname = self.initialize_tmpdir(data, filename=name)

    def convert(self, output_encoding=ENCODING):
        "Convert the document"
        tmpdir = self.tmpdir

        if sys.platform == 'win32':
            paths = os.environ['PATH'].split(';')
            for path in paths:
                config_path = os.path.join(path, 'wvHtml.xml')
                if os.path.exists(config_path):
                    cmd = '%s --charset=%s -x "%s" "%s" > "%s"' % (
                        self.binary,
                        output_encoding,
                        config_path,
                        self.fullname,
                        os.path.join(tmpdir, self.__name__+'.html'))
                    break
            else:
                cmd = ''
        else:
            cmd = 'cd "%s" && %s --charset=%s "%s" "%s.html"' % (
                tmpdir,
                self.binary,
                output_encoding,
                self.fullname,
                self.__name__)

        os.system(cmd)

    def html(self):
        htmlfile = open(os.path.join(self.tmpdir, self.__name__+'.html'))
        html = htmlfile.read()
        htmlfile.close()
        html = scrubHTML(html)
        body = bodyfinder(html)
        return body
