#! /usr/bin/env python
"""
    Traduisons!
    http://traduisons.googlecode.com

    Uses Google Translate from the terminal
    Arabic and Persian are borked.
    Check out scale widgets?
    Some issue with 'auto'. Often unable to translate.
    Works with proper language selected.
"""
"""
    Copyright 2010 John E Tyree <johntyree@gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
    MA 02110-1301, USA.
"""

import urllib2, urllib, string, htmlentitydefs, re, sys, os

# In python <= 2.5, standard 'json' is not included 
try:
    import json
except(ImportError):
    import simplejson as json

msg_VERSION = "0.4.0"
msg_LICENSE = """Traduisons! %s
http://traduisons.googlecode.com

Copyright (C) 201 John E Tyree <johntyree@gmail.com>
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
""" % msg_VERSION
msg_BUGS = "Bugs, suggestions at <http://code.google.com/p/traduisons/issues/list>"
msg_USAGE = """Usage: %s [OPTION]...
Translate a string between languages using Google Translate.

OPTIONS
  -h, --help            Show help and basic usage.
  -n, --no-gui          Run at command line only.
  -v, --version         Print version information and exit.
""" % sys.argv[0]

msg_HELP = """Type the name or code for the desired language.
Format:  <Input Language> | <Target Language>
fi|French    Finnish to French:
auto|en      Auto detect to English:
|ar          Change target Language to Arabic:
es|          Change starting Language to Spanish:

Please visit <http://code.google.com/p/traduisons/wiki> for help."""


appPath = os.path.abspath(os.path.dirname(os.path.realpath(sys.argv[0])))
start_text = ""
fromLang = "auto"
toLang = "en"

