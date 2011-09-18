"""
Uses the http://sf.net/projects/rtf-converter bin to do its handy work
"""

from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.utils import bin_search, basename, sansext
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from os import system

class rtf_to_html(commandtransform):
    __implements__ = itransform

    __name__ = "rtf_to_html"
    inputs   = ('application/rtf',)
    output  = 'text/html'

    binaryName = "unrtf"

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
        kwargs['filename'] = basename((kwargs.get('filename') or 'unknown.rtf'))

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
        # FIXME: windows users...
        htmlfile = "%s/%s.html" % (tmpdir, sansext(fullname))
        cmd = 'cd "%s" && %s "%s" 2>error_log > %s' % (
            tmpdir, self.binary, fullname, htmlfile)
        system(cmd)
        try:
            html = open(htmlfile).read()
        except:
            try:
                return open("%s/error_log" % tmpdir, 'r').read()
            except:
                return ''
        return html

def register():
    return rtf_to_html()
