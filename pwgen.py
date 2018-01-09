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
        else:
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
    def __init__(self, match, replacements, modification_rule=None, _mod_=None):
        self.match = match
        self.replacements = replacements
        self.s = ""
        self.i = 0
        self.idx = None
        self.mod = modification_rule
        self.mod2 = _mod_

    def next(self):
        return self.__next__()

    def __iter__(self):
        return self

    def __next__(self):
        pass

    def reset(self, s):
        self.s = s
        self.idx = self.s.find(self.match)
        if self.idx >= 0:
            if self._mod_ is not None:
                self._mod_.reset(self.s[self.idx + 1:])

        pass


digits = "0123456789"
alpha = "abcdefghijklmnopqrstuvwxyz"
Alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
symbols = "@&$?!"

if __name__ == "__main__":
    import json
    gen = PwGenerator(["foo", "bar", "@", "3141"], max_length=3, min_length=1)
    with open('pwgenerator.json', "w") as file:
        file.write(gen.to_json())
    for pw in gen:
        print(pw)
