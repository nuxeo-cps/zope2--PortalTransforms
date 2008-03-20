# $Id$

from logging import getLogger
import re
import os
import sys
from os.path import basename, splitext, join
from cStringIO import StringIO
from sgmllib import SGMLParser

LOG_KEY = 'PortalTransforms.libtransforms.utils'
logger = getLogger(LOG_KEY)

HAVE_LXML = 0
try:
    from lxml import etree
    if getattr(etree, 'LXML_VERSION', tuple()) >= (1, 0):
        HAVE_LXML = 1
except ImportError:
    pass

bin_search_path = os.environ['PATH'].split(os.pathsep)

class MissingBinary(Exception): pass

def bin_search(binary):
    """search the bin_search_path  for a given binary
    returning its fullname or None"""
    if sys.platform == 'win32':
        # Directory containing 'binary' should be in PATH
        # XXX: I don't get this remark - SF
        return binary
    result = None
    mode   = os.R_OK | os.X_OK
    for p in bin_search_path:
        path = join(p, binary)
        if os.access(path, mode) == 1:
            result = path
            break
    else:
        raise MissingBinary('Unable to find binary "%s"' % binary)
    return result


def sansext(path):
    return splitext(basename(path))[0]


##########################################################################
# The code below is taken from CMFDefault.utils to remove
# dependencies for Python-only installations
##########################################################################

def bodyfinder(text):
    """ Return body or unchanged text if no body tags found.

    Always use html_headcheck() first.
    """
    lowertext = text.lower()
    bodystart = lowertext.find('<body')
    if bodystart == -1:
        return text
    bodystart = lowertext.find('>', bodystart) + 1
    if bodystart == 0:
        return text
    bodyend = lowertext.rfind('</body>', bodystart)
    if bodyend == -1:
        return text
    return text[bodystart:bodyend]


#
#   HTML cleaning code
#

# These are the HTML tags that we will leave intact
VALID_TAGS = { 'a'          : 1
             , 'address'    : 1
             , 'b'          : 1
             , 'base'       : 0
             , 'big'        : 1
             , 'blockquote' : 1
             , 'body'       : 1
             , 'br'         : 0
             , 'caption'    : 1
             , 'cite'       : 1
             , 'code'       : 1
             , 'div'        : 1
             , 'dl'         : 1
             , 'dt'         : 1
             , 'dd'         : 1
             , 'em'         : 1
             , 'font'       : 1
             , 'h1'         : 1
             , 'h2'         : 1
             , 'h3'         : 1
             , 'h4'         : 1
             , 'h5'         : 1
             , 'h6'         : 1
             , 'head'       : 1
             , 'hr'         : 0
             , 'html'       : 1
             , 'i'          : 1
             , 'img'        : 0
             , 'kbd'        : 1
             , 'label'      : 1
             , 'li'         : 1
           # , 'link'       : 1 type="script" hoses us
             , 'meta'       : 0
             , 'ol'         : 1
             , 'p'          : 1
             , 'pre'        : 1
             , 'span'       : 1
             , 'strong'     : 1
             , 'table'      : 1
             , 'tbody'      : 1
             , 'td'         : 1
             , 'tfoot'      : 1
             , 'th'         : 1
             , 'thead'      : 1
             , 'title'      : 1
             , 'tr'         : 1
             , 'tt'         : 1
             , 'u'          : 1
             , 'ul'         : 1
             }

NASTY_TAGS = { 'script'     : 1
             , 'object'     : 1
             , 'embed'      : 1
             , 'applet'     : 1
             }

class StrippingParser( SGMLParser ):
    """ Pass only allowed tags;  raise exception for known-bad.  """

    from htmlentitydefs import entitydefs # replace entitydefs from sgmllib

    def __init__( self ):

        SGMLParser.__init__( self )
        self.result = ""

    def handle_data( self, data ):

        if data:
            self.result = '%s%s' % (self.result, data)

    def handle_charref( self, name ):

        self.result = "%s&#%s;" % ( self.result, name )

    def handle_entityref(self, name):

        if self.entitydefs.has_key(name):
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''

        self.result = "%s&%s%s" % (self.result, name, x)

    def unknown_starttag(self, tag, attrs):

        """ Delete all tags except for legal ones.
        """
        if VALID_TAGS.has_key(tag):

            self.result = self.result + '<' + tag

            for k, v in attrs:

                if k.lower().startswith( 'on' ):
                    logger.debug('Javascript event "%s" not allowed.' % k)

                if v.lower().startswith( 'javascript:' ):
                    logger.debug('Javascript URI "%s" not allowed.' % v)

                self.result = '%s %s="%s"' % (self.result, k, v)

            endTag = '</%s>' % tag
            if VALID_TAGS.get(tag):
                self.result = self.result + '>'
            else:
                self.result = self.result + ' />'

        elif NASTY_TAGS.get( tag ):
            logger.debug('Dynamic tag "%s" not allowed.' % tag)

        else:
            pass    # omit tag

    def unknown_endtag(self, tag):

        if VALID_TAGS.get( tag ):

            self.result = "%s</%s>" % (self.result, tag)
            remTag = '</%s>' % tag


