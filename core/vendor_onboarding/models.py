from django.db import models
import uuid
# Create your models here.

class PendingVendor(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    biz_name    = models.CharField(max_length=255)
    email       = models.EmailField(unique=True)
    phone       = models.CharField(max_length=20)
    address     = models.CharField(max_length=255, blank=True)
    post_code   = models.CharField(max_length=20, blank=True)
    otp_code    = models.CharField(max_length=6, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.biz_name} ({self.email})"

