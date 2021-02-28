from django.urls import path, include
from feed_api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('feedlist', views.FeedViewSet, basename='feeds')

urlpatterns = [
    path('feed/<parameter>/',views.getFeed, name='feed'),
    path('feed/<parameter>/comments',views.getComments, name='comments'),
    path('feed/<parameter>/create',views.postComment, name='commentcreate'),
    path('create/feed', views.postFeed, name='create'),
    path('', include(router.urls)),
]