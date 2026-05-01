
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from accounts.models import Profile
from decimal import Decimal, InvalidOperation
from accounts.utils import send_email_otp
from .models import PendingVendor
from django.contrib.auth.decorators import login_required
from restaurants.forms import RestaurantRegistrationForm
import uuid
import json
import base64
from django.core.files.base import ContentFile
from restaurants.models import Restaurant, Category, MenuItem
# Create your views here.

# STEP 1 — Registration form
# def vendor_register(request):
#     if request.method == 'POST':
#         biz_name  = request.POST.get('business_name', '').strip()
#         email     = request.POST.get('business_email', '').strip()
#         phone     = request.POST.get('phone_number', '').strip()
#         address   = request.POST.get('address', '').strip()
#         post_code = request.POST.get('post_code', '').strip()

#         if not all([biz_name, email, phone]):
#             messages.error(request, "Please fill in all required fields.")
#             return render(request, 'vendor_onboarding/register.html')

#         # ✅ If a record with this email already exists, update it instead of crashing
#         vendor, created = PendingVendor.objects.update_or_create(
#             email=email,
#             defaults={
#                 'biz_name': biz_name,
#                 'phone': phone,
#                 'address': address,
#                 'post_code': post_code,
#                 'is_verified': False,
#             }
#         )

#         otp = send_email_otp(vendor.email)
#         vendor.otp_code = otp
#         vendor.save()

#         return redirect('vendor_onboarding:verify_email', vendor_id=vendor.id)

#     return render(request, 'vendor_onboarding/register.html')


# def vendor_register(request):
#     if request.method == 'POST':
#         biz_name  = request.POST.get('business_name', '').strip()
#         email     = request.POST.get('business_email', '').strip()
#         phone     = request.POST.get('phone_number', '').strip()
#         address   = request.POST.get('address', '').strip()
#         post_code = request.POST.get('post_code', '').strip()

#         if not all([biz_name, email, phone]):
#             messages.error(request, "Please fill in all required fields.")
#             return render(request, 'vendor_onboarding/register.html')

#         # ← If user is already logged in (came from accounts signup flow)
#         if request.user.is_authenticated:
#             restaurant, created = Restaurant.objects.get_or_create(
#                 owner=request.user,
#                 defaults={
#                     'name': biz_name,
#                     'address': f"{address}, {post_code}".strip(', '),
#                     'phone_number': phone,
#                     'business_email': email,
#                     'description': '',
#                 }
#             )
#             return redirect('vendor_onboarding:store_branding')  # ← skip verify/password

#         # ← Direct partner registration — user has no account yet
#         vendor, created = PendingVendor.objects.update_or_create(
#             email=email,
#             defaults={
#                 'biz_name': biz_name,
#                 'phone': phone,
#                 'address': address,
#                 'post_code': post_code,
#                 'is_verified': False,
#             }
#         )

#         otp = send_email_otp(vendor.email)
#         vendor.otp_code = otp
#         vendor.save()

#         return redirect('vendor_onboarding:verify_email', vendor_id=vendor.id)  # ← verify first

#     categories = Category.objects.all()
#     return render(request, 'vendor_onboarding/register.html', {
#         'categories': categories
#     })


