from pyexpat.errors import messages

from django.shortcuts import redirect, render, get_object_or_404

from .forms import RestaurantRegistrationForm
from .models import Restaurant, Category, MenuItem
from django.contrib.auth.decorators import login_required

# --- CUSTOMER FACING VIEWS ---

def home(request):
    # Redirect Vendors to their separate app immediately
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile and profile.role == 'vendor':
            return redirect('vendor_dashboard:dashboard')

    categories = Category.objects.all()
    category_id = request.GET.get('category')
    
    if category_id:
        restaurants = Restaurant.objects.filter(
            menu_items__category_group_id=category_id, 
            status='verified', 
            is_active=True
        ).distinct()
    else:
        restaurants = Restaurant.objects.filter(status='verified', is_active=True)
        
    return render(request, 'restaurants/home.html', {
        'categories': categories,
        'restaurants': restaurants,
    })

def search_restaurants(request):
    query = request.GET.get('q', '')
    results = Restaurant.objects.filter(name__icontains=query, status='verified', is_active=True)
    return render(request, 'partials/restaurant_list.html', {'restaurants': results})

def restaurant_detail(request, pk):
    # Only show if verified
    restaurant = get_object_or_404(Restaurant, pk=pk, status='verified')
    menu_items = restaurant.menu_items.all() 
    return render(request, 'restaurants/detail.html', {
        'restaurant': restaurant,
        'menu_items': menu_items
    })

def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    # Filter only items from verified restaurants
    products = MenuItem.objects.filter(category_group=category, restaurant__status='verified')
    return render(request, 'restaurants/category_list.html', {
        'category': category,
        'products': products
    }) 



@login_required
def register_restaurant(request):
    if request.user.profile.role != 'vendor':
        return redirect('restaurants:home')
    
    if request.user.my_restaurants.exists():
        return redirect('vendor_dashboard:dashboard')

    if request.method == 'POST':
        form = RestaurantRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.owner = request.user
            restaurant.status = 'pending'
            restaurant.save()
            return redirect('vendor_dashboard:dashboard')
    else:
        # PRE-FILL LOGIC: Pass the user's details as initial data
        # 'business_email' and 'phone_number' must match your form's field names
        initial_data = {
            'business_email': request.user.email,
            'phone_number': getattr(request.user.profile, 'phone_number', '')
        }
        form = RestaurantRegistrationForm(initial=initial_data)
        
    categories = Category.objects.all()
    return render(request, 'restaurants/register_restaurant.html', {
        'form': form, 
        'categories': categories
    })
