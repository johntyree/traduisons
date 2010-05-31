#!/usr/bin/env python
from distutils import core

# For side effects!
import py2exe

from py2exe import build_exe
from traduisons import msg_VERSION

class Py2exeCommand(build_exe.py2exe):
    def get_hidden_imports(self):
        d = build_exe.py2exe.get_hidden_imports(self)
        d.setdefault('gtk._gtk', []).extend([
                'cairo', 'pango', 'pangocairo', 'atk'])
        return d

core.setup(
    name = "Traduisons!",
    description = "A front-end to Google Translate",
    version = str(msg_VERSION),
    author = 'John Tyree',
    author_email = 'johntyree@gmail.com',
    url = 'http://traduisons.googlecode.com',
    windows = [
        {"script": "traduisons.py",
        "icon_resources": [(1, "traduisons_icon.ico")]
        }
    ],
    options = {
        'py2exe': {
            'packages': ['simplejson'],
            'dll_excludes': ['msvcr71.dll'],
        },
    },

    data_files = [
        ("google-small-logo.png"),
    ],
    cmdclass={
        'py2exe': Py2exeCommand,
        },
)
