from rest_framework import serializers
from auth_api import models
        
class UserProfileSerializer(serializers.ModelSerializer):
    #followings = FollowingSerializer(models.UserFollowing.objects.all(), many=True, required=False)
    #followers = FollowerSerializer(models.UserFollowing.objects.all(), many=True, required=False)
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = models.UserProfile
        fields = ('id','image', 'email', 'username', 'name', 'password', 'follower_count', 'following_count') #'followings','followers',
        extra_kwargs = {
            'image':{
              'required': False  
            },
            'password':{
                'write_only': True,
                'style': {'input_type': 'password'}
            }
        }
        
    def get_following_count(self, obj):
        return models.UserFollowing.objects.filter(followerUser=obj).count()
        
    def get_follower_count(self, obj):
        return models.UserFollowing.objects.filter(user=obj).count()
    
    def create(self, validate_data):
        user = models.UserProfile.objects.create_user(
            email=validate_data['email'],
            username=validate_data['username'],
            name=validate_data['name'],
            password=validate_data['password']
        )
        
        return user
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
    
class FollowerSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    class Meta:
        model = models.UserFollowing
        fields = ("id", "user", "created")
        
class FollowingSerializer(serializers.ModelSerializer):
    followerUser = UserProfileSerializer()
    class Meta:
        model = models.UserFollowing
        fields = ("id", "followerUser", "created")