def vendor_register(request):
    if request.method == 'POST':
        biz_name  = request.POST.get('business_name', '').strip()
        email     = request.POST.get('business_email', '').strip()
        phone     = request.POST.get('phone_number', '').strip()
        address   = request.POST.get('address', '').strip()
        post_code = request.POST.get('post_code', '').strip()

        if not all([biz_name, email, phone]):
            messages.error(request, "Please fill in all required fields.")
            categories = Category.objects.all()
            return render(request, 'vendor_onboarding/register.html', {
                'categories': categories
            })

        # ← If already logged in (came from accounts signup flow)
        if request.user.is_authenticated:
            Restaurant.objects.get_or_create(
                owner=request.user,
                defaults={
                    'name': biz_name,
                    'address': f"{address}, {post_code}".strip(', '),
                    'phone_number': phone,
                    'business_email': email,
                    'description': '',
                }
            )
            return redirect('vendor_onboarding:location')

        # ← Direct partner — create PendingVendor
        vendor, created = PendingVendor.objects.update_or_create(
            email=email,
            defaults={
                'biz_name': biz_name,
                'phone': phone,
                'address': address,
                'post_code': post_code,
                'is_verified': False,
            }
        )

        # Send OTP
        otp = send_email_otp(email)
        vendor.otp_code = otp
        vendor.save()

        # ← Store in session so accounts verify view can use it
        request.session['temp_email'] = email
        request.session['email_otp'] = str(otp)
        request.session['pending_vendor_id'] = str(vendor.id)  # ← links back to vendor

        return redirect('accounts:verify_signup_email')  # ← use accounts verify page

    categories = Category.objects.all()
    return render(request, 'vendor_onboarding/register.html', {
        'categories': categories
    })




# STEP 2 — Email OTP verification
# def verify_email(request, vendor_id):
#     vendor = get_object_or_404(PendingVendor, id=vendor_id)

#     if vendor.is_verified:
#         return redirect('vendor_onboarding:create_password', vendor_id=vendor.id)

#     if request.method == 'POST':
#         code = request.POST.get('otp_code', '').strip()

#         if code == str(vendor.otp_code):
#             vendor.is_verified = True
#             vendor.save()
#             return redirect('vendor_onboarding:create_password', vendor_id=vendor.id)
#         else:
#             messages.error(request, "Invalid code. Please try again.")

#     return render(request, 'vendor_onboarding/verify_email.html', {'vendor': vendor})



def verify_email(request, vendor_id):
    vendor = get_object_or_404(PendingVendor, id=vendor_id)

    if vendor.is_verified:
        request.session['pending_vendor_id'] = str(vendor.id)  # ← store in session
        return redirect('accounts:create_password')

    if request.method == 'POST':
        code = request.POST.get('otp_code', '').strip()

        if code == str(vendor.otp_code):
            vendor.is_verified = True
            vendor.save()
            request.session['pending_vendor_id'] = str(vendor.id)  # ← store in session
            return redirect('accounts:create_password')
        else:
            messages.error(request, "Invalid code. Please try again.")

    return render(request, 'vendor_onboarding/verify_email.html', {'vendor': vendor})


# STEP 3 — Create password & finalize account
# def create_password(request, vendor_id):
#     vendor = get_object_or_404(PendingVendor, id=vendor_id)

#     if not vendor.is_verified:
#         messages.error(request, "Please verify your email first.")
#         return redirect('vendor_onboarding:vendor_register')

#     if request.method == 'POST':
#         password  = request.POST.get('password', '')
#         password2 = request.POST.get('password2', '')

#         if not password:
#             messages.error(request, "Password cannot be empty.")
#             return render(request, 'vendor_onboarding/create_password.html', {'vendor': vendor})

#         if password != password2:
#             messages.error(request, "Passwords do not match.")
#             return render(request, 'vendor_onboarding/create_password.html', {'vendor': vendor})

#         if User.objects.filter(email=vendor.email).exists():
#             messages.error(request, "An account with this email already exists.")
#             return render(request, 'vendor_onboarding/create_password.html', {'vendor': vendor})

#         # Create User
#         user = User.objects.create_user(
#             username=vendor.email,
#             email=vendor.email,
#             password=password,
#         )

#         # Set up Profile
#         profile = Profile.objects.get(user=user)
#         profile.role = 'vendor'
#         profile.phone_number = vendor.phone
#         profile.save()

#         # Create Restaurant
#         Restaurant.objects.create(
#             owner=user,
#             name=vendor.biz_name,
#             address=f"{vendor.address}, {vendor.post_code}".strip(', '),
#             phone_number=vendor.phone,
#         )

#         # Clean up pending record
#         vendor.delete()

#         login(request, user)
#         messages.success(request, f"Welcome, {user.username}! Your vendor account is ready.")
#         return redirect('restaurants:dashboard')

#     return render(request, 'vendor_onboarding/create_password.html', {'vendor': vendor})





