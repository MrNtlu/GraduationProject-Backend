from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from base_api import serializers

class HelloApiView(APIView):
    serializer_class = serializers.HelloSerializer
    
    def get(self, request, format=None):
       apiView = [
           'GET request made.',
           'Request made by using Django', 
           '3rd Text',
           'Mapped manually to URLs'
       ] 
       
       return Response({'message': 'Hello!', 'apiView': apiView})
   
   #Post via formdata
    def post(self, request):
       serializer = self.serializer_class(data=request.data)
       
       if serializer.is_valid():
           name = serializer.validated_data.get('name')
           message = f'Hello {name}'
           return Response({'message':message})
       else:
           return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       
    def put(self, request, pk=None):
        return Response({'method':'PUT'})
    
    def patch(self, request, pk=None):
        return Response({'method':'PATCH'})
    
    def delete(self, request, pk=None):
        return Response({'method':'DELETE'})
    
class HelloViewSet(viewsets.ViewSet):
    serializer_class = serializers.HelloSerializer

    def list(self, request):
        viewset = [
            "List 1",
            "List 2",
            "List 3"
        ]
        
        return Response({'message': 'Hello!', 'viewset':viewset})
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
           name = serializer.validated_data.get('name')
           message = f'Hello {name}'
           return Response({'message':message})
        else:
           return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       
    def retrieve(self, request, pk=None):
        return Response({'http_method':'GET', 'primary key':pk})
    
    def update(self, request, pk=None):
        return Response({'http_method':'PUT'})
    
    def partial_update(self, request, pk=None):
        return Response({'http_method':'PATCH'})
    
    def destroy(self, request, pk=None):
        return Response({'http_method':'DELETE'})
