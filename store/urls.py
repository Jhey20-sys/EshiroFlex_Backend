from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token  # ✅ Token-based authentication

from .views import (
    ProductViewSet, CategoryViewSet, RegisterView, OrderViewSet, LogoutView, 
    CartViewSet, WishlistViewSet, PaymentViewSet, 
    UserViewSet, ProfileView, LoginView
)

# API Router
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'users', UserViewSet, basename='users')  # Ensure basename is set
router.register(r'orders', OrderViewSet)
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

# URL Patterns
urlpatterns = [
    path('', include(router.urls)), 
    
    # User Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),  # ✅ Token-based login
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # User Profile & Password Management
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Payments
    path("payments/", PaymentViewSet.as_view({"get": "list", "post": "create"}), name="payments"),
    path("payments/<int:pk>/", PaymentViewSet.as_view({"get": "retrieve"}), name="payment-detail"),
    path("payments/<int:pk>/refund/", PaymentViewSet.as_view({"post": "refund"}), name="payment-refund"),
]
