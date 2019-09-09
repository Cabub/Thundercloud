from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from .cryptography import (
    derive_passphrase_key, generate_salt, encrypt_key,
    decrypt_key, generate_random_fernet_key
)
from .models import UserPassphraseKey, File


@receiver(user_logged_in)
def prepare_session_key(sender, user, request, **kwargs):
    # build session key from password
    if 'password' in request.POST:
        passphrase_key = UserPassphraseKey.objects.filter(owner=user).first()
        if passphrase_key is None:
            salt = generate_salt()
            key = derive_passphrase_key(
                request.POST['password'].encode(), salt
            )
            random_key = generate_random_fernet_key()
            print('session key is: {}'.format(random_key.decode()))
            passphrase_key = UserPassphraseKey.objects.create(
                owner=user,
                salt=salt,
                cipher_key=encrypt_key(key, random_key)
            )
        else:
            key = derive_passphrase_key(
                request.POST['password'].encode(), passphrase_key.salt
            )

        # save key to session
        print('session key is: {}'.format(decrypt_key(key, passphrase_key.cipher_key).decode()))
        request.session['session_key'] = decrypt_key(
            key, passphrase_key.cipher_key
        ).decode()
        request.session.modified = True
