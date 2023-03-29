from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from .validators import *

# Create your models here.

# this is the Image model
#used to store info about the uploaded image
class Image(models.Model):
    #get the current logged in user's id and associate it with this uploaded image (set the ownership)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    #save the image to server
    upload_Image = models.ImageField(upload_to='images/', validators=[validate_file_size])
    #setup blank field for storing caption generation later
    caption = models.CharField(max_length = 255, blank=True, null=True)
    #setup blank field for storing keyword generation later
    keywords = models.CharField(max_length = 255, blank=True, null=True)
