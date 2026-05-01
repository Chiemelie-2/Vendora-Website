# from django.urls import path
# from . import views

# app_name = 'vendor_onboarding'

# urlpatterns = [
#     path('register/',                          views.vendor_register,   name='vendor_register'),
#     #path('verify-email/<uuid:vendor_id>/',     views.verify_email,      name='verify_email'),
#     #path('create-password/<uuid:vendor_id>/',  views.create_password,   name='create_password'),
#     path('register-business/', views.register_vendor_business, name='register_business'),
#     path('branding/', views.store_branding, name='store_branding'),
#     path('menu/', views.menu, name='menu'),
#     path('save-menu/', views.save_menu, name='save_menu'),
#     path('review/', views.review, name='review'),
# ]


from django.urls import path
from . import views

app_name = 'vendor_onboarding'

urlpatterns = [
    # Direct partner registration flow
    path('register/', views.vendor_register, name='vendor_register'),
    # path('verify-email/<uuid:vendor_id>/', views.verify_email, name='verify_email'),
    # path('create-password/<uuid:vendor_id>/', views.create_password, name='create_password'),

    # Shared onboarding steps (both flows)
    path('register-business/', views.register_vendor_business, name='register_business'),
    path('location/', views.location, name='location'),
    path('edit-location/', views.edit_location, name='edit_location'),
    path('branding/', views.store_branding, name='store_branding'),
    path('menu/', views.menu, name='menu'),
    path('save-menu/', views.save_menu, name='save_menu'),
    path('review/', views.review, name='review'),
]