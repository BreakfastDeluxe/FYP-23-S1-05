from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# this is the Image model
#used to store info about the uploaded image
class Image(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_Image = models.ImageField(upload_to='images/')
    caption = models.CharField(max_length = 255, blank=True, null=True)
    keywords = models.CharField(max_length = 255, blank=True, null=True)
