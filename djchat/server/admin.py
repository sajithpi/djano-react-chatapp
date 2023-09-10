from django.contrib import admin

from .models import Category, Channels, Server

# Register your models here.

admin.site.register(Channels)
admin.site.register(Server)
admin.site.register(Category)
