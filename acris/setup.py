import os
import sys

from setuptools import setup
from distutils.sysconfig import get_python_lib

'''
is the Python package in your project. It's the top-level folder containing the
__init__.py module that should be in the same directory as your setup.py file
/-
  |- README.rst
  |- CHANGES.txt
  |- setup.py
  |- dogs
     |- __init__.py
     |- catcher.py

To create package and upload:

  python setup.py register
  python setup.py sdist
  twine upload -s dist/path/to/gz

'''
PACKAGE = "acris"

'''
NAME is usually similar to or the same as your PACKAGE name but can be whatever you want.
The NAME is what people will refer to your software as, the name under which your
software is listed in PyPI and—more importantly—under which users will install it
(for example, pip install NAME).
'''
NAME = PACKAGE

'''
DESCRIPTION is just a short description of your project. A sentence will suffice.
'''
DESCRIPTION = '''acris is a python library of programming patterns that we use, at acrisel, in Python projects and choose to contribute to Python community'''

'''
AUTHOR and AUTHOR_EMAIL are what they sound like: your name and email address. This
information is optional, but it's good practice to supply an email address if people
want to reach you about the project.
'''
AUTHOR = 'Acrisel Team'
AUTHOR_EMAIL = 'support@acrisel.com'

'''
URL is the URL for the project. This URL may be a project website, the Github repository,
or whatever URL you want. Again, this information is optional.
'''
URL = 'https://github.com/Acrisel/acris'

version_file=os.path.join(PACKAGE, 'VERSION.py')
with open(version_file, 'r') as vf:
    vline=vf.read()
VERSION = vline.strip().partition('=')[2].replace("'", "")

# Warn if we are installing over top of an existing installation. This can
# cause issues where files that were deleted from a more recent Accord are
# still present in site-packages. See #18115.
overlay_warning = False
if "install" in sys.argv:
    lib_paths = [get_python_lib()]
    if lib_paths[0].startswith("/usr/lib/"):
        # We have to try also with an explicit prefix of /usr/local in order to
        # catch Debian's custom user site-packages directory.
        lib_paths.append(get_python_lib(prefix="/usr/local"))

    for lib_path in lib_paths:
        existing_path = os.path.abspath(os.path.join(lib_path, PACKAGE))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after the
            # command is run, so it's more likely to be seen.
            overlay_warning = True
            break

scripts=['acris/osutils/commdir.py',
         'acris/osutils/bee.py',
         'acris/osutils/csv2xlsx.py',
         'acris/osutils/prettyxml.py',
         'acris/osutils/mail.py',
         'acris/osutils/mrun.py',
         'acris/misc/xlsx2rst.py',]

# Find all sub packages
import os
packages=list()
for root, dirs, files in os.walk(PACKAGE, topdown=False):
    if os.path.isfile(os.path.join(root,'__init__.py')):
        packages.append(root)

setup_info={'name': NAME,
 'version': VERSION,
 'url': URL,
 'author': AUTHOR,
 'author_email': AUTHOR_EMAIL,
 'description': DESCRIPTION,
 'long_description': open("README.rst", "r").read(),
 'license': 'MIT',
 'keywords': 'library sequence logger yield singleton thread synchronize resource pool utilities os ssh xml excel mail',
 'packages': packages,
 'scripts' : scripts,
 'install_requires': ['pexpect', 'openpyxl', 'acrilib'],
 'extras_require': {'dev': [], 'test': []},
 'classifiers': ['Development Status :: 5 - Production/Stable',
                 'Environment :: Other Environment',
                 #'Framework :: Project Settings and Operation',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 3',
                 'Topic :: Software Development :: Libraries :: Application '
                 'Frameworks',
                 'Topic :: Software Development :: Libraries :: Python '
                 'Modules']}
setup(**setup_info)


if overlay_warning:
    sys.stderr.write("""

========
WARNING!
========

You have just installed %(PACKAGE)s over top of an existing
installation, without removing it first. Because of this,
your install may now include extraneous files from a
previous version that have since been removed from
Accord. This is known to cause a variety of problems. You
should manually remove the

%(existing_path)s

directory and re-install %(PACKAGE)s.

""" % {"existing_path": existing_path, 'PACKAGE': PACKAGE})
