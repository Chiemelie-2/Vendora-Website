# from django.urls import path
# from . import views

# # This 'app_name' helps Django distinguish 'home' here from 'home' in other apps
# app_name = 'restaurants'

# urlpatterns = [
#     # Homepage: display all restaurants
#     path('home/', views.home, name='home'),
    
#     # Search: AJAX endpoint to filter restaurants
#     path('search/', views.search_restaurants, name='search'),
    
#     # Detail: Individual restaurant menu page (using the ID/PK)
#     path('<int:pk>/', views.restaurant_detail, name='detail'),
    
#     # Vendor Dashboard: Add Product (only for logged-in vendors)   
#      path('dashboard/add-product/', views.add_product, name='add_product'),
    
#     #vendor registering their restaurant 
#     path('register-business/', views.register_restaurant, name='register_restaurant'),

#     #adding the order status update endpoint for vendors to update the status of each item in an order
#     path('order-item/<int:item_id>/update/<str:new_status>/', views.update_order_status, name='update_status'),

#    # path('dashboard/', views.owner_dashboard, name='dashboard'),
    
#     # verify phone endpoint for restaurant registration
#     path('verify-phone/', views.verify_phone, name='verify_phone'),

#     path('resend-otp/', views.resend_otp, name='resend_otp'),
# ]

from django.urls import path
from . import views

app_name = 'restaurants'

urlpatterns = [
    # Homepage: display all restaurants
    path('home/', views.home, name='home'),
    
    # Search: AJAX endpoint to filter restaurants
    path('search/', views.search_restaurants, name='search'),
    
    # Detail: Individual restaurant menu page (using the ID/PK)
    path('<int:pk>/', views.restaurant_detail, name='detail'),
    
    # vendor registering their restaurant 
    #path('register-business/', views.register_restaurant, name='register_restaurant'),
]
