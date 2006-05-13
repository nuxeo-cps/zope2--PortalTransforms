# $Id$
from Products.PortalTransforms.interfaces import itransform

EXTRACT_BODY  = 1
EXTRACT_STYLE = 0

FIX_IMAGES    = 1
IMAGE_PREFIX  = "img_"

import os
if os.name == 'posix':
    try:
        import PyUNO
        from office_uno import document
    except:
        from office_wvware import document
else:
    #from office_com import document
    from office_wvware import document

from os.path import basename

class word_to_html:
    __implements__ = itransform

    __name__ = 'word_to_html'
    inputs   = ('application/msword',)
    output  = 'text/html'

    def name(self):
        return self.__name__

    def convert(self, data, cache, **kwargs):
        orig_file = basename((kwargs.get('filename') or 'unknown.doc'))

        doc = document(orig_file, data)
        doc.convert()
        html = doc.html()

        path, images = doc.subObjects(doc.tmpdir)
        objects = {}
        if images:
            doc.fixImages(path, images, objects)
        doc.cleanDir(doc.tmpdir)

        cache.setData(html)
        cache.setSubObjects(objects)
        return cache

def register():
    return word_to_html()
