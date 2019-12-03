from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Allergies)
admin.site.register(Genres)
admin.site.register(Menu)
