from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, UserViewSet, CartViewSet, add_to_cart, remove_from_cart

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'users', UserViewSet)  
router.register(r'cart', CartViewSet)  # Register cart API

# Define additional cart-related paths
urlpatterns = [
    path('', include(router.urls)),  # Includes all ViewSet routes
    path('cart/add/<int:product_id>/', add_to_cart, name='cart_add'),
    path('cart/remove/<int:cart_id>/', remove_from_cart, name='cart_remove'),
]
