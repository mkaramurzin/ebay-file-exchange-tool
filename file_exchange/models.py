from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    pass

class Field(models.Model):
    name = models.CharField(max_length=31, default="")
    value = models.CharField(max_length=31, default="")

class ListingInfo(models.Model):
    data = models.ManyToManyField(Field)

class File(models.Model):
    # Many-to-many
    csv_dir = models.CharField(max_length=63, default=None)
    headers = models.ManyToManyField(Field)
    static = models.ManyToManyField(Field, related_name="static_fields")
    listings = models.ManyToManyField(ListingInfo, related_name="unique_fields")

class SavedTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=31)
    file = models.ForeignKey(File, on_delete=models.CASCADE)