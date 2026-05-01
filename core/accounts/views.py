from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from accounts.models import Profile
from .utils import send_email_otp
from restaurants.verify import send_verification, check_verification
from .forms import PersonalInfoForm, RoleSignupForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from vendor_onboarding import views
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import json
from django.http import JsonResponse
from restaurants.models import Restaurant
from django.db import transaction, IntegrityError

# --- AUTH FLOW ---
def signup_view(request):
    if request.method == 'POST':
        form = RoleSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.profile.role == 'vendor':
                return redirect('vendor_onboarding:register_business')
            return redirect('restaurants:home')
    else:
        form = RoleSignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


def signup_start(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # ← Only send OTP if not already sent for this email
        existing_email = request.session.get('temp_email')
        existing_otp = request.session.get('email_otp')

        if not existing_otp or existing_email != email:
            otp = send_email_otp(email)
            request.session['email_otp'] = otp
            request.session['temp_email'] = email

        return redirect('accounts:verify_signup_email')
    return render(request, 'accounts/signup.html')


def signup_profile(request):
    email = request.session.get('temp_email')
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        role = request.POST.get('role') # 'customer' or 'vendor'
        
        request.session['temp_full_name'] = full_name
        request.session['temp_role'] = role

        if role == 'vendor':
            # Vendors go to business creation first
            return redirect('vendor_onboarding:register_business')
        else:
            # Customers go to set their password
            return redirect('accounts:create_password')
            
    return render(request, 'accounts/signup_step3.html')



def otp_status(request):
    otp_sent = bool(request.session.get('email_otp'))
    return JsonResponse({'sent': otp_sent})



def verify_signup_email(request):
    email = request.session.get('temp_email')
    session_otp = request.session.get('email_otp')

    if not email or not session_otp:
        return redirect('accounts:signup')

    if request.method == 'POST':
        user_code = request.POST.get('otp_code')
        if str(user_code) == str(session_otp):
            request.session['email_verified'] = True
            del request.session['email_otp']
            request.session.pop('otp_resend_count', None)

            # ← Check if this came from direct vendor registration
            if request.session.get('pending_vendor_id'):
                # Mark vendor as verified in DB
                try:
                    from vendor_onboarding.models import PendingVendor
                    vendor = PendingVendor.objects.get(
                        id=request.session['pending_vendor_id']
                    )
                    vendor.is_verified = True
                    vendor.save()
                except PendingVendor.DoesNotExist:
                    pass
                return redirect('accounts:create_password')  # ← vendor goes to accounts password page

            # Normal signup flow
            return redirect('accounts:signup_profile')
        else:
            messages.error(request, "Invalid code. Please check your email.")

    return render(request, 'accounts/verify_signup_email.html', {'email': email})


def resend_otp(request):
    if request.method == 'POST':
        email = request.session.get('temp_email')

        if not email:
            return JsonResponse({'success': False, 'message': 'Session expired. Please sign up again.'})

        # ← Rate limit: max 3 resends
        resend_count = request.session.get('otp_resend_count', 0)

        if resend_count >= 3:
            return JsonResponse({
                'success': False,
                'limit_reached': True,
                'message': 'Maximum resend limit reached. Please sign up again.'
            })

        # Send new OTP
        otp = send_email_otp(email)
        request.session['email_otp'] = otp

        # Increment counter
        request.session['otp_resend_count'] = resend_count + 1
        remaining = 3 - request.session['otp_resend_count']

        return JsonResponse({
            'success': True,
            'remaining': remaining  # ← tells frontend how many left
        })

    return JsonResponse({'success': False, 'message': 'Invalid request.'})




def signup_profile(request):
    email_verified = request.session.get('email_verified')
    temp_email = request.session.get('temp_email')
    is_google_user = request.user.is_authenticated

    if not is_google_user and not email_verified:
        return redirect('accounts:signup')

    if is_google_user:
        profile, created = Profile.objects.get_or_create(user=request.user)
        if not created and profile.role:
            return redirect('restaurants:home')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        role = request.POST.get('role')

        request.session['temp_full_name'] = full_name
        request.session['temp_role'] = role

        if is_google_user:
            # Google flow → save directly, redirect immediately
            profile, _ = Profile.objects.get_or_create(user=request.user)
            profile.role = role
            profile.save()

            name_parts = full_name.split(' ', 1)
            request.user.first_name = name_parts[0]
            request.user.last_name = name_parts[1] if len(name_parts) > 1 else ""
            request.user.save()

            if role == 'vendor':
                return redirect('vendor_onboarding:register_business')
            return redirect('restaurants:home')

        else:
            # Email flow → ALWAYS go to create_password first
            # role is saved in session, create_password will handle redirect
            return redirect('accounts:create_password')  # ← both vendor & customer

    return render(request, 'accounts/signup_step3.html', {
        'user': request.user if is_google_user else None,
        'email': temp_email,
    })







def create_password(request):
    if request.method == 'POST':
        password  = request.POST.get('password')
        email     = request.session.get('temp_email')
        full_name = request.session.get('temp_full_name', '')
        role      = request.session.get('temp_role')
        pending_id = request.session.get('pending_vendor_id')

        if not email and not pending_id:
            messages.error(request, "Session expired.")
            return redirect('accounts:signup')

        try:
            with transaction.atomic():
                # 1. Handle Direct Vendor Flow
                if pending_id:
                    from vendor_onboarding.models import PendingVendor
                    vendor = get_object_or_404(PendingVendor, id=pending_id)
                    target_email = vendor.email
                    
                    # Get or Create user to prevent UNIQUE constraint crash
                    user, created = User.objects.get_or_create(
                        username=target_email, 
                        defaults={'email': target_email}
                    )
                    user.set_password(password)
                    user.save()

                    # Update Profile & Restaurant (Idempotent)
                    profile, _ = Profile.objects.get_or_create(user=user)
                    profile.role = 'vendor'
                    profile.phone_number = vendor.phone
                    profile.save()

                    Restaurant.objects.update_or_create(
                        owner=user,
                        defaults={
                            'name': vendor.biz_name,
                            'address': vendor.address,
                            'post_code': vendor.post_code,
                            'phone_number': vendor.phone,
                            'business_email': vendor.email,
                        }
                    )
                    vendor.delete()
                    request.session.pop('pending_vendor_id', None)

                # 2. Handle Normal Signup Flow
                else:
                    user, created = User.objects.get_or_create(
                        username=email, 
                        defaults={'email': email}
                    )
                    user.set_password(password)
                    
                    # Split name safely
                    name_parts = full_name.split(' ', 1)
                    user.first_name = name_parts[0]
                    user.last_name = name_parts[1] if len(name_parts) > 1 else ""
                    user.save()

                    profile, _ = Profile.objects.get_or_create(user=user)
                    profile.role = role
                    profile.save()

                # 3. Finalize
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                if role == 'vendor' or pending_id:
                    return redirect('vendor_onboarding:register_business')
                return redirect('restaurants:home')

        except IntegrityError:
            messages.error(request, "This account is already being processed.")
            return redirect('accounts:login')

    return render(request, 'accounts/create_password.html')




def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.profile.role == 'vendor':
                if not hasattr(user, 'my_restaurants') or not user.my_restaurants.exists():
                    return redirect('vendor_onboarding:register_business')
                return redirect('restaurants:dashboard')
            return redirect('vendor_dashboard:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


# --- OTP Verification Views for Vendor Registration ---

def verify_registration_phone(request):
    data = request.session.get('temp_vendor_data')
    if not data:
        return redirect('accounts:vendor_registration')

    pending_phone = data.get('phone')

    if request.method == 'POST':
        code = request.POST.get('otp_code')
        # Using your imported check_verification util
        if check_verification(pending_phone, code):
            return redirect('accounts:create_password')
        else:
            messages.error(request, "Invalid code. Please try again.")

    return render(request, 'accounts/verify_phone_update.html', {
        'phone': pending_phone,
        'is_registration': True
    })



# --- ACCOUNT SETTINGS ---

@login_required
def manage_account(request):
    """General landing page for Account Settings (Home/Sidebar)"""
    profile = Profile.objects.get(user=request.user)
    return render(request, 'accounts/manage.html', {'profile': profile})


@login_required
def personal_info(request):
    import os
    # Always fetch fresh from DB — never rely on cached request.user.profile
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid() and 'profile_image' in request.FILES:
            uploaded_file = request.FILES['profile_image']
            form.save()  # This saves the User model (e.g. username) and updates the profile image field in memory
            # 1. Delete the old image file from disk first
            if profile.profile_image and profile.profile_image.name:
                try:
                    old_path = profile.profile_image.path
                    if os.path.isfile(old_path):
                        os.remove(old_path)
                except Exception:
                    pass

            # 2. Assign and save ONLY the profile_image field
            #    Using update_fields prevents Django from accidentally
            #    clearing other fields on the profile row
            messages.success(request, "Profile updated successfully!")
            profile.profile_image = uploaded_file
            profile.save(update_fields=['profile_image'])

        # PRG redirect — stops double-submit on browser refresh
        return redirect('accounts:personal_info')

    else:
        form = PersonalInfoForm(instance=request.user)

    # Always re-fetch so template gets the freshest image URL
    profile.refresh_from_db()
    return render(request, 'accounts/personal_info.html', {'form': form, 'profile': profile})


@login_required
def edit_phone(request):
    """
    Dedicated page to update phone number (Uber-style).
    On POST → sends OTP and redirects to verify page.
    """
    profile = request.user.profile

    if request.method == 'POST':
        country_code = request.POST.get('country_code', '+1')
        phone_number = request.POST.get('phone_number', '').strip()

        if not phone_number:
            messages.error(request, "Please enter a phone number.")
            return redirect('accounts:edit_phone')

        # Build the full number (e.g. +2348012345678)
        full_number = country_code + phone_number

        if full_number == profile.phone_number:
            messages.error(request, "This is already your current phone number.")
            return redirect('accounts:edit_phone')

        # Send OTP via Twilio Verify
        send_verification(full_number)
        request.session['pending_phone'] = full_number
        return redirect('accounts:verify_phone_update')

    # GET — show the form pre-filled with current number if any
    current_phone = profile.phone_number or ''
    return render(request, 'accounts/edit_phone.html', {
        'current_phone': current_phone,
    })


@login_required
def verify_phone_update(request):
    pending_phone = request.session.get('pending_phone')
    if not pending_phone:
        return redirect('accounts:personal_info')

    if request.method == 'POST':
        code = request.POST.get('otp_code')
        if check_verification(pending_phone, code):
            profile = request.user.profile
            profile.phone_number = pending_phone
            profile.save()
            del request.session['pending_phone']
            messages.success(request, "Phone number verified and updated!")
            return redirect('accounts:personal_info')
        else:
            messages.error(request, "Invalid or expired code. Please try again.")

    return render(request, 'accounts/verify_otp.html', {
        'type': 'Phone Number',
        'value': pending_phone,
    })

@login_required
def edit_email(request):
    """
    Dedicated page to update email (Uber-style).
    On POST → sends OTP and redirects to verify page.
    """
    if request.method == 'POST':
        new_email = request.POST.get('email', '').strip()

        if not new_email:
            messages.error(request, 'Please enter an email address.')
            return redirect('accounts:edit_email')

        if new_email == request.user.email:
            messages.error(request, 'This is already your current email address.')
            return redirect('accounts:edit_email')

        otp = send_email_otp(new_email)
        request.session['pending_email'] = new_email
        request.session['email_otp'] = otp
        return redirect('accounts:verify_email_update')

    return render(request, 'accounts/edit_email.html')



@login_required
def verify_email_update(request):
    pending_email = request.session.get('pending_email')
    session_otp = request.session.get('email_otp')

    if not pending_email:
        return redirect('accounts:personal_info')

    if request.method == 'POST':
        user_otp = request.POST.get('otp_code')
        if user_otp == session_otp:
            request.user.email = pending_email
            request.user.save()
            del request.session['pending_email']
            del request.session['email_otp']
            messages.success(request, "Email updated successfully!")
            return redirect('accounts:personal_info')
        else:
            messages.error(request, "Invalid code. Please try again.")

    return render(request, 'accounts/verify_otp.html', {
        'type': 'Email',
        'value': pending_email,
    })



@login_required
def security_settings(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # This prevents the user from being logged out after password change
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:security_settings')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/security_settings.html', {'form': form})




def logout_view(request):
    logout(request)
    return redirect('welcome')










