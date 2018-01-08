#!/usr/bin/env python

from keys import decode_keystore_json #keys.py from pyethereum, we only want the decode_keystore_json function
import json
import itertools
import sys
import traceback
from joblib import Parallel, delayed
import multiprocessing
import pwgen
import signal, os


# print(grammar)
def generate_all(el, tr): #taken from pyethrecover
    if el:
        for j in range(len(el[0])):
            for w in generate_all(el[1:], tr + el[0][j]):
                # print(w)
                yield w
    else:
        yield tr


class PasswordFoundException(Exception):
    pass


def attempt(w, pw):
    # print(pw)
    # sys.stdout.write("\r")

    # sys.stdout.write("\rAttempt #%d: %s" % (counter.value, pw)) #prints simple progress with # in list that is tested and the pw string
    #sys.stdout.write("Attempt #%d: %s\n" % (counter.value, pw)) #prints simple progress with # in list that is tested and the pw string
    #sys.stdout.flush()
    #print(counter.value)
    counter.increment()

    #if len(pw) < 10:
    #    return ""
    try:
        o = decode_keystore_json(w, pw)
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


pwgenerator = pwgen.PwGenerator(pwgen.digits + pwgen.alpha + pwgen.Alpha + pwgen.symbols, min_length=8)


def interrupt_handler(signum, frame):
    with open("pwgenerator.json", "w") as file:
        file.write(pwgenerator.to_json())
    exit(1)


def __main__():

    signal.signal(signal.SIGINT, interrupt_handler)

    # Option parsing
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-p', '--password',
                      default=None, dest='pw',
                      help="A single password to try against the wallet.")
    parser.add_option('-f', '--passwords-file',
                      default=None, dest='pwfile',
                      help="A file containing a newline-delimited list of passwords to try. (default: %default)")
    parser.add_option('-s', '--password-spec-file',
                      default=None, dest='pwsfile',
                      help="A file containing a password specification")
    parser.add_option('-w', '--wallet',
                      default='wallet.json', dest='wallet',
                      help="The wallet against which to try the passwords. (default: %default)")
    parser.add_option('-j', '--jobs',
                      default='-1', dest='jobs', type='int',
                      help="Maximum number of threads to use. (default: %default = unbound)")
    parser.add_option('-g', '--pwgenerator',
                      default=None, dest='pwgenerator',
                      help="Saved state of a password generator. "
                            "If specified, the program continues with this generator.")

    (options, args) = parser.parse_args()

    try:
        with open(options.wallet) as wallet_file:
            try:
                w = json.load(wallet_file)
            except json.JSONDecodeError:
                print("Corrupt file '%s'." % options.wallet, file=sys.stderr)
                exit(1)
    except IOError:
        print("Could not load file '%s'." % options.wallet, file=sys.stderr)
        exit(1)

    if not w:
        print("Wallet file not found! (-h for help)")
        exit(1)

    pwds = []

    if options.pw:
        pwds.append(options.pw)

    if options.pwfile:
        try:
            with open(options.pwfile) as pwfile:
                pwlist = pwfile.read().splitlines()
                pwds.extend(pwlist)
        except:
            print("Password file not found! (-h for help)")
            exit(1)

    if options.pwsfile:
        grammar = eval(open(options.pwsfile, 'r').read())
        pwds = itertools.chain(pwds, generate_all(grammar, ''))

    if options.pwgenerator:
        print("Loading pwgenerator file %s" % options.pwgenerator)
        with open(options.pwgenerator) as pwgenfile:
            pwgenerator.from_json(pwgenfile.read())

    global counter
    counter = Counter()
    pwds = itertools.chain(pwds, pwgenerator)

    # n_pws = len(list(pwds))
    # print 'Number of passwords to test: %d' % (n_pws)

    print("Using %d jobs" % options.jobs)
    try:
        Parallel(n_jobs=options.jobs, backend="threading")(delayed(attempt)(w, pw) for pw in pwds)
        # print("\n")
    except Exception as e:
        traceback.print_exc()
        while True:
            sys.stdout.write('\a')
            sys.stdout.flush()
    exit(0)


if __name__ == "__main__":
    __main__()
