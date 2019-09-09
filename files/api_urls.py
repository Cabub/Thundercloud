from django.urls import path, include
from rest_framework import routers
from .api_views import FileViewSet, FolderViewSet

api = routers.DefaultRouter(trailing_slash=False)
api.register(r'file', FileViewSet)
api.register(r'folder', FolderViewSet)

urlpatterns = [
    path('v1/', include(api.urls)),
]
