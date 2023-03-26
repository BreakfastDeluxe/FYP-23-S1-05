from django.db import models
from django.contrib.auth.models import User
from PIL import Image


# Create your models here.

# this is the Image model
#used to store info about the uploaded image
class Image(models.Model):
    #get the current logged in user's id and associate it with this uploaded image (set the ownership)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    #save the image to server
    upload_Image = models.ImageField(upload_to='images/')
    #setup blank field for storing caption generation later
    caption = models.CharField(max_length = 255, blank=True, null=True)
    #setup blank field for storing keyword generation later
    keywords = models.CharField(max_length = 255, blank=True, null=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField()

    def __str__(self):
        return self.user.username
    
# resizing images
def save(self, *args, **kwargs):
    Image.super().save()

    img = Image.open(self.avatar.path)

    if img.height > 100 or img.width > 100:
        new_img = (100, 100)
        img.thumbnail(new_img)
        img.save(self.avatar.path)
    caption = models.CharField(max_length = 255, blank=True, null=True)
    keywords = models.CharField(max_length = 255, blank=True, null=True)


#Brandon changes start here
class MLModel(models.Model):
    model_file = models.FileField(upload_to ='cnn_model.joblib')