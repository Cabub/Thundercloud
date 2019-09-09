from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Folder


@login_required(login_url='/admin/login/')
def index(request):
    # ensure root folder exists
    root = request.user.folder_set.filter(parent__isnull=True).first()
    if root is None:
        root = Folder.objects.create(
            name='',
            owner=request.user,
            parent=None
        )

    return render(request, 'files/index.html', {"root": root})
