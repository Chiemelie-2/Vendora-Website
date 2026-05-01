# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from restaurants.models import Category

class VendorRegistrationForm(forms.ModelForm):
    # Field for the person's name
    full_name = forms.CharField(max_length=150, label="Full Name")
    # Field for the business name (which becomes the Username)
    business_name = forms.CharField(max_length=100, label="Business Name")
    
    password = forms.CharField(widget=forms.PasswordInput)
    address = forms.CharField(max_length=255)
    phone_number = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = ['email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        # Set Business Name as the Username
        user.username = self.cleaned_data['business_name']
        # Set Full Name as the First Name
        user.first_name = self.cleaned_data['full_name']
        user.set_password(self.cleaned_data["password"])
        
        if commit:
            user.save()
        return user



# class RoleSignupForm(UserCreationForm):
#     ROLE_CHOICES = [
#         ('customer', 'Customer'),
#         ('vendor', 'Vendor'),
#     ]
#     role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="I want to join as a:")

#     class Meta(UserCreationForm.Meta):
#         model = User
#         fields = UserCreationForm.Meta.fields + ('email',)

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         if commit:
#             user.save()
#             role = self.cleaned_data.get('role')
#             profile, created = Profile.objects.get_or_create(user=user)
#             profile.role = role
#             profile.save()
#         return user


# accounts/forms.py
class RoleSignupForm(UserCreationForm):
    # Add the Full Name field
    full_name = forms.CharField(max_length=100, required=True, label="Full Name")
    
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="I want to join as a:")

    class Meta(UserCreationForm.Meta):
        model = User
        # Include 'full_name' in the fields
        fields = UserCreationForm.Meta.fields + ('full_name', 'email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Split full_name into first and last name for the User model
        full_name = self.cleaned_data.get('full_name')
        name_parts = full_name.split(' ', 1)
        user.first_name = name_parts[0]
        user.last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        if commit:
            user.save()
            role = self.cleaned_data.get('role')
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()
        return user



class PersonalInfoForm(forms.ModelForm):
    """
    Used only for profile image upload on the personal_info page.
    Phone and Email each have their own dedicated edit pages/views.
    """
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'id': 'id_profile_image'})
    )
    
     # Add Username field here
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'editable-input', 'placeholder': 'Enter new username'}),
    )

    class Meta:
        model = User
        fields = ['username']  # No User model fields — only profile image handled here

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['username'].initial = self.instance.username
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['profile_image'].initial = self.instance.profile.profile_image
            
    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username=username).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This username is already taken.")
        return username
    
    
    
