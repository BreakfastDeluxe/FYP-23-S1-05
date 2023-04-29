# import the trained model (written in other file for compartmentalization)
from .img_caption import inference
import shutil
from gtts import gTTS
import os
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
from django.views.generic.edit import UpdateView
from .forms import ConfirmPasswordForm
from .decorators import confirm_password
from django.http import HttpResponse
from django.shortcuts import redirect
from .forms import *
from django.views.generic.edit import UpdateView
from .forms import ConfirmPasswordForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate

import cv2
import argparse
import glob
import numpy as np
import requests
import zlib

import joblib
from django.conf import settings

# Create your views here.

# webpage implementation views (acts as controller to gather and serve resources to django front-end, associated to URL)

# view for home page (landing page)


def home(request):
    return render(request, "home.html")

# class based view for login page (implement default django login w/ custom html)


class Login(LoginView):
    form_class = LoginForm
    template_name = "login.html"

    def form_valid(self, form):

        # get remember me data from cleaned_data of form
        remember_me = form.cleaned_data['remember_me']
        if not remember_me:
            self.request.session.set_expiry(0)  # if remember me is
            self.request.session.modified = True
        else:
            for key, error in list(form.errors.items()):
                if key == 'captcha' and error[0] == 'This field is required.':
                    messages.error(
                        self.request, "You must pass the reCAPTCHA test")
        return super(Login, self).form_valid(form)

# view for menu (after user login)
# decorator prevents unauthorised access from non-login user


@login_required
def menu(request):
    return render(request, "menu.html")


def task_pass(request):
    if request.method == 'POST':
        sample_pin = request.POST['pin']
        ref_pin = request.user.customuser.pin
        if sample_pin == ref_pin:
            return redirect('tasks')
        else:
            messages.error(request, 'Incorrect Pin!')
    return render(request, "confirm_password.html", {'form': PinForm})


def acc_pass(request):
    if request.method == 'POST':
        sample_pin = request.POST['pin']
        print("sample:")
        print(sample_pin)
        ref_pin = request.user.customuser.pin
        print("ref:")
        print(ref_pin)
        if sample_pin == ref_pin:
            return redirect('user')
        else:
            messages.error(request, 'Incorrect Pin!')
    return render(request, "confirm_password.html", {'form': PinForm})


# class based view for signup page (implement default django signup form w/ custom html)
class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"

# view for user account management
# displays current log-in user info, allows user to edit username, email, password
# redirect back to menu upon success
# view for user account management
# displays current log-in user info, allows user to edit username, email, password
# redirect back to menu upon success


