"""
Uses the xpdf (www.foolabs.com/xpdf)
"""

from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.utils import bin_search, basename, sansext
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from os import system

class pdf_to_text(commandtransform):
    __implements__ = itransform

    __name__ = "pdf_to_text"
    inputs   = ('application/pdf',)
    output  = 'text/plain'

    binaryName = "pdftotext"

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
        kwargs['filename'] = basename((kwargs.get('filename') or 'unknown.pdf'))

        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        text = self.invokeCommand(tmpdir, fullname)
        path, images = self.subObjects(tmpdir)
        objects = {}
        if images:
            self.fixImages(path, images, objects)
        self.cleanDir(tmpdir)
        cache.setData(text)
        cache.setSubObjects(objects)
        return cache

    def invokeCommand(self, tmpdir, fullname):
        # FIXME: windows users...
        textfile = "%s/%s.txt" % (tmpdir, sansext(fullname))
        cmd = 'cd "%s" && %s "%s" "%s" 2>error_log 1>/dev/null' % (
            tmpdir, self.binary, fullname, textfile)
        system(cmd)
        try:
            text = open(textfile).read()
        except:
            try:
                return open("%s/error_log" % tmpdir, 'r').read()
            except:
                return ''
        return text

def register():
    return pdf_to_text()
