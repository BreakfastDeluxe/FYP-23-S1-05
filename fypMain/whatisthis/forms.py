# forms.py
from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
  
 
 # form used to upload image
class ImageForm(forms.ModelForm):
 
    class Meta:
        model = Image
        fields = ['upload_Image']
        #this bit adds in the "uploaded_by" field to determine which user uploaded this image
        def form_valid(self, form):
            form.instance.created_by = self.request.user
            return super().form_valid(form)

#inherit UserCreationForm and extend it to include an email field        
class UserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

#inherit AuthenticationForm and extend it to include remember_me boolean toggle        
class LoginForm(AuthenticationForm):
    #username and password are inherited from AuthenticationForm
    remember_me = forms.BooleanField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'remember_me'] #creates form fields
        
class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']

class CreateTaskForm(forms.ModelForm):
    task_keyword = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    task_complete = False
    
    class Meta:
        model = Task
        fields = ['task_keyword', 'task_complete']