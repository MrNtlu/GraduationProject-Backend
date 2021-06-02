from django.contrib import admin
from feed_api import models

class FeedAdmin(admin.ModelAdmin):
    list_display = ('id','author', 'postedDate','message','type','isSpam','latitude', 'longitude','locationName')
    
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','author', 'postedDate','message', 'isSpam', 'feed')

admin.site.register(models.Feed, FeedAdmin)
admin.site.register(models.Comment, CommentAdmin)
admin.site.register(models.Image)
admin.site.register(models.FeedVote)
admin.site.register(models.Report)
admin.site.register(models.CommentLike)
admin.site.register(models.CommentReport)