# Generated by Django 2.2.4 on 2019-09-19 17:31

from django.db import migrations, models
import django.utils.timezone
import files.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to=files.models.user_directory_path)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField()),
                ('cipher_key', models.BinaryField(max_length=256)),
                ('initialization_vector', models.BinaryField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(blank=True, editable=False, null=True)),
            ],
        ),
    ]
