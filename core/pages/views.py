from django.shortcuts import render, redirect

# def welcome(request):
#     # 1. Check if the user is a logged-in Vendor
#     if request.user.is_authenticated:
#         profile = getattr(request.user, 'profile', None)
#         if profile and profile.role == 'vendor':
#             # Redirect to the dashboard app using the namespace from vendor_dashboard/urls.py
#             return redirect('vendor_dashboard:dashboard')

#     # 2. Otherwise, show the standard landing/welcome page
#     return render(request, 'pages/welcome.html')

# pages/views.py


def welcome(request):
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile and profile.role == 'vendor':
            # Check if they actually have a restaurant record
            if request.user.my_restaurants.exists():
                return redirect('vendor_dashboard:dashboard')
            else:
                # ONLY redirect to registration if the restaurant is missing
                return redirect('vendor_onboarding:register_business')

    return render(request, 'pages/welcome.html')

