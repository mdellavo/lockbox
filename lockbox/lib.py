import json
import base64
import os
import getpass

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITERATIONS = 100000

def get_secret(msg="Secret? "):
    rv = getpass.getpass(msg)
    return rv


def generate_random(count=32):
    return base64.b64encode(os.urandom(count))


def derive_key(salt, secret):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=base64.b64decode(salt),
        iterations=ITERATIONS,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(secret))


def encrypt(secret, val, salt=None):
    salt = salt or generate_random(16)
    key = derive_key(salt, secret)    
    f = Fernet(key)
    token = f.encrypt(bytes(val))
    return salt + "|" + token


def decrypt(secret, val):
    salt, token = val.split("|")
    key = derive_key(salt, secret)    
    f = Fernet(key)
    val = f.decrypt(bytes(token))
    return val


def serialize(doc, f):
    json.dump(doc, f, sort_keys=True, indent=4)
    f.write("\n")


class LockBox(object):
    def __init__(self, secret):
        self.storage = {}
        self.values = {}
        self.secret = secret

    def load(self, f):
        doc = json.load(f)
        self.storage.update(doc)

    def encrypt(self, val):
        return encrypt(self.secret, val)

    def decrypt(self, val):
        return decrypt(self.secret, val)

    def keys(self):
        return [k for k in self.storage.keys() if k[0] != "_"]
    
    def __contains__(self, key):
        return key in self.storage

    def get(self, key):
        if key not in self.storage:
            raise KeyError()

        if key not in self.values:
            self.values[key] = self.decrypt(self.storage[key])

        return self.values[key]

    def set(self, key, val):
        self.values[key] = val
        self.storage[key] = self.encrypt(val)

    def serialize(self, f):
        return serialize(self.storage, f)


def commit_lockbox(path, lockbox):
    tmp_path = path + '.tmp'
    f = open(tmp_path, "w")
    try:
        lockbox.serialize(f)
        f.flush()
        os.fsync(f.fileno())
        os.rename(tmp_path, path)
    finally:
        f.close()

