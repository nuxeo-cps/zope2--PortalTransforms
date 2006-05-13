
modname = 'PortalTransforms'
version = open('version.txt').read().strip()
numversion = version.split('.')

license = 'BSD like'
license_text = open('LICENSE.txt').read()
copyright = '''Copyright (c) 2003 LOGILAB S.A. (Paris, FRANCE)'''

author = "Archetypes developpement team"
author_email = "archetypes-devel@lists.sourceforge.net"

short_desc = "MIME types based transformations for the CMF"
long_desc = """This package provides two new CMF tools in order to
make MIME types based transformations on the portal contents and so an
easy to way to plugin some new transformations for previously
unsupported content types. You will find more info in the package's
README and docs directory.
.
It's part of the Archetypes project, but the only requirement to use it
is to have a CMF based site. If you are using Archetypes, this package
replaces the transform package.
.
Notice this package can also be used as a standalone Python package. If
you've downloaded the Python distribution, you can't make it a Zope
product since Zope files have been removed from this distribution.
"""

web = "http://www.sourceforge.net/projects/archetypes"
ftp = ""
mailing_list = "archetypes-devel@lists.sourceforge.net"

debian_name = "zope-cmftransforms"
debian_maintainer = "Sylvain Thenault"
debian_maintainer_email = "sylvain.thenault@logilab.fr"
debian_handler = "zope"
