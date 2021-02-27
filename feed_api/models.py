from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_delete

def upload_location(instance, filename, **kwargs):
    file_path = 'feed/{uuid}/{filename}'.format(
            uuid=uuid.uuid4(),
            filename=filename
		) 
    return file_path

#https://www.django-rest-framework.org/api-guide/relations/#generic-relationships
#Generic Relations https://simpleisbetterthancomplex.com/tutorial/2016/10/13/how-to-use-generic-relations.html
class Vote(models.Model):
    UP_VOTE = 'U'
    DOWN_VOTE = 'D'
    VOTE_TYPES = (
        (UP_VOTE, 'Up Vote'),
        (DOWN_VOTE, 'Down Vote')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=1, choices=VOTE_TYPES)
    
    #Mandatory fields for generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    
class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(blank=False, null=False)
    postedDate = models.DateTimeField(auto_now_add=True, verbose_name="date posted")
    updatedDate = models.DateTimeField(auto_now=True, verbose_name="date updated")
    likes = GenericRelation(Vote)
    
#On Delete reference https://stackoverflow.com/questions/38388423/what-does-on-delete-do-on-django-models
class Feed(models.Model):
    class FeedType(models.IntegerChoices):
        Feed = 1
        Story = 2
        Ads = 3
        News = 4
        
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(blank=False, null=False)
    #images = models.ManyToManyField(Image, blank=True)
    type = models.IntegerField(choices=FeedType.choices, default=FeedType.Feed)
    comments = models.ManyToManyField(Comment, blank=True)
    likes = GenericRelation(Vote)
    postedDate = models.DateTimeField(auto_now_add=True, verbose_name="date posted")
    updatedDate = models.DateTimeField(auto_now=True, verbose_name="date updated")
    latitude = models.FloatField()
    longitude = models.FloatField()
    locationName = models.TextField()
    
    def getVoteCount(self):
        print(self.likes.all())
        
    def __str__(self):
        return str(self.id) + ' ' + self.author.name + ': ' + self.message
    
    
class Image(models.Model):
    image = models.ImageField(upload_to=upload_location)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="images")
    
    def __str__(self):
        return self.image.name
    
# @receiver(post_delete, sender=Feed)
# def submission_delete(sender, instance, **kwargs):
#     print(instance.clear())
#     print(instance.images.relations)
#     for image in instance.images.all():
#         print(image)
#         image.delete(False)