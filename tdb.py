#!/usr/bin/env python
#
#       filename
#       
#       Copyright 2010 John Tyree <johntyree@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import urllib2, urllib, string, htmlentitydefs, re, sys, os
# In python <= 2.5, standard 'json' is not included 
try:
    import json
except(ImportError):
    import simplejson as json

def detectLang(text):
    '''Return the guessed two letter code corresponding to text'''
    urldata = urllib.urlencode({'v': 1.0, 'q': text})
    response = urllib2.urlopen(urllib2.Request('http://ajax.googleapis.com/ajax/services/language/detect?%s' % urldata, None, {'User-Agent':'Traduisons/%s' % msg_VERSION})).read()
    return json.loads(response)['responseData']['language']

class translator:
    msg_VERSION = "0.3.3"
    msg_BUGS = "Bugs, suggestions at <http://code.google.com/p/traduisons/issues/list>"
    dictLang = {'Detect Language' : 'auto',
                'Afrikaans' : 'af',
                'Albanian' : 'sq',
                'Arabic' : 'ar',
                'Belarusian' : 'be',
                'Bulgarian' : 'bg',
                'Catalan' : 'ca',
                'Chinese' : 'zh-CN',
                'Chinese (Simplified)' : 'zh-CN',
                'Chinese (traditional)' : 'zh-TW',
                'Croation' : 'hr',
                'Czech' : 'cs',
                'Danish' : 'da',
                'Dutch' : 'nl',
                'English' : 'en',
                'Estonian' : 'et',
                'Filipino' : 'tl',
                'Finnish' : 'fi',
                'French' : 'fr',
                'Galician' : 'gl',
                'German' : 'de',
                'Greek' : 'el',
                'Hebrew' : 'iw',
                'Hindi' : 'hi',
                'Hungarian' : 'hu',
                'Icelandic' : 'is',
                'Indonesian' : 'id',
                'Irish' : 'ga',
                'Gaelic' : 'ga',
                'Italian' : 'it',
                'Japanese' : 'ja',
                'Korean' : 'ko',
                'Latvian' : 'lv',
                'Lithuanian' : 'lt',
                'Macedonian' : 'mk',
                'Malay' : 'ms',
                'Maltese' : 'mt',
                'Norwegian' : 'no',
                'Persian' : 'fa',
                'Polish' : 'pl',
                'Portuguese' : 'pt',
                'Romanian' : 'ro',
                'Russian' : 'ru',
                'Serbian' : 'sr',
                'Slovak' : 'sk',
                'Slovenian' : 'sl',
                'Spanish' : 'es',
                'Swahili' : 'sw',
                'Swedish' : 'sv',
                'Thai' : 'th',
                'Turkish' : 'tr',
                'Ukrainian' : 'uk',
                'Vietnamese' : 'vi',
                'Welsh' : 'cy',
                'Yiddish' : 'yi',
                }

    def __init__(self, fromLang = 'auto', toLang = 'en', start_text = None):
        self._fromLang = fromLang
        self._toLang = toLang
        self._text = start_text

    def toLang(self, l = None):
        if l:
            if l == 'auto': return False
            ## Check character code
            if l in self.dictLang.values(): self._toLang = l
            else:
                ## Check language name
                self._toLang = self.dictLang.get(string.capitalize(l), self._toLang)
        return self._toLang

    def fromLang(self, l = None):
        if l:
            ## Check character code
            if l in self.dictLang.values():
                self._toLang = l
            else:
                ## Check language name
                self._toLang = self.dictLang.get(string.capitalize(l), self._toLang)
        return self._fromLang

    def swapLang(self):
        f = self._fromLang
        t = self._toLang
        if not self._toLang(f) or not self._fromLang(t):
            self._toLang(t)
            self._fromLang(f)
            return False
        return True

    def text(self, t = None):
        if t:
            t = unicode(t)
            self._text = t
        return self._text

    def translate(self):
        """Return translated text from fromLang to toLang."""
        if self._text == None: return ''
        try:
            ## Use the official google translate-api via REST
            ## 'auto' needs to be set to blank now
            if self._fromLang == 'auto':
                fromLangTemp = ''
            else:
                fromLangTemp = self._fromLang
            urldata = urllib.urlencode({'v': 1.0,
                                        'q': self._text,
                                        'langpair' : '%s|%s' % (fromLangTemp, self._toLang)
                                       })
            url = 'http://ajax.googleapis.com/ajax/services/language/translate?%s' % (urldata)
            headers = {'User-Agent':'Traduisons/%s' % self.msg_VERSION}
            response = urllib2.urlopen(urllib2.Request(url, None, headers)).read()
            translated_text = self._unquotehtml(json.loads(response)['responseData']['translatedText'])

        ##  If translated_text is empty (no translation found) handle exception.
        except TypeError, e:
            self._error = ('No translation available', e)
            translated_text = False
        ##  Not sure about this, some kind of error when the net is unavailable perhaps?
        except urllib2.HTTPError, e:
            self._error = ('urllib2.HTTPError', e)
            translated_text = False
        ## If the url ever changes...
        except urllib2.URLError, e:
            self._error = (e.reason, e)
        return translated_text

    def _unquotehtml(s):
        """Convert a HTML quoted string into unicode object.
        Works with &#XX; and with &nbsp; &gt; etc."""
        def convertentity(m):
            if m.group(1)=='#':
                try:
                    return chr(int(m.group(2)))
                except XValueError:
                    return '&#%s;' % m.group(2)
            try:
                return htmlentitydefs.entitydefs[m.group(2)]
            except KeyError:
                return ('&%s;' % m.group(2)).decode('ISO-8859-1')
        return re.sub(r'&(#)?([^;]+);',convertentity,s)

def main():
    return 0

if __name__ == '__main__': main()
