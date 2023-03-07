from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView

from django.http import HttpResponse
from django.shortcuts import redirect
from .forms import *

import cv2
import argparse
import glob
import numpy as np

# Create your views here.
def index(request):
    return render(request, 'index.html')

def home(request):
    return render(request, "home.html")

def login(request):
    return render(request, "login.html")

class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"

def upload_image(request):

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)

        if form.is_valid():
            author = form.save(commit=False)
            author.created_by = request.user
            author.save()
            form.save_m2m()
            return redirect('display_image')
    else:
        form = ImageForm()
    return render(request, 'upload_image.html', {'form': form})

def display_image(request):

    if request.method == 'GET':

        # getting all the objects of Image by userid.
        id = request.user  # get current userid
        # Images = Image.objects.filter(created_by_id=id)#retrieve all image objects, filtered by current userid
        # getting latest uploaded Image by id attribute
        Images = Image.objects.latest('id')
        blur_value = blur_check(Images.upload_Image.url)
        # send template and model to renderer
        return render(request, 'display_image.html', {'image': Images, 'blur' : blur_value})

#HELPER FUNCTIONS

#openCV2 implementation to determine blur level
def blur_check(file):
    # Read the image
    file = '.'+file #look one folder above to ./media/images
    print(file)
    img = cv2.imread(file)

    # Convert to greyscale
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the laplacian of this image and
    # calculate the variance
    var = cv2.Laplacian(grey, cv2.CV_64F).var()

    # if variance is less than the set threshold
    # image is blurred otherwise not
    if var < 20:
        return('Image might be Blurred: '+str(var))
    else:
        return('Image Not Blurred: '+str(var))
    
#ML implementation to generate caption
def generate_caption():
        caption = None
        return caption
    
#ML implementation to generate keywords
def generate_keywords():
        keywords = None
        return keywords
    
#API implementation to generate caption TTS audio
def generate_audio():
        audio = None
        return audio