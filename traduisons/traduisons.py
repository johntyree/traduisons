#! /usr/bin/env python

# Copyright 2010 John E Tyree <johntyree@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""
    Traduisons!
    http://traduisons.googlecode.com

    Python bindings to Google Translate RESTful API
"""

import base64
import htmlentitydefs
# In python <= 2.5, standard 'json' is not included 
try:
    import json
except(ImportError):
    import simplejson as json
import os
import re
import string
import sys
import threading
import urllib
import urllib2
from distutils import version


msg_VERSION = version.StrictVersion('0.4.1')
msg_DOWNLOAD = 'http://code.google.com/p/traduisons/downloads/list'
msg_LICENSE = """Traduisons! %s
http://traduisons.googlecode.com

Copyright (C) 201 John E Tyree <johntyree@gmail.com>
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
""" % (msg_VERSION,)
msg_BUGS = "Bugs, suggestions at <http://code.google.com/p/traduisons/issues/list>"
msg_USAGE = """Usage: %s [OPTION]...
Translate a string between languages using Google Translate.

OPTIONS
  -h, --help            Show help and basic usage.
  -n, --no-gui          Run at command line only.
  -v, --version         Print version information and exit.
""" % (sys.argv[0],)

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

def echo(f):
    def newfunc(*args, **kwargs):
        print f.__name__, "BEGIN"
        f(*args, **kwargs)
        print f.__name__, "END"
    return newfunc

def backgroundThread(f):
    echo = False
    if echo: print "backgroundThread definition start"
    def newfunc(*args, **kwargs):
        if echo: print "newfunc definition start"
        class bgThread(threading.Thread):
            def __init__(self, f, *args, **kwargs):
                if echo: print "bgThread Init Start"
                self.f = f
                threading.Thread.__init__(self)
                if echo: print "bgThread Init End"
                return
            def __call__(self, *args, **kwargs):
                if echo: print "__call__ start"
                resp = self.start()
                if echo: print "__call__ end"
                return resp
            def run(self):
                if echo: print "Thead start"
                result = self.f(*args, **kwargs)
                if echo: print "Thead end"
                if echo: print "newfunc definition end"
        #return bgThread(target = f, args = args, kwargs = kwargs).start()
        return bgThread(f).start()
    if echo: print "backgroundThread definition end"
    return newfunc

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



## -----v----- BEGIN GUI -----v-----
class TranslateWindow(translator):
    '''Gui frontend to translate function.'''
    ## If gtk or pygtk fails to import, warn user and run at cli.
    try:
        import gtk, gobject; global gtk; global gobject
        gobject.threads_init()
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
            """ % (sys.argv[0],)
        sys.exit()
    except NameError:
        pass

    def __init__(self, fromLang = 'auto', toLang = 'en'):
        iconfile = os.path.join(appPath, "data", "traduisons_icon.ico")
        traduisons_icon = gtk.gdk.pixbuf_new_from_file(iconfile)
        google_logo = gtk.gdk.PixbufLoader('png')
        google_logo.write(base64.b64decode('''
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
                                 '''))
        google_logo.close()
        google_logo = google_logo.get_pixbuf()
        self.pixbufs = {
            'google_logo': google_logo,
            'traduisons_icon': traduisons_icon,
            }

		## localize variables
        translator.__init__(self, fromLang, toLang)

        ## Generate user messages
        self.msg_LANGTIP  = self.pretty_print_languages(0)
        self.msg_MODAL = ''

        ## Set window properties
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(250, 95)
        self.window.set_title("Traduisons!")

        ## Try to load icon or skip
        try:
            self.window.set_icon(self.pixbufs["traduisons_icon"])
        except Exception, e:
            pass
        self.window.connect("delete_event", lambda w, e: sys.exit())

        ## Keyboard Accelerators
        self.AccelGroup = gtk.AccelGroup()
        #self.AccelGroup.connect_group(ord('Q'), gtk.gdk.CONTROL_MASK,
                                      #gtk.ACCEL_LOCKED,
                                      #lambda w, x, y, z: gtk.main_quit())
        self.AccelGroup.connect_group(ord('Q'), gtk.gdk.CONTROL_MASK,
                                      gtk.ACCEL_LOCKED,
                                      lambda w, x, y, z: sys.exit())
        self.AccelGroup.connect_group(ord('N'), gtk.gdk.CONTROL_MASK,
                                      gtk.ACCEL_LOCKED,
                                      lambda w, x, y, z:
                                          self.resultbuffer1.set_text(''))
        self.window.add_accel_group(self.AccelGroup)

        self.vbox1 = gtk.VBox(False, 0)
        self.window.add(self.vbox1)

##  ----v---- Upper half of window ----v----
        self.hbox1 = gtk.HBox(False, 0)
        self.vbox1.pack_start(self.hbox1, False, False, 3)

        ## language label
        self.langbox = gtk.Label()
        self.langbox.set_markup(str(self.fromLang()) + ' | ' + \
                                str(self.toLang()) + ':  ')
        self.hbox1.pack_start(self.langbox, False, False, 1)
        self.langbox.set_tooltip_text(self.msg_LANGTIP)

        ## Entry box
        self.entry = gtk.Entry()
        self.entry.set_max_length(0)
        self.entry.connect('activate', self.enter_callback)
        self.entry.set_tooltip_text(msg_HELP)
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
        self.resultbuffer1.create_mark('end',
                                       self.resultbuffer1.get_end_iter(),
                                       False)

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
            googleLogo = gtk.Image()
            googleLogo.set_from_pixbuf(self.pixbufs['google_logo'])
            self.statusBar2.set_text("powered by ")
            self.hbox3.pack_start(googleLogo, False)
        except Exception, e:
            self.statusBar2.set_text("powered by Google ")
        self.statusBar2.set_alignment(1, 0.5)

