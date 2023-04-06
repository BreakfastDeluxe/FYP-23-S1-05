from django.contrib import admin
#allows registered models to be managed from admin console (websiteurl)/admin
#login with superuser credentials to access console

# Register your models here.
from .models import *

admin.site.register(Image)
admin.site.register(Task)