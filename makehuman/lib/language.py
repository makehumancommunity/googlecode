
import os

class Language(object):
    def __init__(self):
        self.language = None
        self.languageStrings = None
        self.missingStrings = set()
        self.rtl = False

    def setLanguage(self, language):
        self.languageStrings = None
        path = os.path.join("data/languages/", language + ".ini")
        if not os.path.isfile(path):
            return
        with open(path, 'rU') as f:
            try:
                self.languageStrings = eval(f.read(), {"__builtins__":None}, {'True':True, 'False':False})
            except:
                import traceback
                traceback.print_exc()
                print('Error in language file %s' % language)
                self.languageStrings = None
        self.language = language
        self.rtl = False
        if self.languageStrings and '__options__' in self.languageStrings:
            self.rtl = self.languageStrings['__options__'].get('rtl', False)
            
    def getLanguageString(self, string):
        if not self.languageStrings:
            return string
        result = self.languageStrings.get(string)
        if result is not None:
            return result
        self.missingStrings.add(string)
        return string
            
    def dumpMissingStrings(self):
        if not self.language:
            return
        path = os.path.join("data", "languages", self.language + ".missing")
        with open(path, 'w') as f:
            for string in self.missingStrings:
                f.write("'%s':'',\n" % string.encode('utf8'))

language = Language()