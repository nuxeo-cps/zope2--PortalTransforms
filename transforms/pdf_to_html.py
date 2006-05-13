"""
Uses the http://sf.net/projects/pdftohtml bin to do its handy work

"""
# $Id$
import os
import sys

from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.utils import bin_search, basename, sansext
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform


class pdf_to_html(commandtransform):
    __implements__ = itransform

    __name__ = "pdf_to_html"
    inputs   = ('application/pdf',)
    output  = 'text/html'

    binaryName = "pdftohtml"
    binaryArgs = "-noframes"

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
        kwargs['filename'] = basename((kwargs.get('filename') or 'unknown.pdf'))

        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        html = self.invokeCommand(tmpdir, fullname)
        path, images = self.subObjects(tmpdir)
        objects = {}
        if images:
            self.fixImages(path, images, objects)
        self.cleanDir(tmpdir)
        cache.setData(html)
        cache.setSubObjects(objects)
        return cache

    def invokeCommand(self, tmpdir, fullname):
        if sys.platform == 'win32':
            cmd = '%s %s "%s" 2>"%s"' % (self.binary, self.binaryArgs,
                                         fullname,
                                         os.path.join(tmpdir, 'error_log'))
        else:
            cmd = 'cd "%s" && %s %s "%s" 2>error_log 1>/dev/null' % (
                tmpdir, self.binary, self.binaryArgs, fullname)
        os.system(cmd)
        try:
            htmlfile = open(os.path.join(tmpdir, sansext(fullname)+'.html'))
            html = htmlfile.read()
            htmlfile.close()
        except:
            try:
                return open(os.path.join(tmpdir, 'error_log')).read()
            except:
                return ''
        return html

def register():
    return pdf_to_html()
