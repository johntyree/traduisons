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
    Copyright 2009 John E Tyree <johntyree@gmail.com>

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

import urllib2, urllib, string, htmlentitydefs, re, sys, os, pygtk, pango

# In python <= 2.5, standard 'json' is not included 
try:
    import json
except(ImportError):
    import simplejson as json

msg_VERSION = "0.3.0"
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
dictLang = {'Detect Language' : 'auto',
            'Albanian' : 'sq',
            'Arabic' : 'ar',
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
            'Indonesian' : 'id',
            'Italian' : 'it',
            'Japanese' : 'ja',
            'Korean' : 'ko',
            'Latvian' : 'lv',
            'Lithuanian' : 'lt',
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
            'Swedish' : 'sv',
            'Thai' : 'th',
            'Turkish' : 'tr',
            'Ukrainian' : 'uk',
            'Vietnamese' : 'vi'
            }

def convertentity(m):
    """Convert a HTML entity into normal string (ISO-8859-1)"""

    if m.group(1)=='#':
        try:
            return chr(int(m.group(2)))
        except XValueError:
            return '&#%s;' % m.group(2)
    try:
        return htmlentitydefs.entitydefs[m.group(2)]
    except KeyError:
        return '&%s;' % m.group(2)


def unquotehtml(s):
    """Convert a HTML quoted string into normal string (ISO-8859-1).
    Works with &#XX; and with &nbsp; &gt; etc."""

    return re.sub(r'&(#?)(.+?);',convertentity,s)

def clearBuffer(ViewObj):
    if ViewObj:
        ViewObj.resultbuffer1.set_text('')
    return

def changelang(start_text, fromLang, toLang, ViewObj = None):
    """Change target languages according to dictLang."""
    
    ## SendFlag gets changed to false if not sending an http request.
    SendFlag = True
    if start_text == "": SendFlag = False
    elif start_text in ('.exit', '.quit', '.quitter', 'exit()'): sys.exit()
    elif start_text in ('.clear', 'clear()'):
        SendFlag = False
        clearBuffer(ViewObj)

	## Use the '/' character to reverse translation direction. Then strip.
    elif start_text[0] == '/' or start_text[-1] == '/':
        ## 'auto' is not a valid toLang. Prevent swapping.
        if not fromLang == 'auto':
            toLang, fromLang = fromLang, toLang
        try:
            # Cut off the '/' character if necessary
            if start_text == '/': (SendFlag, start_text) = (False, "")
            elif start_text[-1] == '/': start_text = start_text[:-1]
            elif start_text[0] == '/': start_text = start_text[1:]
        except:
            pass

    elif start_text in ('?', 'help', '-h', '-help', '--help'):
        print '\n'
        for item in sorted(dictLang.keys()):
            print item + ' : ' + dictLang.get(item)
        print '\n', msg_HELP, '\n'

        if guiflag:
            ViewObj.resultbuffer1.insert(ViewObj.resultbuffer1.get_end_iter(), '\nPlease visit:\nhttp://code.google.com/p/traduisons/wiki')
            ViewObj.result1.scroll_mark_onscreen(ViewObj.resultbuffer1.get_mark('end'))

        start_text = ''
        SendFlag = False

    ## Use '|' character to change translation language(s).
    elif start_text.find('|') + 1:
        ## Check language name
        if dictLang.get(string.capitalize(start_text[0:start_text.find('|')])):
            fromLang = dictLang.get(string.capitalize(start_text[0:start_text.find('|')]))

        ## Check 2-character code
        elif start_text[0:start_text.find('|')] in dictLang.values():
            fromLang = start_text[0:start_text.find('|')]

        ## If start_text is in dictLang, set new toLang and restart loop.
        if dictLang.get(string.capitalize(start_text[start_text.find('|') + 1:])):
            toLang = dictLang.get(string.capitalize(start_text[start_text.find('|') + 1:]))

        ## Check 2-character code
        elif start_text[start_text.find('|') + 1:] in dictLang.values() and start_text[start_text.find('|') + 1:] != 'auto':
            toLang = start_text[start_text.find('|') + 1:]

        start_text = ''
        SendFlag = False

    return (start_text, fromLang, toLang, SendFlag)

