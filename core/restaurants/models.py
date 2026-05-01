from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    def __str__(self):
        return self.name

# restaurants/models.py
class Restaurant(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('verified', 'Verified (Public)'),
        ('rejected', 'Rejected'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_restaurants')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    logo = models.ImageField(upload_to='restaurant_logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='restaurant_covers/', blank=True, null=True)

    address = models.CharField(max_length=300, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)        # ← new
    landmark = models.CharField(max_length=200, blank=True, null=True)    # ← new
    post_code = models.CharField(max_length=20, blank=True, null=True)
    business_email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)                     # ← new
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)

    def __str__(self):
        return f"{self.name} - [{self.get_status_display()}]"
    

class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('Main', 'Main'),
        ('Side', 'Side'),
        ('Drink', 'Drink'),
    ]
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    category_group = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/')
    item_type = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Main')
    
    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

# Alias to solve your ImportError in vendor_dashboard/views.py
Product = MenuItem
