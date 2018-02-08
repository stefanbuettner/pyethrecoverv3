# pyethrecover for wallet v3
This is a tool for those of you who've somehow lost your Ethereum wallet password.

## Features
- Supports adding a wordlist to broaden cracking dictionary.
- Parallelizes cracking. More CPU cores and hyperthreading, faster cracking.
- An alternative python generator which allows brute force checking.
- Provide character replacement rules (currently, only via code).

This tool is compatible with Python 3. It depends on the following libraries

- joblib
- bitcoin
- json
- itertools

Based on [pyethrecoverv3](https://github.com/danielchalef/pyethrecoverv3), [pyethrecover](https://github.com/burjorjee/pyethrecover) and [How to apply pyethrecover.py on v3 .json/transfor v3 .json to .v1](http://ethereum.stackexchange.com/questions/6845/how-to-apply-pyethrecover-py-on-v3-json-transfor-v3-json-to-v1/12249#12249) and [pyethereum](https://github.com/ethereum/pyethereum).

## Please use for good, not evil

## Wordlists
Google for a wordlist in your language or covering topics that you're likely to have used in your phrase. Some useful wordlists [here](http://ftp.icm.edu.pl/packages/wordlists/) and [here](https://wiki.skullsecurity.org/Passwords).


## Example1

Let's say you have a wallet file named ethereum-wallet.json protected by the password correct horse battery staple. You enter your guesses into a file named passwords.txt, like so:

    shelly sells seashells down by the seashore
    It was the best time of times, it was the worst of times...
    Password1
    correct horse battery staple
    mean mr mustard sleeps in the park

If you run the utility like so...

    ./pyethrecover.py -w ethereum-wallet.json -f passwords.txt

...you should get back something like this:

    shelly sells seashells down by the seashore
    It was the best time of times, it was the worst of times...
    Password1
    correct horse battery staple
    
    Your seed is:
    abc123abc123...
    
    Your password is:
    correct horse battery staple

## Example2

Let's say you have a wallet file named ethereum-wallet.json and you remember that you password is a greeting in some language followed by the name of an american president. Say you're not sure if the president is addressed with a title; if he is, you're certain it's either "president" or "mister". You would create a file password_spec.txt like so ...

    [
        ('hello', 'bonjour', 'hola'),
        ('', 'mister', 'president'),
        ('smith', 'jefferson')
    ]

and call it like so...

    ./pyethrecover.py -w ethereum-wallet.json -s password_spec.txt

Check out the comments in password_spec.txt for more details.
