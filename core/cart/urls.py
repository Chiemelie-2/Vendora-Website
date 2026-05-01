from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('add/<int:item_id>/', views.cart_add, name='cart_add'),
    path('decrement/<int:item_id>/', views.cart_decrement, name='cart_decrement'), # New
    path('remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('clear/', views.cart_clear, name='cart_clear'), # New
    path('detail/', views.cart_detail, name='cart_detail'),
]

