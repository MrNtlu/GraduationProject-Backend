from django.urls import path, include
from auth_api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('user', views.UserProfileViewSet, basename='user') #Because we have queryset on view

urlpatterns = [
    path('login',views.LoginUser.as_view()),
    path('register',views.registerUser, name='register'),
    path('user/<parameter>', views.getUserInfo, name='user_info'),
    path('user/<parameter>/followers', views.getUserFollowers, name='user_followers'),
    path('user/<parameter>/followings', views.getUserFollowings, name='user_followings'),
    path('user/<parameter>/follow', views.followUser, name='follow'),
    path('user/<parameter>/edit', views.updateUserInfo, name='user_edit'),
    path('change_password/<int:pk>', views.ChangePasswordView.as_view(), name='change_password'),
    path('', include(router.urls)),
]
