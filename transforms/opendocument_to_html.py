"""
Transform OOo OpenDocument file to HTML through XSL
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

XSL_STYLESHEET_TRANSFORM = os.path.join(
                               os.getcwd(),
                               os.path.dirname(__file__),
                               'od2ml',
                               'document2xhtml.xsl')

#style sheet for preview : content will be append as subobjects
XSL_STYLESHEET_DIRECTORY = os.path.join(
                               os.getcwd(),
                               os.path.dirname(__file__),
                               'od2ml',
                               'preview_css' )

class opendocument_to_html(commandtransform):
    __implements__ = itransform

    __name__ = 'opendocument_to_html'
    inputs = ('application/vnd.oasis.opendocument.text',
              'application/vnd.oasis.opendocument.text-template',
              'application/vnd.oasis.opendocument.spreadsheet',
              'application/vnd.oasis.opendocument.spreadsheet-template',
              'application/vnd.oasis.opendocument.presentation',
              'application/vnd.oasis.opendocument.presentation-template',
             # 'application/vnd.oasis.opendocument.graphics',
             # 'application/vnd.oasis.opendocument.graphics-template',
              )
    output = 'text/html'

    def convert(self, data, cache, **kwargs):
        kwargs['filename'] = basename((kwargs.get('filename') or 'unknown.pdf'))

        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        html = self.invokeCommand(tmpdir, fullname)

        #opendocument returns utf-8, re-encode according to site
        #encoding comes from CPSSchemas/FileUtils.py
        encoding = kwargs.get('encoding')
        if encoding is not None:
            html = html.decode('utf8').encode(encoding)

        subObjectsPaths = [tmpdir,
                           os.path.join(tmpdir, 'Pictures'),
                           XSL_STYLESHEET_DIRECTORY]

        objects = {}
        for subObjectsPath in subObjectsPaths:
            if os.path.exists(subObjectsPath):
                path, images = self.subObjects(subObjectsPath)
                if images:
                    self.fixImages(path, images, objects)

        # add the css files
        if os.path.exists(XSL_STYLESHEET_DIRECTORY):
            for css_item in os.listdir(XSL_STYLESHEET_DIRECTORY):
                if css_item.endswith(".css"):
                    objects[css_item] = open(
                        os.path.join(XSL_STYLESHEET_DIRECTORY,css_item),
                        'rb'
                        ).read()

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

        #process transform
        if sys.platform == 'win32':
            cmd = 'xsltproc --novalid "%s" "%s" > "%s"' % (
                XSL_STYLESHEET_TRANSFORM,
                os.path.join(tmpdir, 'content.xml'),
                os.path.join(tmpdir, sansext(fullname)+'.html'))
        else:
            cmd = ('cd "%s" && xsltproc --novalid %s content.xml >"%s.html" '
                   '2>"%s.log-xsltproc"') % (
                                            tmpdir,
                                            XSL_STYLESHEET_TRANSFORM,
                                            sansext(fullname),
                                            sansext(fullname)
                                            )
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
    return opendocument_to_html()
