#!/usr/bin/python

from keys import decode_keystore_json #keys.py from pyethereum, we only want the decode_keystore_json function
import json
import itertools
import sys
import traceback
from joblib import Parallel, delayed
import multiprocessing

wordlist = "words3.txt"
with open(wordlist) as f:
    dictlist = f.read().splitlines()

w = {
  "address": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "crypto": {
    "cipher": "aes-128-ctr",
    "ciphertext": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "cipherparams": {
      "iv": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    },
    "kdf": "scrypt",
    "kdfparams": {
      "dklen": 32,
      "n": 262144,
      "p": 1,
      "r": 8,
      "salt": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    },
    "mac": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  },
  "id": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "version": 3
}

# Constructing passwords from possible combinations (see doc of pyethrecover)
grammar=[
    ('abe ', 'dan ', 'mary '),
    ('lincoln ', 'jesus ', 'johnson '),
    dictlist  # we append the wordlist. This isn't necessary if you think you've included all possible words above
]

# print(grammar)
def generate_all(el, tr): #taken from pyethrecover
    if el:
        for j in xrange(len(el[0])):
            for w in generate_all(el[1:], tr + el[0][j]):
                # print(w)
                yield w
    else:
        yield tr

def attempt(w, pw):
    # print(pw)
    # sys.stdout.write("\r")

    # sys.stdout.write("\rAttempt #%d: %s" % (counter.value, pw)) #prints simple progress with # in list that is tested and the pw string
    sys.stdout.write("Attempt #%d: %s\n" % (counter.value, pw)) #prints simple progress with # in list that is tested and the pw string
    sys.stdout.flush()
    #print(counter.value)
    counter.increment()

    if len(pw) < 10:
        return ""
    try:
        o = decode_keystore_json(w,pw)
        print(o)
        # print (pw)q
        raise PasswordFoundException(
            """\n\nYour password is:\n%s""" % o)
    except ValueError as e:
        # print(e)
        return ""

class Counter(object):
    def __init__(self):
        self.val = multiprocessing.Value('i', 0)

    def increment(self, n=1):
        with self.val.get_lock():
            self.val.value += n

    @property
    def value(self):
        return self.val.value

def __main__():
    global counter
    counter = Counter()
    pwds = []
    pwds = itertools.chain(pwds, generate_all(grammar,''))

    # n_pws = len(list(pwds))
    # print 'Number of passwords to test: %d' % (n_pws)

    try:
        Parallel(n_jobs=-1)(delayed(attempt)(w, pw) for pw in pwds)
        # print("\n")
    except Exception, e:
        traceback.print_exc()
        while True:
            sys.stdout.write('\a')
            sys.stdout.flush()

if __name__ == "__main__":
    __main__()
