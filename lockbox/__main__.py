import os
import sys
import base64
import getpass
from argparse import ArgumentParser

from .lib import commit_lockbox, open_lockbox


def get_secret(msg="Secret? "):
    rv = getpass.getpass(msg)
    return rv


def generate_random(bytes=32):
    return base64.b64encode(os.urandom(bytes))


def cmd_set(lockbox, args):
    v = get_secret("v? ")

    if not v:
        raise ValueError("abort")

    lockbox.set(args.key, v)

    commit_lockbox(args.lockbox, lockbox)


def cmd_get(lockbox, args):
    print lockbox.get(args.key)


def cmd_gen(lockbox, args):
    v = generate_random()
    lockbox.set(args.key, v)
    commit_lockbox(args.lockbox, lockbox)

CMDS = [("set", cmd_set), ("get", cmd_get), ("gen", cmd_gen)]


def main():
    parser = ArgumentParser(prog="lockbox")
    subparsers = parser.add_subparsers()

    for name, func in CMDS:
        subparser = subparsers.add_parser(name)
        subparser.add_argument("lockbox")
        subparser.add_argument("key")
        subparser.set_defaults(func=func)

    args = parser.parse_args()

    lockbox = open_lockbox(args.lockbox, get_secret("secret? "))
    args.func(lockbox, args)
    return 0

if __name__ == "__main__":
    sys.exit(main())
