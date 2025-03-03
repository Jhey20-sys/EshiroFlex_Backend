from django.contrib import admin
from .models import Product, Category, User, Order, Cart, Wishlist, Payment, Profile  

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(User)  
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(Payment)
admin.site.register(Profile)