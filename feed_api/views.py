from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets, filters, status
from rest_framework.authentication import TokenAuthentication

from feed_api import models, serializers

@api_view(['GET'])
def getFeed(request, parameter):
    try:
        feed = models.Feed.objects.get(id=parameter)
    except:
        return Response({'status':status.HTTP_404_NOT_FOUND})
    
    serializer = serializers.FeedSerializer(feed)
    return Response(serializer.data)


@api_view(['POST'])
def postFeed(request):
    serializer = serializers.FeedSerializer(data=request.data, 
                                            context={
                                                'images': request.data.getlist('images'),
                                                'user': request.user
                                                })
    data = {}
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def getComments(request, parameter):
    try:
        feed = models.Feed.objects.get(id=parameter)
    except:
        return Response({'status':status.HTTP_404_NOT_FOUND})
    
    serializer = serializers.FeedSerializer(feed)
    return Response(serializer.data)


class FeedViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.FeedSerializer
    queryset = models.Feed.objects.all()
    authentication_classes = (TokenAuthentication,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('author', 'message')