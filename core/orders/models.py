from django.db import models
from django.contrib.auth.models import User
from restaurants.models import MenuItem

# Create your models here.
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created = models.DateTimeField(auto_now_add=True)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=250)
    is_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Order {self.id}'

# We create a separate OrderItem model to track each product in an order, along with its status for the vendor
class OrderItem(models.Model):
    # Add a status specifically for vendor tracking
    STATUS_CHOICES = (
        ('received', 'Order Received'),
        ('preparing', 'Preparing'),
        ('on_way', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    # NEW STATUS FIELD
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')

    def __str__(self):
        return f"Item {self.id} for Order {self.order.id}"

