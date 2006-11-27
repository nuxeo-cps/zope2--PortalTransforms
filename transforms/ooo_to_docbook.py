"""
Transform DocBook XML to HTML through XSL
"""
# $Id$
import os
import sys

from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.utils import bin_search, basename, sansext
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from zLOG import LOG, DEBUG, WARNING

class ooo_to_docbook(commandtransform):
    __implements__ = itransform

    __name__ = 'ooo_to_docbook'
    inputs   = ('application/vnd.oasis.opendocument.text',
                'application/vnd.sun.xml.writer',
                )
    output  = 'application/docbook+xml'

    binaryName = os.path.join(
        os.getcwd(), os.path.dirname(__file__), 'ooo2dbk', 'ooo2dbk')

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
        kwargs['filename'] = basename((kwargs.get('filename') or 'unknown.sxw'))

        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        generated_file_data = self.invokeCommand(tmpdir, fullname)

        subObjectsPaths = [tmpdir, os.path.join(tmpdir, 'images')]
        for subObjectsPath in subObjectsPaths:
            if os.path.exists(subObjectsPath):
                path, images = self.subObjects(subObjectsPath)
                objects = {}
                if images:
                    self.fixImages(path, images, objects)

        self.cleanDir(tmpdir)
        cache.setData(generated_file_data)
        cache.setSubObjects(objects)
        return cache

    def invokeCommand(self, tmpdir, fullname):
        if sys.platform == 'win32':
            paths = os.environ['PATH'].split(';')
            for path in paths:
                config_path = os.path.join(path, 'ooo2dbk.exe')
                if os.path.exists(config_path):
                    cmd = '%s --dbkfile "%s.docb.xml" -c "%s" -x "%s" "%s"' % (
                        os.path.basename(self.binary),
                        os.path.join(tmpdir, sansext(fullname)),
                        os.path.join(path, 'ooo2dbk.xml'),
                        os.path.join(path, 'ooo2dbk.xsl'),
                        fullname)
                    break
            else:
                cmd = ''
        else:
            cmd = ('cd "%s" && %s --dbkfile %s.docb.xml %s '
                   '2>"%s.log-xsltproc"') % (
                tmpdir, self.binary, sansext(fullname), fullname, sansext(fullname))
        LOG(self.__name__, DEBUG, "cmd = %s" % cmd)
        os.system(cmd)
        try:
            generated_file = open(os.path.join(tmpdir, "%s.docb.xml" % sansext(fullname)),
                            'r')
            generated_file_data = generated_file.read()
            generated_file.close()
        except:
            try:
                return open(os.path.join(tmpdir, 'error_log'), 'r').read()
            except:
                return ''
        return generated_file_data

def register():
    return ooo_to_docbook()