@login_required
# @confirm_password
def user(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        Pin_Form = PinForm(request.POST, instance=request.user.customuser)
        if user_form.is_valid():
            user_form.save()
            Pin_Form.save()
            return redirect(to='menu')
    else:
        Pin_Form = PinForm(instance=request.user.customuser)
        user_form = UpdateUserForm(instance=request.user)

    return render(request, 'user.html', {'user_form': user_form, 'PinForm': Pin_Form})

# class based view for reset password e-mailer


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('login')

# class based view for password change form


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('menu')

# view for gallery, displays all images previously uploaded by the user


@login_required
def gallery(request):
    id = request.user  # get current userid
    if request.method == 'POST':
        search_query = request.POST.get('search_query')
        gallery_images = Image.objects.filter(created_by_id=id, keywords__icontains=search_query) | Image.objects.filter(
            created_by_id=id, caption__icontains=search_query)  # retrieve all image objects, filtered by current userid and (matching keyword/caption)
        return render(request, "gallery.html", {'gallery_images': gallery_images})
    else:

        # retrieve all image objects, filtered by current userid
        gallery_images = Image.objects.filter(created_by_id=id)
        # print(gallery_images)
        # for image in gallery_images:
        #    print(image.upload_Image.url)
        return render(request, "gallery.html", {'gallery_images': gallery_images})

# main function, accessed when user presses "start" button


@login_required
def upload_image(request):
    id = request.user  # get current userid
    current_task = Task.objects.filter(created_by_id=id)  # get current task
    if not current_task:  # if no current task, dont display
        current_task = None
    else:  # display current task
        current_task = current_task.latest('id')
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        # rating system
        rating = request.POST.get('rating')
        if (rating):
            id = request.user  # get current userid
            # getting latest uploaded Image by id attribute
            Images = Image.objects.filter(created_by_id=id).latest('id')
            rate_caption(Images.id, rating)  # rate the caption +vely or -vely

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

            # blur checking function (using opencv2) determine if image is blurry, tell user if it is. (warn that it will affect result)
            blur_value = blur_check(Images.upload_Image.url)
            if (blur_value):
                caption = 'This picture looks blurry but...'
                blur_warn = 'This picture might be blurry, could you try again?'
            else:
                caption = ''
                blur_warn = ''

            # image caption + keyword generation function ((pytorch - DenseNet pretrained model + MSCOCO model training))
            keywords = generate_caption(file)[1]
            img_cap = generate_caption(file)[0]
            caption += img_cap
            Images.caption = caption
            Images.keywords = keywords
            Images.save()
            # audio generation function (GTTS)
            audio = generate_audio(caption, file)
            task_completion = check_task_completion(keywords, caption, request)
            return render(request, 'upload_image.html', {'form': form, 'image': file, 'blur': blur_warn,
                                                         'keywords': keywords, 'audio': audio,
                                                         'caption': caption, 'task_completion': task_completion, 'current_task': current_task})
    else:  # display blank upload_image form, display task if outstanding task exists
        form = ImageForm()
        return render(request, 'upload_image.html', {'form': form, 'current_task': current_task})


# allow current user to delete their own account
# initially links to prompt page to confirm delete
@login_required
def delete_user(request):
    user = request.user
    if request.method == 'POST':
        user.delete()
        return redirect(to='login')

    return render(request, 'delete_user.html')


def delete_image(request):
    # when delete button in image selected, delete image and reload gallery
    image_id = request.POST.get('image_id')
    # print('image id = ' + image_id)
    image = Image.objects.get(id=image_id)
    image.delete()
    return redirect(to='gallery')

# view for task management page


def manage_tasks(request):
    if request.method == 'POST':  # if form was submitted, process form data
        form = CreateTaskForm(request.POST)
        if form.is_valid():
            author = form.save(commit=False)
            author.created_by = request.user
            author.save()
            form.save_m2m()
            form.save()
    else:  # display create task page
        form = CreateTaskForm()
    id = request.user  # get current userid
    # get all of the tasks of this user
    tasks = Task.objects.filter(created_by_id=id)
    if (tasks):
        # get the latest task (outstanding task)
        current_task = Task.objects.filter(created_by_id=id).latest('id')
        if (current_task.task_complete == False):  # if the task is not complete
            # print('blocking')
            block_new_task = False  # dont allow a new task to be created
        else:
            block_new_task = True  # allow new task to be created
        return render(request, 'tasks.html', {'form': form, 'tasks': tasks, 'current_task': current_task, 'block_new_task': block_new_task})
    else:
        block_new_task = True  # allow new task to be created
    return render(request, 'tasks.html', {'form': form, 'tasks': tasks, 'block_new_task': block_new_task})

def delete_task(request):
    # when delete button in image selected, delete image and reload gallery
    task_id = request.POST.get('task_id')
    task = Task.objects.get(id=task_id)
    task.delete()
    return redirect(to='tasks')

# HELPER FUNCTIONS - called by view implementation functions

# openCV2 implementation to determine blur level


def blur_check(file):
    # Read the image
    file = '.'+file  # look one folder above to ./media/images
    # print(file) #debug use
    img = cv2.imread(file)
    # Convert to greyscale
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Find the laplacian of this image and
    # calculate the variance
    var = cv2.Laplacian(grey, cv2.CV_64F).var()
    # if variance is less than the set threshold
    # image is blurred otherwise not
    if var < 20:  # if blurry, return 1
        return (1)
    else:  # else return 0
        return (0)


# ML implementation to generate caption


def generate_caption(file):
    content_bytes = img_to_bytes(file)  # convert image to byte-data
    # call ML evaluation function, returns a list of caption:confidence pairs
    caption_list = inference(content_bytes)
    # print("Full caption list")
    # print(caption_list)
    # extract and collate generated keywords across spread of confidence levels
    fullStr = ""
    for item in caption_list:
        fullStr += item[0]
        fullStr += ' '

    def unique_list(l):
        ulist = []
        [ulist.append(x) for x in l if x not in ulist]
        return ulist

    fullStr = ' '.join(unique_list(fullStr.split()))
    print("Extracted Keywords list")
    print(fullStr)

    caption = caption_list[0][0]  # extract caption with highest confidence
    if (caption):
        # return array[caption, keyword]
        return 'I think i see...' + caption, fullStr
    else:
        return "Error: Caption not generated"


# package implementation to generate caption TTS audio
# using gTTS, feed in text and language params, save output audio as filename.mp3


def generate_audio(text, file):
    audioFilename = os.path.basename(file)+'.mp3'
    lang = 'en'
    tts = gTTS(text, lang=lang)
    save_path = './media/audio/' + audioFilename
    tts.save(save_path)

    return save_path

# pytorch helpers

# convert image to raw byte-data for ML processing (used by caption-er)


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


# used in upload_image view after user uploads an image.
# checks current task keyword against caption & keywords, if there is a match, increase customuser.score , else do nothing
def check_task_completion(keywords, caption, request):
    user_id = request.user.id  # get current userid
    try:
        current_task = Task.objects.filter(created_by_id=user_id).latest('id')
    except Task.DoesNotExist:
        return 0

    def complete_task():
        current_task.task_complete = True
        current_task.save()
        user = User.objects.get(id=user_id)
        user.customuser.score += 1
        user.customuser.save()

    if current_task.task_keyword in caption:
        complete_task()
        return 1
    else:
        if current_task.task_keyword in keywords:
            complete_task()
            return 1
        else:
            return 0

# used in upload_image view, take in image_id and user option(thumb up(1)/down(0)), set image(model).rating accordingly


def rate_caption(image_id, option):
    # print(option)
    image = Image.objects.get(id=image_id)
    option = int(option)

    if (option >= 1):
        image.rating = 1
    else:
        if (option <= 0):
            image.rating = -1
    image.save()
    return 0


class ConfirmPasswordView(UpdateView):
    form_class = ConfirmPasswordForm
    template_name = 'confirm_password.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return self.request.get_full_path()
