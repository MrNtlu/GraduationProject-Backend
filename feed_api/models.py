from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.db.models import Func, F

def upload_location(instance, filename, **kwargs):
    file_path = 'feed/{uuid}/{filename}'.format(
            uuid=uuid.uuid4(),
            filename=filename
		) 
    return file_path

#On Delete reference https://stackoverflow.com/questions/38388423/what-does-on-delete-do-on-django-models
class Feed(models.Model):
    class FeedType(models.IntegerChoices):
        Feed = 1
        Story = 2
        Ads = 3
        News = 4
        
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(blank=False, null=False)
    type = models.IntegerField(choices=FeedType.choices, default=FeedType.Feed)
    postedDate = models.DateTimeField(auto_now_add=True, verbose_name="date posted")
    updatedDate = models.DateTimeField(auto_now=True, verbose_name="date updated")
    latitude = models.FloatField()
    longitude = models.FloatField()
    locationName = models.TextField()
        
    def __str__(self):
        return str(self.id) + ' ' + self.author.name + ': ' + self.message
    
    def delete(self, *args, **kwargs):
        for image in self.images.all():
            storage, path = image.image.storage, image.image.path
            storage.delete(path)
        super(Feed, self).delete(*args, **kwargs)
        
class FeedVote(models.Model):
    class VoteType(models.IntegerChoices):
        UpVote = 1
        DownVote = -1
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    vote = models.IntegerField(choices=VoteType.choices, default=VoteType.UpVote)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="votes")
    
    def __str__(self):
        return str(self.user.name) + ' voted ' + str(self.feed.id) + ' vote type is ' + str(self.vote)
    
class Report(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="reports")
    reportDate = models.DateTimeField(auto_now_add=True, verbose_name="date reported")
    
class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(blank=False, null=False)
    postedDate = models.DateTimeField(auto_now_add=True, verbose_name="date posted")
    updatedDate = models.DateTimeField(auto_now=True, verbose_name="date updated")
    #likes = GenericRelation(Vote)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="comments")
    
    def __str__(self):
        return self.author,': ',self.message
    

class Image(models.Model):
    image = models.ImageField(upload_to=upload_location)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="images")
    
    def __str__(self):
        return self.image.name