##  ----^---- Lower Half of window ----^----

        self.window.show_all()
        self.check_for_update()

## ------*------ START CALLBACKS ------*------

    def modal_message(self, msg = None):
        if msg is None:
            msg = self.msg_MODAL
        gobject.idle_add(self.statusBar1.set_text, msg)

    @backgroundThread
    def check_for_update(self):
        '''
        Update language list. Check the server for a new version of
        Traduisons and notify the user.
        '''
        self.update_languages()
        self.msg_LANGTIP = self.pretty_print_languages(0)
        gobject.idle_add(self.langbox.set_tooltip_text, self.msg_LANGTIP)
        if not self.is_latest():
            self.msg_MODAL = 'Update Available!'
            print self.msg_MODAL
            self.modal_message(self.msg_MODAL)
            tooltip = 'Get Traduisons! %s\n%s' % (self.msg_LATEST,
                                                  msg_DOWNLOAD)
            gobject.idle_add(self.statusBar1.set_tooltip_text, tooltip)
        return

    def enter_callback(self, widget, data = None):
        '''Submit entrybox text for translation.'''
        buf = self.resultbuffer1
        if self.entry.get_text() in ('.clear', 'clear()'):
            buf.set_text('')
            self.entry.set_text('')
            return
        result = self.text(self.entry.get_text())
        if result is None:
            return

        if 'HELP' in result:
            help_text = '\nPlease visit:\nhttp://code.google.com/p/traduisons/wiki'
            buf.insert(buf.get_end_iter(), help_text)
            self.result1.scroll_mark_onscreen(buf.get_mark('end'))
            self.entry.set_text('')
            return
        elif 'SWAP' in result or 'CHANGE' in result:
            self.langbox.set_markup(self.fromLang() + ' | ' +
                                    self.toLang() + ':  ')
            if 'SWAP' in result:
                self.entry.set_text(self.text())
            elif 'CHANGE' in result:
                self.entry.set_text('')
                return
        elif 'EXIT' in result:
            gtk.main_quit()
            return

        self.modal_message('translating...')
        self.entry.select_region(0, -1)

        ## If it's not blank, stick a newline on the end.
        if buf.get_text(buf.get_start_iter(), buf.get_end_iter()) != '':
            buf.insert(buf.get_end_iter(), '\n')

        # Sending out text for translation
        fromLangTemp = self.fromLang()
        if self.fromLang() == 'auto':
            fromLangTemp = self.detect_lang()
        if not self.translate():
            print repr(self._error)
            raise self._error[1]
        translation = self.result
        self.modal_message()
        if translation == '': return

        # Setting marks to apply fromLang and toLang color tags
        buf.insert(buf.get_end_iter(), '%s:' % (fromLangTemp,))
        front = buf.get_iter_at_mark(buf.get_insert())
        front.backward_word_start()
        back = buf.get_iter_at_mark(buf.get_insert())
        buf.apply_tag_by_name('fromLang', front, back)
        self.result1.scroll_mark_onscreen(buf.get_mark('end'))

        buf.insert(buf.get_end_iter(), ' %s\n  %s:' % (self.entry.get_text(),
                                                       self.toLang()))
        front = buf.get_iter_at_mark(buf.get_insert())
        front.backward_word_start()
        back = buf.get_iter_at_mark(buf.get_insert())
        buf.apply_tag_by_name('toLang', front, back)
        buf.insert(buf.get_end_iter(), ' %s' % (translation,))
        self.result1.scroll_mark_onscreen(buf.get_mark('end'))
        print "%s: %s\n  %s: %s" % (fromLangTemp, self.entry.get_text(),
                                    self.toLang(), translation)

        try:
            self.clipboard
        except AttributeError:
            self.clipboard = clipboard_get()
        self.clipboard.set_text(translation)
        self.clipboard.store()

## ------*------ End CALLBACKS ------*------
## ------*------ End CLASS ------*------
## ------*------ END GUI ------*------


def main():
    guiflag = True
    for arg in sys.argv[1:]:
        if arg in ('--help', '-h', "/?"):
            print msg_USAGE, "\n", msg_HELP
            sys.exit()
        elif arg in ('--no-gui', '-n', "/n"):
            guiflag = False
        elif arg in ("--version", "-v", "/v"):
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
        if not t.is_latest():
            print "Version %s now available! %s" % (t.msg_LATEST,
                                                    msg_DOWNLOAD)
        # This is blocking, who wants to wait around?
        # t.update_languages()
        while True:
            t.text('')
            while t.text() == '':
                stringLang = t.fromLang() + "|" + t.toLang() + ": "
                try:
                    result = t.text(raw_input(stringLang))
                    if None == result:
                       break
                    elif 'HELP' == result[1]:
                        print msg_HELP
                        print t.pretty_print_languages()
                except EOFError:
                    print
                    sys.exit()
            if t.translate():
                if t.result != '':
                    if t.fromLang() == 'auto':
                        l = t.detect_lang()
                        for k, v in t.dictLang.items():
                            if v == l:
                                print k, '-', v
                    print t.result
            else:
                raise t.result[1]


if __name__ == '__main__': main()
