from django.core import paginator
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken, AuthTokenSerializer
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework import generics
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets, filters
from auth_api import serializers, models, permissions
from graduation_project.base_response import handleResponseMessage
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from rest_framework.pagination import PageNumberPagination

### TODO
# Forgot password
# Email confirmation
#

FOLLOW_PAGINATION_LIMIT = 15
SEARCH_PAGINATION_LIMIT = 25


@api_view(['GET'])
def getUserInfo(request, parameter):
    if request.user.is_authenticated:
        try:
            userProfile = models.UserProfile.objects.get(id=parameter) 
        except:
            return handleResponseMessage(status.HTTP_404_NOT_FOUND,'User not found.')
    
        serializer = serializers.UserProfileSerializer(userProfile)
        return handleResponseMessage(
            status.HTTP_200_OK,
            'Successfully received User info.',
            serializer.data)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')


class LoginUser(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=serializer.validated_data['user'])
            return handleResponseMessage(status.HTTP_200_OK,
                                         'Successfully logged in.',
                                         {
                                             "token": token.key,
                                             "id": user.pk
                                         })
        else:
            error_message = ""
            try:
                error_message = serializer.errors["non_field_errors"][0]
            except:
                error_message = "Unable to login. Please check credentials."
            return handleResponseMessage(status.HTTP_400_BAD_REQUEST,error_message)


@api_view(['POST'])
def registerUser(request):
    data = {}
    params = request.data
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
        isEmailInvalid = serializer.errors.get('email')
        isUsernameInvalid = serializer.errors.get('username')
        error_message = "Error occured, please try again."
        if isEmailInvalid and isUsernameInvalid:
            error_message = "Username and Email already exists."
        elif isEmailInvalid:
            error_message = "Email already exists."
        elif isUsernameInvalid:
            error_message = "Username already exists."
            
        return handleResponseMessage(status.HTTP_400_BAD_REQUEST, error_message)


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


@api_view(['GET'])
def getUserFollowers(request, parameter):
    if request.user.is_authenticated:
        try:
            user = models.UserProfile.objects.get(id=parameter) 
        except:
            return handleResponseMessage(status.HTTP_404_NOT_FOUND,'User not found.')

        followers = models.UserFollowing.objects.filter(user=user)
        page = request.GET.get('page')
        paginator = Paginator(followers, FOLLOW_PAGINATION_LIMIT)
        
        try:
            followerPagination = paginator.page(page)
        except PageNotAnInteger:
            followerPagination = paginator.page(1)
        except EmptyPage:
            return handleResponseMessage(status.HTTP_200_OK, "No item left.")
        
        serializer = serializers.FollowerSerializer(followerPagination, many=True)

        return handleResponseMessage(
            status.HTTP_200_OK,
            'Successfully received follower info.',
            serializer.data)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')


@api_view(['GET'])
def getUserFollowings(request, parameter):
    if request.user.is_authenticated:
        try:
            user = models.UserProfile.objects.get(id=parameter) 
        except:
            return handleResponseMessage(status.HTTP_404_NOT_FOUND,'User not found.')
    
        followings = models.UserFollowing.objects.filter(followerUser=user)
        page = request.GET.get('page')
        paginator = Paginator(followings, FOLLOW_PAGINATION_LIMIT)
        
        try:
            followingsPagination = paginator.page(page)
        except PageNotAnInteger:
            followingsPagination = paginator.page(1)
        except EmptyPage:
            return handleResponseMessage(status.HTTP_200_OK, "No item left.")
        
        serializer = serializers.FollowerSerializer(followingsPagination, many=True)
        
        return handleResponseMessage(
            status.HTTP_200_OK,
            'Successfully received User info.',
            serializer.data)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')


@api_view(['PUT'])
def updateUserImage(request, parameter):
    if request.user.is_authenticated:
        try:
            userProfile = models.UserProfile.objects.get(id=parameter) 
        except:
            return handleResponseMessage(status.HTTP_404_NOT_FOUND,'User not found.')
        
        serializer = serializers.UserProfileImageSerializer(
            userProfile, 
            data=request.data,
            context=request.user)
        
        if serializer.is_valid():
            serializer.save()
            return handleResponseMessage(status.HTTP_200_OK, "Image uploaded successfully.")
        return handleResponseMessage(status.HTTP_400_BAD_REQUEST, serializer.errors)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')


@api_view(['PUT'])
def updateUserInfo(request, parameter):
    if request.user.is_authenticated:
        try:
            userProfile = models.UserProfile.objects.get(id=parameter) 
        except:
            return handleResponseMessage(status.HTTP_404_NOT_FOUND,'User not found.')
        
        serializer = serializers.UpdateUserSerializer(
            userProfile, 
            data=request.data,
            context=request.user)
        
        if serializer.is_valid():
            serializer.save()
            return handleResponseMessage(status.HTTP_200_OK, "Updated successfully.")
        else:
            isEmailInvalid = serializer.errors.get('email')
            isUsernameInvalid = serializer.errors.get('username')
            error_message = "Error occured, please try again."
            if isEmailInvalid and isUsernameInvalid:
                error_message = "Username and Email already exists."
            elif isEmailInvalid:
                error_message = "Email already exists."
            elif isUsernameInvalid:
                error_message = "Username already exists."
                
            return handleResponseMessage(status.HTTP_400_BAD_REQUEST, error_message)
    else:
        return handleResponseMessage(status.HTTP_401_UNAUTHORIZED,'Authentication error.')


class PaginationModel(PageNumberPagination):
    page_size = SEARCH_PAGINATION_LIMIT
    page_size_query_param = 'page_size'


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.UpdateOwnProfile,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'name',)
    paginator = PaginationModel()


class ChangePasswordView(generics.UpdateAPIView):
    queryset = models.UserProfile.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.UpdateOwnProfile,)
    serializer_class = serializers.ChangePasswordSerializer