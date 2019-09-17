from uuid import uuid4
from django.db import models
from django.db.models import Value
from django.conf import settings
from django.utils import timezone


def user_directory_path(instance, filename):
    return '{0}/{1}'.format(instance.owner.id, uuid4())


class Folder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(blank=True, null=False, max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        'files.Folder',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created = models.DateTimeField(editable=False, default=timezone.now)
    modified = models.DateTimeField(null=True, blank=True, editable=False)

    @property
    def path(self):
        if self.parent is None:
            return '/'
        parent_path = self.parent.path
        if parent_path.endswith('/'):
            return parent_path + self.name
        return parent_path + '/' + self.name

    @property
    def children(self):
        folders = Folder.objects.filter(parent=self).annotate(
            type=Value('d', output_field=models.CharField(max_length=1))
        )
        files = File.objects.filter(parent=self).annotate(
            type=Value('f', output_field=models.CharField(max_length=1))
        )
        return folders.values(
            'id', 'name', 'type', 'created', 'modified'
        ).union(files.values(
            'id', 'name', 'type', 'created', 'modified'
        ))

    def save(self, *args, **kwargs):
        self.modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        if self.parent is not None:
            return str(self.parent) + '/' + self.name
        return ''

    class Meta:
        unique_together = (('name', 'owner', 'parent'),)


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(blank=False, null=False, max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        'files.Folder',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    file = models.FileField(upload_to=user_directory_path)
    created = models.DateTimeField(editable=False, default=timezone.now)
    modified = models.DateTimeField()
    cipher_key = models.BinaryField(max_length=256, null=False, blank=False)
    initialization_vector = models.BinaryField(
        max_length=16, null=False, blank=False
    )

    @property
    def path(self):
        if self.parent is None:
            return '/'
        parent_path = self.parent.path
        if parent_path.endswith('/'):
            return parent_path + self.name
        return parent_path + '/' + self.name

    def save(self, *args, **kwargs):
        self.modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        if self.parent is not None:
            return str(self.parent) + '/' + self.name
        return '/' + self.name

    class Meta:
        unique_together = (('name', 'owner', 'parent'),)
