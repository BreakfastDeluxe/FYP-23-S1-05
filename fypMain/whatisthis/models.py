from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from .validators import *
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    rating = models.IntegerField(default=0)

class Task(models.Model):
    #get the current logged in user's id and associate it with this uploaded image (set the ownership)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    #used to describe the task given to the child
    #used to score the image taken
    task_keyword = models.CharField(max_length=255)
    task_complete = models.BooleanField()

from django.db.models.signals import post_save
from django.dispatch import receiver
#1-1 relationship, auto created with each user to store score
#invoke using User.customuser
class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) #1-1 foreign key
    score = models.IntegerField(default=0) #task system running score
    pin = models.CharField(max_length=6, default='000000')

@receiver(post_save, sender=User)#when user is created, create associated customUser
def create_custom_user(sender, instance, created, **kwargs):
    if created:
        CustomUser.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_custom_user(sender, instance, **kwargs):
    instance.customuser.save()
