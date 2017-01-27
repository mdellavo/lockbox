import json
import base64
import os
import getpass

from Crypto.Cipher import AES
from Crypto import Random


def get_secret(msg="Secret? "):
    rv = getpass.getpass(msg)
    return rv


def generate_random(bytes=32):
    return base64.b64encode(os.urandom(bytes))


def encrypt(key, val):
    random = Random.new()
    iv = random.read(AES.block_size)
    cipher = AES.AESCipher(key.ljust(32), AES.MODE_CFB, iv)
    payload = iv + cipher.encrypt(val)
    return base64.b64encode(payload)


def decrypt(key, val):
    bytes = base64.b64decode(val)
    iv, payload = bytes[:AES.block_size], bytes[AES.block_size:]
    cipher = AES.AESCipher(key.ljust(32), AES.MODE_CFB, iv)
    return cipher.decrypt(payload)


class LockBox(object):
    def __init__(self, secret):
        self.secret = secret
        self.storage = {}
        self.values = {}

    def load(self, f):
        self.storage.update(json.load(f))

    @classmethod
    def from_file(cls, secret, f):
        rv = cls(secret)
        rv.load(f)
        return rv

    def encrypt(self, val):
        return encrypt(self.secret, val)

    def decrypt(self, val):
        return decrypt(self.secret, val)

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
        return json.dump(self.storage, f, sort_keys=True, indent=4)


def open_lockbox(path, secret):
    if os.path.exists(path):
        with open(path) as f:
            return LockBox.from_file(secret, f)
    return LockBox(secret)


def commit_lockbox(path, lockbox):
    tmp_path = path + '.tmp'
    f = open(tmp_path, "w")
    lockbox.serialize(f)
    f.flush()
    os.fsync(f.fileno())
    f.close()
    os.rename(tmp_path, path)
