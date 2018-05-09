from django.contrib import admin
from .models import Meow, UserProfile

# Register your models here.

admin.site.register(Meow)
admin.site.register(UserProfile)