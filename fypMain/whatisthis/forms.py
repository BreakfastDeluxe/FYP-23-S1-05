# forms.py
from django import forms
from .models import *
 
 # form used to upload image
class ImageForm(forms.ModelForm):
 
    class Meta:
        model = Image
        fields = ['upload_Image']
        #this bit adds in the "uploaded_by" field to determine which user uploaded this image
        def form_valid(self, form):
            form.instance.created_by = self.request.user
            return super().form_valid(form)