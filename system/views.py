from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse as url_reverse
from django.contrib.auth import login
from django.contrib.auth.password_validation import validate_password
from .models import User
from .forms import RegistrationForm, PasswordResetForm
from .models import UserPassphraseKey, UserBackupKey
from django.contrib.auth.views import PasswordChangeView
from .cryptography import (
    generate_backup_passphrase, generate_salt, derive_passphrase_key,
    decrypt_key, encrypt_key
)


def register(request):
    template_name = 'registration/register.html'
    context = {
        'form': RegistrationForm
    }
    if request.method == 'POST':
        form = context['form'](request.POST)
        if form.is_valid():
            # do create user thing
            backup_passphrase = generate_backup_passphrase()
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                backup_passphrase=backup_passphrase
            )
            template_name = 'registration/welcome.html'
            context['backup_passphrase'] = backup_passphrase.decode().strip()
            login(request, user)
        else:
            context['errors'] = form.errors
    return render(request, template_name, context)


def reset_password(request):
    template_name = 'registration/password_reset_form.html'
    context = {
        'form': PasswordResetForm
    }
    if request.method == 'POST':
        form = context['form'](request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            backup_passphrase = form.cleaned_data.get('backup_passphrase')
            user_backup_key = UserBackupKey.objects.filter(
                owner__username=username
            ).select_related('owner').first()

            if user_backup_key is None:
                form.add_error(None, 'Username or Backup Key is incorrect')
            else:
                try:
                    validate_password(
                        form.cleaned_data['password'], user_backup_key.owner
                    )
                except forms.ValidationError as error:
                    form.add_error('password', error)

            # check again
            if form.is_valid():
                user = user_backup_key.owner
                user.set_password(form.cleaned_data['password'])
                user.save()
                backup_key = derive_passphrase_key(
                    backup_passphrase.encode(), user_backup_key.salt
                )
                # now that it's decrypted, re-encrypt it using the new password
                salt = generate_salt()
                passphrase_key = derive_passphrase_key(
                    form.cleaned_data['password'].encode(), salt
                )
                UserPassphraseKey.objects.update_or_create(
                    owner=user,
                    defaults={
                        'salt': salt,
                        'cipher_key': encrypt_key(passphrase_key, decrypt_key(
                            backup_key, user_backup_key.cipher_key
                        ))
                    }
                )
                return HttpResponseRedirect(url_reverse('password_reset_done'))
            else:
                context['errors'] = form.errors
    return render(request, template_name, context)


def reset_password_done(request):
    return render(request, 'registration/password_reset_done.html')


def change_password(request):
    response = PasswordChangeView.as_view()(request)
    if request.method == 'POST' and response.status_code == 302:
        # update UserPassphraseKey
        salt = generate_salt()
        passphrase_key = derive_passphrase_key(
            request.POST['new_password1'].encode(), salt
        )
        UserPassphraseKey.objects.update_or_create(
            owner=request.user,
            defaults={
                'salt': salt,
                'cipher_key': encrypt_key(
                    passphrase_key, request.session['session_key']
                )
            }
        )
    return response
