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

    def get_num_matches(self):
        return len(self.matches)

    def get_num_replacements(self):
        return len(self.replacements)

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
        self.matches = self.find_matches()
        if len(self.matches) >= 0:
            if self.mod is not None:
                self.mod.reset(s)

    def find_matches(self):
        """
        :return: Returns a list of indices where the rule matches.
        """
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


class RuleCollection:
    def __init__(self, rules, string=""):
        self.string = string
        self.rules = rules
        self.replacements = dict()
        self.replacement_indices = list()
        self.beginning = True
        if self.string != "":
            self.reset(string)

    def __iter__(self):
        return self

    def reset(self, s):
        self.replacements.clear()
        for r in self.rules:
            r.reset(s)
            for mIdx in r.find_matches():
                if mIdx in self.replacements:
                    self.replacements[mIdx].extend(r.replacements)
                else:
                    self.replacements[mIdx] = r.replacements
        if len(self.replacements) > 0:
            self.replacement_indices.append((self._find_next_free_match_(0), 0))
            self.beginning = True

    def next(self):
        return self.__next__()

    def __next__(self):
        if len(self.replacement_indices) <= 0:
            raise StopIteration

        s = self.string
        offset = 0
        print(self.replacement_indices)
        for match_idx, rep_idx in self.replacement_indices:
            s = s[:match_idx + offset] + self.replacements[match_idx][rep_idx] + s[match_idx + offset + 1:]

        must_pop = True
        while must_pop:
            must_pop = False
            pos, k = self.replacement_indices.pop()
            k += 1
            if k >= len(self.replacements[pos]):
                new_pos = self._find_next_free_match_(pos + 1)
                if new_pos >= len(self.string):
                    new_pos = self._find_next_free_match_(0)
                    if new_pos != pos and new_pos < len(self.string):
                        self.replacement_indices.append((new_pos, 1))
                        # new_pos = self._find_next_free_match_(new_pos + 1)
                        # if new_pos < len(self.string):
                        #     self.replacement_indices.append((new_pos, 1))
                    else:
                        must_pop = True
                else:
                    self.replacement_indices.append((new_pos, 1))
            else:
                self.replacement_indices.append((pos, k))
        return s

    def _find_next_free_match_(self, pos):
        """
        Finds the next free match beginning at position pos.

        :return: The index of the next free match.
        """
        #in_replacements = True
        #while in_replacements:
        for m in self.replacements:
            if m < pos:
                continue
            in_replacements = False
            for p, l in self.replacement_indices:
                if p == m:
                    in_replacements = True
                    break
            if not in_replacements:
                return m
        return len(self.string)





digits = "0123456789"
alpha = "abcdefghijklmnopqrstuvwxyz"
Alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
symbols = "@&$?!"

if __name__ == "__main__":
    import json
    import itertools
    r_A = Rule("A", "4@")
    r_a = Rule("a", "A", r_A)

    r_O = Rule("O", "0", r_a)
    r_o = Rule("o", "O", r_O)

    r_l = Rule("l", "1", r_o)

    r_E = Rule("E", "3", r_l)
    r_e = Rule("e", "E", r_E)

    r_S = Rule("S", "$", r_e)
    r_s = Rule("s", "S", r_S)

    r_I = Rule("I", "!", r_s)
    r_i = Rule("i", "I", r_I)

    r_B = Rule("B", "8", r_i)
    r_b = Rule("b", "B", r_B)

    r_T = Rule("T", "7", r_b)
    r_t = Rule("t", "T", r_T)

    r_p = Rule("p", "P", r_t)

    pwds = RuleCollection([r_A, r_e], "AnAbel")
    for pw in pwds:
        print(pw)
