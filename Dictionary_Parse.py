import json

class Dictionary:
    def __init__(self):
        with open('dictionaries/dictionary.json', 'r', encoding="utf8") as f:
            self.dictionary = json.load(f)
        with open('dictionaries/exact-match.json', 'r', encoding="utf8") as f:
            self.exact = json.load(f)
        with open('dictionaries/greek-match.json', 'r', encoding="utf8") as f:
            self.greek = json.load(f)
        with open('dictionaries/latin-match.json', 'r', encoding="utf8") as f:
            self.latin = json.load(f)

    def to_dict(self):
        return {
            'dictionary': self.dictionary,
            'exact': self.exact,
            'greek': self.greek,
            'latin': self.latin
        }

class Parser:
    def __init__(self, dictionary):
        self.matchers = [dictionary['exact'], dictionary['greek'], dictionary['latin']]
        self.dictionary = dictionary['dictionary']

    def lookup(self, string):
        key = string.lower()
        results = []
        headwords = {}
        dictionary = self.dictionary

        for matcher in self.matchers:
            if key in matcher:
                for headword in matcher[key]:
                    if headword not in headwords:
                        headwords[headword] = True
                        results.append({'headword': headword, 'definition': dictionary[headword]})

        return results