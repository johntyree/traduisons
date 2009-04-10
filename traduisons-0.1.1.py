#! /usr/bin/python
#-*- coding: utf-8 -*-

##Traduisons! 0.1.1
##Uses Google Translate from the terminal
##Gui requires GTK2

##go through and comment this

##Help doesn't display in gui yet
##Check out scale widgets?

import urllib2, string, htmlentitydefs, re, sys

try:
    from BeautifulSoup import BeautifulSoup
except:
    print """
        import module BeautifulSoup: FAIL
        Traduisons! requires BeautifulSoup.
        Please make sure it is correctly installed.
        http://www.crummy.com/software/BeautifulSoup/
        """
    sys.exit()

try:
    import gtk
    clipboard = gtk.clipboard_get()
except:
    sys.argv.append('--no-gui')
    print """
        Module gtk: FAIL
        Running with --no-gui flag.
        """


start_text = ""
fromLang = 'auto'
toLang = 'en'
dictLang = {'Detect Language' : 'auto',
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
            'Filipino' : 'tl',
            'Finnish' : 'fi',
            'French' : 'fr',
            'German' : 'de',
            'Greek' : 'el',
            'Hebrew' : 'iw',
            'Hindi' : 'hi',
            'Indonesian' : 'id',
            'Italian' : 'it',
            'Japanese' : 'ja',
            'Korean' : 'ko',
            'Latvian' : 'lv',
            'Lithuanian' : 'lt',
            'Norwegian' : 'no',
            'Polish' : 'pl',
            'Portuguese' : 'pt',
            'Romanian' : 'ro',
            'Russian' : 'ru',
            'Serbian' : 'sr',
            'Slovak' : 'sk',
            'Slovenian' : 'sl',
            'Spanish' : 'es',
            'Swedish' : 'sv',
            'Ukrainian' : 'uk',
            'Vietnamese' : 'vi'}


def convertentity(m):
    # Convert a HTML entity into normal string (ISO-8859-1)
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
    # Convert a HTML quoted string into normal string (ISO-8859-1).
    # Works with &#XX; and with &nbsp; &gt; etc."""
    return re.sub(r'&(#?)(.+?);',convertentity,s)


def changelang(start_text, fromLang, toLang):
    # Reference dictLang to change target languages.
    # SendFlag gets changed to false if not actually translating.
    SendFlag = True
    if start_text in ('.exit', '.quit', '.quitter', 'exit()'): sys.exit()

	# Use the '/' character to reverse translation direction. Then strip.
    elif start_text[0] == '/' or start_text[-1] == '/': 
        # 'auto' is not a valid toLang. Prevent swapping.
        if not fromLang == 'auto':
            toLang, fromLang = fromLang, toLang
        try:        
            if start_text == '/': SendFlag, start_text = False, ""
            elif start_text[-1] == '/': start_text = start_text[:-1]
            elif start_text[0] == '/': start_text = start_text[1:]
	    #~ print SendFlag
        except:
            pass

    elif start_text in ('?', 'help', '-h', '-help', '--help'):

        for item in sorted(dictLang.keys()):
            print item + ' : ' + dictLang.get(item)

        print """\n
            Type the name or code for the desired language.
            Format:  <From This Language> | <To This Language>
            ex: Finnish to French:                   fi|french
            Auto detect to English:              auto|en
            Change target Language to Arabic:    |ar
            Change starting Language to Spanish: es|
            """
    
        start_text = ''
        SendFlag = False

    #~ Use '|' character to change translation language(s).
    elif start_text.find('|') + 1:
        # Check language name
        if dictLang.get(string.capitalize(start_text[0:start_text.find('|')])):
            fromLang = dictLang.get(string.capitalize(start_text[0:start_text.find('|')]))

        # Check 2-character code
        elif start_text[0:start_text.find('|')] in dictLang.values():
            fromLang = start_text[0:start_text.find('|')]

        # If start_text is in dictLang, set new toLang and restart loop.
        if dictLang.get(string.capitalize(start_text[start_text.find('|') + 1:])):
            toLang = dictLang.get(string.capitalize(start_text[start_text.find('|') + 1:]))

        # Check 2-character code
        elif start_text[start_text.find('|') + 1:] in dictLang.values() and start_text[start_text.find('|') + 1:] != 'auto':
            toLang = start_text[start_text.find('|') + 1:]

        start_text = ''
        SendFlag = False

##HERHERHER    start_text_old = start_text    
    return (start_text, fromLang, toLang, SendFlag)


def translate(start_text, fromLang, toLang):
    try:
    ##  Open the URL, parse it with BeautifulSoup, convert to UTF 8, and store string.
        translated_text = unquotehtml(BeautifulSoup(urllib2.urlopen(urllib2.Request('http://www.google.com/translate_t?', 'text=%s&sl=%s&tl=%s' % (start_text, fromLang, toLang), {'User-Agent':'Mozilla/5.0'})).read()).find("div", id="result_box").contents[0])
        
    ##  Paste to clipboard
        clipboard.set_text(translated_text)
        clipboard.store()    
    except:
        translated_text = "Unable to translate text."
    return translated_text
    
    
class TranslateWindow:
## -----v----- BEGIN GUI -----v-----
    def __init__(self, fromLang, toLang, dictLang):
##      localize variables
        self.fromLang, self.toLang, self.dictLang = fromLang, toLang, dictLang


