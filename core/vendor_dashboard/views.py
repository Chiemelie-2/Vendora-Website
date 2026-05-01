from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from restaurants.models import Restaurant, Product
from orders.models import OrderItem
from restaurants.forms import ProductForm # Import from restaurants

from pages.models import DashboardSettings # Import your settings model

def vendor_required(view_func):
    """Decorator: user must be logged in AND have vendor role."""
    @login_required
    def wrapped(request, *args, **kwargs):
        if request.user.profile.role != 'vendor':
            return redirect('restaurants:home')
        restaurant = request.user.my_restaurants.first()
        if not restaurant:
            return redirect('restaurants:register_restaurant')
        return view_func(request, *args, **kwargs)
    return wrapped


@vendor_required
def dashboard(request):
    restaurant = request.user.my_restaurants.first()
    products   = Product.objects.filter(restaurant=restaurant)
    orders     = OrderItem.objects.filter(
        product__restaurant=restaurant
    ).select_related('order', 'product').order_by('-order__created')[:10]

    # --- Analytics ---
    from django.db.models import Sum, Count
    from orders.models import Order

    total_revenue = OrderItem.objects.filter(
        product__restaurant=restaurant,
        status='delivered'
    ).aggregate(total=Sum('price'))['total'] or 0

    total_orders = OrderItem.objects.filter(
        product__restaurant=restaurant
    ).values('order').distinct().count()

    total_products = products.count()
    low_stock = products.filter(stock__lte=5).count() if hasattr(Product, 'stock') else 0

    context = {
        'restaurant':    restaurant,
        'products':      products[:4],        # latest 4 for preview grid
        'orders':        orders,
        'total_revenue': total_revenue,
        'total_orders':  total_orders,
        'total_products': total_products,
        'low_stock':     low_stock,
    }
    return render(request, 'vendor_dashboard/dashboard.html', context)


@vendor_required
def products_list(request):
    restaurant = request.user.my_restaurants.first()
    products   = Product.objects.filter(restaurant=restaurant)
    return render(request, 'vendor_dashboard/products.html', {
        'restaurant': restaurant,
        'products':   products,
    })


@vendor_required
def orders_list(request):
    restaurant = request.user.my_restaurants.first()
    orders = OrderItem.objects.filter(
        product__restaurant=restaurant
    ).select_related('order', 'product').order_by('-order__created')
    return render(request, 'vendor_dashboard/orders.html', {
        'restaurant': restaurant,
        'orders':     orders,
    })


@vendor_required
def update_order_status(request, item_id, new_status):
    restaurant = request.user.my_restaurants.first()
    item = get_object_or_404(OrderItem, id=item_id, product__restaurant=restaurant)
    allowed = ['pending', 'preparing', 'ready', 'delivered', 'cancelled']
    if new_status in allowed:
        item.status = new_status
        item.save()
        messages.success(request, f"Order updated to {new_status}.")
    return redirect('vendor_dashboard:orders')


@vendor_required
def store_settings(request):
    restaurant = request.user.my_restaurants.first()
    if request.method == 'POST':
        restaurant.name    = request.POST.get('name', restaurant.name)
        restaurant.address = request.POST.get('address', restaurant.address)
        restaurant.phone_number = request.POST.get('phone_number', restaurant.phone_number)
        if 'image' in request.FILES:
            restaurant.image = request.FILES['image']
        restaurant.save()
        messages.success(request, "Store profile updated.")
        return redirect('vendor_dashboard:settings')
    return render(request, 'vendor_dashboard/settings.html', {'restaurant': restaurant})


# vendor_dashboard/views.py


@vendor_required
def add_product(request):
        
    # 1. Security Check: Only vendors can access this view
    if request.user.profile.role != 'vendor':
        return redirect('restaurants:home')
    
    # 2. Get the vendor's Restaurant
    restaurant = request.user.my_restaurants.first()
    
    #if they somehow skipped registering their restaurant, send them to the registration page instead of crashing
    if not restaurant:
        return redirect('restaurants:register_restaurant')  
    
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.restaurant = restaurant
            product.save()
            messages.success(request, "Product added successfully!")
            return redirect('vendor_dashboard:products')
    else:
        form = ProductForm()
    
    return render(request, 'vendor_dashboard/add_product.html', {
        'form': form,
        'restaurant': restaurant
    })



@vendor_required
def add_product(request):
    restaurant = request.user.my_restaurants.first()
    # Fetch the background settings from Admin
    dashboard_settings = DashboardSettings.objects.first()
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.restaurant = restaurant
            product.save()
            return redirect('vendor_dashboard:dashboard')
    else:
        form = ProductForm()

    return render(request, 'vendor_dashboard/add_product.html', {
        'form': form,
        'restaurant': restaurant,
        'dashboard_settings': dashboard_settings # Send to template
    })
    
@vendor_required
def delete_product(request, product_id):
    restaurant = request.user.my_restaurants.first()
    # Security: Only get the product if it belongs to THIS vendor's restaurant
    product = get_object_or_404(Product, id=product_id, restaurant=restaurant)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, f"Product '{product.name}' has been deleted.")
        return redirect('vendor_dashboard:products')
    
    # If they just visit the URL (GET), show a confirmation or redirect
    return redirect('vendor_dashboard:products')

