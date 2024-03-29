from django.urls import path, include
from feed_api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('feedlist', views.FeedViewSet, basename='feeds')

urlpatterns = [
    path('feed/<parameter>/',views.getFeed, name='feed'),
    path('feed/user/<parameter>/',views.getUserFeed, name='userfeed'),
    path('create/feed', views.postFeed, name='create'),
    path('feed/<parameter>/comments',views.getComments, name='comments'),
    path('feed/<parameter>/create',views.postComment, name='commentcreate'),
    path('feed/<parameter>/vote',views.postFeedVote, name='voteFeed'),
    path('feed/<parameter>/report',views.postReport, name='reportFeed'),
    path('feed/<parameter>/delete',views.deleteFeed, name='deleteFeed'),
    path('feed/location',views.getFeedByLocation, name='feedsbylocation'),
    path('feed/follow',views.getFeedByFollowings, name='feedByFollowings'),
    path('comment/<parameter>/delete',views.deleteComment, name='deleteComment'),
    path('comment/<parameter>/like',views.postLike, name='commentLike'),
    path('comment/<parameter>/report',views.postCommentReport, name='commentReport'),
    path('', include(router.urls)),
]