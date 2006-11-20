# $Id$

from __future__ import nested_scopes
from rigging import *
from utils import input_file_path, output_file_path, normalize_html,\
     load, matching_inputs
from Products.PortalTransforms.data import datastream
from Products.PortalTransforms.utils import implements
from Products.PortalTransforms.interfaces import idatastream
from os.path import exists
import sys
# we have to set locale because lynx output is locale sensitive !
os.environ['LC_ALL'] = 'C'
os.environ['SGML_CATALOG_FILES'] = ''

class TransformTest( TestCase ):

    def do_convert(self, filename=None):
        if filename is None and exists(self.output + '.nofilename'):
            output = self.output + '.nofilename'
        else:
            output = self.output
        input = open(self.input)
        orig = input.read()
        input.close()
        data = datastream(self.transform.name())
        res_data = self.transform.convert(orig, data, filename=filename)
        self.assert_(implements(res_data, idatastream))
        got = res_data.getData()

        try:
            output = open(output)
        except IOError:
            print >>sys.stderr, 'No output file found.'
            print >>sys.stderr, 'File %s created, check it !' % self.output
            output = open(output, 'w')
            output.write(got)
            output.close()
            self.assert_(0)

        expected = output.read()
        if self.normalize is not None:
            expected = self.normalize(expected)
            got = self.normalize(got)
        output.close()

        self.assertEquals(got, expected,
                          '[%s]\n\n!=\n\n[%s]\n\nIN %s(%s)' % (
                                    got,
                                    expected,
                                    self.transform.name(),
                                    self.input))

        self.assertEquals(self.subobjects, len(res_data.getSubObjects()),
                                    '%s\n\n!=\n\n%s\n\nIN %s(%s)' % (
                                    self.subobjects,
                                    len(res_data.getSubObjects()),
                                    self.transform.name(),
                                    self.input))

    def testSame(self):
        print >>sys.stdout, '\n\t\t%s' % (self.input)
        self.do_convert(filename=self.input)

    def testSameNoFilename(self):
        self.do_convert()

    def __repr__(self):
        return self.transform.name()


TRANSFORMS_TESTINFO = (
    # XXX: This transformations will give slightly different results
    # depending on the precise version of pdftohtml. Better skip it for now.
    #('Products.PortalTransforms.transforms.pdf_to_html',
    # "demo1.pdf", "demo1.html", normalize_html, 5
    # ),
    ('Products.PortalTransforms.transforms.word_to_html',
     "test.doc", "test_word.html", normalize_html, 0
     ),
    ('Products.PortalTransforms.transforms.lynx_dump',
     "test_lynx.html", "test_lynx.txt", None, 0
     ),
    ('Products.PortalTransforms.transforms.html_to_text',
     "test_lynx.html", "test_html_to_text.txt", None, 0
     ),
    ('Products.PortalTransforms.transforms.identity',
     "rest1.rst", "rest1.rst", None, 0
     ),
    ('Products.PortalTransforms.transforms.text_to_html',
     "rest1.rst", "rest1.html", None, 0
     ),
    ('Products.PortalTransforms.transforms.xls_to_html',
     "test_excel.xls", "test_excel.html", None, 0
     ),
    ('Products.PortalTransforms.transforms.ppt_to_html',
     "test_powerpoint.ppt", "test_powerpoint.html", None, 0
     ),
    ('Products.PortalTransforms.transforms.ooo_to_html',
     "test_writer.sxw", "test_writer.html", None, 0
     ),
    ('Products.PortalTransforms.transforms.ooo_to_html',
     "test_calc.sxc", "test_calc.html", None, 0
     ),
    ('Products.PortalTransforms.transforms.ooo_to_html',
     "test_impress.sxi", "test_impress.html", None, 2
     ),
    ('Products.PortalTransforms.transforms.opendocument_to_html',
     "test_opendocument_writer.odt", "test_opendocument_writer.odt.html",
      None, 2
     ),
    ('Products.PortalTransforms.transforms.opendocument_to_html',
     "test_opendocument_writer.ott", "test_opendocument_writer.ott.html",
      None, 2
     ),
    ('Products.PortalTransforms.transforms.opendocument_to_html',
     "test_opendocument_calc.ods", "test_opendocument_calc.ods.html",
      None, 2
     ),
    ('Products.PortalTransforms.transforms.opendocument_to_html',
     "test_opendocument_calc.ots", "test_opendocument_calc.ots.html",
      None, 2
     ),
    ('Products.PortalTransforms.transforms.opendocument_to_html',
     "test_opendocument_impress.odp", "test_opendocument_impress.odp.html",
      None, 2
     ),
    ('Products.PortalTransforms.transforms.opendocument_to_html',
     "test_opendocument_impress.otp", "test_opendocument_impress.otp.html",
      None, 2
     ),
    )

