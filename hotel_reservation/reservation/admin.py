from django.contrib import admin
from .models import User, Hotel, Review, Room, Booking, Payment

# Register your models here.

admin.site.register(User)
admin.site.register(Hotel)
admin.site.register(Review)
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(Payment)

