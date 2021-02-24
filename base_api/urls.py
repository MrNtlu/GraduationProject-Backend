from django.urls import path, include
from base_api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('viewset', views.HelloViewSet, basename='viewset')

urlpatterns = [
    path('test/',views.HelloApiView.as_view()),
    path('', include(router.urls))
]
