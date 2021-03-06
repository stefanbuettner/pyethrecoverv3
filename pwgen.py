import itertools


class PwGenerator(object):
    def __init__(self, alphabet, max_length=-1, min_length=1, modification_rule=None):
        self.alphabet = alphabet
        self.modification_rule = modification_rule
        self.min_length = min_length
        self.max_length = max_length
        self._i = 0
        self._max_i = -1

    def __iter__(self):
        n = len(self.alphabet)
        if self._i <= 0:
            min_length = self.min_length
            self._i = 0
            while min_length > 0:
                self._i = 1 + self._i * n
                min_length -= 1

        if self._max_i < 0:
            max_length = self.max_length
            self._max_i = 0
            while max_length >= 0:
                self._max_i = 1 + self._max_i * n
                max_length -= 1
            self._max_i -= 1
        return self

    def __next__(self):
        return self.next()

    def next(self):
        while True:
            if self.modification_rule is not None:
                try:
                    return next(self.modification_rule)
                except StopIteration:
                    pass
            s = self._get_str_(self._i)
            self._i += 1
            if self.modification_rule is not None:
                self.modification_rule.reset(s)
            else:
                return s

    def _get_str_(self, i):
        if self._max_i >= 0 and i > self._max_i:
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
        self._i = obj['_i']
        self._max_i = obj['_max_i']
        self.min_length = obj['min_length']
        self.max_length = obj['max_length']


class Rule(object):
    def __init__(self, match, replacements, modification_rule=None):
        if len(match) != 1:
            raise RuntimeError("match must be one character but is %s" % match)
        self.match = match
        self.replacements = replacements
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


class RuleCollection(object):
    """
    This generator applies the given rules to the given string beginning with replacing one occurrence, then two,... .


    It is equivalent to the following loop
    # for replacement_count in range(len(replacement_indices) + 1):
    #     for match_comb in itertools.combinations(replacement_indices, replacement_count):
    #         rep = list()
    #         for m in match_comb:
    #             rep.append(replacements[m])
    #
    #         for rep_comb in itertools.product(*rep):
    #             # print(str(match_comb) + " " + str(rep_comb))
    #             s = string
    #             for i in range(len(match_comb)):
    #                 s = s[:match_comb[i]] + rep_comb[i] + s[match_comb[i] + 1:]
    #             yield s
    """
    def __init__(self, rules=[], max_replacements=-1, string=None):
        self.string = string
        self.rules = rules
        self.replacements = dict()
        self.matches = list()
        self.replacement_count = 0
        self.desired_max_replacements = max_replacements
        self.max_replacements = self.desired_max_replacements
        self.match_combinations = None
        self.replacement_combinations = None
        if self.string is not None:
            self.reset(string)

    def __iter__(self):
        return self

    def add(self, rule):
        self.rules.append(rule)

    def reset(self, s):
        self.string = s
        self.replacements.clear()
        self.matches.clear()
        self.replacement_count = 0
        self.match_combinations = None
        self.replacement_combinations = None

        for r in self.rules:
            r.reset(self.string)
            for mIdx in r.find_matches():
                if mIdx in self.replacements:
                    self.replacements[mIdx].extend(r.replacements)
                else:
                    self.matches.append(mIdx)
                    self.replacements[mIdx] = r.replacements
        self.matches.sort()
        self.max_replacements = self.desired_max_replacements
        if self.max_replacements < 0:
            self.max_replacements = len(self.matches)
        self.match_combinations = iter(itertools.combinations(self.matches, self.replacement_count))

    def next(self):
        return self.__next__()

    def __next__(self):
        if self.string is None:
            raise StopIteration

        while True:
            if self.replacement_count > self.max_replacements:
                raise StopIteration

            if self.replacement_combinations is not None:
                try:
                    rep_comb = next(self.replacement_combinations)
                    s = self.string
                    offset = 0
                    for i in range(len(self.match_comb)):
                        s = s[:self.match_comb[i] + offset] + rep_comb[i] + s[self.match_comb[i] + offset + 1:]
                        offset += len(rep_comb[i]) - 1
                    return s
                except StopIteration:
                    pass

            try:
                self.match_comb = next(self.match_combinations)
                rep = list()
                for m in self.match_comb:
                    rep.append(self.replacements[m])
                self.replacement_combinations = iter(itertools.product(*rep))
            except StopIteration:
                self.replacement_count += 1
                self.match_combinations = iter(itertools.combinations(self.matches, self.replacement_count))
                self.replacement_combinations = None


def combine_rules(string, rules):
    replacements = dict()
    replacement_indices = list()

    for r in rules:
        r.reset(string)
        for mIdx in r.find_matches():
            if mIdx in replacements:
                replacements[mIdx].extend(r.replacements)
            else:
                replacement_indices.append(mIdx)
                replacements[mIdx] = r.replacements

    for replacement_count in range(len(replacement_indices) + 1):
        for match_comb in itertools.combinations(replacement_indices, replacement_count):
            rep = list()
            for m in match_comb:
                rep.append(replacements[m])

            for rep_comb in itertools.product(*rep):
                #print(str(match_comb) + " " + str(rep_comb))
                s = string
                for i in range(len(match_comb)):
                    s = string[:match_comb[i]] + rep_comb[i] + string[match_comb[i] + 1:]
                yield s


class ApplyRules(object):
    """
    This is a generator which applies the given rule to every element in the given iterable.
    """
    def __init__(self, iterable, rule):
        """
        :param iterable: An iterator over strings.
        :param rule: Might be a Rule or a RuleCollection.
        """
        self.iterable = iterable
        self.rule = rule

    def __iter__(self):
        self.iterable = iter(self.iterable)
        return self

    def next(self):
        return self.__next__()

    def __next__(self):
        while True:
            try:
                return next(self.rule)
            except StopIteration:
                string = next(self.iterable)
                self.rule.reset(string)


digits = "0123456789"
alpha = "abcdefghijklmnopqrstuvwxyz"
Alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
symbols = "@&$?!"

if __name__ == "__main__":
    import json
    import itertools
    r_A = Rule("A", "4@")
    r_a = Rule("a", "A4@")

    r_O = Rule("O", "0")
    r_o = Rule("o", "O")

    r_l = Rule("l", "1")

    r_E = Rule("E", "3")
    r_e = Rule("e", "E")

    r_S = Rule("S", "$")
    r_s = Rule("s", "S")

    r_I = Rule("I", "!")
    r_i = Rule("i", "I")

    r_B = Rule("B", "8")
    r_b = Rule("b", "B")

    r_T = Rule("T", "7")
    r_t = Rule("t", "T")

    r_p = Rule("p", "P")

    pwds = PwGenerator(["Anabel"], max_length=2, modification_rule=RuleCollection([r_a], max_replacements=1))
    for pw in pwds:
        print(pw)
