#!/usr/bin/env python
from distutils import core
from traduisons.traduisons import msg_VERSION

core.setup(
    name = "Traduisons",
    description = "A front-end to Google Translate",
    long_description = open('README').read(),
    version = str(msg_VERSION),
    author = 'John Tyree',
    author_email = '',
    url = 'http://traduisons.googlecode.com',
    license = "LICENSE",
    packages = ['traduisons'],
    #scripts = ['bin/traduisons.py']
    #package_data = [
        #{ 'traduisons' : ['../lICENSE'] }
    #],
    data_files = [
        ('', ["LICENSE"]),
        #('', ["LICENSE", "google-small-logo.png", "traduisons_icon.png"]),
    ],
)
