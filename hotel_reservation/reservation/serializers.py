from .models import User, Hotel, Booking, Room, Payment, Review
from rest_framework import serializers

class UserCreateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name','username','password', 'confirm_password','email','bio']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        
        return value
    
    def validate(self, validated_data):
        if validated_data['password'] != validated_data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        
        return validated_data
    
    def create(self,validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user
    
class HotelSerializers(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    total_rooms = serializers.SerializerMethodField()
    class Meta:
        model = Hotel
        fields = ['name', 'description', 'location','amenities', 'owner_name', 'phone_number', 'email_address', 'total_rooms']

    def get_owner_name(self,obj):
        return obj.owner.first_name
    
    def get_total_rooms(self, obj):
        return obj.rooms.count()
    
##  hotel/1/room (nested inside of the hotel)
class RoomSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Room
        fields = ['room_number', 'room_type', 'capacity', 'is_available', 'price_per_night', 'amenities', 'created_at']
        read_only_fields = ['created_at', 'is_available']


class ReviewSerializer(serializers.ModelSerializer):
 ## Review can be room specific or hotel specific, we need to manage both in our case:
 ##Anyone can see reviews: hotel/1/reviews : or hotel/1/rooms/reviews
    hotel_name = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = ['comment', 'rating', 'created_at', 'hotel_name']
        read_only_fields = ['created_at']


    def get_hotel_name(self, obj):
        return obj.hotel.name
    
class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = ['id','room', 'customer', 'status', 'created_at', 'checked_in_date', 'checked_out_date', 'total_amount']
        read_only_fields = ['id','customer', 'status', 'created_at', 'total_amount']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "booking",
            "amount",
            "payment_choices",
            "status",
            "transaction_id",
            "created_at",
        ]
        read_only_fields = ["id", "booking", "amount", "status", "transaction_id", "created_at"]




    


    

    