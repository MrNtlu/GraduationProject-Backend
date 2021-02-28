from rest_framework import serializers
from feed_api import models
from auth_api.serializers import UserProfileSerializer

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = ['image']    

class FeedSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)
    author = UserProfileSerializer(required=False)
    type = serializers.CharField(source='get_type_display') 
    class Meta:
        model = models.Feed
        fields = ['id','author','message','type','postedDate', 'latitude', 'longitude', 'locationName', 'images']
    
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
    class Meta:
        model = models.Comment
        fields = ['message']
        
class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Vote
        fields = ['activity_type']
        
