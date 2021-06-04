from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets, filters, status
from rest_framework.authentication import TokenAuthentication
from feed_api import models, serializers
from auth_api.models import UserFollowing
from django.db.models.expressions import RawSQL
from graduation_project.base_response import handleResponseMessage
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from rest_framework.pagination import PageNumberPagination
import math


FEED_PAGINATION_LIMIT = 15
COMMENT_PAGINATION_LIMIT = 20

### FEED API

@api_view(['GET'])
def getFeed(request, parameter):
    if request.user.is_authenticated:
        try:
            feed = models.Feed.objects.get(id=parameter)
        except:
            return handleResponseMessage(status.HTTP_404_NOT_FOUND,
                                         "Couldn't find the corresponding Feed.")
        
        serializer = serializers.FeedSerializer(feed, context={ 'user': request.user })
        return handleResponseMessage(
            status.HTTP_200_OK,
            'Successfully retrieved feed.',
            serializer.data)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')


@api_view(['GET'])
def getUserFeed(request, parameter):
    if request.user.is_authenticated:
        feeds = models.Feed.objects.filter(author__id=parameter).order_by("-postedDate")
        page = request.GET.get('page')
        paginator = Paginator(feeds, FEED_PAGINATION_LIMIT)
        
        try:
            feedPagination = paginator.page(page)
        except PageNotAnInteger:
            feedPagination = paginator.page(1)
        except EmptyPage:
            return handleResponseMessage(status.HTTP_200_OK, "No item left.")
        
        serializer = serializers.FeedSerializer(feedPagination, many=True, context={ 'user': request.user })
        
        return handleResponseMessage(
            status.HTTP_200_OK,
            'Successfully received data.',
            serializer.data)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')


@api_view(['GET'])
def getFeedByFollowings(request):
    if request.user.is_authenticated:
        user = request.user
        user_followings = UserFollowing.objects.filter(followerUser=user).values('user')
        feeds = models.Feed.objects.filter(author__in = user_followings).order_by("-postedDate")
        page = request.GET.get('page')
        paginator = Paginator(feeds, FEED_PAGINATION_LIMIT)
        
        try:
            feedPagination = paginator.page(page)
        except PageNotAnInteger:
            feedPagination = paginator.page(1)
        except EmptyPage:
            return handleResponseMessage(status.HTTP_200_OK, "No item left.")
        
        serializer = serializers.FeedSerializer(feedPagination, many=True, context={ 'user': request.user })
        
        return handleResponseMessage(
            status.HTTP_200_OK,
            'Successfully retrieved feed.',
            serializer.data)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')

 
@api_view(['GET'])
def getFeedByLocation(request):
    if request.user.is_authenticated:
        queryLat = request.GET.get('lat')
        queryLong = request.GET.get('long')
        distance = request.GET.get('distance')
        
        if (queryLat is None) or (queryLong is None) or (distance is None):
            return handleResponseMessage(status.HTTP_400_BAD_REQUEST,'Missing params.')
        else:
            distanceFormula = "6371 * acos(least(greatest(\
            cos(radians(%s)) * cos(radians(latitude)) \
            * cos(radians(longitude) - radians(%s)) + \
            sin(radians(%s)) * sin(radians(latitude)) \
            , -1), 1))"
            distanceRawSQL = RawSQL(
                distanceFormula,
                (queryLat, queryLong, queryLat)
            )
            nearbyFeeds = models.Feed.objects.all() \
            .annotate(distance=distanceRawSQL)\
            .order_by('distance')
            nearbyFeeds = nearbyFeeds.filter(distance__lt=distance).order_by("-postedDate")
            
            page = request.GET.get('page')
            paginator = Paginator(nearbyFeeds, FEED_PAGINATION_LIMIT)
            
            try:
                feedPagination = paginator.page(page)
            except PageNotAnInteger:
                feedPagination = paginator.page(1)
            except EmptyPage:
                return handleResponseMessage(status.HTTP_200_OK, "No item left.")
            
            serializer = serializers.FeedSerializer(feedPagination, many=True, context={ 'user': request.user })
            
            return handleResponseMessage(
                status.HTTP_200_OK,
                'Successfully received feeds in range of {distance} KM.',
                serializer.data)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')


