from rigging import *
from Products.PortalTransforms.utils import TransformException

import urllib
import time

class BaseTransform:
    def name(self):
        return getattr(self, '__name__', self.__class__.__name__)


class HtmlToText(BaseTransform):
    __implements__ = itransform
    inputs = ('text/html',)
    output = 'text/plain'

    def __call__(self, orig, **kwargs):
        orig = re.sub('<[^>]*>(?i)(?m)', '', orig)
        return urllib.unquote(re.sub('\n+', '\n', orig)).strip()

    def convert(self, orig, data, **kwargs):
        orig = self.__call__(orig)
        data.setData(orig)
        return data

class HtmlToTextWithEncoding(HtmlToText):
    output_encoding = 'ascii'

class FooToBar(BaseTransform):
    __implements__ = itransform
    inputs = ('text/*',)
    output = 'text/plain'

    def __call__(self, orig, **kwargs):
        orig = re.sub('foo', 'bar', orig)
        return urllib.unquote(re.sub('\n+', '\n', orig)).strip()

    def convert(self, orig, data, **kwargs):
        orig = self.__call__(orig)
        data.setData(orig)
        return data


class TransformNoIO(BaseTransform):
    __implements__ = itransform

class BadTransformMissingImplements(BaseTransform):
    __implements__ = None
    inputs = ('text/*',)
    output = 'text/plain'

class BadTransformBadMIMEType1(BaseTransform):
    __implements__ = itransform
    inputs = ('truc/muche',)
    output = 'text/plain'

class BadTransformBadMIMEType2(BaseTransform):
    __implements__ = itransform
    inputs = ('text/plain',)
    output = 'truc/muche'

class BadTransformNoInput(BaseTransform):
    __implements__ = itransform
    inputs = ()
    output = 'text/plain'

class BadTransformWildcardOutput(BaseTransform):
    __implements__ = itransform
    inputs = ('text/plain',)
    output = 'text/*'



class TestEngine(TestCase):
    def setUp(self):
        self.engine = TransformTool()
        self.engine.mimetypes_registry = MimeTypesTool()
        self.data = '<b>foo</b>'

    def tearDown(self):
        pass

    def register(self):
        #A default set of transforms to prove the interfaces work
        self.engine.registerTransform(HtmlToText())
        self.engine.registerTransform(FooToBar())

    def testRegister(self):
        self.register()

    def testFailRegister(self):
        register = self.engine.registerTransform
        self.assertRaises(TransformException, register, TransformNoIO())
        self.assertRaises(TransformException, register, BadTransformMissingImplements())
        self.assertRaises(TransformException, register, BadTransformBadMIMEType1())
        self.assertRaises(TransformException, register, BadTransformBadMIMEType2())
        self.assertRaises(TransformException, register, BadTransformNoInput())
        self.assertRaises(TransformException, register, BadTransformWildcardOutput())

    def testCall(self):
        self.register()
        data = self.engine('HtmlToText', self.data)
        self.failUnlessEqual(data, "foo")

        data = self.engine('FooToBar', self.data)
        self.failUnlessEqual(data, "<b>bar</b>")

    def testConvert(self):
        self.register()

        data = self.engine.convert('HtmlToText', self.data)
        self.failUnlessEqual(data.getData(), "foo")
        self.failUnlessEqual(data.getMetadata()['mimetype'], 'text/plain')
        self.failUnlessEqual(data.getMetadata().get('encoding'), None)
        self.failUnlessEqual(data.name(), "HtmlToText")

        self.engine.registerTransform(HtmlToTextWithEncoding())
        data = self.engine.convert('HtmlToTextWithEncoding', self.data)
        self.failUnlessEqual(data.getMetadata()['mimetype'], 'text/plain')
        self.failUnlessEqual(data.getMetadata()['encoding'], 'ascii')
        self.failUnlessEqual(data.name(), "HtmlToTextWithEncoding")

    def testConvertTo(self):
        self.register()

        data = self.engine.convertTo('text/plain', self.data, mimetype="text/html")
        self.failUnlessEqual(data.getData(), "foo")
        self.failUnlessEqual(data.getMetadata()['mimetype'], 'text/plain')
        self.failUnlessEqual(data.getMetadata().get('encoding'), None)
        self.failUnlessEqual(data.name(), "text/plain")

        self.engine.unregisterTransform('HtmlToText')
        self.engine.unregisterTransform('FooToBar')
        self.engine.registerTransform(HtmlToTextWithEncoding())

        data = self.engine.convertTo('text/plain', self.data, mimetype="text/html")
        self.failUnlessEqual(data.getMetadata()['mimetype'], 'text/plain')
        self.failUnlessEqual(data.getMetadata()['encoding'], 'ascii')
        self.failUnlessEqual(data.name(), "text/plain")

    def testChain(self):
        self.register()
        hb = chain('hbar')
        hb.registerTransform(HtmlToText())
        hb.registerTransform(FooToBar())

        self.engine.registerTransform(hb)
        cache = self.engine.convert('hbar', self.data)
        self.failUnlessEqual(cache.getData(), "bar")
        self.failUnlessEqual(cache.name(), "hbar")

    def testSame(self):
        data = "This is a test"
        mt = "text/plain"
        out = self.engine.convertTo('text/plain', data, mimetype=mt)
        self.failUnlessEqual(out.getData(), data)
        self.failUnlessEqual(out.getMetadata()['mimetype'], 'text/plain')

    def testCache(self):
        data = "This is a test"
        other_data = 'some different data'
        mt = "text/plain"
        self.engine.max_sec_in_cache = 20
        out = self.engine.convertTo(mt, data, mimetype=mt, object=self)
        self.failUnlessEqual(out.getData(), data, out.getData())
        out = self.engine.convertTo(mt, other_data, mimetype=mt, object=self)
        self.failUnlessEqual(out.getData(), data, out.getData())
        self.engine.max_sec_in_cache = -1
        out = self.engine.convertTo(mt, data, mimetype=mt, object=self)
        self.failUnlessEqual(out.getData(), data, out.getData())
        out = self.engine.convertTo(mt, other_data, mimetype=mt, object=self)
        self.failUnlessEqual(out.getData(), other_data, out.getData())


def test_suite():
    return TestSuite([
        makeSuite(TestEngine),
        ])


if __name__=='__main__':
    main(defaultTest='test_suite')
