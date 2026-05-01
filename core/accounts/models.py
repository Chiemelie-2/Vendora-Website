from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
import uuid
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    # Roles from your PDF
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin'),
    )
    role = models.CharField(
    max_length=10, 
    choices=ROLE_CHOICES, 
    blank=True, 
    null=True, 
    default=None
)
    # OTP Logic Fields
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def generate_otp(self):
        self.otp_code = str(random.randint(100000, 999999))
        self.save()
        return self.otp_code

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
        


class PendingVendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    biz_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    is_verified = models.BooleanField(default=False)
    token = models.UUIDField(default=uuid.uuid4, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
