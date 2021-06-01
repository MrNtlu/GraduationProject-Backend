from django.contrib import admin
from feed_api import models

admin.site.register(models.Feed)
admin.site.register(models.Comment)
admin.site.register(models.Image)
admin.site.register(models.FeedVote)
admin.site.register(models.Report)
admin.site.register(models.CommentLike)
admin.site.register(models.CommentReport)