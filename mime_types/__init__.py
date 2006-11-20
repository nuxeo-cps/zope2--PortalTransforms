# $Id$

from Products.PortalTransforms.interfaces import iclassifier
from Products.PortalTransforms.MimeTypeItem import MimeTypeItem, \
     MimeTypeException

from types import InstanceType
import re

class text_plain(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = "Plain Text"
    mimetypes  = ('text/plain',)
    extensions = ('txt',)
    binary     = 0

class text_structured(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = "Structured Text"
    mimetypes  = ('text/structured',)
    extensions = ('stx',)
    binary     = 0

class text_rest(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = "reST"
    mimetypes  = ("text/x-rst", "text/restructured",)
    extensions = ("rst", "rest", "restx") #txt?
    binary     = 0

class text_python(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = "python"
    mimetypes  = ("text/python-source", "text/x-python",)
    extensions = ("py",)
    binary     = 0

class application_rtf(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = 'rtf'
    mimetypes  = ('application/rtf',)
    extensions = ('rtf',)
    binary     = 1

class application_msword(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "Microsoft Word Document"
    mimetypes  = ('application/msword',)
    extensions = ('doc',)
    binary     = 1

class application_msexcel(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "Microsoft Excel Document"
    mimetypes  = ('application/vnd.ms-excel',)
    extensions = ('xls',)
    binary     = 1

class application_mspowerpoint(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "Microsoft PowerPoint Document"
    mimetypes  = ('application/vnd.ms-powerpoint',)
    extensions = ('ppt',)
    binary     = 1

class application_docbook(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "DocBook XML Document"
    mimetypes  = ('application/docbook+xml',)
    extensions = ('doc.xml', 'docb.xml', 'docb',)
    binary     = 0

class application_writer(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 1.x Writer Document"
    mimetypes  = ('application/vnd.sun.xml.writer',)
    extensions = ('sxw',)
    binary     = 1

class application_writer_template(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 1.x Writer Template"
    mimetypes  = ('application/vnd.sun.xml.writer.template',)
    extensions = ('stw',)
    binary     = 1

class application_impress(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 1.x Impress Document"
    mimetypes  = ('application/vnd.sun.xml.impress',)
    extensions = ('sxi',)
    binary     = 1

class application_impress_template(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 1.x Impress Template"
    mimetypes  = ('application/vnd.sun.xml.impress.template',)
    extensions = ('sti',)
    binary     = 1

class application_calc(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 1.x Calc Document"
    mimetypes  = ('application/vnd.sun.xml.calc',)
    extensions = ('sxc',)
    binary     = 1

class application_calc_template(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 1.x Calc Template"
    mimetypes  = ('application/vnd.sun.xml.calc.template',)
    extensions = ('stc',)
    binary     = 1

class application_draw(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 1.x Draw Document"
    mimetypes  = ('application/vnd.sun.xml.draw',)
    extensions = ('sxd',)
    binary     = 1
    
class application_draw_template(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 1.x Draw Template"
    mimetypes  = ('application/vnd.sun.xml.draw.template',)
    extensions = ('std',)
    binary     = 1

class application_opendocument_calc(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 2.x Calc Document"
    mimetypes  = ('application/vnd.oasis.opendocument.spreadsheet',)
    extensions = ('ods',)
    binary     = 1

class application_opendocument_calc_template(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 2.x Calc Template"
    mimetypes  = ('application/vnd.oasis.opendocument.spreadsheet-template',)
    extensions = ('ots',)
    binary     = 1
    
class application_opendocument_writer(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 2.x Writer Document"
    mimetypes  = ('application/vnd.oasis.opendocument.text',)
    extensions = ('odt',)
    binary     = 1
    
class application_opendocument_writer_template(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 2.x Writer Template"
    mimetypes  = ('application/vnd.oasis.opendocument.text-template',)
    extensions = ('ott',)
    binary     = 1

class application_opendocument_impress(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 2.x Impress Document"
    mimetypes  = ('application/vnd.oasis.opendocument.presentation',)
    extensions = ('odp',)
    binary     = 1

class application_opendocument_impress_template(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 2.x Impress Template"
    mimetypes  = ('application/vnd.oasis.opendocument.presentation-template',)
    extensions = ('otp',)
    binary     = 1

class application_opendocument_graphics(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 2.x Draw Document"
    mimetypes  = ('application/vnd.oasis.opendocument.graphics',)
    extensions = ('odg',)
    binary     = 1

class application_opendocument_graphics_template(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 2.x Draw Template"
    mimetypes  = ('application/vnd.oasis.opendocument.graphics-template',)
    extensions = ('otg',)
    binary     = 1

class application_openofficeorg_extension(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "OpenOffice.org 2.0.4+ Extension"
    mimetypes  = ('application/vnd.openofficeorg.extension',)
    extensions = ('oxt',)
    binary     = 1

class text_xml(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__ + (iclassifier,)

    __name__   = "Extensible Markup Language"
    mimetypes  = ('text/xml',)
    extensions = ('xml',)
    binary     = 0

    def classify(self, data):
        m = re.search('<?xml.*?>', data)
        if m:
            return 1 # True
        return None  # False

class application_octet_stream(MimeTypeItem):
    """we need to be sure this one exists"""
    __name__   = "Octet Stream"
    mimetypes = ('application/octet-stream',)
    binary     = 1
    extensions = ()

class application_x_gtar(MimeTypeItem):
    __implements__ = MimeTypeItem.__implements__
    __name__   = "application/x-gtar"
    mimetypes = ('application/x-gtar',)
    binary     = 1
    extensions = ('tar.gz', 'tgz', )

# TODO: this list should be automagically computed using introspection.
reg_types = [
    text_plain,
    application_msword,
    application_msexcel,
    application_mspowerpoint,
    application_docbook,
    application_writer,
    application_writer_template,
    application_impress,
    application_impress_template,
    application_calc,
    application_calc_template,
    application_draw,
    application_draw_template,
    application_opendocument_writer,
    application_opendocument_writer_template,
    application_opendocument_impress,
    application_opendocument_impress_template,
    application_opendocument_calc,
    application_opendocument_calc_template,
    application_opendocument_graphics,
    application_opendocument_graphics_template,
    application_openofficeorg_extension,
    text_xml,
    text_structured,
    text_rest,
    text_python,
    application_octet_stream,
    application_rtf,
    application_x_gtar,
]

import mimetypes as pymimetypes

def initialize(registry):
    for mt in reg_types:
        if type(mt) != InstanceType:
            mt = mt()
        registry.register(mt)

    #Find things that are not in the specially registered mimetypes
    #and add them using some default policy, none of these will impl
    #iclassifier
    for ext, mt in pymimetypes.types_map.items():
        if ext[0] == '.':
            ext = ext[1:]
        try:
            mto =  registry.lookup(mt)
        except MimeTypeException:
            # malformed MIME type
            continue
        if mto:
            mto = mto[0]
            if not ext in mto.extensions:
                registry.register_extension(ext, mto)
                mto.extensions += (ext, )
            continue
        isBin = mt.split('/', 1)[0] != "text"
        registry.register(MimeTypeItem(mt, (mt,), (ext,), isBin))