def detectLang(text):
    '''Return the guessed two letter code corresponding to text'''
    urldata = urllib.urlencode({'v': 1.0, 'q': text})
    response = urllib2.urlopen(urllib2.Request('http://ajax.googleapis.com/ajax/services/language/detect?%s' % urldata, None, {'User-Agent':'Traduisons/%s' % msg_VERSION})).read()
    return json.loads(response)['responseData']['language']

def translate(start_text, fromLang, toLang):
    """Return translated start_text from fromLang to toLang."""

    global unicodeflag ## Declare as global to avoid UnboundLocalError
    try:
    ##  Open the URL, parse it with regex, convert to UTF-8 if possible, and store string.
        ## Use the official google translate-api via REST
        ## 'auto' needs to be set to blank now
        if fromLang == 'auto':
            fromLangTemp = detectLang(start_text) 
            print '%s detected' % fromLangTemp
        else:
            fromLangTemp = fromLang
        urldata = urllib.urlencode({'v': 1.0,
                                    'q': start_text,
                                    'langpair' : '%s|%s' % (fromLangTemp, toLang)
                                   })
        response = unquotehtml(urllib2.urlopen(urllib2.Request('http://ajax.googleapis.com/ajax/services/language/translate?%s' % (urldata), None, {'User-Agent':'Traduisons/%s' % msg_VERSION})).read())
        translated_text = json.loads(response)['responseData']['translatedText']
            
        if unicodeflag: translated_text = translated_text.encode("utf-8")
    ##  If translated_text is empty (no translation found) handle exception.
    except (AttributeError, urllib2.HTTPError):
        translated_text = "Unable to translate text."

    except UnicodeDecodeError:
        print "Error: UTF-8 decoding error. Unable to print some special characters."
        unicodeflag = False
    return translated_text


