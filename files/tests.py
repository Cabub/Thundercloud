from django.test import TestCase
from django.conf import settings
from files.models import File
from system.models import User
from .models import (
    UserBackupKey,
    UserPassphraseKey,
    FileEncryption,
)
from .cryptography import *
import re
from io import BytesIO


class CryptoTestCase(TestCase):

    def setUp(self):
        pass

    def test_backup_passphrase(self):
        passphrase = generate_backup_passphrase()
        self.assertTrue(re.match(
            b'^([a-z]+\ ){19}[a-z]+$', passphrase) is not None
        )

    def test_derive_from_passphrase(self):
        passphrase = b'passphrase'
        salt = generate_salt()
        key = derive_passphrase_key(passphrase, salt)
        self.assertTrue(re.match(b'.{16}', key) is not None)

    def test_keys_are_reproducible(self):
        passphrase = b'passphrase'
        salt = generate_salt()
        key = derive_passphrase_key(passphrase, salt)
        key2 = derive_passphrase_key(passphrase, salt)
        self.assertEqual(
            key, key2, 'derive_passphrase_key is returning different values'
            ' with the same inputs'
        )

    def test_encryption(self):
        passphrase = b'passphrase'
        data = 'some super secret data'.encode()
        salt = generate_salt()
        key = derive_passphrase_key(passphrase, salt)
        context = Fernet(key)
        cipher_text = context.encrypt(data)
        self.assertNotEqual(cipher_text, data, 'ciphertext matches cleartext')
        clear_text = context.decrypt(cipher_text)
        self.assertEqual(clear_text, data, 'encryption successfully decrypted')

    def test_stream_encryption(self):
        key = generate_random_key()
        data = 'some super secret data'.encode()
        stream = BytesIO(data)
        disk = BytesIO()
        output_stream = BytesIO()

        with EncryptingStreamWriter(disk, key) as ew:
            initialization_vector = ew.initialization_vector
            ew.write(data)
            ew.flush()
            # verify what we wrote to disk was encrypted
            disk.seek(0)
            disk_contents = disk.read()
            self.assertNotEqual(disk_contents, data)

        disk = BytesIO(disk_contents)

        with DecryptingStreamReader(disk, key, initialization_vector) as dr:
            output_stream.write(dr.read())

        output_stream.seek(0)
        output = output_stream.read()

        self.assertEqual(
            output, data, 'Data has changed during crypto process'
        )

    def test_encryption_classes(self):
        file_key = generate_random_key()
        data = 'some super secret data'.encode()
        encrypter = Encrypter(file_key)
        iv = encrypter.initialization_vector
        encrypted_data = encrypter.encrypt(data)
        self.assertNotEqual(encrypted_data, data)
        decrypter = Decrypter(file_key, iv)
        decrypted_data = decrypter.decrypt(encrypted_data)
        self.assertEqual(decrypted_data, data)
