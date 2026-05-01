from django.contrib import admin
from .models import LandingPage
from .models import DashboardSettings
# Register your models here.

admin.site.register(LandingPage)
admin.site.register(DashboardSettings)
