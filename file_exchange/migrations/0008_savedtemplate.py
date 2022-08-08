# Generated by Django 4.0.5 on 2022-08-07 22:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('file_exchange', '0007_field_value_alter_field_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=31)),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='file_exchange.file')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
