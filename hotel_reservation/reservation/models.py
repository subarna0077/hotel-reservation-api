from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
        ('CUSTOMER', 'Customer'),   
    )
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True)
    role = models.CharField(max_length=20, choices = ROLE_CHOICES, default='CUSTOMER')

    def __str__(self):
        return f"{self.username} ({self.role})"

class Hotel(models.Model):
    name = models.CharField()
    description = models.TextField()
    location = models.CharField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotels')

    def __str__(self):
        return f"{self.name}"
    
class Room(models.Model):
    ROOM_CHOICES = (
        ('SINGLE', 'Single'),
        ('DOUBLE', 'Double'),
        ('SUITE', 'Suite'),
        ('DELUXE', 'Deluxe'),
    )
    hotel = models.ForeignKey(Hotel, related_name='rooms', on_delete=models.CASCADE)
    room_number = models.PositiveIntegerField()
    room_type = models.CharField(max_length=12, choices=ROOM_CHOICES, default='SINGLE')
    price_per_stay = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)


class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(User, on_delete= models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

class Payment(models.Model):
    PAYMENT_CHOICES = (
        ('CARD', 'Card'),
        ('ESEWA', 'Esewa'),
        ('KHALTI', 'Khalti'),
        ('CASH', 'Cash'),
    )
    booking = models.OneToOneField(Booking)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    payment_choices = models.CharField(choices = PAYMENT_CHOICES, default='CASH')


class Review(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel-reviews')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room-reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



## Analytics and tracking, to be added in future
