import os
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F, Value, CharField, IntegerField
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, StreamingHttpResponse
from .models import File, Folder
from .serializers import FileSerializer, FolderSerializer, DirectorySerializer
from system.cryptography import DecryptingStreamReader, decrypt_key

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

    @action(detail=True)
    def download(self, request, pk):
        object = get_object_or_404(self.get_queryset(), pk=pk)
        session_key = request.session['session_key']
        reader = DecryptingStreamReader(
            object.file.file,
            decrypt_key(session_key, object.cipher_key),
            object.initialization_vector
        )
        response = StreamingHttpResponse(
            reader, content_type='application/octet-stream'
        )
        response['Content-Disposition'] = 'inline; filename={}'.format(
            object.name
        )
        response['Content-Length'] = object.file.file.size
        return response


class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer

    @action(detail=True, url_path='list')
    def list_directory(self, request, pk):
        instance = self.get_object()
        serializer = DirectorySerializer(instance)
        return Response(serializer.data)
