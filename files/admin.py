from django.contrib import admin
from .models import File, Folder

print("test")


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    pass


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    pass
