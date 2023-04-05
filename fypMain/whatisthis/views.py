from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import UpdateUserForm
from django.contrib.auth.views import PasswordChangeView

from django.http import HttpResponse
from django.shortcuts import redirect
from .forms import *

import cv2
import argparse
import glob
import numpy as np
import requests
import zlib

import joblib
from django.conf import settings

# Create your views here.


def index(request):
    return render(request, 'index.html')


def home(request):
    return render(request, "home.html")


class Login(LoginView):
    form_class = LoginForm
    template_name = "login.html"

    def form_valid(self, form):

        # get remember me data from cleaned_data of form
        remember_me = form.cleaned_data['remember_me']
        if not remember_me:
            self.request.session.set_expiry(0)  # if remember me is
            self.request.session.modified = True
        return super(Login, self).form_valid(form)

@login_required
def menu(request):
    return render(request, "menu.html")


class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"

def signup(request):
    if request.method == 'POST':
        sign_form = UserCreationForm(request.POST, instance=request.signup)

        if sign_form.is_valid():
            sign_form.save()
            name = sign_form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + name) 
            return redirect(to='login')

@login_required
def user(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='menu')
    else:
        user_form = UpdateUserForm(instance=request.user)
        
    return render(request, 'profile.html', {'user_form': user_form})

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('login')

class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('menu')

@login_required
def history(request):
    id = request.user  # get current userid
    if request.method == 'POST':
        search_query = request.POST.get('search_query')
        gallery_images = Image.objects.filter(created_by_id=id, keywords__icontains=search_query) | Image.objects.filter(created_by_id=id, caption__icontains=search_query)#retrieve all image objects, filtered by current userid and (matching keyword/caption)
        return render(request, "history.html", {'gallery_images': gallery_images})
    else: 
        
        gallery_images = Image.objects.filter(created_by_id=id)#retrieve all image objects, filtered by current userid
        #print(gallery_images)
        #for image in gallery_images:
        #    print(image.upload_Image.url)
        return render(request, "history.html", {'gallery_images': gallery_images})

@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        #rating system
        rating=request.POST.get('rating')
        if(rating):
            id = request.user  # get current userid
            # getting latest uploaded Image by id attribute
            Images = Image.objects.filter(created_by_id=id).latest('id')
            rate_caption(Images.id, rating)
        
        if form.is_valid():
            author = form.save(commit=False)
            author.created_by = request.user
            author.save()
            form.save_m2m()
            form.save()
            # Getting the current instance object to display in the template
            id = request.user  # get current userid
            # getting latest uploaded Image by id attribute
            Images = Image.objects.filter(created_by_id=id).latest('id')
            file = Images.upload_Image.url
            #blur checking function
            blur_value = blur_check(Images.upload_Image.url)
            if(blur_value):
                caption = 'This picture looks blurry but...'
                blur_warn = 'This picture might be blurry, could you try again?'
            else: 
                caption = ''
                blur_warn = ''
            #keyword generation function (everypixel API)
            keywords = generate_keywords(file)
            #brandon's image classifier
            #label = predict_image(file)
            #label = ''
            #image classifier (pytorch - DenseNet pretrained model)
            img_class = get_classification(file)
            #image captioner (pytorch - MSCOCO model - DO NOT USE FOR NOW)
            img_cap = generate_caption(file)
            caption += img_cap
            Images.caption = caption
            Images.keywords = keywords
            Images.save()
            #audio generation function (GTTS)
            audio = generate_audio(caption, file)
            task_completion = check_task_completion(keywords, request)
            return render(request, 'upload_image.html', {'form': form, 'image': file, 'blur' : blur_warn, 
                                                         'keywords': keywords, 'audio': audio, 'img_class' : img_class, 
                                                         'caption' : caption, 'task_completion': task_completion})
    else:
        form = ImageForm()
        id = request.user  # get current userid
        current_task = Task.objects.filter(created_by_id=id).latest('id')

    return render(request, 'upload_image.html', {'form': form, 'current_task' : current_task})
	

