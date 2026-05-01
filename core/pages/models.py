from django.db import models

# Create your models here.

class LandingPage(models.Model):
    title = models.CharField(max_length=200, default="Order delivery near you")
    hero_image = models.ImageField(upload_to='landing_pages/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Landing Page Image - {self.id}"

# pages/models.py

class DashboardSettings(models.Model):
    name = models.CharField(max_length=100, default="Dashboard Configuration")
    background_image = models.ImageField(upload_to='backgrounds/', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Dashboard Setting"
        verbose_name_plural = "Dashboard Settings"