@api_view(['POST'])
def postFeed(request):
    if request.user.is_authenticated:
        images = []
        try:
            images = request.data.getlist('images')
        except:
            images = request.data.get('images')
            
        serializer = serializers.FeedSerializer(
            data=request.data, 
            context={
                'images': images,
                'user': request.user})
        
        if serializer.is_valid():
            serializer.save()
            return handleResponseMessage(
                status.HTTP_200_OK,
                'Successfully created post.',
                serializer.data)
        return handleResponseMessage(status.HTTP_400_BAD_REQUEST, 'Invalid post.')
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')


@api_view(['POST'])
def postReport(request, parameter):
    if request.user.is_authenticated:
        try:
            feed = models.Feed.objects.get(id=parameter)
        except:
            return handleResponseMessage(
                status.HTTP_404_NOT_FOUND,
                "Couldn't find the corresponding Feed.")
            
        serializer = serializers.ReportSerializer(data=request.data, context={
            'feed': feed,
            'user': request.user
        })
        
        if serializer.is_valid():
            try:
                serializer.save()
                return handleResponseMessage(
                    status.HTTP_200_OK,
                    'Successfully reported.',
                    serializer.data)
            except:
                    return handleResponseMessage(status.HTTP_400_BAD_REQUEST, 'Internal error! Please try again.') 
        return handleResponseMessage(status.HTTP_400_BAD_REQUEST, 'Invalid report.')
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')


@api_view(['POST','PUT', 'DELETE'])
def postFeedVote(request, parameter):
    if request.user.is_authenticated:
        try:
            feed = models.Feed.objects.get(id=parameter)
        except:
            return handleResponseMessage(
                status.HTTP_404_NOT_FOUND,
                "Couldn't find the corresponding Feed.")
        
        if request.method == 'POST':
            serializer = serializers.FeedVoteSerializer(data=request.data, context={
                'feed': feed,
                'user': request.user
                })
            
            if serializer.is_valid():
                try:
                    serializer.save()
                    finalFeedData = serializers.FeedSerializer(feed, context={ 'user': request.user }).data
                    return handleResponseMessage(
                        status.HTTP_200_OK,
                        'Successfully voted.',
                        finalFeedData)
                except:
                    return handleResponseMessage(status.HTTP_400_BAD_REQUEST, 'Internal error! Please try again.') 
            return handleResponseMessage(status.HTTP_400_BAD_REQUEST, 'Invalid vote.')
        
        elif request.method == 'PUT':
            try:
                feedVote = models.FeedVote.objects.get(feed=feed, user=request.user)
            except:
                return handleResponseMessage(status.HTTP_404_NOT_FOUND,"Couldn't find the corresponding vote.")
                
            serializer = serializers.FeedVoteSerializer(feedVote, data=request.data)
            if serializer.is_valid():
                serializer.save()
                finalFeedData = serializers.FeedSerializer(feed, context={ 'user': request.user }).data
                return handleResponseMessage(
                    status.HTTP_200_OK,
                    'Successfully updated.',
                    finalFeedData)
            return handleResponseMessage(status.HTTP_400_BAD_REQUEST, 'Invalid vote.')
        
        elif request.method == 'DELETE':            
            try:
                feedVote = models.FeedVote.objects.get(feed=feed, user=request.user)
            except:
                return handleResponseMessage(status.HTTP_404_NOT_FOUND,"Couldn't find the corresponding vote.")
            
            feedVote.delete()
            finalFeedData = serializers.FeedSerializer(feed, context={ 'user': request.user }).data
            return handleResponseMessage(
                status.HTTP_200_OK,
                'Successfully deleted.',
                finalFeedData)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')

### COMMENT API