def create_password(request, vendor_id):
    vendor = get_object_or_404(PendingVendor, id=vendor_id)

    if not vendor.is_verified:
        messages.error(request, "Please verify your email first.")
        return redirect('vendor_onboarding:verify_email', vendor_id=vendor.id)

    if request.method == 'POST':
        password  = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not password:
            messages.error(request, "Password cannot be empty.")
            return render(request, 'vendor_onboarding/create_password.html', {'vendor': vendor})

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'vendor_onboarding/create_password.html', {'vendor': vendor})

        if User.objects.filter(email=vendor.email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, 'vendor_onboarding/create_password.html', {'vendor': vendor})

        # Create User
        user = User.objects.create_user(
            username=vendor.email,
            email=vendor.email,
            password=password,
        )

        # Set up Profile
        profile = Profile.objects.get(user=user)
        profile.role = 'vendor'
        profile.phone_number = vendor.phone
        profile.save()

        # Create Restaurant
        Restaurant.objects.create(
            owner=user,
            name=vendor.biz_name,
            address=vendor.address,       # ← separate
            post_code=vendor.post_code,   # ← separate
            phone_number=vendor.phone,
            business_email=vendor.email,
            description='',

        )

        vendor.delete()

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, f"Welcome, {user.username}! Your vendor account is ready.")
        return redirect('vendor_onboarding:store_branding')

    return render(request, 'vendor_onboarding/create_password.html', {'vendor': vendor})

# @login_required
# def store_branding(request):
#     restaurant = request.user.my_restaurants.first()

#     # Guard — if no restaurant yet, send to register
#     if not restaurant:
#         return redirect('vendor_onboarding:register_business')

#     if request.method == 'POST':
#         logo = request.FILES.get('logo')
#         cover = request.FILES.get('cover_image')
#         if logo:
#             restaurant.logo = logo
#         if cover:
#             restaurant.cover_image = cover
#         restaurant.save()
#         return redirect('vendor_onboarding:menu')

#     return render(request, 'vendor_onboarding/store_branding.html', {
#         'restaurant': restaurant
#     })


# @login_required
# def menu(request):
#     restaurant = request.user.my_restaurants.first()
#     if not restaurant:
#         return redirect('vendor_onboarding:register_business')
#     return render(request, 'vendor_onboarding/menu.html', {
#         'restaurant': restaurant
#     })
    
    


# @login_required
# def save_menu(request):
#     if request.method == 'POST':
#         menu_data = request.POST.get('menu_data', '[]')
#         try:
#             items = json.loads(menu_data)
#             restaurant = request.user.my_restaurants.first()
#             for item in items:
#                 MenuItem.objects.create(
#                     restaurant=restaurant,
#                     name=item.get('name'),
#                     price=item.get('price'),
#                     description=item.get('desc', ''),
#                     category=item.get('category', ''),
#                 )
#         except Exception:
#             pass
#         return redirect('vendor_dashboard:dashboard')
#     return redirect('vendor_onboarding:menu')



# @login_required
# def save_menu(request):
#     if request.method == 'POST':
#         menu_data = request.POST.get('menu_data', '[]')
#         try:
#             items = json.loads(menu_data)
#             restaurant = request.user.my_restaurants.first()

#             if not restaurant:
#                 messages.error(request, "No restaurant found.")
#                 return redirect('vendor_onboarding:menu')

#             for item in items:
#                 menu_item = MenuItem(
#                     restaurant=restaurant,
#                     name=item.get('name', ''),
#                     description=item.get('desc', ''),
#                     price=item.get('price', 0),
#                     item_type=item.get('category', 'Main') or 'Main',
#                 )

#                 # Handle base64 image from frontend
#                 image_data = item.get('image')
#                 if image_data and image_data.startswith('data:image'):
#                     try:
#                         # Strip the data:image/jpeg;base64, prefix
#                         format, imgstr = image_data.split(';base64,')
#                         ext = format.split('/')[-1]
#                         filename = f"menu_{item.get('name', 'item').replace(' ', '_')}.{ext}"
#                         menu_item.image = ContentFile(
#                             base64.b64decode(imgstr),
#                             name=filename
#                         )
#                     except Exception:
#                         pass

