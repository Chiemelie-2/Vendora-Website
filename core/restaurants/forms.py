from django import forms
from .models import MenuItem, Restaurant, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'image', 'category_group', 'item_type']
        labels = {
            'category_group': 'Food Category (e.g. Pizza, Burger)',
            'item_type': 'Meal Type (Main/Side/Drink)'
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class RestaurantRegistrationForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = [
            'name',           # Step 1 — Business info
            'description',    # Step 1 — Business info
            'business_email', # Step 1 — Business info
            'phone_number',   # Step 1 — Business info
            'address',        # Step 2 — Location
            'post_code',      # Step 2 — Location
            'logo',           # Step 3 — Store branding
            'cover_image',    # Step 3 — Store branding
            'image',          # General restaurant image
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Step 1 — only these are required upfront
        self.fields['name'].required = True
        self.fields['business_email'].required = True
        self.fields['phone_number'].required = True

        # Step 2 — filled later in location step
        self.fields['description'].required = False
        self.fields['address'].required = False
        self.fields['post_code'].required = False

        # Step 3 — filled later in branding step
        self.fields['logo'].required = False
        self.fields['cover_image'].required = False
        self.fields['image'].required = False