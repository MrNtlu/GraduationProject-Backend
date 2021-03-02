from django.contrib import admin
from auth_api import models

admin.site.register(models.UserProfile)
admin.site.register(models.UserFollowing)