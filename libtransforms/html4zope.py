# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Simple HyperText Markup Language document tree Writer.

The output conforms to the HTML 4.01 Transitional DTD and to the Extensible
HTML version 1.0 Transitional DTD (*almost* strict).  The output contains a
minimum of formatting information.  A cascading style sheet ("default.css" by
default) is required for proper viewing with a modern graphical browser.

http://cvs.zope.org/Zope/lib/python/docutils/writers/Attic/html4zope.py?rev=1.1.2.2&only_with_tag=ajung-restructuredtext-integration-branch&content-type=text/vnd.viewcvs-markup
"""

__docformat__ = 'reStructuredText'

from docutils import nodes
from docutils.writers.html4css1 import Writer as CSS1Writer, HTMLTranslator as CSS1HTMLTranslator
import os

default_level = int(os.environ.get('STX_DEFAULT_LEVEL', 3))

class Writer(CSS1Writer):
    def __init__(self):
        CSS1Writer.__init__(self)
        self.translator_class = HTMLTranslator

class HTMLTranslator(CSS1HTMLTranslator):

    def astext(self):
        return ''.join(self.body)

    def visit_title(self, node):
        """Only 6 section levels are supported by HTML."""

        if isinstance(node.parent, nodes.topic):
            self.body.append(
                  self.starttag(node, 'p', '', CLASS='topic-title'))
            if node.parent.hasattr('id'):
                self.body.append(
                    self.starttag({}, 'a', '', name=node.parent['id']))
                self.context.append('</a></p>\n')
            else:
                self.context.append('</p>\n')
        elif self.section_level == 0:
            # document title
            self.head.append('<title>%s</title>\n'
                             % self.encode(node.astext()))
            self.body.append(self.starttag(node, 'h%d' % default_level, '', CLASS='title'))
            self.context.append('</h%d>\n' % default_level)
        else:
            self.body.append(
                  self.starttag(node, 'h%s' % (default_level+self.section_level-1), ''))
            atts = {}
            if node.parent.hasattr('id'):
                atts['name'] = node.parent['id']
            if node.hasattr('refid'):
                atts['class'] = 'toc-backref'
                atts['href'] = '#' + node['refid']
            self.body.append(self.starttag({}, 'a', '', **atts))
            self.context.append('</a></h%s>\n' % ((default_level+self.section_level-1)))

    def visit_subtitle(self, node):
        if isinstance(node.parent, nodes.sidebar):
            self.body.append(self.starttag(node, 'p', '',
                                           CLASS='sidebar-subtitle'))
            self.context.append('</p>\n')
        else:
            self.body.append(
                  self.starttag(node, 'h%s' % (default_level+1), '', CLASS='subtitle'))
            self.context.append('</h%s>\n' % (default_level+1))
