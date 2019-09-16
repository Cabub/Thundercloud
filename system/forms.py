from django import forms


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField()
    registration_code = forms.CharField(max_length=10)
    
