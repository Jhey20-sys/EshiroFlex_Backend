from django.contrib import admin
from .models import Product, Category, User  # Import all necessary models
from django.contrib import admin
from .models import Cart

admin.site.register(Cart)
# Register models to be manageable in the Django Admin Panel
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(User)  # Register User model if using a custom one
