from distutils import core

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
    name = "Traduisons!",
    description = "A front-end to Google Translate.",
    version = "0.2.3",
    windows = [
        {"script": "traduisons.py",
        "icon_resources": [(1, "traduisons.ico")]
        }
    ],
#    options=opts,
    data_files=[("traduisons.png")],
    cmdclass={
        'py2exe': Py2exeCommand,
        },
)
