from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token

from rest_framework import status, viewsets, filters
from auth_api import serializers, models, permissions

@api_view(['GET'])
def getUserInfo(request, parameter):
    try:
        userProfile = models.UserProfile.objects.get(id=parameter) 
    except:
        return Response({'status':status.HTTP_404_NOT_FOUND})
    
    if request.user.is_authenticated:
        serializer = serializers.UserProfileSerializer(userProfile)
        return Response(serializer.data)
    else:
        return Response({'status':status.HTTP_401_UNAUTHORIZED})



@api_view(['PUT'])
def updateUserInfo(request, parameter, test):
    try:
        userProfile = models.UserProfile.objects.get(id=parameter) 
    except:
        return Response({'status':status.HTTP_404_NOT_FOUND})
    
    serializer = serializers.UserProfileSerializer(userProfile, data=request.data)
    data = {}
    print({
        'parameter': parameter,
        'test': test,
        'request': request.data,
        'auth_user': request.user,
        'is_authenticated': request.user.is_authenticated 
    })
    if serializer.is_valid():
        serializer.save()
        data['success'] = "Updated successfully."
        return Response(data=data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def registerUser(request):
    data = {}
    params = request.query_params
    try:
        username = params['username']
        email = params['email']
        name = params['name']
        password = params['password']
        serializer = serializers.UserProfileSerializer(data={
            'username': username,
            'email': email,
            'name': name,
            'password': password
        })
    except:
        return Response({'status':status.HTTP_400_BAD_REQUEST})

    if serializer.is_valid():
        user = serializer.save()
        data['response'] = f'{user.name} successfully registered.'
        data['email'] = user.email
        token = Token.objects.get(user=user).key
        data['token'] = token
    else:
        data = serializer.errors
    return Response(data=data)

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.UpdateOwnProfile,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'email',)
    
class LoginUser(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES