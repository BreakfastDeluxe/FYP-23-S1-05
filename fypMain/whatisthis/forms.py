# forms.py
from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
 
 # form used to upload image
class ImageForm(forms.ModelForm):
 
    class Meta:
        model = Image
        fields = ['upload_Image']
        #this bit adds in the "uploaded_by" field to determine which user uploaded this image
        def form_valid(self, form):
            form.instance.created_by = self.request.user
            return super().form_valid(form)
        
class UserCreationForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ['username', 'password', 'email'] #creates form fields     
        
class LoginForm(AuthenticationForm):
    
    class Meta:
        model = User
        fields = ['username', 'password', 'remember_me'] #creates form fields
        
class UpdateUserForm(forms.ModelForm, PasswordChangeForm):
    
    class Meta:
        model = User
        fields = ['email', 'old_password', 'new_password1', 'new_password2']