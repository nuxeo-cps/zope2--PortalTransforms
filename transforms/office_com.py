import win32api
import pythoncom
from win32com.client import constants, Dispatch

from Products.PortalTransforms.libtransforms.commandtransform \
    import commandtransform
from Products.PortalTransforms.libtransforms.utils import bodyfinder, scrubHTML

class document(commandtransform):

    def __init__(self, name, data):
        """Initialization: create tmp work
        directory and copy the document into a file"""
        commandtransform.__init__(self, name)
        name = self.name()
        if not name.endswith('.doc'):
            name += ".doc"
        self.tmpdir, self.fullname = self.initialize_tmpdir(data, filename=name)

    def convert(self):
        pythoncom.CoInitialize()

        try:
            word = Dispatch("Word.Application")
            word.Visible = 0
            doc = word.Documents.Open(self.fullname)
            #Let's set up some html saving options for this document
            word.ActiveDocument.WebOptions.RelyOnCSS = 1
            word.ActiveDocument.WebOptions.OptimizeForBrowser = 1
            word.ActiveDocument.WebOptions.BrowserLevel = constants.wdBrowserLevelV4
            word.ActiveDocument.WebOptions.OrganizeInFolder = 0
            word.ActiveDocument.WebOptions.UseLongFileNames = 1
            word.ActiveDocument.WebOptions.RelyOnVML = 0
            word.ActiveDocument.WebOptions.AllowPNG = 1
            #And then save the document into HTML
            doc.SaveAs(FileName="%s.htm" % (self.fullname),
                       FileFormat=constants.wdFormatHTML)

            #TODO -- Extract Metadata (author, title, keywords) so we
            #can populate the dublin core
            #Converter will need to be extended to return a dict of
            #possible MD fields

            doc.Close()
            word.Quit()
        finally:
            win32api.Sleep(1000) #Waiting for Word to close
            pythoncom.CoUninitialize()

    def html(self):
        htmlfile = open(self.fullname + '.htm', 'r')
        html = htmlfile.read()
        htmlfile.close()
        html = scrubHTML(html)
        body = bodyfinder(html)
        return body

## This function has to be done. It's more difficult to delete the temp
## directory under Windows, because there is sometimes a directory in it.
##    def cleanDir(self, tmpdir):
