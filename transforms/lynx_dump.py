"""
Uses lynx -dump
"""
from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.utils import bin_search, basename, sansext
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from os import system

class lynx_dump(commandtransform):
    __implements__ = itransform

    __name__ = "lynx_dump"
    inputs   = ('text/html',)
    output  = 'text/plain'

    binaryName = "lynx"
    binaryArgs = "-dump"

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
        orig_name = basename((kwargs.get('filename') or 'unknown'))
        kwargs['filename'] = orig_name + '.html'
        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        outname = "%s/%s.txt" % (tmpdir, orig_name)
        self.invokeCommand(tmpdir, fullname, outname)
        text = self.astext(outname)
        self.cleanDir(tmpdir)
        cache.setData(text)
        return cache

    def invokeCommand(self, tmpdir, inputname, outname):
        system('cd "%s" && %s %s "%s" 1>"%s" 2>/dev/null' % \
               (tmpdir, self.binary, self.binaryArgs, inputname, outname))

    def astext(self, outname):
        txtfile = open("%s" % (outname), 'r')
        txt = txtfile.read()
        txtfile.close()
        return txt

def register():
    return lynx_dump()
