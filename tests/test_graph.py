from rigging import *
from utils import input_file_path
FILE_PATH = input_file_path("demo1.pdf")


class TestGraph(TestCase):
    def testGraph(self):
        ### XXX Local file and expected output
        data = open(FILE_PATH, 'r').read()
        out = transformer.convertTo('text/plain', data, filename=FILE_PATH)
        assert(out.getData())


def test_suite():
    return TestSuite([
        makeSuite(TestGraph),
        ])


if __name__=='__main__':
    main(defaultTest='test_suite')