#                 menu_item.save()

#         except json.JSONDecodeError:
#             messages.error(request, "Invalid menu data.")
#             return redirect('vendor_onboarding:menu')

#         return redirect('vendor_dashboard:dashboard')

#     return redirect('vendor_onboarding:menu')

# @login_required
# def register_vendor_business(request):
#     # 1. Security: Only vendors allowed
#     if request.user.profile.role != 'vendor':
#         return redirect('restaurants:home')
    
#     # 2. Check if they already have a restaurant
#     if request.user.my_restaurants.exists():
#         return redirect('vendor_dashboard:dashboard')

#     if request.method == 'POST':
#         form = RestaurantRegistrationForm(request.POST, request.FILES)
#         if form.is_valid():
#             restaurant = form.save(commit=False)
#             restaurant.owner = request.user
#             restaurant.save()
#             return redirect('vendor_dashboard:dashboard')
#     else:
#         # 3. AUTO-UPDATE: Pre-fill using existing User/Profile data
#         initial_data = {
#             'business_email': request.user.email,
#             'phone_number': getattr(request.user.profile, 'phone_number', '')
#         }
#         form = RestaurantRegistrationForm(initial=initial_data)
        
#     categories = Category.objects.all()
#     return render(request, 'vendor_onboarding/register.html', {
#         'form': form, 
#         'categories': categories
#     })

# @login_required
# def register_vendor_business(request):
#     if request.user.profile.role != 'vendor':
#         return redirect('restaurants:home')

#     if request.user.my_restaurants.exists():
#         return redirect('vendor_dashboard:dashboard')

#     if request.method == 'POST':
#         form = RestaurantRegistrationForm(request.POST, request.FILES)
#         if form.is_valid():
#             restaurant = form.save(commit=False)
#             restaurant.owner = request.user
#             restaurant.save()
#             return redirect('vendor_onboarding:store_branding')  # ← was dashboard, now branding
#     else:
#         initial_data = {
#             'business_email': request.user.email,
#             'phone_number': getattr(request.user.profile, 'phone_number', '')
#         }
#         form = RestaurantRegistrationForm(initial=initial_data)

#     categories = Category.objects.all()
#     return render(request, 'vendor_onboarding/register.html', {
#         'form': form,
#         'categories': categories
#     })
    
    
    
# @login_required
# def register_vendor_business(request):
#     if request.user.profile.role != 'vendor':
#         return redirect('restaurants:home')

#     if request.user.my_restaurants.exists():
#         return redirect('vendor_onboarding:store_branding')  # ← already has restaurant, skip to branding

#     if request.method == 'POST':
#         form = RestaurantRegistrationForm(request.POST, request.FILES)
#         if form.is_valid():
#             restaurant = form.save(commit=False)
#             restaurant.owner = request.user
#             restaurant.save()
#             return redirect('vendor_onboarding:location')  # ← Step 1 done → Step 2
#     else:
#         initial_data = {
#             'business_email': request.user.email,
#             'phone_number': getattr(request.user.profile, 'phone_number', '')
#         }
#         form = RestaurantRegistrationForm(initial=initial_data)

#     categories = Category.objects.all()
#     return render(request, 'vendor_onboarding/register.html', {
#         'form': form,
#         'categories': categories
#     })



# @login_required
# def register_vendor_business(request):
#     if request.user.profile.role != 'vendor':
#         return redirect('restaurants:home')

#     restaurant = request.user.my_restaurants.first()  # ← get ONCE at top

#     if restaurant and not request.GET.get('edit'):
#         return redirect('vendor_onboarding:store_branding')

#     if request.method == 'POST':
#         form = RestaurantRegistrationForm(
#             request.POST,
#             request.FILES,
#             instance=restaurant  # ← updates existing, not creates new
#         )
#         if form.is_valid():
#             saved = form.save(commit=False)
#             saved.owner = request.user
#             saved.save()
#             return redirect('vendor_onboarding:location')
#         # ← if form invalid, falls through and re-renders with errors
#     else:
#         form = RestaurantRegistrationForm(instance=restaurant)  # ← pre-fills from DB

