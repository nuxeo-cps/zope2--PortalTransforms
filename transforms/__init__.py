### Register Transforms
### This is interesting because we don't expect all transforms to be
### available on all platforms. To do this we allow things to fail at
### two levels
### 1) Imports
###    If the import fails the module is removed from the list and
###    will not be processed/registered
### 2) Registration
###    A second phase happens when the loaded modules register method
###    is called and this produces an instance that will used to
###    implement the transform, if register needs to fail for now it
###    should raise an ImportError as well (dumb, I know)
#
# $Id$

from Products.PortalTransforms.libtransforms.utils import MissingBinary
from zLOG import LOG, DEBUG, WARNING

logKey = 'PortalTransforms'

modules = [
    'st',             # zopish
    'rest',           # docutils
    'word_to_html',   # uno, com, wvware
    'word_to_text',   # lxml, wvware
    'xls_to_html',    # xlhtml
    'ppt_to_html',    # ppthtml
    'ooo_to_html',    # unzip + xsltproc
    'opendocument_to_html',    # unzip + xsltproc http://opendocumentfoundation.org
    'ooo_to_docbook', # OOo2sDBK http://www.chez.com/ebellot/ooo2sdbk/
    'docbook_to_html',# xsltproc + http://docbook.sourceforge.net/
    'text_to_html',   # wrap text in a verbatim env
    'pdf_to_html',    # sf.net/projects/pdftohtml
    'pdf_to_text',    # www.foolabs.com/xpdf
    'rtf_to_html',    # sf.net/projects/rtf-converter
    'rtf_to_xml',     # sf.net/projects/rtf2xml
    'lynx_dump',      # lynx -dump
    'html_to_text',   # re based transform
    'python',         # python source files, no dependancies
    'identity',       # identity transform, no dependancies
    ]

g = globals()
transforms = []
for m in modules:
    try:
        LOG(logKey, DEBUG, "Importing module = %s" % m)
        ns = __import__(m, g, g, None)
        LOG(logKey, DEBUG, "Appending transform = %s" % ns)
        transforms.append(ns.register())
    except Exception, exc:
        LOG(logKey, WARNING, exc)


def initialize(engine):
    for transform in transforms:
        engine.registerTransform(transform)

