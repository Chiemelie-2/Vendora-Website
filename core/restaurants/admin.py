from django.contrib import admin
from .models import Restaurant, Category, MenuItem

# Register your models here.
# Register them all so they appear in the dashboard


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status', 'is_active')
    list_filter = ('status',)
    search_fields = ('name',)
    list_editable = ('status',) # Allows you to approve/reject directly from the list!

admin.site.register(Restaurant, RestaurantAdmin)

admin.site.register(Category)
admin.site.register(MenuItem)
