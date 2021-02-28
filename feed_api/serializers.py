from rest_framework import serializers
from feed_api import models
from auth_api.serializers import UserProfileSerializer

#REF https://www.django-rest-framework.org/api-guide/relations/#generic-relationships
# https://stackoverflow.com/questions/38721923/serializing-a-generic-relation-in-django-rest-framework
class VoteObjectRelatedField(serializers.RelatedField):
    
    def to_representation(self, value):
        if isinstance(value, models.Feed):
            return 'Feed: ' + value.likes
        elif isinstance(value, models.Comment):
            return 'Comment: ' + value.likes
        raise Exception('Unexpected type of voted object')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = ['image']    


class FeedSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)
    author = UserProfileSerializer(required=False)
    likes = VoteObjectRelatedField(many=True, queryset=models.Vote.objects.all(), required=False)
    type = serializers.CharField(source='get_type_display')
    class Meta:
        model = models.Feed
        fields = ['id','author','message','type','postedDate','updatedDate',
                  'latitude', 'longitude', 'locationName', 'images', 'likes']
    
    def create(self, validated_data):
        images = self.context['images']
        user = self.context['user']
        
        feed = models.Feed.objects.create(
            author=user,
            message=validated_data['message'],
            type=validated_data['get_type_display'],
            latitude=validated_data['latitude'],
            longitude=validated_data['longitude'],
            locationName=validated_data['locationName']
        )
        
        for image in images:
            models.Image.objects.create(feed=feed, image=image)
            
        return feed
    
        
class CommentSerializer(serializers.ModelSerializer):
    likes = VoteObjectRelatedField(many=True, queryset=models.Vote.objects.all(), required=False)
    author = UserProfileSerializer(required=False)

    class Meta:
        model = models.Comment
        fields = ['id','author','message','postedDate','updatedDate', 'likes']
        
    def create(self, validated_data):
        user = self.context['user']
        feed = self.context['feed']
        
        comment = models.Comment.objects.create(
            author=user,
            message=validated_data['message'],
            feed=feed
        )
            
        return comment