#allow current user to delete their own account
#initially links to prompt page to confirm delete
@login_required
def delete_user(request):
    user = request.user
    if request.method == 'POST':
        user.delete()
        return redirect(to='login')

    return render(request, 'delete_user.html')

# HELPER FUNCTIONS

# openCV2 implementation to determine blur level
def blur_check(file):
    # Read the image
    file = '.'+file  # look one folder above to ./media/images
    #print(file) #debug use
    img = cv2.imread(file)
    # Convert to greyscale
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Find the laplacian of this image and
    # calculate the variance
    var = cv2.Laplacian(grey, cv2.CV_64F).var()
    # if variance is less than the set threshold
    # image is blurred otherwise not
    if var < 20:#if blurry, return 1
        return (1)
    else:#else return 0
        return (0)

# ML implementation to generate caption
from .img_caption import inference
def generate_caption(file):
    content_bytes= img_to_bytes(file)
    caption_list = inference(content_bytes)#returns a list of caption:confidence pairs
    caption = caption_list[0][0]#extract caption with highest confidence
    if(caption):
        return 'I think i see...' + caption
    else:
        return "Error: Caption not generated"

# API implementation to generate keywords
def generate_keywords(file):
    # Read the image
    file = '.'+file  # look one folder above to ./media/images
    #print(file)  # debug print out filename
    #set API parameters
    client_id = 'aYCcWMVTisX1yqoSYKfGPgke'
    client_secret = '16BexRsEz3gI7vcJ7SbssuXVxYTabAMTF6mybzSK3GlaAqah'
    params = {'url': 'http://image.everypixel.com/2014.12/67439828186edc79b9be81a4dedea8b03c09a12825b_b.jpg', 'num_keywords': 10}
    keywords = requests.get('https://api.everypixel.com/v1/keywords',
                            params=params, auth=(client_id, client_secret)).json()
    #open image file and send to API to get keywords
    imageName = file
    with open(imageName, 'rb') as image:
        data = {'data': image}
        keywords = requests.post('https://api.everypixel.com/v1/keywords',
                                 files=data, auth=(client_id, client_secret)).json()

    classified_keywords = ""
    #print(keywords)  # debug print out dictionary of keyword:confidence
    if(keywords):
        #iterate though dictionary to extract keywords
        for i in keywords['keywords']:
            classified_keywords += "\n"
            if i['score'] > 0.6:  # filter keywords by high confidence
                classified_keywords += i['keyword']
                # print(i['keyword']) #debug print out keywords
            else:
                classified_keywords += 'Low Confidence: '
                classified_keywords += i['keyword']
    else:
        classified_keywords = 'Error: No Keywords could be generated'

    #print(classified_keywords)  # debug print out high confidence keywords

    keywords = classified_keywords
    return keywords

# API implementation to generate caption TTS audio
import os
from gtts import gTTS
import shutil

def generate_audio(text, file):
    audioFilename = os.path.basename(file)+'.mp3'
    lang = 'en'
    tts = gTTS(text, lang=lang)
    save_path = './media/audio/' + audioFilename
    tts.save(save_path)

    return save_path

from django.shortcuts import render
from PIL import Image as myImage
import numpy as np
import keras
import os
from joblib import load

def predict_image(file):
    
    model_path = './whatisthis/MLmodel/cnn_model.joblib'

    if os.path.exists(model_path):
        model_load = joblib.load(model_path)
    else:
        raise Exception(f"{model_path} does not exist")
    
    file = '.'+file  # look one folder above to ./media/images
 
    img = myImage.open(file).convert('RGB')
    img = img.resize((128, 128)) 
    img = np.array(img) / 255.0 # Normalize 
        
	# Make the prediction
    pred = model_load.predict(np.array([img]))
    label = 'Dog' if pred[0] >= 0.5 else 'Cat'
    
    return label

