"""
Transform OOo file to HTML through XSL
"""
# $Id$
import os
import sys

from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.utils \
    import basename, sansext
from Products.PortalTransforms.libtransforms.commandtransform \
    import commandtransform
from zLOG import LOG, DEBUG, WARNING

XSL_STYLESHEET = os.path.join(
  os.getcwd(), os.path.dirname(__file__), 'sx2ml', 'main_html.xsl')

class ooo_to_html(commandtransform):
    __implements__ = itransform

    __name__ = 'ooo_to_html'
    inputs = ('application/vnd.sun.xml.writer',
              'application/vnd.sun.xml.impress',
              'application/vnd.sun.xml.calc',
              'application/vnd.sun.xml.writer.template',
              'application/vnd.sun.xml.impress.template',
              'application/vnd.sun.xml.calc.template',
              )
    output = 'text/html'

    def convert(self, data, cache, **kwargs):
        kwargs['filename'] = basename((kwargs.get('filename') or 'unknown.pdf'))

        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        html = self.invokeCommand(tmpdir, fullname)

        subObjectsPaths = [tmpdir, os.path.join(tmpdir, 'Pictures')]
        for subObjectsPath in subObjectsPaths:
            if os.path.exists(subObjectsPath):
                path, images = self.subObjects(subObjectsPath)
                objects = {}
                if images:
                    self.fixImages(path, images, objects)

        self.cleanDir(tmpdir)
        cache.setData(html)
        cache.setSubObjects(objects)
        return cache

    def invokeCommand(self, tmpdir, fullname):
        if sys.platform == 'win32':
            cmd = 'unzip %s -d %s' % (fullname, tmpdir)
        else:
            cmd = 'cd "%s" && unzip %s 2>error_log 1>/dev/null' % (
                tmpdir, fullname)
        os.system(cmd)
        if sys.platform == 'win32':
            cmd = 'xsltproc --novalid "%s" "%s" > "%s"' % (
                XSL_STYLESHEET,
                os.path.join(tmpdir, 'content.xml'),
                os.path.join(tmpdir, sansext(fullname)+'.html'))
        else:
            cmd = ('cd "%s" && xsltproc --novalid %s content.xml >"%s.html" '
                   '2>"%s.log-xsltproc"') % (
                tmpdir, XSL_STYLESHEET, sansext(fullname), sansext(fullname))
        LOG(self.__name__, DEBUG, "cmd = %s" % cmd)
        os.system(cmd)
        try:
            htmlfile = open(os.path.join(tmpdir, "%s.html" % sansext(fullname)),
                            'r')
            html = htmlfile.read()
            htmlfile.close()
        except:
            try:
                return open(os.path.join(tmpdir, 'error_log'), 'r').read()
            except:
                return ''
        return html

def register():
    return ooo_to_html()
