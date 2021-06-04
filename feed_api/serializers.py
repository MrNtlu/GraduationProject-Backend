from rest_framework import serializers
from feed_api import models
from auth_api.serializers import UserProfileSerializer

class FeedVoteSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(required=False)
    vote = serializers.ChoiceField(choices=models.FeedVote.VoteType)
    
    class Meta:
        model = models.FeedVote
        fields = ['user', 'vote']
        
    def create(self, validated_data):
        user = self.context['user']
        feed = self.context['feed']
        
        feedVote = models.FeedVote.objects.create(
            user = user,
            feed = feed,
            vote = validated_data['vote']
        )
        return feedVote

class ReportSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(required=False)
    
    class Meta:
        model = models.Report
        fields = ['user', 'reportDate']
        
    def create(self, validated_data):
        user = self.context['user']
        feed = self.context['feed']
        
        report = models.Report.objects.create(
            user = user,
            feed = feed
        )
        return report

class CommentReportSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(required=False)
    
    class Meta:
        model = models.CommentReport
        fields = ['user', 'reportDate']
        
    def create(self, validated_data):
        user = self.context['user']
        comment = self.context['comment']
        
        report = models.CommentReport.objects.create(
            user = user,
            comment = comment
        )
        return report

class CommentLikeSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(required=False)
    
    class Meta:
        model = models.CommentLike
        fields = ['user']
        
    def create(self, validated_data):
        user = self.context['user']
        comment = self.context['comment']
        
        commentLike = models.CommentLike.objects.create(
            user = user,
            comment = comment
        )
        return commentLike

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
    user_vote = serializers.SerializerMethodField()
    
    class Meta:
        model = models.Feed
        fields = ['id','author','message','type','postedDate','updatedDate',
                  'latitude', 'longitude', 'locationName', 'images', 'votes',
                  'upvote_count', 'downvote_count', 'user_vote', 'isSpam']
    
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
        
        if images is not None:
            for image in images:
                models.Image.objects.create(feed=feed, image=image)
            
        return feed
    
    def get_upvote_count(self, obj):
        return models.FeedVote.objects.filter(feed=obj, vote=1).count()
    
    def get_downvote_count(self, obj):
        return models.FeedVote.objects.filter(feed=obj, vote=-1).count()
    
    def get_user_vote(self, obj):
        user_vote = models.FeedVote.objects.filter(feed=obj, user=self.context['user'])
        vote_type = None
        if user_vote.exists():
            vote_type = user_vote[0].vote
        return {
                'is_voted': user_vote.exists(),
                'vote_type': vote_type
                }
    
class CommentSerializer(serializers.ModelSerializer):
    #likes = VoteObjectRelatedField(many=True, queryset=models.Vote.objects.all(), required=False)
    author = UserProfileSerializer(required=False)
    likes = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = models.Comment
        fields = ['id','author','message','postedDate','updatedDate', 'isSpam', 'likes', 'is_liked']
        
    def create(self, validated_data):
        user = self.context['user']
        feed = self.context['feed']
        
        comment = models.Comment.objects.create(
            author=user,
            message=validated_data['message'],
            feed=feed
        )
            
        return comment
    
    def get_likes(self, obj):
        return models.CommentLike.objects.filter(comment=obj, user=obj.author).count()
    
    def get_is_liked(self, obj):
        user_like = models.CommentLike.objects.filter(comment=obj, user=self.context['user'])
        return user_like.exists()