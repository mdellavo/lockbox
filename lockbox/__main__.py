import os
import sys
import pprint
import StringIO
from argparse import ArgumentParser
from contextlib import closing

from .lib import LockBox, commit_lockbox, get_secret, generate_random, serialize

ENV_KEY = "LOCKBOX_SECRET"


def cmd_set(lockbox, args):
    """
    Add a key to the lockbox
    """
    v = get_secret("v? ")

    if not v:
        raise ValueError("abort")

    lockbox.set(args.key, v)

    store_lockbox(args.lockbox, lockbox)


def cmd_get(lockbox, args):
    """
    Get a key from the lockbox
    """
    print lockbox.get(args.key)


def cmd_gen(lockbox, args):
    """
    Generate a key and store in lockbox
    """
    v = generate_random()
    lockbox.set(args.key, v)
    store_lockbox(args.lockbox, lockbox)

def cmd_dump(lockbox, args):
    """
    Dump plain-text lockbox as JSON
    """
    doc = {k: lockbox.get(k) for k in lockbox.keys()}
    f = StringIO.StringIO()
    serialize(doc, f)
    print f.getvalue()
    
CMDS = [("set", cmd_set), ("get", cmd_get), ("gen", cmd_gen), ("dump", cmd_dump)]

def parse_args():
    parser = ArgumentParser(prog="lockbox")
    subparsers = parser.add_subparsers()

    def add_subparser(name, func):
        subparser = subparsers.add_parser(name, help=func.__doc__)
        subparser.add_argument("lockbox", help="path to lockbox")
        subparser.set_defaults(func=func)
        return subparser

    subparser_set, subparser_get, subparser_gen, subparser_dump = [add_subparser(name, func) for name, func in CMDS]

    for subparser in (subparser_set, subparser_get, subparser_gen):
        subparser.add_argument("key", help="key to operate on")

    args = parser.parse_args()
    return args

def open_lockbox(path):
    f = None
    if path == "-":
        f = sys.stdin
    else:
        if os.path.exists(path):
            f = open(path, mode=mode)
    return f


def store_lockbox(path, lockbox):
    if path == "-":
        lockbox.serialize(sys.stdout)
    else:
        commit_lockbox(path, lockbox)


def main():
    args = parse_args()

    secret = os.environ[ENV_KEY] if ENV_KEY in os.environ else get_secret("secret? ")

    lockbox = LockBox(secret)

    f = open_lockbox(args.lockbox)
    if f:
        with closing(f):
            lockbox.load(f)

    args.func(lockbox, args)
    return 0

if __name__ == "__main__":
    sys.exit(main())
