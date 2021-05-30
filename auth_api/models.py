from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

def upload_location(instance, filename, **kwargs):
	file_path = 'profile/{user_id}-{filename}.jpg'.format(
			user_id=str(instance.id),
            filename=str(filename)
		) 
	return file_path

class UserProfileManager(BaseUserManager):
    
    def create_user(self, email, username, name, password=None):
        if not email:
            raise ValueError("Email shouldn't be empty.")
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, name=name)
        
        user.set_password(password)
        user.save(using=self._db)
        
        return user

    def create_superuser(self, email, username, name, password):
        user = self.create_user(email, username, name, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    class UserType(models.IntegerChoices):
        User = 1
        Commercial = 2
        
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    isActive = models.BooleanField(default=True)
    image = models.ImageField(upload_to=upload_location)
    userType = models.IntegerField(choices=UserType.choices, default=UserType.User)
    is_staff = models.BooleanField(default=False)

    objects = UserProfileManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','name']
    
    def get_full_name(self):
        return self.name
    
    def get_short_name(self):
        return self.name
    
    def __str__(self):
        return str(self.id) + ' ' + self.email + ' ' + self.name
        
        
#Login
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def createAuthToken(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
      
        
class UserFollowing(models.Model):
    # Followings = Takip Edilen
    user = models.ForeignKey(UserProfile, related_name='followings', on_delete=models.CASCADE)
    followerUser = models.ForeignKey(UserProfile, related_name='followers', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'followerUser'], name='uniqueConstraint')
        ]
        ordering = ["-created"]
        
    def __str__(self):
        return f'{self.followerUser} follows {self.user}'
    