#     categories = Category.objects.all()
#     return render(request, 'vendor_onboarding/register.html', {
#         'form': form,
#         'categories': categories
#     })

# @login_required
# def register_vendor_business(request):
#     if request.user.profile.role != 'vendor':
#         return redirect('restaurants:home')

#     restaurant = request.user.my_restaurants.first()

#     if restaurant and not request.GET.get('edit'):
#         return redirect('vendor_onboarding:store_branding')

#     if request.method == 'POST':
#         form = RestaurantRegistrationForm(
#             request.POST,
#             request.FILES,
#             instance=restaurant  # ← updates if exists, creates if None
#         )
#         if form.is_valid():
#             saved = form.save(commit=False)
#             saved.owner = request.user
#             saved.save()
#             if request.GET.get('edit'):
#                 return redirect('vendor_onboarding:review')  # ← back to review if editing
#             return redirect('vendor_onboarding:location')    # ← next step if new
#         # form errors fall through and re-render
#     else:
#         form = RestaurantRegistrationForm(instance=restaurant)

#     categories = Category.objects.all()
#     return render(request, 'vendor_onboarding/register.html', {
#         'form': form,
#         'categories': categories
#     })
    

# @login_required
# def register_vendor_business(request):
#     if request.user.profile.role != 'vendor':
#         return redirect('restaurants:home')

#     restaurant = request.user.my_restaurants.first()

#     if restaurant and not request.GET.get('edit'):
#         return redirect('vendor_onboarding:store_branding')

#     if request.method == 'POST':
#         form = RestaurantRegistrationForm(
#             request.POST,
#             request.FILES,
#             instance=restaurant
#         )
#         if form.is_valid():
#             saved = form.save(commit=False)
#             saved.owner = request.user
#             saved.save()
#             if request.GET.get('edit'):
#                 return redirect('vendor_onboarding:review')
#             return redirect('vendor_onboarding:location')
#     else:
#         form = RestaurantRegistrationForm(instance=restaurant)

#     categories = Category.objects.all()
#     return render(request, 'vendor_onboarding/register.html', {
#         'form': form,
#         'categories': categories,
#         'restaurant': restaurant,  # ← this was missing!
#         'is_edit': bool(request.GET.get('edit')),
#     })
    
    
    
@login_required
def register_vendor_business(request):
    if request.user.profile.role != 'vendor':
        return redirect('restaurants:home')

    restaurant = request.user.my_restaurants.first()

    if restaurant and not request.GET.get('edit'):
        return redirect('vendor_onboarding:store_branding')

    if request.method == 'POST':
        form = RestaurantRegistrationForm(
            request.POST,
            request.FILES,
            instance=restaurant
        )
        if form.is_valid():
            saved = form.save(commit=False)
            saved.owner = request.user
            # ← Only save Step 1 fields
            saved.save(update_fields=[
                'name',
                'description',
                'business_email',
                'phone_number',
            ] if restaurant else None)  # None = save all fields on first create
            if request.GET.get('edit'):
                return redirect('vendor_onboarding:review')
            return redirect('vendor_onboarding:location')
    else:
        form = RestaurantRegistrationForm(instance=restaurant)

    categories = Category.objects.all()
    return render(request, 'vendor_onboarding/register.html', {
        'form': form,
        'categories': categories,
        'restaurant': restaurant,
    })
# @login_required
# def register_vendor_business(request):
#     if request.user.profile.role != 'vendor':
#         return redirect('restaurants:home')

#     # ← Only skip if NOT editing
#     if request.user.my_restaurants.exists() and not request.GET.get('edit'):
#         return redirect('vendor_onboarding:store_branding')

