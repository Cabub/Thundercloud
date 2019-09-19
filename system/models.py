from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.conf import settings
from uuid import uuid4
from .cryptography import (
    derive_passphrase_key, generate_salt, encrypt_key,
    decrypt_key, generate_random_fernet_key
)

class UserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """ Override default UserManager and create the user's Keys
        """
        backup_passphrase = extra_fields.pop('backup_passphrase', None)
        if backup_passphrase is None:
            raise ValueError('All users must have a backup_passphrase.')
        user = super()._create_user(username, email, password, **extra_fields)
        salt = generate_salt()
        key = derive_passphrase_key(
            password.encode(), salt
        )
        secret_key = generate_random_fernet_key()
        UserPassphraseKey.objects.create(
            owner=user,
            salt=salt,
            cipher_key=encrypt_key(key, secret_key)
        )
        salt = generate_salt()
        backup_key = derive_passphrase_key(
            backup_passphrase, salt
        )
        UserBackupKey.objects.create(
            owner=user,
            salt=salt,
            cipher_key=encrypt_key(backup_key, secret_key)
        )
        return user


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    objects = UserManager()


class UserBackupKey(models.Model):
    """ This key is derived using the salt, and the user's backup code
    """
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True
    )
    salt = models.BinaryField(max_length=16, null=False, blank=False)
    cipher_key = models.BinaryField(max_length=256, null=False, blank=False)


class UserPassphraseKey(models.Model):
    """ This key is derived using the salt, and the user's password
    """
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True
    )
    salt = models.BinaryField(max_length=16, null=False, blank=False)
    cipher_key = models.BinaryField(max_length=256, null=False, blank=False)


class RegistrationCode(models.Model):
    """ This is a one-time code that will allow a user to register
    this will allow a user to register without the server operator knowing
    specifically which code they used (unless they brute force the hashes)
    """
    code_hash = models.BinaryField(max_length=32, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    def __str__(self):
        if self.user is None:
            return 'Unused Registration Code'
        return '{}\'s Registration Code'.format(self.user.username)
