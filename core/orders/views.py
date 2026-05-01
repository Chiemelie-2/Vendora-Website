from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import OrderItem, Order
from cart.cart import Cart
from .models import Order

# Create your views here.
@login_required
def order_list(request):
    orders = request.user.orders.all()
    return render(request, 'orders/order_list.html', {'orders': orders})

#  Create the Order Creation View

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        # 1. Create the main Order
        order = Order.objects.create(
            user=request.user,
            address=request.POST.get('address'),
            total_paid=cart.get_total_price(),
            is_paid=True # Setting to True for now since we haven't added Stripe yet
        )
        
        # 2. Move items from Cart (Session) to OrderItem (Database)
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['item'],
                price=item['price'],
                quantity=item['quantity']
            )
            
        # 3. Clear the session cart
        cart.clear()
        
        # 4. Redirect to the History page we built earlier
        return redirect('orders:order_list')
    
    return render(request, 'orders/create.html', {'cart': cart})
