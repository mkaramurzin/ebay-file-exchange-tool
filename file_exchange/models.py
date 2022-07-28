from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    pass

class Field(models.Model):
    name = models.CharField(max_length=31)

class ListingInfo(models.Model):
    data = models.ManyToManyField(Field)

class File(models.Model):
    # Many-to-many
    csv_dir = models.CharField(max_length=63, default=None)
    headers = models.ManyToManyField(Field)
    listings = models.ManyToManyField(ListingInfo)