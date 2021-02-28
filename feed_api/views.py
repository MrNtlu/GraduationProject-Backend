from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets, filters, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from feed_api import models, serializers
from rest_framework.utils import json

### FEED API

@api_view(['GET'])
#@permission_classes([IsAuthenticated])
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
        #return Response(serializer.data)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')

@api_view(['POST'])
#@permission_classes([IsAuthenticated])
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
            #return Response(serializer.data, status=status.HTTP_201_CREATED)
        return handleResponseMessage(status.HTTP_400_BAD_REQUEST, 'Invalid post.')
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')
    
### COMMENT API

@api_view(['GET'])
#@permission_classes([IsAuthenticated])
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
        #return Response(serializer.data)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')

@api_view(['POST'])
#@permission_classes([IsAuthenticated])
def postComment(request, parameter):
    if request.user.is_authenticated:
        try:
            feed = models.Feed.objects.get(id=parameter)
        except:
            return handleResponseMessage(status.HTTP_404_NOT_FOUND,
                                         "Couldn't find the corresponding Feed.")
            #return Response({'status':status.HTTP_404_NOT_FOUND})
        
        serializer = serializers.CommentSerializer(data=request.data, 
                                                context={
                                                    'user': request.user,
                                                    'feed': feed
                                                    })
        data = {}
        if serializer.is_valid():
            serializer.save()
            handleResponseMessage(status.HTTP_201_CREATED,
                                  'Successfully posted commet.',
                                  serializer.data)
            #return Response(serializer.data, status=status.HTTP_201_CREATED)
        return handleResponseMessage(status.HTTP_400_BAD_REQUEST, 'Invalid comment.')
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')

def handleResponseMessage(status, message, data=None):
    response = {}

    response['status'] = status
    response['message'] = message
    response['data'] = data
        
    return Response(response)

class FeedViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.FeedSerializer
    queryset = models.Feed.objects.all()
    authentication_classes = (TokenAuthentication,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('author', 'message')