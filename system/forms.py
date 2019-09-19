from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.forms.models import InlineForeignKeyField
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import AnonymousUser
from .models import RegistrationCode
from .cryptography import derive_unsalted_hash


def validate_registration_code_unused(value):
    # validate that this registration code exists and hasn't been used
    if not RegistrationCode.objects.filter(
            user__isnull=True, code_hash=derive_unsalted_hash(value.encode())
       ).exists():
        raise ValidationError(
            "This registration code either doesn't exist, or is in use"
        )


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')
    password = forms.CharField(
        max_length=150,
        label='Password',
        widget=widgets.PasswordInput
    )
    password2 = forms.CharField(
        max_length=150,
        label='Confirm Password',
        widget=widgets.PasswordInput,
    )
    registration_code = forms.CharField(
        max_length=10, min_length=10, label='Registration Code',
        validators=(
            validators.MaxLengthValidator, validators.MinLengthValidator,
            validate_registration_code_unused
        )
    )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get('password2')
        if password:
            try:
                validate_password(password, AnonymousUser())
            except forms.ValidationError as error:
                self.add_error('password2', error)


class PasswordResetForm(forms.Form):
    username = forms.CharField(
        max_length=150, label='Username'
    )
    backup_passphrase = forms.CharField(
        max_length=500,
        label='Backup Passphrase'
    )
    password = forms.CharField(
        max_length=150,
        label='New Password',
        widget=widgets.PasswordInput
    )
    password2 = forms.CharField(
        max_length=150,
        label='Confirm Password',
        widget=widgets.PasswordInput
    )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2


class RegistrationCodeModelForm(forms.ModelForm):
    registration_code = forms.CharField(
        max_length=10, min_length=10
    )

    def _post_clean(self):
        opts = self._meta

        exclude = self._get_validation_exclusions()

        for name, field in self.fields.items():
            if isinstance(field, InlineForeignKeyField):
                exclude.append(name)

        try:
            self.instance = RegistrationCode(
                code_hash=derive_unsalted_hash(
                    self.cleaned_data['registration_code'].encode()
                )
            )
        except ValidationError as e:
            self._update_errors(e)

        try:
            self.instance.full_clean(exclude=exclude, validate_unique=False)
        except ValidationError as e:
            self._update_errors(e)

        # Validate uniqueness if needed.
        if self._validate_unique:
            self.validate_unique()

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            # errors for code_hash are actually for registration_code
            code_hash_errors = e.args[0].pop('code_hash', None)
            if code_hash_errors is not None:
                e = ValidationError({
                    'registration_code': code_hash_errors
                }, *e.args[1:])
            self._update_errors(e)

    class Meta:
        model = RegistrationCode
        exclude = ('code_hash', 'user')
