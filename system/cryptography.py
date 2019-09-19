import base64
import os
import io
import math
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


def generate_random_key():
    return get_random_bytes(16)


def generate_random_fernet_key():
    return Fernet.generate_key()


def generate_salt():
    return os.urandom(16)


def derive_unsalted_hash(text):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'',
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(text)


def derive_passphrase_key(passphrase, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(passphrase))
    return key


def encrypt_key(encryption_key, key_to_encrypt):
    context = Fernet(encryption_key)
    return context.encrypt(key_to_encrypt)


def decrypt_key(encryption_key, cipher_key):
    context = Fernet(encryption_key)
    return context.decrypt(cipher_key)


def generate_backup_passphrase():
    """ Picks random words from a wordlist to generate a backup passphrase
    I'm aware that it's not super efficient to loop through the whole
    dictionary, but the idea is that this would only happen once per each
    new user. If we're getting a lot of signups later, we could cache the
    dictionary in memory, but that seems wasteful
    Perhaps we should use a database table, and just query using the indices
    In any case, this is how I've implemented it now, deal with it.
    """
    # generate backup_token_count random indices between 0 - word_list_count
    word_list_length = settings.ENCRYPTION_BACKUP_KEY['backup_word_list_count']
    random_byte_count = math.ceil(math.log2(word_list_length + 1) / 8)
    max_int = (2 ** (random_byte_count * 8)) - 1
    token_count = settings.ENCRYPTION_BACKUP_KEY['backup_token_count']
    indices = [
        int.from_bytes(os.urandom(random_byte_count), 'big', signed=False)
        * word_list_length
        // max_int
        for _ in range(token_count)
    ]

    # read those words from the word list
    file_path = settings.ENCRYPTION_BACKUP_KEY['words_list_path']
    ordered_indices = sorted(indices)
    tokens = []
    with open(file_path, 'rb') as fs:
        current_line = 0
        for index in ordered_indices:
            while current_line != index:
                fs.readline()
                current_line += 1
            tokens.append(fs.readline().strip())

    return b' '.join(tokens)


class Encrypter:
    context = None

    @property
    def initialization_vector(self):
        return self.context.iv

    def __init__(self, key):
        self.context = AES.new(key, AES.MODE_CFB)

    def __del__(self):
        del self.context

    def encrypt(self, chunk):
        if type(chunk) is not bytes:
            raise RuntimeError('Chunk must be bytes')
        return self.context.encrypt(chunk)


class Decrypter:
    context = None

    def __init__(self, key, initialization_vector):
        self.context = AES.new(key, AES.MODE_CFB, initialization_vector)

    def __del__(self):
        del self.context

    def decrypt(self, chunk):
        if type(chunk) is not bytes:
            raise RuntimeError('Chunk must be bytes')
        return self.context.decrypt(chunk)


class DecryptingStreamReader(io.BufferedReader):
    _decrypter = None

    def __init__(self, raw, *args, **kwargs):
        if len(args) == 0:
            raise RuntimeError(
                'DecryptingStreamReader missing key/iv or Decrypter argument'
            )
        elif isinstance(args[0], Decrypter):
            # decrypter is supplied
            self._decrypter = args[0]
            args = args[1:]
        elif type(args[0]) is bytes and type(args[1]) is bytes:
            # key and iv are supplied
            self._decrypter = Decrypter(args[0], args[1])
            args = args[2:]

        super().__init__(raw, *args, **kwargs)

    def peek(self, *args):
        raise RuntimeError('DecryptingStreamReader cannot be peeked')

    def read(self, *args):
        result = super().read(*args)
        return self._decrypter.decrypt(result)

    def read1(self, *args):
        result = super().read1(*args)
        return self._decrypter.decrypt(result)

    def __iter__(self):
        buffer = self.read1(io.DEFAULT_BUFFER_SIZE)
        while buffer != b'':
            yield buffer
            buffer = self.read1(io.DEFAULT_BUFFER_SIZE)


class EncryptingStreamWriter(io.BufferedWriter):
    _encrypter = None

    def __init__(self, raw, *args, **kwargs):
        if len(args) == 0:
            raise RuntimeError(
                'EncryptingStreamWriter missing key or Encrypter argument'
            )
        elif isinstance(args[0], Encrypter):
            # encrypter is supplied
            self._encrypter = args[0]
        elif type(args[0]) is bytes:
            # key is supplied
            self._encrypter = Encrypter(args[0])
        args = args[1:]

        super().__init__(raw, *args, **kwargs)

    @property
    def initialization_vector(self):
        return self._encrypter.initialization_vector

    def peek(self, *args):
        raise RuntimeError('EncryptingStreamWriter cannot be peeked')

    def write(self, b):
        return super().write(self._encrypter.encrypt(b))