def sgmllibScrubHTML( html ):
    """ Strip illegal HTML tags from string text.  """
    parser = StrippingParser()
    parser.feed( html )
    parser.close()
    return parser.result


class BodyTextParser( StrippingParser ):
    """ Get body's text;  raise exception for known-bad tags.  """

    from htmlentitydefs import entitydefs # replace entitydefs from sgmllib

    def __init__( self ):

        StrippingParser.__init__( self )
        self.in_body = False

    def handle_data( self, data ):

        if data and self.in_body:
            self.result = '%s%s' % (self.result, data)

    def unknown_starttag(self, tag, attrs):

        if tag == "body":
            self.in_body = True
        elif NASTY_TAGS.get( tag ):
            logger.debug('Dynamic tag "%s" not allowed.' % tag)
        elif self.in_body:
            self.result = '%s ' % self.result

    def unknown_endtag(self, tag):

        pass    # omit tag


def sgmllibGetBodyText( html_fd ):
    """ Get the text of an html <body>.
    """
    parser = BodyTextParser()
    parser.feed( html_fd.read() )
    parser.close()
    return parser.result


if HAVE_LXML:
    _valid_tags = VALID_TAGS.keys()
    _valid_tags.sort()

    ENCODING = 'iso-8859-15'            # Should this be tunable?

    SCRUB_TRANSFORM = """
    <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
        <xsl:output method="html" encoding="%s"/>

        <xsl:template match="@*|$ALLOWED_NODE_TYPES">
            <xsl:copy>
                <xsl:apply-templates select="@*|node()"/>
            </xsl:copy>
        </xsl:template>
    </xsl:stylesheet>
    """ % ENCODING
    _transform = SCRUB_TRANSFORM.replace('$ALLOWED_NODE_TYPES', '|'.join(_valid_tags))
    _xslt_doc = etree.parse(StringIO(_transform))
    scrub_transform = etree.XSLT(_xslt_doc)

    def lxmlScrubHTML( html ):
        """ Strip illegal HTML tags from string text. Fast.  """
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html), parser)

        # First pass: check for forbidden tags/attribs, adapt content-type.
        for elem in tree.getroot().getiterator():
            if elem.tag in NASTY_TAGS:
                raise IllegalHTML(
                    'Dynamic tag "%s" not allowed.' % elem.tag)
            else:
                for attrib, value in elem.attrib.iteritems():
                    if attrib.startswith('on'):
                        raise IllegalHTML(
                            'Javascript event "%s" not allowed.' % attrib)
                    if value.lower().startswith('javascript:'):
                        raise IllegalHTML(
                            'Javascript URI "%s" not allowed.' % value)
            if elem.tag == 'meta' and 'http-equiv' in elem.attrib:
                if elem.attrib['http-equiv'].lower() == 'content-type':
                    if 'content' in elem.attrib:
                        content = elem.attrib['content'].lower()
                        if 'charset' in content:
                            elem.attrib['content'] = re.sub(
                                r'^(.*charset=)\s*\S+(.*)$', r'\1%s\2' % ENCODING,
                                content)
        # Second pass: remove non-approved tags.
        result = scrub_transform(tree)
        return str(result)

    TEXT_TRANSFORM = """
    <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
        <xsl:output method="text" encoding="%s"/>
        <xsl:template match="*">
            <xsl:text> </xsl:text>
            <xsl:copy>
                <xsl:apply-templates/>
            </xsl:copy>
        </xsl:template>

        <xsl:template match="/html/head//*">
        </xsl:template>

    </xsl:stylesheet>
    """ % ENCODING
    _xslt_doc = etree.parse(StringIO(TEXT_TRANSFORM))
    text_transform = etree.XSLT(_xslt_doc)

    def lxmlGetBodyText( html_fd ):
        """ Get the text of an html <body>.
        """
        parser = etree.HTMLParser()
        tree = etree.parse(html_fd, parser)
        result = text_transform(tree)
        return str(result)


if HAVE_LXML:
    scrubHTML = lxmlScrubHTML
    getBodyText = lxmlGetBodyText
else:
    scrubHTML = sgmllibScrubHTML
    getBodyText = sgmllibGetBodyText
