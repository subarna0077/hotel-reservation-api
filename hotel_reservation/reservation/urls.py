from django.urls import path, include
from .views import UserCreateView, HotelView, RoomView, ReviewView
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
router = DefaultRouter()
router.register('hotels', HotelView, basename='hotel')
hotels_router = NestedDefaultRouter(router, 'hotels', lookup='hotel')
hotels_router.register('rooms',RoomView, basename='hotel-rooms')
hotels_router.register('reviews', ReviewView, basename='hotel-reviews')

urlpatterns = [
    path('create-user/', UserCreateView.as_view(), name='create-user'),
    path('', include(router.urls)),
    path('', include(hotels_router.urls))
]


