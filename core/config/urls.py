"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),   # Login/Signup App
    path('accounts/', include('allauth.urls')),
    path('', include('pages.urls')),         # Landing Page
    path('restaurants/', include('restaurants.urls')), # Restaurant App

    path('vendor/', include('vendor_onboarding.urls')),   # Vendor Onboarding App
    path('vendor/dashboard/', include('vendor_dashboard.urls')),   # Vendor Dashboard App
    path('cart/', include('cart.urls')),  # Add to Cart App
    path('orders/', include('orders.urls')),  # Orders App
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)