#     if request.method == 'POST':
#         restaurant = request.user.my_restaurants.first()
#         form = RestaurantRegistrationForm(request.POST, request.FILES, instance=restaurant)
#         if form.is_valid():
#             restaurant = form.save(commit=False)
#             restaurant.owner = request.user
#             restaurant.save()
#             return redirect('vendor_onboarding:location')
#     else:
#         restaurant = request.user.my_restaurants.first()
#         initial_data = {
#             'business_email': request.user.email,
#             'phone_number': getattr(request.user.profile, 'phone_number', '')
#         }
#         form = RestaurantRegistrationForm(
#             instance=restaurant,      # ← pre-fills existing data
#             initial=initial_data
#         )

    # categories = Category.objects.all()
    # return render(request, 'vendor_onboarding/register.html', {
    #     'form': form,
    #     'categories': categories
    # })



# @login_required
# def location(request):
#     restaurant = request.user.my_restaurants.first()
#     if not restaurant:
#         return redirect('vendor_onboarding:register_business')

#     if request.method == 'POST':
#         address   = request.POST.get('address', '').strip()
#         city      = request.POST.get('city', '').strip()
#         post_code = request.POST.get('post_code', '').strip()
#         landmark  = request.POST.get('landmark', '').strip()

#         if not address or not city:
#             messages.error(request, "Please provide at least address and city.")
#             return render(request, 'vendor_onboarding/location.html', {
#                 'restaurant': restaurant
#             })

#         # Build full address string
#         full_address = f"{address}, {city}"
#         if landmark:
#             full_address += f" (near {landmark})"

#         restaurant.address = full_address
#         restaurant.post_code = post_code
#         restaurant.save()

#         return redirect('vendor_onboarding:store_branding')  # ← Step 2 → Step 3

#     return render(request, 'vendor_onboarding/location.html', {
#         'restaurant': restaurant
#     })
    


# @login_required
# def store_branding(request):
#     restaurant = request.user.my_restaurants.first()
#     if not restaurant:
#         return redirect('vendor_onboarding:register_business')

#     if request.method == 'POST':
#         logo = request.FILES.get('logo')
#         cover = request.FILES.get('cover_image')
#         if logo:
#             restaurant.logo = logo
#         if cover:
#             restaurant.cover_image = cover
#         restaurant.save()
#         return redirect('vendor_onboarding:menu')  # ← Step 3 done → Step 4
#     return render(request, 'vendor_onboarding/store_branding.html', {
#         'restaurant': restaurant
#     })


# @login_required
# def location(request):
#     restaurant = request.user.my_restaurants.first()
#     if not restaurant:
#         return redirect('vendor_onboarding:register_business')

#     if request.method == 'POST':
#         form = RestaurantRegistrationForm(
#             request.POST,
#             instance=restaurant
#         )
#         # Only validate location fields
#         if form.data.get('address') and form.data.get('post_code'):
#             restaurant.address = form.data.get('address')
#             restaurant.post_code = form.data.get('post_code')
#             restaurant.save()
#             if request.GET.get('edit'):
#                 return redirect('vendor_onboarding:review')
#             return redirect('vendor_onboarding:store_branding')
#         else:
#             messages.error(request, "Please provide both address and post code.")

#     return render(request, 'vendor_onboarding/location.html', {
#         'restaurant': restaurant
#     })



# @login_required
# def store_branding(request):
#     restaurant = request.user.my_restaurants.first()
#     if not restaurant:
#         return redirect('vendor_onboarding:register_business')

#     if request.method == 'POST':
#         form = RestaurantRegistrationForm(
#             request.POST,
#             request.FILES,
#             instance=restaurant
#         )
#         logo = request.FILES.get('logo')
#         cover = request.FILES.get('cover_image')
#         if logo:
#             restaurant.logo = logo
#         if cover:
#             restaurant.cover_image = cover
#         restaurant.save()
#         if request.GET.get('edit'):
#             return redirect('vendor_onboarding:review')
#         return redirect('vendor_onboarding:menu')

#     return render(request, 'vendor_onboarding/store_branding.html', {
#         'restaurant': restaurant
#     })




# @login_required
# def location(request):
#     restaurant = request.user.my_restaurants.first()
#     if not restaurant:
#         return redirect('vendor_onboarding:register_business')

