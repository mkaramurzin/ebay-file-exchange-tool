# Generated by Django 4.0.5 on 2022-07-28 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('file_exchange', '0002_field_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='csv',
        ),
        migrations.AddField(
            model_name='file',
            name='csv_dir',
            field=models.CharField(default=None, max_length=63),
        ),
    ]