class translator:
    dictLang = {'Detect Language' : 'auto',
                'Afrikaans' : 'af',
                'Albanian' : 'sq',
                'Arabic' : 'ar',
                'Belarusian' : 'be',
                'Bulgarian' : 'bg',
                'Catalan' : 'ca',
                'Chinese' : 'zh-CN',
                'Chinese (Simplified)' : 'zh-CN',
                'Chinese (Traditional)' : 'zh-TW',
                'Croatian' : 'hr',
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

    def __init__(self, fromLang = 'auto', toLang = 'en', start_text = ''):
        if not self.fromLang(fromLang): self.fromLang('auto')
        if not self.toLang(toLang): self.toLang('en')
        self._text = start_text
        x = self.dictLang
        self.update_languages()
        for k in x:
            if not self.dictLang.has_key(k): print k, ': Unavailable'

    def update_languages(self):
        '''Naively try to determine if new languages are available by scraping http://translate.google.com'''
        restr = '<meta name="description" content="Google&#39;s free online language translation service instantly translates text and web pages. This translator supports: (.*?)">'
        resp = urllib2.urlopen(urllib2.Request('http://translate.google.com', None, {'User-Agent':'Traduisons/%s' % msg_VERSION})).read()
        m = re.search(restr, resp)
        d = {}
        if m:
            names = m.group(1).split(', ')
            for name in names:
                n = re.search('<option  value="([^"]+)">%s</option>' % name, resp)
                if n:
                    d[name] = n.group(1)
                else:
                    return False
            for k, v in [('Detect Language', 'auto'), ('Gaelic', 'el'), ('Chinese (Traditional)', 'zh-TW'), ('Chinese (Simplified)', 'zh-CN')]:
                d[k] = v
            self.dictLang = d
        return False

    def languages(self):
        '''Return a string of pretty-printed, newline-delimited languages in the format Name : code'''
        l = []
        width = max([len(x) for x in self.dictLang.keys()])
        for item in sorted(self.dictLang.keys()):
            l.append(("%" + str(width) + 's' + ' : %s') % (item, self.dictLang[item]))
        return '\n'.join(l)

    def toLang(self, l = None):
        '''Get or set target language'''
        if l is not None:
            if l == 'auto': return False
            ## Check character code
            if l in self.dictLang.values(): self._toLang = l
            else:
                ## Check language name
                self._toLang = self.dictLang.get(string.capitalize(l), self._toLang)
        return self._toLang

    def fromLang(self, l = None):
        '''Get or set source language'''
        if l is not None:
            ## Check character code
            if l in self.dictLang.values():
                self._fromLang = l
            else:
                ## Check language name
                self._fromLang = self.dictLang.get(string.capitalize(l), self._fromLang)
        return self._fromLang

    def swapLang(self):
        '''Reverse direction the direction of translation'''
        f = self._fromLang
        t = self._toLang
        if not self.toLang(f) or not self.fromLang(t):
            self._toLang = t
            self._fromLang = f
            return False
        return True

    def raw_text(self, t = None):
        '''Get or set translation text, ignoring embedded directives such as '/' and '.' '''
        if t is not None:
            t = unicode(t)
            self._text = t
        return self._text

    def text(self, text = None):
        '''Get or set translation text, handling embedded directives such as '/' and '.' '''
        if text is None: return self._text
        if text == '':
            self._text = u''
            return
        RETURN_CODE = False
        if text in ('.exit', '.quit', '.quitter', 'exit()'): RETURN_CODE = 'EXIT'
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
        '''Return the guessed two letter code corresponding to translation text'''
        urldata = urllib.urlencode({'v': 1.0, 'q': self._text})
        response = urllib2.urlopen(urllib2.Request('http://ajax.googleapis.com/ajax/services/language/detect?%s' % urldata, None, {'User-Agent':'Traduisons/%s' % msg_VERSION})).read()
        return json.loads(response)['responseData']['language']

    def translate(self):
        '''Return translated text from fromLang to toLang.'''
        if self._text == '':
            self.result = ''
        else:
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
                headers = {'User-Agent':'Traduisons/%s' % msg_VERSION}
                response = urllib2.urlopen(urllib2.Request(url, None, headers)).read()
                self.result = self._unquotehtml(json.loads(response)['responseData']['translatedText'])
            ##  If translated_text is empty (no translation found) handle exception.
            except TypeError, e:
                self._error = ('No translation available', e)
                return False
            ##  Not sure about this, some kind of error when the net is unavailable perhaps?
            except urllib2.HTTPError, e:
                self._error = ('urllib2.HTTPError', e)
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
                    return '&#%s;' % m.group(2)
            try:
                return htmlentitydefs.entitydefs[m.group(2)]
            except KeyError:
                return ('&%s;' % m.group(2)).decode('ISO-8859-1')
        return re.sub(r'&(#)?([^;]+);',convertentity,s)

## ------*------ End TRANSLATOR ------*------



## -----v----- BEGIN GUI -----v-----
class TranslateWindow(translator):
    '''Gui frontend to translate function.'''
    ## If gtk or pygtk fails to import, warn user and run at cli.
    try:
        import gtk; global gtk
    except ImportError:
        print """  Import module GTK: FAIL"""
        guiflagfail = False
    try:
        import pygtk
        pygtk.require('2.0')
    except ImportError:
        guiflagfail = False
        print """  Import module pyGTK: FAIL"""
    try:
        import pango
    except ImportError:
        print """  Import modules pango: FAIL"""
    try:
        guiflagfail
        print """
        Install modules or try:
            python "%s" --no-gui
            """ % (sys.argv[0])
        sys.exit()
    except NameError:
        pass

    def __init__(self, fromLang = 'auto', toLang = 'en'):
		## localize variables
        translator.__init__(self, fromLang, toLang)

        ## making help tip string
        msg_LANGTIP  = "Language : symbol\n"
        for item in sorted(self.dictLang.keys()):
            msg_LANGTIP += '\n' + item + ' : ' + self.dictLang.get(item)

        ## Generate tooltips
        self.tooltips = gtk.Tooltips()

        ## Set window properties
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(250, 95)
        self.window.set_title("Traduisons!")

        ## Try to load tooltip or skip
        try:
            self.window.set_icon_from_file(os.path.join(appPath, "traduisons_icon.ico"))
        except Exception, e:
            pass
            #print e.message
            #sys.exit(1)
        self.window.connect("delete_event", lambda w, e: gtk.main_quit())

        ## Keyboard Accelerators
        self.AccelGroup = gtk.AccelGroup()
        self.AccelGroup.connect_group(ord('Q'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, lambda w, x, y, z: gtk.main_quit())
        self.AccelGroup.connect_group(ord('N'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, lambda w, x, y, z: self.result_buffer.set_text(''))
        self.window.add_accel_group(self.AccelGroup)

        self.vbox1 = gtk.VBox(False, 0)
        self.window.add(self.vbox1)

##  ----v---- Upper half of window ----v----
        self.hbox1 = gtk.HBox(False, 0)
        self.vbox1.pack_start(self.hbox1, False, False, 3)

        ## language label
        self.langbox = gtk.Label()
        self.langbox.set_markup('' + str(self.fromLang()) + ' | ' + str(self.toLang()) + ':  ')
        self.hbox1.pack_start(self.langbox, False, False, 1)
        self.tooltips.set_tip(self.langbox, msg_LANGTIP)

        ## Entry box
        self.entry = gtk.Entry()
        self.entry.set_max_length(0)
        self.entry.connect('activate', self.enter_callback)
        self.tooltips.set_tip(self.entry, msg_HELP)
        self.hbox1.pack_start(self.entry, True, True, 1)
##  ----^---- Upper half of window ----^----

##  ----v---- Lower Half of window ----v----
        self.hbox2 = gtk.HBox(False, 0)
        self.vbox1.pack_start(self.hbox2)

        ## Result window
        self.result1 = gtk.TextView()
        self.result1.set_cursor_visible(False)
        self.result1.set_editable(False)
        self.result1.set_wrap_mode(gtk.WRAP_WORD)
        self.result1.set_indent(-12)
        self.resultbuffer1 = self.result1.get_buffer()
        self.resultbuffer1.create_tag('fromLang', foreground = "dark red")
        self.resultbuffer1.create_tag('toLang',foreground = "dark blue")
        self.resultbuffer1.create_mark('end', self.resultbuffer1.get_end_iter(), False)

        ## Scroll Bar
        self.resultscroll = gtk.ScrolledWindow()
        self.resultscroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.resultscroll.add(self.result1)
        self.hbox2.pack_start(self.resultscroll, True, True, 1)

        ## Custom status bar
        self.hbox3 = gtk.HBox(False, 0)
        self.statusBar1 = gtk.Label()
        self.statusBar1.set_alignment(0, 0.5)
        self.statusBar2 = gtk.Label()
        self.vbox1.pack_start(self.hbox3, False)
        self.hbox3.pack_start(self.statusBar1)
        self.hbox3.pack_start(self.statusBar2, False)
        try:
            googleLogoPath = os.path.join(appPath, 'google-small-logo.png')
            if not os.path.isfile(googleLogoPath):
                raise Exception
            googleLogo = gtk.Image()
            googleLogo.set_from_file(googleLogoPath)
            self.statusBar2.set_text("powered by ")
            self.hbox3.pack_start(googleLogo, False)
        except Exception, e:
            self.statusBar2.set_text("powered by Google ")
        self.statusBar2.set_alignment(1, 0.5)

##  ----^---- Lower Half of window ----^----

        self.window.show_all()

## ------*------ START CALLBACKS ------*------

    def enter_callback(self, widget, data = None):
        '''Submit entrybox text for translation.'''

        if self.entry.get_text() in ('.clear', 'clear()'):
            self.resultbuffer1.set_text('')
            self.entry.set_text('')
            return
        result = self.text(self.entry.get_text())

        if 'HELP' in result:
            ViewObj.resultbuffer1.insert(ViewObj.resultbuffer1.get_end_iter(), '\nPlease visit:\nhttp://code.google.com/p/traduisons/wiki')
            ViewObj.result1.scroll_mark_onscreen(ViewObj.resultbuffer1.get_mark('end'))
            self.entry.set_text('')
            return
        elif 'SWAP' in result or 'CHANGE' in result:
            self.langbox.set_markup('' + self.fromLang() + ' | ' + self.toLang() + ':  ')
            if 'SWAP' in result:
                self.entry.set_text(self.text())
            elif 'CHANGE' in result:
                self.entry.set_text('')
                return
        elif 'EXIT' in result: gtk.main_quit()

        self.entry.select_region(0, -1)

        ## If it's not blank, stick a newline on the end.
        if self.resultbuffer1.get_text(self.resultbuffer1.get_start_iter(), self.resultbuffer1.get_end_iter()) != '':
            self.resultbuffer1.insert(self.resultbuffer1.get_end_iter(), '\n')

        # Sending out text for translation
        self.statusBar1.set_text('translating...')
        fromLangTemp = self.fromLang()
        if self.fromLang() == 'auto':
            fromLangTemp = self.detect_lang()
        if not self.translate():
            print repr(self._error)
            raise self._error[1]
        translation = self.result
        self.statusBar1.set_text('')
        if translation == '': return

        # Setting marks to apply fromLang and toLang tags
        self.resultbuffer1.insert(self.resultbuffer1.get_end_iter(), '%s:' % fromLangTemp)
        front = self.resultbuffer1.get_iter_at_mark(self.resultbuffer1.get_insert())
        front.backward_word_start()
        back = self.resultbuffer1.get_iter_at_mark(self.resultbuffer1.get_insert())
        self.resultbuffer1.apply_tag_by_name('fromLang', front, back)
        self.result1.scroll_mark_onscreen(self.resultbuffer1.get_mark('end'))
        self.resultbuffer1.insert(self.resultbuffer1.get_end_iter(), ' %s\n  %s:' % (self.entry.get_text(), self.toLang()))
        front = self.resultbuffer1.get_iter_at_mark(self.resultbuffer1.get_insert())
        front.backward_word_start()
        back = self.resultbuffer1.get_iter_at_mark(self.resultbuffer1.get_insert())
        self.resultbuffer1.apply_tag_by_name('toLang', front, back)
        self.resultbuffer1.insert(self.resultbuffer1.get_end_iter(), ' %s' % (translation))
        self.result1.scroll_mark_onscreen(self.resultbuffer1.get_mark('end'))
        print "%s: %s\n  %s: %s" % (fromLangTemp, self.entry.get_text(), self.toLang(), translation)

        ## Copy to clipboard
        ## Commenting this out due to overwhelming lag when running a clipboard manager
        #c = clipboard()
        try:
            self.clipboard
        except AttributeError:
            self.clipboard = gtk.clipboard_get()
        self.clipboard.set_text(translation)
        self.clipboard.store()

## ------*------ End CALLBACKS ------*------
## ------*------ End CLASS ------*------
## ------*------ END GUI ------*------

def clipboard_get():
    '''Return a gtk.Clipboard object or False if gtk in unavailable'''
    try:
        import gtk
        class clipboard(gtk.Clipboard):
            def __init__(self, text = None):
                gtk.Clipboard.__init__(self)

            def set_text(self, text, len=-1):
                targets = [ ("STRING", 0, 0),
                            ("TEXT", 0, 1),
                            ("COMPOUND_TEXT", 0, 2),
                            ("UTF8_STRING", 0, 3) ]
                def text_get_func(clipboard, selectiondata, info, data):
                    selectiondata.set_text(data)
                    return
                def text_clear_func(clipboard, data):
                    del data
                    return
                self.set_with_data(targets, text_get_func, text_clear_func, text)
                return
## ------*------ End CLASS ------*------
        return clipboard()
    except ImportError:
        return False
## ------*------ End CLIPBOARD ------*------

def main():
    guiflag = True
    for arg in sys.argv[1:]:
        if arg in ('--help', '-h'):
            print msg_USAGE, "\n", msg_HELP
            sys.exit()
        elif arg in ('--no-gui', '-n'):
            guiflag = False
        elif arg in ("--version", "-v"):
            print msg_LICENSE
            sys.exit()
        else:
            print msg_USAGE, "\n", msg_BUGS
            sys.exit()


    ## Start traduisons!
    if guiflag:
        TranslateWindow()
        gtk.main()
    else:
        print "\npowered by Google ..."
        t = translator()
        while True:
            t.text('')
            while t.text() == '':
                stringLang = t.fromLang() + "|" + t.toLang() + ": "
                try:
                    t.text(raw_input(stringLang))
                except EOFError:
                    sys.exit()
            if t.translate():
                if t.fromLang() == 'auto':
                    l = t.detect_lang()
                    for k, v in t.dictLang.items():
                        if v == l:
                            print k, '-', v
                print t.result
            else:
                raise t.result[1]


if __name__ == '__main__': main()
