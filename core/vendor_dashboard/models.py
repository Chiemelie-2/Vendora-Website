from django.db import models

# Create your models here.
class DashboardSettings(models.Model):
    name = models.CharField(max_length=255, default="Global Settings")
    background_image = models.ImageField(upload_to='dashboard_backgrounds/', blank=True, null=True)

    def __str__(self):
        return self.name