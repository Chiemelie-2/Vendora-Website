from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
app_name = 'accounts'

urlpatterns = [
    path('signup/',        views.signup_start,        name='signup'), 
    path('login/',         views.login_view,          name='login'),
    path('logout/',        views.logout_view,         name='logout'),
    path('manage/',        views.manage_account,      name='manage_account'),
    path('personal-info/', views.personal_info,       name='personal_info'),
    path('edit-phone/',    views.edit_phone,          name='edit_phone'),
    path('verify-phone/',  views.verify_phone_update, name='verify_phone_update'),
    path('edit-email/',    views.edit_email,          name='edit_email'),
    path('otp-status/', views.otp_status, name='otp_status'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('verify-email/',  views.verify_email_update, name='verify_email_update'),
    path('security/',      views.security_settings,   name='security_settings'),
    path('signup/profile/', views.signup_profile,      name='signup_profile'),
    path('signup/password/', views.create_password,    name='create_password'),
    path('signup/verify/', views.verify_signup_email, name='verify_signup_email'),
        # ── Password Reset ──────────────────────────────────────────
    path('password-reset/',
    auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        extra_email_context={},
        success_url=reverse_lazy('accounts:password_reset_done'),
    ),
    name='password_reset'),

    path('password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html',
        ),
        name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url=reverse_lazy('accounts:password_reset_complete'),  # ← fixes step 3→4
        ),
        name='password_reset_confirm'),

    path('reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html',
        ),
        name='password_reset_complete'),
    


]

