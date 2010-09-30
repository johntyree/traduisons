#!/usr/bin/env python
#
#       translator.py
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

"""
    Traduisons!
    http://traduisons.googlecode.com

    Python bindings to Google Translate RESTful API
"""

class translator:
    '''Abstraction of the Google Translate RESTful API'''

    dictLang = {'Detect Language': 'auto',
                'Afrikaans': 'af',
                'Albanian': 'sq',
                'Arabic': 'ar',
                'Armenian': 'hy',
                'Azerbaijani': 'az',
                'Basque': 'eu',
                'Belarusian': 'be',
                'Bulgarian': 'bg',
                'Catalan': 'ca',
                'Chinese': 'zh-CN',
                'Chinese (Simplified)': 'zh-CN',
                'Chinese (Traditional)': 'zh-TW',
                'Croatian': 'hr',
                'Czech': 'cs',
                'Danish': 'da',
                'Dutch': 'nl',
                'English': 'en',
                'Estonian': 'et',
                'Filipino': 'tl',
                'Finnish': 'fi',
                'French': 'fr',
                'Gaelic': 'ga',
                'Galician': 'gl',
                'Georgian': 'ka',
                'German': 'de',
                'Greek': 'el',
                'Haitian Creole': 'ht',
                'Hebrew': 'iw',
                'Hindi': 'hi',
                'Hungarian': 'hu',
                'Icelandic': 'is',
                'Indonesian': 'id',
                'Irish': 'ga',
                'Italian': 'it',
                'Japanese': 'ja',
                'Korean': 'ko',
                'Latvian': 'lv',
                'Lithuanian': 'lt',
                'Macedonian': 'mk',
                'Malay': 'ms',
                'Maltese': 'mt',
                'Norwegian': 'no',
                'Persian': 'fa',
                'Polish': 'pl',
                'Portuguese': 'pt',
                'Romanian': 'ro',
                'Russian': 'ru',
                'Serbian': 'sr',
                'Slovak': 'sk',
                'Slovenian': 'sl',
                'Spanish': 'es',
                'Swahili': 'sw',
                'Swedish': 'sv',
                'Thai': 'th',
                'Turkish': 'tr',
                'Ukrainian': 'uk',
                'Urdu': 'ur',
                'Vietnamese': 'vi',
                'Welsh': 'cy',
                'Yiddish': 'yi',
                }

    def __init__(self, fromLang = 'auto', toLang = 'en', start_text = ''):
        if not self.fromLang(fromLang): self.fromLang('auto')
        if not self.toLang(toLang): self.toLang('en')
        self._text = start_text

    def is_latest(self):
        '''Phone home to check if we are up to date.'''
        try:
            self.msg_LATEST
        except AttributeError:
            url = 'http://traduisons.googlecode.com/svn/trunk/LATEST-IS'
            ver = urllib2.urlopen(url).read().strip()
            self.msg_LATEST = version.StrictVersion(ver)
        return msg_VERSION >= self.msg_LATEST

    def update_languages(self):
        '''
        Naively try to determine if new languages are available by scraping
        http://translate.google.com
        '''

        headers = {'User-Agent': 'Traduisons/%s' % (msg_VERSION,)}
        req = urllib2.Request('http://translate.google.com', None, headers)
        resp = urllib2.urlopen(req).read()
        # namelist_regex should match Capitalized list of languages names:
        # "English, French, Klingon, Etc...."
        namelist_regex = '<meta name=description content="Google&#39;s free online language translation service instantly translates text and web pages. This translator supports: (.*?)">'
        m = re.search(namelist_regex, resp)
        d = {}
        if m:
            names = m.group(1).split(', ')
            for name in names:
                # Match abbreviated language code to language name from m
                code_regex = '<option  value="([^"]+)">%s[^<]*</option>'
                n = re.search(code_regex % (name,), resp)
                if n:
                    d[name] = n.group(1)
                else:
                    # If no match found, just abort. Things are too messy
                    return False
            # These aren't listed, but are expected by users
            for k, v in [('Detect Language', 'auto'),
                         ('Gaelic', 'ga'),
                         ('Chinese (Traditional)', 'zh-TW'),
                         ('Chinese (Simplified)', 'zh-CN')]:
                d[k] = v
            # Remove any default languages that were not found
            for k in self.dictLang:
                if not d.has_key(k): print k, ': Unavailable'
            self.dictLang = d
        else:
            print 'Unable to update_languages'
        return False

    def pretty_print_languages(self, right_justify = True):
        '''
        Return a string of pretty-printed, newline-delimited languages in
        the format Name : code
        '''
        l = []
        width = 0
        if right_justify:
            width = max([len(x) for x in self.dictLang.keys()])
        for item in sorted(self.dictLang.keys()):
            line = ''.join(["%", str(width), 's : %s']) % \
                (item, self.dictLang[item])
            l.append(line)
        return '\n'.join(l)

    def toLang(self, l = None):
        '''Get or set target language'''
        if l is not None:
            if l == 'auto': return False
            ## Check character code
            if l in self.dictLang.values(): self._toLang = l
            else:
                ## Check language name
                self._toLang = self.dictLang.get(string.capitalize(l),
                                                 self._toLang)
        return self._toLang

    def fromLang(self, l = None):
        '''Get or set source language.'''
        if l is not None:
            ## Check character code
            if l in self.dictLang.values():
                self._fromLang = l
            else:
                ## Check language name
                self._fromLang = self.dictLang.get(string.capitalize(l),
                                                   self._fromLang)
        return self._fromLang

    def swapLang(self):
        '''Reverse direction the direction of translation.'''
        f = self._fromLang
        t = self._toLang
        if not self.toLang(f) or not self.fromLang(t):
            self._toLang = t
            self._fromLang = f
            return False
        return True

    def raw_text(self, t = None):
        '''
        Get or set translation text, ignoring embedded directives such
        as '/' and '.'.
        '''
        if t is not None:
            t = unicode(t)
            self._text = t
        return self._text

    def text(self, text = None):
        '''
        Get or set translation text, handling embedded directives such
        as '/' and '.'.
        '''
        if text is None: return self._text
        if text == '':
            self._text = u''
            return
        RETURN_CODE = False
        if text in ('.exit', '.quit', '.quitter', 'exit()'):
            RETURN_CODE = 'EXIT'
        ## Use the '/' character to reverse translation direction.
        elif text[0] == '/' or text[-1] == '/':
            self.swapLang()
            try:
                # Cut off the '/' character if necessary
                if text[-1] == '/': text = text[:-1]
                elif text[0] == '/': text = text[1:]
            except:
                pass
            self._text = text
            RETURN_CODE = 'SWAP'
        elif text in ('?', 'help', '-h', '-help', '--help'):
            RETURN_CODE = 'HELP'
        ## Use '|' character to change translation language(s).
        elif text.find('|') + 1:
            self.fromLang(text[0:text.find('|')])
            self.toLang(text[text.find('|') + 1:])
            RETURN_CODE = 'CHANGE'
        else:
            self._text = text
        return (self._text, RETURN_CODE)

    def detect_lang(self):
        '''
        Return the guessed two letter code corresponding to translation
        text.
        '''
        urldata = urllib.urlencode({'v': 1.0, 'q': self._text})
        url = 'http://ajax.googleapis.com/ajax/services/language/detect?%s' % \
                (urldata,)
        headers = {'User-Agent': 'Traduisons/%s' % (msg_VERSION,)}
        req = urllib2.Request(url, None, headers)
        response = urllib2.urlopen(req).read()
        return json.loads(response)['responseData']['language']

    def translate(self):
        '''Return translated text from fromLang to toLang.'''
        if self._text == '':
            self.result = ''
            return True
        try:
            # Use the official google translate-api via REST
            # 'auto' needs to be set to blank now
            if self._fromLang == 'auto':
                fromLangTemp = ''
            else:
                fromLangTemp = self._fromLang
            langpair = '%s|%s' % (fromLangTemp, self._toLang)
            urldata = urllib.urlencode({'v': 1.0,
                                        'q': self._text,
                                        'langpair': langpair
                                       })
            url = 'http://ajax.googleapis.com/ajax/services/language/translate?%s' % \
                (urldata,)
            headers = {'User-Agent': 'Traduisons/%s' % (msg_VERSION,)}
            req = urllib2.Request(url, None, headers)
            response = urllib2.urlopen(req).read()
            result = json.loads(response)['responseData']['translatedText']
            self.result = self._unquotehtml(result)
        # If 'result' is empty (pretty generic error) handle exception.
        except TypeError, e:
            self._error = ('No translation available', e)
            return False
        except urllib2.HTTPError, e:
            self._error = ('urllib2.HTTPError: Check network connection', e)
            return False
        ## If the url ever changes...
        except urllib2.URLError, e:
            self._error = (e.reason, e)
            return False
        return True

    def _unquotehtml(self, s):
        '''Convert a HTML quoted string into unicode object.
        Works with &#XX; and with &nbsp; &gt; etc.'''
        def convertentity(m):
            if m.group(1)=='#':
                try:
                    return chr(int(m.group(2)))
                except XValueError:
                    return '&#%s;' % (m.group(2),)
            try:
                return htmlentitydefs.entitydefs[m.group(2)]
            except KeyError:
                return ('&%s;' % (m.group(2),)).decode('ISO-8859-1'),
        return re.sub(r'&(#)?([^;]+);',convertentity,s)

## ------*------ End TRANSLATOR ------*------

def main():

    return 0

if __name__ == '__main__': main()
