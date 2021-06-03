from rest_framework import serializers
from auth_api import models
from feed_api.models import Feed
from django.contrib.auth.password_validation import validate_password
        
        
class UserProfileSerializer(serializers.ModelSerializer):
    #followings = FollowingSerializer(models.UserFollowing.objects.all(), many=True, required=False)
    #followers = FollowerSerializer(models.UserFollowing.objects.all(), many=True, required=False)
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = models.UserProfile
        fields = ('id','image', 'email', 'username', 'name', 'password', 'follower_count', 'following_count', 'post_count') #'followings','followers',
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
    
    def get_post_count(self, obj):
        return Feed.objects.filter(author=obj).count()
    
    def create(self, validate_data):
        user = models.UserProfile.objects.create_user(
            email=validate_data['email'],
            username=validate_data['username'],
            name=validate_data['name'],
            password=validate_data['password']
        )
        
        return user


class UserProfileImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    
    class Meta:
        model = models.UserProfile
        fields = ('image',)

    def update(self, instance, validated_data):
        if self.context.id != instance.id:
            raise serializers.ValidationError({"authorize": "You dont have permission for this user."})
        
        if instance.image:
            instance.image.delete()
        instance.image = validated_data['image']
        instance.save()
        return instance


class UpdateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)

    class Meta:
        model = models.UserProfile
        fields = ('email','username', 'name')
        extra_kwargs = {
            'name': {
                'required': False
            },
            'username': {
                'required': False
            },
            'email': {
                'required': False
            },
        }

    def validate_email(self, value):
        if models.UserProfile.objects.exclude(id=self.context.id).filter(email=value).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})
        return value

    def validate_username(self, value):
        if models.UserProfile.objects.exclude(id=self.context.id).filter(username=value).exists():
            raise serializers.ValidationError({"username": "This username is already in use."})
        return value

    def update(self, instance, validated_data):   
        if self.context.id != instance.id:
            raise serializers.ValidationError({"authorize": "You dont have permission for this user."})
                
        name, email, username = "","",""
        if validated_data.get('name') is None:
            name = self.context.name
        else:
            name = validated_data.get('name')
        
        if validated_data.get('email') is None:
            email = self.context.email
        else:
            email = validated_data.get('email')
            
        if validated_data.get('username') is None:
            username = self.context.username
        else:
            username = validated_data.get('username')
        
        instance.name = name
        instance.email = email
        instance.username = username

        instance.save()

        return instance 

class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = models.UserProfile
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Password fields didn't match.")

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.id != instance.id:
            raise serializers.ValidationError("You dont have permission for this user.")

        instance.set_password(validated_data['password'])
        instance.save()

        return instance
    
class FollowerSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(source="followerUser")
    class Meta:
        model = models.UserFollowing
        fields = ("id", "user", "created")
        
class FollowingSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    class Meta:
        model = models.UserFollowing
        fields = ("id", "user", "created")