#     if request.method == 'POST':
#         address   = request.POST.get('address', '').strip()
#         city      = request.POST.get('city', '').strip()
#         post_code = request.POST.get('post_code', '').strip()
#         landmark  = request.POST.get('landmark', '').strip()

#         if not address or not city:
#             messages.error(request, "Please provide at least address and city.")
#             return render(request, 'vendor_onboarding/location.html', {
#                 'restaurant': restaurant
#             })

#         # ← Save each field separately now
#         restaurant.address = address
#         restaurant.city = city
#         restaurant.post_code = post_code
#         if landmark:
#             restaurant.landmark = landmark  # only if you added this field too
#         restaurant.save()

#         if request.GET.get('edit'):
#             return redirect('vendor_onboarding:review')
#         return redirect('vendor_onboarding:store_branding')

#     return render(request, 'vendor_onboarding/location.html', {
#         'restaurant': restaurant,
#     })
    
    
@login_required
def location(request):
    restaurant = get_object_or_404(Restaurant, owner=request.user)

    if request.method == 'POST':
        address   = request.POST.get('address', '').strip()
        city      = request.POST.get('city', '').strip()
        post_code = request.POST.get('post_code', '').strip()
        landmark  = request.POST.get('landmark', '').strip()

        if not address or not city:
            messages.error(request, "Please provide at least address and city.")
            return render(request, 'vendor_onboarding/location.html', {
                'restaurant': restaurant
            })

        restaurant.address   = address
        restaurant.city      = city
        restaurant.post_code = post_code
        restaurant.landmark  = landmark
        restaurant.save(update_fields=['address', 'city', 'post_code', 'landmark'])

        return redirect('vendor_onboarding:store_branding')

    return render(request, 'vendor_onboarding/location.html', {
        'restaurant': restaurant,
    })


@login_required
def edit_location(request):
    restaurant = get_object_or_404(Restaurant, owner=request.user)

    if request.method == 'POST':
        address   = request.POST.get('address', '').strip()
        city      = request.POST.get('city', '').strip()
        post_code = request.POST.get('post_code', '').strip()
        landmark  = request.POST.get('landmark', '').strip()

        if not address or not city:
            messages.error(request, "Please provide at least address and city.")
            return render(request, 'vendor_onboarding/location.html', {
                'restaurant': restaurant
            })

        restaurant.address   = address
        restaurant.city      = city
        restaurant.post_code = post_code
        restaurant.landmark  = landmark
        restaurant.save(update_fields=['address', 'city', 'post_code', 'landmark'])

        return redirect('vendor_onboarding:review')

    return render(request, 'vendor_onboarding/location.html', {
        'restaurant': restaurant,
    })
    

# @login_required
# def store_branding(request):
#     restaurant = request.user.my_restaurants.first()
#     if not restaurant:
#         return redirect('vendor_onboarding:register_business')

#     if request.method == 'POST':
#         logo = request.FILES.get('logo')
#         cover = request.FILES.get('cover_image')
#         if logo:
#             restaurant.logo = logo
#         if cover:
#             restaurant.cover_image = cover
#         restaurant.save()

#         if request.GET.get('edit'):
#             return redirect('vendor_onboarding:review')
#         return redirect('vendor_onboarding:menu')

#     return render(request, 'vendor_onboarding/store_branding.html', {
#         'restaurant': restaurant,  # ← was missing
#     })
    
    
# @login_required
# def store_branding(request):
#     restaurant = get_object_or_404(Restaurant, owner=request.user)

#     if request.method == 'POST':
#         logo = request.FILES.get('logo')
#         cover = request.FILES.get('cover_image')

#         # ← Only update branding fields, nothing else
#         if logo:
#             restaurant.logo = logo
#         if cover:
#             restaurant.cover_image = cover

#         # ← update_fields prevents other fields being touched
#         restaurant.save(update_fields=[
#             'logo' if logo else None,
#             'cover_image' if cover else None,
#         ])

#         if request.GET.get('edit'):
#             return redirect('vendor_onboarding:review')
#         return redirect('vendor_onboarding:menu')

