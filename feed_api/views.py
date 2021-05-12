from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets, filters, status
from rest_framework.authentication import TokenAuthentication
from feed_api import models, serializers
#from rest_framework.permissions import IsAuthenticated
from django.db.models.expressions import RawSQL

from graduation_project.base_response import handleResponseMessage
import math

### FEED API

@api_view(['GET'])
def getFeed(request, parameter):
    if request.user.is_authenticated:
        try:
            feed = models.Feed.objects.get(id=parameter)
        except:
            return handleResponseMessage(status.HTTP_404_NOT_FOUND,
                                         "Couldn't find the corresponding Feed.")
        
        serializer = serializers.FeedSerializer(feed)
        return handleResponseMessage(status.HTTP_200_OK,
                              'Successfully retrieved feed.',
                              serializer.data)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')


@api_view(['GET'])
def getUserFeed(request, parameter):
    if request.user.is_authenticated:
        feeds = models.Feed.objects.filter(author__id=parameter)
        serializer = serializers.FeedSerializer(feeds, many=True)
        return handleResponseMessage(status.HTTP_200_OK,
                                         f'Successfully received data.',
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
            nearbyFeeds = nearbyFeeds.filter(distance__lt=distance)
            serializer = serializers.FeedSerializer(nearbyFeeds, many=True)
            
            return handleResponseMessage(status.HTTP_200_OK,
                                         f'Successfully received feeds in range of {distance} KM.',
                                         serializer.data)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')


@api_view(['POST'])
def postFeed(request):
    if request.user.is_authenticated:
        serializer = serializers.FeedSerializer(data=request.data, 
                                                context={
                                                    'images': request.data.getlist('images'),
                                                    'user': request.user
                                                    })
        data = {}
        if serializer.is_valid():
            serializer.save()
            return handleResponseMessage(status.HTTP_201_CREATED,
                              'Successfully created post.',
                              serializer.data)
        return handleResponseMessage(status.HTTP_400_BAD_REQUEST, 'Invalid post.')
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')
    
@api_view(['POST','PUT', 'DELETE'])
def postFeedVote(request, parameter):
    if request.user.is_authenticated:
        try:
            feed = models.Feed.objects.get(id=parameter)
        except:
            return handleResponseMessage(status.HTTP_404_NOT_FOUND,
                                         "Couldn't find the corresponding Feed.")
        
        if request.method == 'POST':
            serializer = serializers.FeedVoteSerializer(data=request.data, 
                                                    context={
                                                        'feed': feed,
                                                        'user': request.user
                                                        })
            
            if serializer.is_valid():
                serializer.save()
                return handleResponseMessage(status.HTTP_201_CREATED,
                                'Successfully voted.',
                                serializer.data)
            return handleResponseMessage(status.HTTP_400_BAD_REQUEST, 'Invalid vote.')
        
        elif request.method == 'PUT':
            try:
                feedVote = models.FeedVote.objects.get(feed=feed, user=request.user)
            except:
                return handleResponseMessage(status.HTTP_404_NOT_FOUND,
                                            "Couldn't find the corresponding vote.")
                
            #feedVote.vote = models.FeedVote.VoteType(request.data['vote'])
            serializer = serializers.FeedVoteSerializer(feedVote, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return handleResponseMessage(status.HTTP_200_OK,
                                'Successfully updated.',
                                serializer.data)
            return handleResponseMessage(status.HTTP_400_BAD_REQUEST, 'Invalid vote.')
        
        elif request.method == 'DELETE':            
            try:
                feedVote = models.FeedVote.objects.get(feed=feed, user=request.user)
            except:
                return handleResponseMessage(status.HTTP_404_NOT_FOUND,
                                            "Couldn't find the corresponding vote.")
            feedVote.delete()
            return handleResponseMessage(status.HTTP_200_OK,
                                'Successfully deleted.')
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')
    
### COMMENT API

@api_view(['GET'])
def getComments(request, parameter):
    if request.user.is_authenticated:
        try:
            feed = models.Feed.objects.get(id=parameter)
        except:
            return handleResponseMessage(status.HTTP_404_NOT_FOUND,
                                         "Couldn't find the corresponding Feed.")
        
        comments = feed.comments.all()
        serializer = serializers.CommentSerializer(comments, many=True)
        return handleResponseMessage(status.HTTP_200_OK,
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
            return handleResponseMessage(status.HTTP_404_NOT_FOUND,
                                         "Couldn't find the corresponding Feed.")
        
        serializer = serializers.CommentSerializer(data=request.data, 
                                                context={
                                                    'user': request.user,
                                                    'feed': feed
                                                    })
        if serializer.is_valid():
            serializer.save()
            return handleResponseMessage(status.HTTP_201_CREATED,
                                  'Successfully posted comment.',
                                  serializer.data)
        return handleResponseMessage(status.HTTP_400_BAD_REQUEST, 'Invalid comment.')
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


class FeedViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.FeedSerializer
    queryset = models.Feed.objects.all()
    authentication_classes = (TokenAuthentication,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('author', 'message')