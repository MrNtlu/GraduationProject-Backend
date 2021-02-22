from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserProfileManager(BaseUserManager):
    
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError("Email shouldn't be empty.")
        
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        
        user.set_password(password)
        user.save(using=self._db)
        
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password)
        user.is_superuser = True
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
    image = models.ImageField(upload_to='profile')
    userType = models.IntegerField(choices=UserType.choices, default=UserType.User)

    objects = UserProfileManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    def get_full_name(self):
        return self.name
    
    def get_short_name(self):
        return self.name
    
    def __str__(self):
        return self.email
        