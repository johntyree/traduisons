#!/usr/bin/env python
import sys
from distutils import core
from traduisons import msg_VERSION

Py2exeCommand = None
py2exe_args = {}
cmdclass_dict = {}

if 'py2exe' in sys.argv:
    # For side effects!
    import py2exe
    from py2exe import build_exe
    py2exe_args = {'windows':
                       [{"script": "traduisons/traduisons.py",
                         "icon_resources":
                             [(1, "traduisons/data/traduisons_icon.ico")]}],
                   'options': {'py2exe': {'includes': ['gio']}},
        }
    cmdclass_dict['py2exe'] = Py2exeCommand

    class Py2exeCommand(build_exe.py2exe):
        def get_hidden_imports(self):
            d = build_exe.py2exe.get_hidden_imports(self)
            d.setdefault('gtk._gtk', []).extend([
                    'cairo', 'pango', 'pangocairo', 'atk'])
            return d


core.setup(
    name = "traduisons",
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
    },
    cmdclass = cmdclass_dict,
    **py2exe_args
)
