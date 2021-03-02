from rest_framework import serializers
from auth_api import models

class FollowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.UserFollowing
        fields = ("id", "followerUser", "created")
        

class FollowersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserFollowing
        fields = ("id", "user", "created")


class UserProfileSerializer(serializers.ModelSerializer):
    followings = FollowingSerializer(models.UserFollowing.objects.all(), many=True, required=False)
    followers = FollowersSerializer(models.UserFollowing.objects.all(), many=True, required=False)

    class Meta:
        model = models.UserProfile
        fields = ('id', 'email', 'username', 'name', 'password', 'followings','followers')
        extra_kwargs = {
            'password':{
                'write_only': True,
                'style': {'input_type': 'password'}
            }
        }
    
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