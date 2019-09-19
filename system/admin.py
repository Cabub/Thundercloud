from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, RegistrationCode
from .forms import RegistrationCodeModelForm


admin.site.register(User, UserAdmin)


class RegistrationCodeAdmin(admin.ModelAdmin):
    form = RegistrationCodeModelForm


admin.site.register(RegistrationCode, RegistrationCodeAdmin)
