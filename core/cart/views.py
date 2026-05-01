from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect, get_object_or_404
from restaurants.models import MenuItem
from .cart import Cart

def cart_add(request, item_id):
    cart = Cart(request)
    item = get_object_or_404(MenuItem, id=item_id)
    cart.add(item=item)
    return redirect('restaurants:detail', pk=item.restaurant.id)

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})


# cart/views.py
def cart_remove(request, item_id):
    cart = Cart(request)
    item = get_object_or_404(MenuItem, id=item_id)
    cart.remove(item)
    return redirect('cart:cart_detail')


# cart/views.py

def cart_decrement(request, item_id):
    cart = Cart(request)
    item = get_object_or_404(MenuItem, id=item_id)
    cart.decrement(item=item)
    return redirect('cart:cart_detail')

def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect('cart:cart_detail')
