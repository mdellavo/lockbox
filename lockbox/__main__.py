import os
import sys
import json
import pprint
import StringIO
from argparse import ArgumentParser
from contextlib import closing

from .lib import LockBox, commit_lockbox, get_secret, generate_random, serialize

ENV_KEY = "LOCKBOX_SECRET"
CMD_PREFIX = "cmd_"

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

    
def cmd_import(lockbox, args):
    doc = json.load(sys.stdin)
    for k, v in doc.items():
        lockbox.set(k, v)
    store_lockbox(args.lockbox, lockbox)


CMDS = {k[len(CMD_PREFIX):]: v for k, v in locals().items() if k.startswith(CMD_PREFIX) and callable(v)}


def parse_args():
    parser = ArgumentParser(prog="lockbox")
    subparsers = parser.add_subparsers()

    def add_subparser(name, key=False, stdin=False):
        func = CMDS[name]
        subparser = subparsers.add_parser(name, help=func.__doc__)
        subparser.add_argument("lockbox", help="path to lockbox")
        if key:
            subparser.add_argument("key", help="key to operate on")
        if stdin:
            subparser.add_argument("--stdin", action="store_true", help="load dropbox from stdin")
        subparser.set_defaults(func=func, stdin=False)
        return subparser
    
    subparsers_set = add_subparser("set", key=True, stdin=True)
    subparsers_get = add_subparser("get", key=True, stdin=True)
    subparsers_gen = add_subparser("gen", key=True, stdin=True)
    subparsers_dump = add_subparser("dump")
    subparsers_import = add_subparser("import")

    args = parser.parse_args()
    return args


def store_lockbox(path, lockbox):
    if path == "-":
        lockbox.serialize(sys.stdout)
    else:
        commit_lockbox(path, lockbox)


def main():
    args = parse_args()
    secret = os.environ[ENV_KEY] if ENV_KEY in os.environ else get_secret("secret? ")
    lockbox = LockBox(secret)

    if args.stdin:
        f = sys.stdin
    elif os.path.exists(args.lockbox):
        f = open(args.lockbox)
    else:
        f = None

    if f:
        with closing(f):
            lockbox.load(f)
    args.func(lockbox, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
