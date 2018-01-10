class PwGenerator(object):
    def __init__(self, alphabet, max_length=-1, min_length=1, modification_rule=None):
        self.alphabet = alphabet
        self.i = 0
        self.mod = modification_rule
        n = len(alphabet)
        while min_length > 0:
            self.i = 1 + self.i * n
            min_length -= 1
        self.max_length = 0
        while max_length >= 0:
            self.max_length = 1 + self.max_length * n
            max_length -= 1
        self.max_length -= 1

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self.mod is not None:
            try:
                return self.mod.__next__()
            except StopIteration:
                pass
        s = self._get_str_(self.i)
        self.i += 1
        if self.mod is not None:
            self.mod.reset(s)
            return self.mod.__next__()
        return s

    def _get_str_(self, i):
        if self.max_length >= 0 and i > self.max_length:
            raise StopIteration()
        s = ""
        m = len(self.alphabet)
        while i > 0:
            s = self.alphabet[(i - 1) % m] + s
            i = (i-1) // m
        return s

    def to_json(self):
        import json
        return json.dumps(self, default=lambda o : o.__dict__, sort_keys=True, indent=4)

    def from_json(self, pwgen_json):
        import json
        obj = json.loads(pwgen_json)
        self.alphabet = obj['alphabet']
        self.i = obj['i']
        self.max_length = obj['max_length']


class Rule:
    def __init__(self, match, replacements, modification_rule=None):
        if len(match) != 1:
            raise RuntimeError("match must be one character but is %s" % match)
        self.match = match
        self.replacements = match + replacements
        self.s = ""
        self.i = 0
        self.matches = []
        self.mod = modification_rule

    def next(self):
        return self.__next__()

    def __iter__(self):
        return self

    def __next__(self):
        if self.mod is not None:
            if self.i == 0:
                self.i += 1
            try:
                return self.mod.__next__()
            except StopIteration:
                pass
        s = self._get_str_(self.i)
        self.i += 1
        if self.mod is not None:
            self.mod.reset(s)
            return self.mod.__next__()
        return s

    def reset(self, s):
        self.s = s
        self.i = 0
        self.matches = self._find_matches_()
        if len(self.matches) >= 0:
            if self.mod is not None:
                self.mod.reset(s)

    def _find_matches_(self):
        matches = []
        idx = self.s.find(self.match)
        while idx >= 0:
            matches.append(idx)
            idx = self.s.find(self.match, idx + 1)
        return matches

    def _get_str_(self, i):
        len_alphabet = len(self.replacements)
        combinations = len_alphabet ** len(self.matches)
        if self.i >= combinations:
            raise StopIteration()
        k = 0
        s = self.s
        while i > 0:
            idx = self.matches[k]
            s = s[:idx] + self.replacements[i % len_alphabet] + s[idx+1:]
            i = i // len_alphabet
            k += 1
        return s


digits = "0123456789"
alpha = "abcdefghijklmnopqrstuvwxyz"
Alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
symbols = "@&$?!"

if __name__ == "__main__":
    import json
    gen = Rule("a", "4@")
    #gen2 = Rule("n", "70", gen)
    gen2 = PwGenerator(["foo", "bar"], max_length=3, min_length=1, modification_rule=gen)
    #with open('pwgenerator.json', "w") as file:
    #    file.write(gen.to_json())
    #gen2.reset("anan")
    for pw in gen2:
        print(pw)
