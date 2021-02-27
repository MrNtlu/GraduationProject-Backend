from django.urls import path, include
from feed_api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('feedlist', views.FeedViewSet, basename='feeds')

urlpatterns = [
    path('feeds/<parameter>',views.getFeed, name='feed'),
    path('feed/create', views.postFeed, name='create'),
    path('', include(router.urls)),
]