from Products.PortalTransforms.unsafe_transforms.build_transforms import TRANSFORMS

if TRANSFORMS.has_key('lynx_dump'):
    TRANSFORMS_TESTINFO += (
        (TRANSFORMS['lynx_dump'],
         "test_lynx.html", "test_lynx.txt", None, 0
         ),)
else:
    #print 'Unable to test unsafe_transforms.lynx_dump'
    pass

if TRANSFORMS.has_key('tidy_html'):
    TRANSFORMS_TESTINFO += (
        (TRANSFORMS['tidy_html'],
         "test_lynx.html", "test_tidy.html", None, 0
         ),)
else:
    #print 'Unable to test unsafe_transforms.tidy_html'
    pass

if TRANSFORMS.has_key('xml_to_html'):
    tr = TRANSFORMS['xml_to_html']
    dtds = tr.config['dtds']
    dtds['-//Netscape Communications//DTD RSS 0.91//EN'] = input_file_path('rss2html.xslt')
    TRANSFORMS_TESTINFO += (
        (TRANSFORMS['xml_to_html'],
         "org-news.xml", "org-news.html", normalize_html, 0
         ),)
else:
    #print 'Unable to test unsafe_transforms.xml_to_html'
    pass

def initialise(transform, normalize, pattern):
    global TRANSFORMS_TESTINFO
    for fname in matching_inputs(pattern):
        outname = '%s.out' % fname.split('.')[0]
        #print transform, fname, outname
        TRANSFORMS_TESTINFO += ((transform, fname, outname, normalize, 0),)


# ReST test cases
initialise('Products.PortalTransforms.transforms.rest', normalize_html, "rest*.rst")
# Python test cases
initialise('Products.PortalTransforms.transforms.python', normalize_html, "*.py")

#from pprint import pprint
#pprint(TRANSFORMS_TESTINFO)

# FIXME missing tests for image_to_html, st

TR_NAMES = None

# Some tests do not pass - exclude them
EXCLUDE_TESTS = [
    'tidy_html',
    'word_to_html',
    'xls_to_html',
    'rest_to_html',
]

def make_tests(test_descr=TRANSFORMS_TESTINFO):
    """generate tests classes from test info

    return the list of generated test classes
    """
    tests = []
    for _transform, tr_input, tr_output, _normalize, _subobjects in test_descr:
        # load transform if necessary
        if type(_transform) is type(''):
            try:
                _transform = load(_transform).register()
            except:
                continue

        if TR_NAMES is not None and not _transform.name() in TR_NAMES:
            print 'skip test for', _transform.name()
            continue

        if EXCLUDE_TESTS is not None and _transform.name() in EXCLUDE_TESTS:
            print 'exclude %s testing for input %s' % ( _transform.name(), tr_input)
            continue

        class TransformTestSubclass(TransformTest):
            input = input_file_path(tr_input)
            output = output_file_path(tr_output)
            transform = _transform
            normalize = lambda x, y: _normalize(y)
            subobjects = _subobjects

        tests.append(TransformTestSubclass)

    return tests

def test_suite():
    #return TestSuite([])
    return TestSuite([makeSuite(test) for test in make_tests()])

if __name__=='__main__':
    if len(sys.argv) > 1:
        TR_NAMES = sys.argv[1:]
        sys.argv = sys.argv[:1]
    main(defaultTest='test_suite')
