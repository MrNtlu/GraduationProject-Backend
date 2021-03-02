from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets, filters
from auth_api import serializers, models, permissions
from collections import OrderedDict
from graduation_project.base_response import handleResponseMessage

@api_view(['GET'])
def getUserInfo(request, parameter):
    if request.user.is_authenticated:
        try:
            userProfile = models.UserProfile.objects.get(id=parameter) 
        except:
            return handleResponseMessage(status.HTTP_404_NOT_FOUND,'User not found.')
    
        serializer = serializers.UserProfileSerializer(userProfile)
        return handleResponseMessage(status.HTTP_200_OK,
                              'Successfully received User info.',
                              serializer.data)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')

class LoginUser(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

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
        return handleResponseMessage(status.HTTP_400_BAD_REQUEST,'Invalid parameters.')

    if serializer.is_valid():
        user = serializer.save()
        data['email'] = user.email
        token = Token.objects.get(user=user).key
        data['token'] = token
        return handleResponseMessage(status.HTTP_200_OK,
                              f'{user.name} successfully registered.',
                              data)
    else:
        data = serializer.errors
        return handleResponseMessage(status.HTTP_400_BAD_REQUEST,
                                "Couldn't registered.",
                                data)


@api_view(['POST'])
def followUser(request, parameter):
    if request.user.is_authenticated:
        try:
            #User that will be (followed/unfollowed)'s profile
            userProfile = models.UserProfile.objects.get(id=parameter) 
        except:
            return handleResponseMessage(status.HTTP_404_NOT_FOUND,'User not found.')
        
        # Loggedin Users serializer     
        serializer = serializers.UserProfileSerializer(userProfile)
        
        if int(request.user.id) == int(parameter):
            return handleResponseMessage(status.HTTP_400_BAD_REQUEST,
                                         'You cannot follow yourself.')
        else:
            filteredList = list(filter(lambda item: request.user.id == item['followerUser'], serializer.data.get('followings')))

            if len(filteredList) > 0:
                try:
                    instance = models.UserFollowing.objects.get(pk=filteredList[0].get('id'))
                    instance.delete()
                except ObjectDoesNotExist:
                    return handleResponseMessage(status.HTTP_404_NOT_FOUND,
                                                "You cannot unfollow a person who you don't follow.")
                except:
                    return handleResponseMessage(status.HTTP_404_NOT_FOUND,
                                                 "Error occured while deleting the object.")

                return handleResponseMessage(status.HTTP_200_OK,
                                            f'Successfully unfollowed',
                                            f'{request.user.name} unfollowed {userProfile.name}')
            else:
                following = models.UserFollowing.objects.create(user=userProfile, followerUser=request.user)
                return handleResponseMessage(status.HTTP_200_OK,
                                                'Successfully Followed',
                                                f'{request.user.name} follows {userProfile.name}')

    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')

### MISSING APIs ###
# UPLOAD IMAGE
# UPDATE PROFILE
# 

# @api_view(['PUT'])
# def updateUserInfo(request, parameter, test):
#     try:
#         userProfile = models.UserProfile.objects.get(id=parameter) 
#     except:
#         return Response({'status':status.HTTP_404_NOT_FOUND})
    
#     serializer = serializers.UserProfileSerializer(userProfile, data=request.data)
#     data = {}
#     print({
#         'parameter': parameter,
#         'test': test,
#         'request': request.data,
#         'auth_user': request.user,
#         'is_authenticated': request.user.is_authenticated 
#     })
#     if serializer.is_valid():
#         serializer.save()
#         data['success'] = "Updated successfully."
#         return Response(data=data)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.UpdateOwnProfile,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'email',)
    

class UserFollowingViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = serializers.FollowingSerializer
    queryset = models.UserFollowing.objects.all()