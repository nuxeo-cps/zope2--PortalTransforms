# -*- coding: iso-8859-15 -*-
# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com>
# Author: Stéfane Fermigier <sf@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

"""

"""
import os
import re
import sys

from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.utils import basename, sansext
from Products.PortalTransforms.libtransforms.commandtransform \
    import commandtransform


class ppt_to_html(commandtransform):
    __implements__ = itransform

    __name__ = "ppt_to_html"
    inputs = ('application/vnd.ms-powerpoint',)
    output = 'text/html'

    binaryName = "ppthtml"
    binaryArgs = ""

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
        kwargs['filename'] = basename((kwargs.get('filename') or 'unknown.ppt'))

        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        html = self.invokeCommand(tmpdir, fullname)
        path, images = self.subObjects(tmpdir)
        objects = {}
        if images:
            self.fixImages(path, images, objects)
        self.cleanDir(tmpdir)
        cache.setData(html)
        cache.setSubObjects(objects)
        return cache

    def invokeCommand(self, tmpdir, fullname):
        # FIXME: character encoding
        basename = sansext(fullname)
        if sys.platform == 'win32':
            cmd = '%s %s "%s" > "%s.html" 2>"%s"' % (
                self.binary,
                self.binaryArgs,
                fullname,
                os.path.join(tmpdir, basename),
                os.path.join(tmpdir, 'error_log'))
        else:
            cmd = 'cd "%s" && %s %s "%s" 1> "%s.html" 2>error_log' % (
                tmpdir, self.binary, self.binaryArgs, fullname, basename)
        os.system(cmd)
        try:
            htmlfile = open(os.path.join(tmpdir, basename+'.html'))
            html = htmlfile.read()
            htmlfile.close()
            # Remove filename inserted by ppthtml
            html = re.sub("<TITLE>(.*?)</TITLE>", "", html)
        # XXX: qualify this except !
        except:
            try:
                return open(os.path.join(tmpdir, 'error_log')).read()
            except:
                return ''
        return html

def register():
    return ppt_to_html()
