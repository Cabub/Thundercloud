from django.shortcuts import render
from django.contrib.auth import login
from .models import User
from .forms import RegistrationForm
from .models import UserPassphraseKey, UserBackupKey
from .cryptography import generate_backup_passphrase


def register(request):
    template_name = 'registration/register.html'
    context = {
        'form': RegistrationForm
    }
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
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