#     return render(request, 'vendor_onboarding/store_branding.html', {
#         'restaurant': restaurant,
#     })


@login_required
def store_branding(request):
    restaurant = get_object_or_404(Restaurant, owner=request.user)

    if request.method == 'POST':
        fields_to_update = []

        logo = request.FILES.get('logo')
        cover = request.FILES.get('cover_image')

        if logo:
            restaurant.logo = logo
            fields_to_update.append('logo')
        if cover:
            restaurant.cover_image = cover
            fields_to_update.append('cover_image')

        if fields_to_update:
            restaurant.save(update_fields=fields_to_update)  # ← ONLY touches logo/cover

        if request.GET.get('edit'):
            return redirect('vendor_onboarding:review')
        return redirect('vendor_onboarding:menu')

    return render(request, 'vendor_onboarding/store_branding.html', {
        'restaurant': restaurant,
    })



@login_required
def menu(request):
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    if not restaurant:
        return redirect('vendor_onboarding:register_business')
    menu_items = restaurant.menu_items.all()  # ← fetch existing items
    return render(request, 'vendor_onboarding/menu.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,             # ← pass to template
    })


@login_required
def save_menu(request):
    if request.method != 'POST':
        return redirect('vendor_onboarding:menu')

    menu_data = request.POST.get('menu_data', '[]')
    try:
        items = json.loads(menu_data)
        restaurant = get_object_or_404(Restaurant, owner=request.user)
        
        # 1. Track which IDs are coming from the frontend
        # We use a list comprehension and filter out None/empty values
        valid_received_ids = [item.get('id') for item in items if item.get('id')]

        # 2. Cleanup: Delete items that were removed in the UI
        restaurant.menu_items.exclude(id__in=valid_received_ids).delete()

        for item in items:
            item_id = item.get('id')
            image_data = item.get('image')

            # 3. Smart Get or Create
            if item_id:
                # Update existing item
                menu_item = get_object_or_404(MenuItem, id=item_id, restaurant=restaurant)
            else:
                # Create brand new item
                menu_item = MenuItem(restaurant=restaurant)

            # 4. Update Fields
            menu_item.name = item.get('name', '')
            menu_item.description = item.get('desc', '')
            raw_price = item.get('price')
            if not raw_price:
                continue

            try:
                price = Decimal(str(raw_price))
            except InvalidOperation:
                continue
            menu_item.price = price 
            menu_item.item_type = item.get('category', 'Main') or 'Main'

            # 5. Image Logic (The Fix)
            if image_data and image_data.startswith('data:image'):
                # New image uploaded - Process Base64
                try:
                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    filename = f"menu_{uuid.uuid4().hex[:8]}.{ext}"
                    menu_item.image.save(filename, ContentFile(base64.b64decode(imgstr)), save=False)
                except Exception as e:
                    print(f"Image error: {e}")
            
            # Note: If image_data is a URL (starts with /media/), 
            # we do NOTHING. We don't re-assign it; the old file stays in the DB.

            menu_item.save()

    except json.JSONDecodeError:
        messages.error(request, "Invalid menu data.")
        return redirect('vendor_onboarding:menu')

    return redirect('vendor_onboarding:review')


# @login_required
# def review(request):
#     restaurant = request.user.my_restaurants.first()
#     if not restaurant:
#         return redirect('vendor_onboarding:register_business')

#     menu_items = restaurant.menu_items.all()

#     if request.method == 'POST':
#         return redirect('vendor_dashboard:dashboard')  # ← Step 5 done → Dashboard

#     return render(request, 'vendor_onboarding/review.html', {
#         'restaurant': restaurant,
#         'menu_items': menu_items,
#     })
    
@login_required
def review(request):
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    menu_items = restaurant.menu_items.all()

    if request.method == 'POST':
        restaurant.is_completed = True  # ← mark as completed
        restaurant.save()
        return redirect('vendor_dashboard:dashboard')

    return render(request, 'vendor_onboarding/review.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
    })
    
    
    
    
    
    
    
    
    
    
    