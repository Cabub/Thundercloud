from django.shortcuts import render
from django.contrib.auth import login
from .models import User
from .forms import RegistrationForm
from files.cryptography import (
    derive_passphrase_key, generate_salt, encrypt_key,
    decrypt_key, generate_random_fernet_key, generate_backup_passphrase
)
from files.models import UserPassphraseKey, UserBackupKey


def register(request):
    template_name = 'registration/register.html'
    context = dict()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # do create user thing
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            salt = generate_salt()
            key = derive_passphrase_key(
                request.POST['password'].encode(), salt
            )
            secret_key = generate_random_fernet_key()
            UserPassphraseKey.objects.create(
                owner=user,
                salt=salt,
                cipher_key=encrypt_key(key, secret_key)
            )
            salt = generate_salt()
            backup_passphrase = generate_backup_passphrase()
            backup_key = derive_passphrase_key(
                backup_passphrase, salt
            )
            UserBackupKey.objects.create(
                owner=user,
                salt=salt,
                cipher_key=encrypt_key(backup_key, secret_key)
            )
            template_name = 'registration/welcome.html'
            context['backup_passphrase'] = backup_passphrase.decode().strip()
            login(request, user)
        else:
            context['errors'] = form.errors
    return render(request, template_name, context)
