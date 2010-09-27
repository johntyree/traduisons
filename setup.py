#!/usr/bin/env python
from distutils import core
from traduisons.traduisons import msg_VERSION
import sys

Py2exeCommand = None
if 'py2exe' in sys.argv:
    # For side effects!
    import py2exe
    from py2exe import build_exe
    class Py2exeCommand(build_exe.py2exe):
        def get_hidden_imports(self):
            d = build_exe.py2exe.get_hidden_imports(self)
            d.setdefault('gtk._gtk', []).extend([
                    'cairo', 'pango', 'pangocairo', 'atk'])
            return d

core.setup(
    name = "Traduisons",
    description = "A front-end to Google Translate",
    long_description = open('README').read(),
    version = str(msg_VERSION),
    author = 'John Tyree',
    author_email = 'test',
    url = 'http://traduisons.googlecode.com',
    license = open('LICENSE').read(),
    packages = ['traduisons'],
    package_data = {
        'traduisons' : ['data/traduisons_icon.png',
                        'data/traduisons_icon.ico',
                        'data/google-small-logo.png']
    }

    # py2exe data
    windows = [
        {"script": "traduisons.py",
        "icon_resources": [(1, "traduisons_icon.ico")]
        }
    ],
    options = {
        'py2exe': {
            'includes': ['gio'],
        },
    },
    cmdclass={
        'py2exe': Py2exeCommand,
    },
)

