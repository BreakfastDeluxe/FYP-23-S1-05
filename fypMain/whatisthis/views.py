from django.shortcuts import render
from django.urls import reverse_lazy
#from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.http import HttpResponse
from django.shortcuts import redirect
from .forms import *

import cv2
import argparse
import glob
import numpy as np
import requests

# Create your views here.
def index(request):
    return render(request, 'index.html')

def home(request):
    return render(request, "home.html")

class Login(LoginView):
    form_class = LoginForm
    template_name = "login.html"
    def form_valid(self, form):
       
        remember_me = form.cleaned_data['remember_me']  # get remember me data from cleaned_data of form
        if not remember_me:
            self.request.session.set_expiry(0)  # if remember me is 
            self.request.session.modified = True
        return super(Login, self).form_valid(form)

def menu(request):
    return render(request, "menu.html")

class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"

@login_required
def user(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your account was updated successfully')
            return redirect(to='user')
    else:
        user_form = UpdateUserForm(instance=request.user)
    return render(request, 'user.html', {'user_form': user_form})


def upload_image(request):

    if request.method == 'POST':  
        form = ImageForm(request.POST, request.FILES)  
        if form.is_valid():
            author = form.save(commit=False)
            author.created_by = request.user
            author.save()
            form.save_m2m()  
            form.save()  
            # Getting the current instance object to display in the template  
            id = request.user  # get current userid
            # Images = Image.objects.filter(created_by_id=id)#retrieve all image objects, filtered by current userid
            # getting latest uploaded Image by id attribute
            Images = Image.objects.latest('id')
            file = Images.upload_Image.url
            blur_value = blur_check(Images.upload_Image.url)
            keywords = generate_keywords(file) 
              
            return render(request, 'upload_image.html', {'form': form, 'image': file, 'blur' : blur_value, 'keywords':keywords})  
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
        file = Images.upload_Image.url
        blur_value = blur_check(Images.upload_Image.url)
        # send template and model to renderer
        return render(request, 'display_image.html', {'image': file, 'blur' : blur_value})

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
    
#API implementation to generate keywords
def generate_keywords(file):
    # Read the image
    file = '.'+file #look one folder above to ./media/images
    print(file)#debug print out filename
    
    client_id = 'aYCcWMVTisX1yqoSYKfGPgke'
    client_secret = '16BexRsEz3gI7vcJ7SbssuXVxYTabAMTF6mybzSK3GlaAqah'
    params = {'url': 'http://image.everypixel.com/2014.12/67439828186edc79b9be81a4dedea8b03c09a12825b_b.jpg', 'num_keywords': 10}
    keywords = requests.get('https://api.everypixel.com/v1/keywords', params=params, auth=(client_id, client_secret)).json()
    imageName = file
    with open(imageName,'rb') as image:
        data = {'data': image}
        keywords = requests.post('https://api.everypixel.com/v1/keywords', files=data, auth=(client_id, client_secret)).json()

    classified_keywords = ""
    print(keywords)#debug print out dictionary of keyword:confidence

    for i in keywords['keywords']:
        classified_keywords += "\n"
        if i['score'] > 0.8: #filter keywords by high confidence
            classified_keywords += i['keyword']
            #print(i['keyword'])

    print(classified_keywords)#debug print out high confidency keywords
    
    keywords = classified_keywords
    return keywords
    
#API implementation to generate caption TTS audio
def generate_audio():
        audio = None
        return audio