#pytorch helpers

from torchvision import models
from torchvision import transforms
from django.conf import settings
import json, io
import PIL.Image #can't iuse Image as it will conflict with Image(object) used for upload_image

#model_DenseNet = models.densenet121(pretrained=True) #depreciated
model_DenseNet = models.densenet121(weights='DenseNet121_Weights.DEFAULT')
model_DenseNet.eval()
#get imagenet natural language text mappings
json_path = os.path.join(settings.STATIC_ROOT, "imagenet_class_index.json")
imagenet_mapping = json.load(open(json_path))

from torchvision import transforms

def transform_image(image_bytes):
    """
    Transforms image into required DenseNet format: 224x224 with 3 RGB channels and normalized.
    And returns the corresponding tensor.
    """
    my_transforms = transforms.Compose([transforms.Resize(255),
                                        transforms.CenterCrop(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    image = PIL.Image.open(io.BytesIO(image_bytes))
    return my_transforms(image).unsqueeze(0)

#convert image to raw bytes for ML processing (used by both classifier and caption-er)
def img_to_bytes(file):
    # Load image (it is loaded as BGR by default)
    file = '.'+file  # look one folder above to ./media/images
    image = cv2.imread(file)
    # Conver array to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # image encoding
    success, encoded_image = cv2.imencode('.jpeg', image)
    # convert encoded image to bytearray
    return encoded_image.tobytes()
    
def get_classification(file):
    """For given image bytes, predict the classification label using the pretrained DenseNet"""
    # convert encoded image to bytearray
    content_bytes = img_to_bytes(file)
    #print(content_bytes) #debug print raw data
    tensor = transform_image(content_bytes)
    outputs = model_DenseNet.forward(tensor)
    _, y_hat = outputs.max(1)
    predicted_idx = str(y_hat.item())
    class_name, human_label = imagenet_mapping[predicted_idx]#map predicted index to imagenet text map
    return human_label

def delete_image(request):
    #when delete button in image selected, delete image and reload gallery
    image_id = request.POST.get('image_id')
    #print('image id = ' + image_id)
    image = Image.objects.get(id=image_id)
    image.delete()
    return redirect(to='gallery')

def manage_tasks(request):
    if request.method == 'POST':
        form = CreateTaskForm(request.POST)
        if form.is_valid():
            author = form.save(commit=False)
            author.created_by = request.user
            author.save()
            form.save_m2m()
            form.save()
    else: 
        form  = CreateTaskForm()
    id = request.user  # get current userid
    #get all of the tasks of this user
    tasks = Task.objects.filter(created_by_id=id)
    if(tasks):
        #get the latest task (outstanding task)
        current_task = Task.objects.filter(created_by_id=id).latest('id')
        if(current_task.task_complete == False): #if the task is not complete
            #print('blocking')
            block_new_task = False#dont allow a new task to be created
        else:
            block_new_task = True
        return render(request, 'tasks.html', {'form': form, 'tasks':tasks, 'current_task': current_task, 'block_new_task': block_new_task})
    else:
        block_new_task = True
    return render(request, 'tasks.html', {'form': form, 'tasks':tasks, 'block_new_task': block_new_task})

def check_task_completion(keywords, request):
    user_id = request.user.id  # get current userid
    current_task = Task.objects.filter(created_by_id=user_id).latest('id')
    if current_task.task_keyword in keywords:
        current_task.task_complete = True
        current_task.save()
        user = User.objects.get(id=user_id)
        user.customuser.score += 1
        user.customuser.save()
        return 1
    else:
        return 0
    
def rate_caption(image_id, option):
    #print(option)
    image = Image.objects.get(id = image_id)
    option = int(option)
    
    if(option >= 1):
        image.rating = 1
    else:
        if(option <= 0):
            image.rating = -1
    image.save()
    return 0