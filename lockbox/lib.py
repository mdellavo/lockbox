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


def derive_key(salt, password):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=base64.b64decode(salt),
        iterations=ITERATIONS,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password))


def encrypt(key, val):
    f = Fernet(key)
    token = f.encrypt(val)
    return token


def decrypt(key, token):
    f = Fernet(key)
    val = f.decrypt(bytes(token))
    return val


def serialize(doc, f):
    return json.dump(doc, f, sort_keys=True, indent=4)


class LockBox(object):
    def __init__(self, secret, f=None):
        self.storage = {}
        self.values = {}
        self.key = self.derive_key(secret)

    def load(self, secret, f):
        doc = json.load(f)
        self.derive_key(secret, doc["_salt"])
        self.storage.update(doc)

    def derive_key(self, secret, salt=None):
        if not salt:
            salt = generate_random(16)
        self.salt = salt
        self.key = derive_key(self.salt, secret)
         
    def encrypt(self, val):
        return encrypt(self.key, val)

    def decrypt(self, val):
        return decrypt(self.key, val)

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
        self.storage["_salt"] = self.salt
        return serialize(self.storage, f)


def open_lockbox(path, secret):
    lockbox = LockBox(secret)
    if os.path.exists(path):
        with open(path) as f:
            lockbox.load(secret, f)
    return lockbox


def commit_lockbox(path, lockbox):
    tmp_path = path + '.tmp'
    f = open(tmp_path, "w")
    lockbox.serialize(f)
    f.flush()
    os.fsync(f.fileno())
    f.close()
    os.rename(tmp_path, path)