##      making help tip string
        helptip  = ''
        for item in sorted(dictLang.keys()):
            helptip += item + ' : ' + dictLang.get(item) + '\n'

        helptip += """
Type the name or code for the desired language.
Format:  <From This Language> | <To This Language>
fi|French    Finnish to French:
auto|en      Auto detect to English:
|ar           Change target Language to Arabic:
es|           Change starting Language to Spanish:
"""

##      Generate tooltips
        self.tooltips = gtk.Tooltips()

##      create a new window        
        self.inputwindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.inputwindow.set_size_request(250, 89)
        self.inputwindow.set_title("Traduisons!")
        self.inputwindow.connect("delete_event", lambda w, e: gtk.main_quit())

        self.AccelGroup = gtk.AccelGroup()
        self.AccelGroup.connect_group(ord('Q'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, lambda w, x, y, z:gtk.main_quit())
        self.inputwindow.add_accel_group(self.AccelGroup)
##        self.inputwindow.add_accelerator("activate", self.AccelGroup, ord('Q'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)        

        self.vbox1 = gtk.VBox(False, 0)
        self.inputwindow.add(self.vbox1)
        self.vbox1.show()
        
##  ----v---- Upper half of window ----v----
        self.hbox1 = gtk.HBox(False, 0)
        self.vbox1.pack_start(self.hbox1, False, False, 3)
        self.hbox1.show()

##      Language label
        self.langbox = gtk.Label()
        self.langbox.set_text(self.fromLang + ' | ' + self.toLang + ':  ')
        self.hbox1.pack_start(self.langbox, False, False, 1)
        self.tooltips.set_tip(self.langbox, "Input language | Target language:")
        self.langbox.show()
 
##      Text box
        self.entry = gtk.Entry()
        self.entry.set_max_length(0)
        self.entry.connect('activate', self.enter_callback)

        self.entry.select_region(0, len(self.entry.get_text()))
        self.hbox1.pack_start(self.entry, True, True, 1)
        self.tooltips.set_tip(self.entry, helptip)
        self.entry.set_text("Mouse over for helpful tooltips")
        self.entry.show()
##  ----^---- Upper half of window ----^----

##  ----v---- Lower Half of window ----v----
        self.hbox2 = gtk.HBox(False, 0)
        self.vbox1.pack_start(self.hbox2)
        self.hbox2.show()

##      Result window
        self.result1 = gtk.TextView()
        self.result1.set_cursor_visible(False)
        self.result1.set_editable(False)
        self.result1.set_wrap_mode(gtk.WRAP_WORD)
        self.result1.set_indent(-12)
        self.resultbuffer1 = self.result1.get_buffer()
        self.resultbuffer1.create_mark('end', self.resultbuffer1.get_end_iter(), False)

        self.result1.show()
    ##  Scroll Bar
        self.resultscroll = gtk.ScrolledWindow()
        self.resultscroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.resultscroll.add(self.result1)

        self.hbox2.pack_start(self.resultscroll, True, True, 1)
        self.resultscroll.show()
##  ----^---- Lower Half of window ----^----
        
        self.inputwindow.show()


## ------*------ END GUI ------*------

## ------*------ START CALLBACKS ------*------

    def enter_callback(self, widget, data = None):
##  Sends EVERYTHING to changelang which then handles it
##  Ideally, ? should print list of languages, / should switch to and from
        entry_set_text, self.fromLang, self.toLang, SendFlag = changelang(self.entry.get_text(), self.fromLang, self.toLang)
        self.langbox.set_text(self.fromLang + ' | ' + self.toLang + ':  ')            
        self.entry.set_text(entry_set_text)
        self.entry.select_region(0, len(self.entry.get_text()))
        if SendFlag:
            if self.resultbuffer1.get_text(self.resultbuffer1.get_start_iter(), self.resultbuffer1.get_end_iter()) != '': self.resultbuffer1.insert(self.resultbuffer1.get_end_iter(), '\n')
            self.resultbuffer1.insert(self.resultbuffer1.get_end_iter(), '%s: %s' % (self.fromLang, self.entry.get_text()))
            self.result1.scroll_mark_onscreen(self.resultbuffer1.get_mark('end'))
			#~ Had to convert translation to utf-8 to get non-latin chars.
            translation = translate(self.entry.get_text(), self.fromLang, self.toLang).encode("utf-8")
            print translation
            self.resultbuffer1.insert(self.resultbuffer1.get_end_iter(), '\n   %s: %s' % (self.toLang, translation))
            self.result1.scroll_mark_onscreen(self.resultbuffer1.get_mark('end'))

## ------*------ End CLASS ------*------



if __name__ == '__main__':
    for arg in sys.argv:
        if arg in ('--no-gui', '-n'):
            while True:
                stringLang = fromLang + "|" + toLang + ": "
                start_text = ''
                while start_text == '':
                    start_text = raw_input(stringLang)
                start_text, fromLang, toLang, SendFlag = changelang(start_text, fromLang, toLang)
                #~ Had to convert translation to utf-8 to get non-latin chars.
                if SendFlag: print translate(start_text, fromLang, toLang).encode("utf-8")

    import pygtk
    pygtk.require('2.0')

    def main():
        gtk.main()
        return 0

    TranslateWindow(fromLang, toLang, dictLang)
    main()
    
