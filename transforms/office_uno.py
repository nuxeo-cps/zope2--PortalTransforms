import re, os, tempfile
from uno import uno
from Products.PortalTransforms.libtransforms.utils import scrubHTML, bodyfinder
from Products.PortalTransforms.libtransforms.commandtransform \
    import commandtransform

class document(commandtransform):

    def __init__(self, name, data):
        """Initialization: create tmp work directory and copy the
        document into a file"""
        commandtransform.__init__(self, name)
        name = self.name()
        if not name.endswith('.doc'):
            name += ".doc"
        self.tmpdir, self.fullname = self.initialize_tmpdir(data, filename=name)

    def convert(self):
        "Convert the document"
        xStorable = None
        try:
            rUNO = uno()
            properties =  [ {
               'Name'  : 'Hidden',
               'Value' : rUNO.newBoolean(1)
               }]

            rProperties = rUNO.newPropertyValues(properties)
            xStorable = rUNO.new(
                "file://%s" % self.file, propertyValues=rProperties)[0]

            properties = [ { 'Name' : 'FilterName',
                             'Value' : 'swriter: HTML (StarWriter)' },
                           { 'Name' : 'Overwrite',
                             'Value' : rUNO.newBoolean(1) }
                           ]

            rProperties = rUNO.newPropertyValues(properties)

            xStorable.storeAsURL("file://%s.html" % self.file, rProperties)
        except Exception, e:
            from zLOG import LOG, ERROR
            LOG('PortalTransforms.office_uno', ERROR,
                "Unable to do conversion: %s" % str(e))
            pass

        if xStorable is not None:
            xStorable.dispose()

    def html(self):
        htmlfile = open("%s/%s.html" % (self.tmpdir, self.__name__), 'r')
        html = htmlfile.read()
        htmlfile.close()
        html = scrubHTML(html)
        body = bodyfinder(html)
        return body
