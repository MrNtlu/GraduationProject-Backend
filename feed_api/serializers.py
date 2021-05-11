from rest_framework import serializers
from feed_api import models
from auth_api.serializers import UserProfileSerializer

class FeedVoteSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    vote = serializers.CharField(source='get_vote_display')
    class Meta:
        model = models.FeedVote
        fields = ['user', 'vote']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = ['image']
            
class FeedSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)
    author = UserProfileSerializer(required=False)
    votes = FeedVoteSerializer(models.FeedVote.objects.all(), many=True, required=False)
    upvote_count = serializers.SerializerMethodField()
    downvote_count = serializers.SerializerMethodField()
    type = serializers.CharField(source='get_type_display')
    class Meta:
        model = models.Feed
        fields = ['id','author','message','type','postedDate','updatedDate',
                  'latitude', 'longitude', 'locationName', 'images', 'votes',
                  'upvote_count', 'downvote_count']
    
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
    
    def get_upvote_count(self, obj):
        return models.FeedVote.objects.filter(feed=obj, vote=1).count()
    
    def get_downvote_count(self, obj):
        return models.FeedVote.objects.filter(feed=obj, vote=-1).count()
    
        
class CommentSerializer(serializers.ModelSerializer):
    #likes = VoteObjectRelatedField(many=True, queryset=models.Vote.objects.all(), required=False)
    author = UserProfileSerializer(required=False)

    class Meta:
        model = models.Comment
        fields = ['id','author','message','postedDate','updatedDate', ] #'likes'
        
    def create(self, validated_data):
        user = self.context['user']
        feed = self.context['feed']
        
        comment = models.Comment.objects.create(
            author=user,
            message=validated_data['message'],
            feed=feed
        )
            
        return comment