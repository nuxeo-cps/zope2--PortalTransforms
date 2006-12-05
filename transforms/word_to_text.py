# $Id$

import os
import sys
import re
from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.transforms import office_wvware
from Products.PortalTransforms.libtransforms.utils import getBodyText

_re_compactwhites = re.compile(r'\s+')

class document(office_wvware.document):

    def text(self):
        htmlfile = open(os.path.join(self.tmpdir, self.__name__+'.html'))
        text = getBodyText(htmlfile)
        text = _re_compactwhites.sub(' ', text)
        return text


class word_to_text:
    __implements__ = itransform

    __name__ = 'word_to_text'
    inputs   = ('application/msword',)
    output  = 'text/plain'

    def name(self):
        return self.__name__

    def convert(self, data, cache, **kwargs):
        orig_file = os.path.basename((kwargs.get('filename') or 'unknown.doc'))

        doc = document(orig_file, data)
        doc.convert()
        text = doc.text()

        doc.cleanDir(doc.tmpdir)

        cache.setData(text)
        return cache

def register():
    return word_to_text()
