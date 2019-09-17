from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from .cryptography import (
    derive_passphrase_key, generate_salt, encrypt_key,
    decrypt_key, generate_random_fernet_key
)
from .models import UserPassphraseKey


@receiver(user_logged_in)
def prepare_session_key(sender, user, request, **kwargs):
    # build session key from password
    if 'password' in request.POST:
        passphrase_key = UserPassphraseKey.objects.filter(owner=user).first()
        key = derive_passphrase_key(
            request.POST['password'].encode(), passphrase_key.salt
        )
        request.session['session_key'] = decrypt_key(
            key, passphrase_key.cipher_key
        ).decode()
        request.session.modified = True
