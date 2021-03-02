from django.urls import path, include
from auth_api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('user', views.UserProfileViewSet, basename='user') #Because we have queryset on view

urlpatterns = [
    path('login',views.LoginUser.as_view()),
    path('register',views.registerUser, name='register'),
    path('user/<parameter>', views.getUserInfo, name='user_info'),
    path('user/<parameter>/follow', views.followUser, name='follow'),
    # path('user/<parameter>/edit/<test>', views.updateUserInfo, name='user_edit'),
    path('', include(router.urls)),
]
