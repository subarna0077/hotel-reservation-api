from django.shortcuts import render
from .serializers import UserCreateSerializer, HotelSerializers, RoomSerializer, ReviewSerializer, PaymentSerializer, BookingSerializer
from rest_framework.generics import CreateAPIView
from .models import User, Hotel, Room, Review, Payment, Booking
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
# from rest_framework.decorators import api_view, authentication_classes, permission_classes
# from django.http.response import Response 

class IsGuestOrManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):  
        if request.method in SAFE_METHODS:
            return True
        
        if request.user.is_superuser:
            return True
        
        if request.user.role == 'MANAGER' & obj.owner == request.user:
            return True
        
        return False

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsReviewOwnerOrManagerOrAdminOrReadOnly(BasePermission):
    """
    Allow read-only access to everyone.
    Allow write access if:
    - User is the review owner
    - User is a manager
    - User is staff/admin
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        return user == obj.user or user.role == 'MANAGER' or user.is_staff


# Create your views here.
class UserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication]

# @api_view(['POST'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsGuestOrManagerOrAdmin])
# def hotel_create(request):
#     serializer = HotelSerializers(request.data)

#     if serializer.is_valid():
#         hotel = serializer.save(author = request.user)
#         return Response(HotelSerializers(hotel).data, status = status.HTTP_201_CREATED)

class HotelView(viewsets.ModelViewSet):
    ##anyone can view the hotel, only hotel manager can crud their own hotels, admin can do all
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializers
    permission_classes = [IsGuestOrManagerOrAdmin]
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        serializer.save(owner = self.request.user)

class RoomView(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsGuestOrManagerOrAdmin]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        hotel_id = self.kwargs.get('hotel_id')
        if hotel_id:
            return Room.objects.filter(hotel_pk = hotel_id)
        return super().get_queryset()
        

##anyone can see the reviews, only the customer can give the reviews, and manage their own reviews, hotel owner can reply the review and the admin can manage all reviews 
class ReviewView(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewOwnerOrManagerOrAdminOrReadOnly]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return super().get_queryset()

class BookingView(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        serializer.save(customer = self.request.user)

    
class PaymentView(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        booking_id = self.kwargs.get('booking_pk')
        booking = Booking.objects.get(id=booking_id)
        serializer.save(booking = booking)


@api_view(['POST'])
def callback_esewa(request):
    pid = request.data.get('pid')
    refId = request.data.get('refId')
    amt = request.data.get('amt')
    status_from_gateway = request.data.get('status')

    try:
        payment = Payment.objects.get(id=pid)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND) 
    
    payment.transaction_id = refId
    if status_from_gateway == "success":
        payment.status = "COMPLETED"
    else:
        payment.status = "FAILED"
    payment.save()

    return Response({"message": "Payment updated"}, status=status.HTTP_200_OK)