@api_view(['GET'])
def getComments(request, parameter):
    if request.user.is_authenticated:
        try:
            feed = models.Feed.objects.get(id=parameter)
        except:
            return handleResponseMessage(status.HTTP_404_NOT_FOUND, "Couldn't find the corresponding Feed.")
        
        sort = request.query_params.get('sort')
        comments = feed.comments.all()
        
        if sort is not None:
            comments = feed.comments.all().order_by(sort)
            
        page = request.GET.get('page')
        paginator = Paginator(comments, FEED_PAGINATION_LIMIT)
        
        try:
            commentPagination = paginator.page(page)
        except PageNotAnInteger:
            commentPagination = paginator.page(1)
        except EmptyPage:
            return handleResponseMessage(status.HTTP_200_OK, "No item left.")

        serializer = serializers.CommentSerializer(commentPagination, many=True, context={ 'user': request.user })
        
        return handleResponseMessage(
            status.HTTP_200_OK,
            'Successfully queried comments.',
            serializer.data)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')


@api_view(['POST'])
def postComment(request, parameter):
    if request.user.is_authenticated:
        try:
            feed = models.Feed.objects.get(id=parameter)
        except:
            return handleResponseMessage(status.HTTP_404_NOT_FOUND, "Couldn't find the corresponding Feed.")
        
        serializer = serializers.CommentSerializer(data=request.data, 
                                                context={
                                                    'user': request.user,
                                                    'feed': feed
                                                    })
        if serializer.is_valid():
            serializer.save()
            return handleResponseMessage(
                status.HTTP_200_OK,
                'Successfully posted comment.',
                serializer.data)
        return handleResponseMessage(status.HTTP_400_BAD_REQUEST, 'Invalid comment.')
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')


@api_view(['POST','DELETE'])
def postLike(request, parameter):
    if request.user.is_authenticated:
        try:
            comment = models.Comment.objects.get(id=parameter)
        except:
            return handleResponseMessage(
                status.HTTP_404_NOT_FOUND,
                "Couldn't find the corresponding comment.")
            
        if request.method == 'POST':
            serializer = serializers.CommentLikeSerializer(data=request.data, context={
                'comment': comment,
                'user': request.user
            })
            
            if serializer.is_valid():
                try:
                    serializer.save()
                    finalCommentData = serializers.CommentSerializer(comment, context={ 'user': request.user }).data
                    return handleResponseMessage(
                        status.HTTP_200_OK,
                        'Successfully liked.',
                        finalCommentData)
                except:
                        return handleResponseMessage(status.HTTP_400_BAD_REQUEST, 'Internal error! Please try again.') 
            return handleResponseMessage(status.HTTP_400_BAD_REQUEST, 'Invalid report.')
        elif request.method == 'DELETE':
            try:
                like = models.CommentLike.objects.get(comment=comment, user=request.user)
            except:
                return handleResponseMessage(status.HTTP_404_NOT_FOUND,"Couldn't find the corresponding like.")
            
            like.delete()
            finalCommentData = serializers.CommentSerializer(comment, context={ 'user': request.user }).data
            return handleResponseMessage(
                status.HTTP_200_OK,
                'Successfully deleted.',
                finalCommentData)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')


@api_view(['POST'])
def postCommentReport(request, parameter):
    if request.user.is_authenticated:
        try:
            comment = models.Comment.objects.get(id=parameter)
        except:
            return handleResponseMessage(
                status.HTTP_404_NOT_FOUND,
                "Couldn't find the corresponding comment.")
            
        serializer = serializers.CommentReportSerializer(data=request.data, context={
            'comment': comment,
            'user': request.user
        })
        
        if serializer.is_valid():
            try:
                serializer.save()
                return handleResponseMessage(
                    status.HTTP_200_OK,
                    'Successfully reported.',
                    serializer.data)
            except:
                    return handleResponseMessage(status.HTTP_400_BAD_REQUEST, "You've already reported this comment.") 
        return handleResponseMessage(status.HTTP_400_BAD_REQUEST, 'Invalid report.')
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')


def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d


class PaginationModel(PageNumberPagination):
    page_size = FEED_PAGINATION_LIMIT
    page_size_query_param = 'page_size'


class FeedViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.FeedSerializer
    queryset = models.Feed.objects.all()
    authentication_classes = (TokenAuthentication,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('author', 'message')
    paginator = PaginationModel()