## -----v----- BEGIN GUI -----v-----
class TranslateWindow:
    """Gui frontend to translate function."""
    ## If gtk or pygtk fails to import, warn user and run at cli.
    try:
        import gtk; global gtk
        global clipboard; clipboard = gtk.clipboard_get()
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
        guiflagfail
        print """
        Install modules or try:
            python "%s" --no-gui
            """ % (sys.argv[0])
        sys.exit()
    except NameError:
        pass

    def __init__(self, fromLang, toLang, dictLang):
		## localize variables
        self.fromLang, self.toLang, self.dictLang = fromLang, toLang, dictLang

        ## making help tip string
        msg_LANGTIP  = "Language : symbol\n"
        for item in sorted(dictLang.keys()):
            msg_LANGTIP += '\n' + item + ' : ' + dictLang.get(item)

        ## Generate tooltips
        self.tooltips = gtk.Tooltips()

        ## create a new window
        self.inputwindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.inputwindow.set_size_request(250, 95)
        self.inputwindow.set_title("Traduisons!")

        ## Try to load tooltip or skip
        try:
            self.inputwindow.set_icon_from_file(os.path.join(appPath, "traduisons_icon.ico"))
        except Exception, e:
            pass
            #print e.message
            #sys.exit(1)
        self.inputwindow.connect("delete_event", lambda w, e: gtk.main_quit())

        ## Keyboard Accelerators
        self.AccelGroup = gtk.AccelGroup()
        self.AccelGroup.connect_group(ord('Q'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, lambda w, x, y, z: gtk.main_quit())
        self.AccelGroup.connect_group(ord('N'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, lambda w, x, y, z: clearBuffer(self))
        self.inputwindow.add_accel_group(self.AccelGroup)

        self.vbox1 = gtk.VBox(False, 0)
        self.inputwindow.add(self.vbox1)

##  ----v---- Upper half of window ----v----
        self.hbox1 = gtk.HBox(False, 0)
        self.vbox1.pack_start(self.hbox1, False, False, 3)

        ## language label
        self.langbox = gtk.Label()
        self.langbox.set_markup('' + self.fromLang + ' | ' + self.toLang + ':  ')
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
            googlePNG = gtk.Image()
            googlePNG.set_from_file(os.path.join(appPath, 'google-small-logo.png'))
            self.statusBar2.set_text("powered by ")
            self.hbox3.pack_start(googlePNG, False)
        except Exception, e:
            self.statusBar2.set_text("powered by Google ")
        self.statusBar2.set_alignment(1, 0.5)

##  ----^---- Lower Half of window ----^----

        self.inputwindow.show_all()

## ------*------ START CALLBACKS ------*------

    def enter_callback(self, widget, data = None):
        """Submit entrybox text for translation."""

        ##  Sends EVERYTHING to changelang which then handles it
        ##  Ideally, ? should print list of languages, / should switch to and from
        entry_set_text, self.fromLang, self.toLang, SendFlag = changelang(self.entry.get_text(), self.fromLang, self.toLang, self)
        self.langbox.set_markup('' + self.fromLang + ' | ' + self.toLang + ':  ')
        self.entry.set_text(entry_set_text)
        self.entry.select_region(0, -1)
        if SendFlag:
            if self.resultbuffer1.get_text(self.resultbuffer1.get_start_iter(), self.resultbuffer1.get_end_iter()) != '':
                self.resultbuffer1.insert(self.resultbuffer1.get_end_iter(), '\n')
            # Sending out text for translation
            self.statusBar1.set_text('translating...')
            translation = translate(self.entry.get_text(), self.fromLang, self.toLang)
            ##  Paste to clipboard
            clipboard.set_text(translation)
            clipboard.store()
            self.statusBar1.set_text('')
            # Setting marks to apply fromLang and toLang tags
            if self.fromLang == 'auto':
                fromLangTemp = detectLang(self.entry.get_text())
            else:
                fromLangTemp = self.fromLang
            self.resultbuffer1.insert(self.resultbuffer1.get_end_iter(), '%s:' % fromLangTemp)
            front = self.resultbuffer1.get_iter_at_mark(self.resultbuffer1.get_insert())
            front.backward_word_start()
            back = self.resultbuffer1.get_iter_at_mark(self.resultbuffer1.get_insert())
            self.resultbuffer1.apply_tag_by_name('fromLang', front, back)
            self.result1.scroll_mark_onscreen(self.resultbuffer1.get_mark('end'))
            self.resultbuffer1.insert(self.resultbuffer1.get_end_iter(), ' %s\n  %s:' % (self.entry.get_text(), self.toLang))
            front = self.resultbuffer1.get_iter_at_mark(self.resultbuffer1.get_insert())
            front.backward_word_start()
            back = self.resultbuffer1.get_iter_at_mark(self.resultbuffer1.get_insert())
            self.resultbuffer1.apply_tag_by_name('toLang', front, back)
            self.resultbuffer1.insert(self.resultbuffer1.get_end_iter(), ' %s' % (translation))
            self.result1.scroll_mark_onscreen(self.resultbuffer1.get_mark('end'))
            print "%s: %s\n  %s: %s" % (self.fromLang, self.entry.get_text(), self.toLang, translation)

## ------*------ End CALLBACKS ------*------
## ------*------ End CLASS ------*------
## ------*------ END GUI ------*------


def main():
    global guiflag; guiflag = True
    global unicodeflag; unicodeflag = True
    global fromLang, toLang
    for arg in sys.argv[1:]:
        if arg in ('--help', '-h'):
            print msg_USAGE, "\n", msg_HELP
            sys.exit()
        elif arg in ('--no-gui', '-n'):
            guiflag = False
        elif arg in ("--version", "-v"):
            print """Traduisons! %s
http://traduisons.googlecode.com

Copyright (C) 2009 John E Tyree <johntyree@gmail.com>
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
""" % msg_VERSION
            sys.exit()
        else:
            print msg_USAGE, "\n", msg_BUGS
            sys.exit()


    ## Start traduisons!
    if guiflag:
        TranslateWindow(fromLang, toLang, dictLang)
        gtk.main()
    else:
        while True:
            stringLang = fromLang + "|" + toLang + ": "
            start_text = ''
            while start_text == '':
                start_text = raw_input(stringLang)
            start_text, fromLang, toLang, SendFlag = changelang(start_text, fromLang, toLang)
            if SendFlag: print translate(start_text, fromLang, toLang)


if __name__ == '__main__': main()
