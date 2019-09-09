from django.contrib import admin
from django.urls import path, include
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
]


for app in settings.LOCAL_APPS:
    urlpatterns.append(path(app + '/', include('{0}.urls'.format(app))))
