#!/usr/bin/env python
from distutils import core
from traduisons.traduisons import msg_VERSION

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
)
