from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.core.files.uploadedfile import TemporaryUploadedFile
from .cryptography import Encrypter, generate_random_key, encrypt_key
from django.core.files import temp as tempfile
from django.conf import settings
from base64 import b64decode
import os

class EncryptedTemporaryUploadedFile(TemporaryUploadedFile):
    """
    A file uploaded to a temporary location (i.e. stream-to-disk).
    """

    def __init__(self, name, content_type, size, charset,
                 content_type_extra=None, cipher_key=None,
                 initialization_vector=None):
        self.cipher_key = cipher_key
        self.initialization_vector = initialization_vector
        _, ext = os.path.splitext(name)
        file = tempfile.NamedTemporaryFile(
            suffix='.upload' + ext, dir=settings.FILE_UPLOAD_TEMP_DIR
        )
        super().__init__(
             name, content_type, size, charset, content_type_extra
        )


class TemporaryFileEncryptingUploadHandler(TemporaryFileUploadHandler):
    def new_file(self, field_name, file_name, content_type, content_length,
                 charset=None, content_type_extra=None):
        if 'session_key' not in self.request.session:
            raise KeyError('session_key not in request.session')
        self.field_name = field_name
        self.file_name = file_name
        self.content_type = content_type
        self.content_length = content_length
        self.charset = charset
        self.content_type_extra = content_type_extra
        session_key = self.request.session['session_key'].encode()
        file_key = generate_random_key()
        self.encrypter = Encrypter(file_key)
        self.file = EncryptedTemporaryUploadedFile(
            self.file_name, self.content_type, 0, self.charset,
            self.content_type_extra, encrypt_key(session_key, file_key),
            self.encrypter.initialization_vector
        )

    def receive_data_chunk(self, raw_data, start):
        self.file.write(self.encrypter.encrypt(raw_data))
