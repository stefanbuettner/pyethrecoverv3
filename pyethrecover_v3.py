#!/usr/bin/env python3

from keys import decode_keystore_json #keys.py from pyethereum, we only want the decode_keystore_json function
import json
import itertools
import sys
from joblib import Parallel, delayed
import multiprocessing
import pwgen
import signal


ethereum_minimum_pw_length = 8


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
    sys.stdout.write("Attempt #%d: %s\n" % (counter.value, pw)) #prints simple progress with # in list that is tested and the pw string
    sys.stdout.flush()
    counter.increment()

    if len(pw) < ethereum_minimum_pw_length:
        return ""
    try:
        o = decode_keystore_json(w, pw)
        with open("password.txt", "w") as pwfile:
            pwfile.write(pw)
            print("\n\nYour password is:\n%s\n\n" % pw)
        raise PasswordFoundException(
            """\n\nYour password is:\n%s""" % o)
    except ValueError:
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


# Needs to be in front of the interrupt_handler
brute_force_passwords = pwgen.PwGenerator(pwgen.digits + pwgen.alpha + pwgen.Alpha + pwgen.symbols, min_length=ethereum_minimum_pw_length)


def interrupt_handler(signum, frame):
    with open("pwgenerator.json", "w") as file:
        file.write(brute_force_passwords.to_json())
    exit(1)


def __main__():

    signal.signal(signal.SIGINT, interrupt_handler)

    # Option parsing
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--password',
                        default=None, dest='pw',
                        help="A single password to try against the wallet.")
    parser.add_argument('-f', '--passwords-file',
                        default=None, dest='pwfile',
                        help="A file containing a newline-delimited list of passwords to try.")
    parser.add_argument('-s', '--password-spec-file',
                        default=None, dest='pwsfile',
                        help="A file containing a password specification")
    parser.add_argument(dest='wallet', type=str, metavar="wallet-file",
                        help="The wallet against which to try the passwords.")
    parser.add_argument('-b', '--brute-force',
                        dest='brute_force', action='store_true',
                        help='Brute force the password over the alphabet set in code, after all given password combinations (including replacements) have been tested.')
    parser.add_argument('--brute-force-min-length',
                        dest='brute_force_min_length', type=int, metavar='N', default=ethereum_minimum_pw_length,
                        help='Default: 8 because ethereumwallet requires at least 8 characters.')
    parser.add_argument('--brute-force-max-length',
                        dest='brute_force_max_length', type=int, metavar='N', default=-1)
    parser.add_argument('-g', '--pwgenerator',
                        default=None, dest='pwgenerator',
                        help="Saved state of a password generator. If specified, the program continues with this generator.")
    parser.add_argument('-r', '--rules',
                        dest='use_rules', action='store_true',
                        help="Apply replacement rules to the given passwords. See the code for more details.")
    parser.add_argument('--max-replacements',
                        dest='max_replacements', type=int, default=3,
                        help='Replace at most this number of characters when using replacement rules. Default: 3')
    parser.add_argument('-j', '--jobs',
                        default='1', dest='jobs', type=int,
                        help='Maximum number of threads to use. Default: 1')

    args = parser.parse_args()

    try:
        with open(args.wallet) as wallet_file:
            try:
                w = json.load(wallet_file)
            except json.JSONDecodeError:
                print("Corrupt file '%s'." % args.wallet, file=sys.stderr)
                exit(1)
    except IOError:
        print("Could not load file '%s'." % args.wallet, file=sys.stderr)
        exit(1)

    if not w:
        print("Wallet file not found! (-h for help)")
        exit(1)

    passwords = []

    if args.pw:
        passwords.append(args.pw)

    if args.pwfile:
        file_read = False
        encoding = None
        while not file_read:
            try:
                with open(args.pwfile, "r", encoding=encoding) as pwfile:
                    pwlist = pwfile.read().splitlines()
                    file_read = True
                    passwords.extend(pwlist)
            except IOError:
                print("Password file not found! (-h for help)")
                exit(1)
            except ValueError:
                encoding = "ISO-8859-1"

    if args.pwsfile:
        grammar = eval(open(args.pwsfile, 'r').read())
        passwords = itertools.chain(passwords, generate_all(grammar, ''))

    if args.use_rules:
        replacement_rules = pwgen.RuleCollection(max_replacements=args.max_replacements)

        replacement_rules.add(pwgen.Rule("ö", ["oe", "Oe", "oE", "OE"]))
        replacement_rules.add(pwgen.Rule("h", "H"))
        replacement_rules.add(pwgen.Rule("M", "m"))
        replacement_rules.add(pwgen.Rule("m", "M"))
        replacement_rules.add(pwgen.Rule("ü", ["ue", "Ue", "uE", "UE"]))
        replacement_rules.add(pwgen.Rule("ä", ["ae", "Ae", "aE", "AE"]))
        replacement_rules.add(pwgen.Rule("A", "4@a"))
        replacement_rules.add(pwgen.Rule("a", "A4@"))
        replacement_rules.add(pwgen.Rule("O", "o0"))
        replacement_rules.add(pwgen.Rule("o", "O0"))
        replacement_rules.add(pwgen.Rule("l", "1"))
        replacement_rules.add(pwgen.Rule("E", "3e"))
        replacement_rules.add(pwgen.Rule("e", "3E"))
        replacement_rules.add(pwgen.Rule("S", "$s"))
        replacement_rules.add(pwgen.Rule("s", "S$"))
        replacement_rules.add(pwgen.Rule("I", "!i"))
        replacement_rules.add(pwgen.Rule("i", "!I"))
        replacement_rules.add(pwgen.Rule("B", "8b"))
        replacement_rules.add(pwgen.Rule("b", "B8"))
        replacement_rules.add(pwgen.Rule("T", "7t"))
        replacement_rules.add(pwgen.Rule("t", "T7"))
        replacement_rules.add(pwgen.Rule("p", "P"))
        replacement_rules.add(pwgen.Rule("r", "R"))

        passwords = pwgen.ApplyRules(passwords, replacement_rules)

    if args.brute_force:
        if args.pwgenerator:
            print("Loading pwgenerator file %s" % args.pwgenerator)
            with open(args.pwgenerator) as pwgenfile:
                # pwgenerator exists at global scope.
                brute_force_passwords.from_json(pwgenfile.read())
        else:
            brute_force_passwords.min_length = args.brute_force_min_length
            brute_force_passwords.max_length = args.brute_force_max_length

        passwords = itertools.chain(passwords, brute_force_passwords)

    global counter
    counter = Counter()

    # n_pws = len(list(passwords))
    # print 'Number of passwords to test: %d' % (n_pws)

    print("Using %d jobs" % args.jobs)
    try:
        Parallel(n_jobs=args.jobs, backend="threading")(delayed(attempt)(w, pw) for pw in passwords)
    except Exception as e:
        exit(0)
        pass
    exit(1)


if __name__ == "__main__":
    __main__()
