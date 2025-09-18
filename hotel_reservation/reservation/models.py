from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

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

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # change default 'user_set' to avoid clash
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='custom_user',
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

class Hotel(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    location = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotels')
    amenities = models.TextField(help_text= "Comma-separated list of amenities")

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
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=12, choices=ROOM_CHOICES, default='SINGLE')
    capacity = models.PositiveIntegerField(default=1)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    amenities = models.CharField(max_length=100, blank=True, help_text='room-specific amenities')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hotel.name} - Room {self.room_number} ({self.room_type})"
    
    class Meta:
        unique_together = ['hotel', 'room_number']
        ordering = ['hotel', 'room_number']

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    )
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(User, on_delete= models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    checked_in_date = models.DateField()
    checked_out_date = models.DateField()
    nights = models.PositiveIntegerField(editable=False)


    def save(self, *args, **kwargs):
        if self.checked_in_date and self.checked_out_date:
            self.nights = (self.checked_out_date - self.checked_in_date).days
            self.total_amount = self.nights * self.room.price_per_night
        return super().save(*args, **kwargs)


class Payment(models.Model):
    PAYMENT_CHOICES = (
        ('CARD', 'Card'),
        ('ESEWA', 'Esewa'),
        ('KHALTI', 'Khalti'),
        ('CASH', 'Cash'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    payment_choices = models.CharField(max_length=10,choices = PAYMENT_CHOICES, default='CASH')
    status = models.CharField(max_length=12, default='PENDING', choices=STATUS_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.amount = self.booking.total_amount
        return super().save(*args, **kwargs)



class Review(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_reviews')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_reviews', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        ordering =['-created_at'] 



## Analytics and tracking, to be added in future
