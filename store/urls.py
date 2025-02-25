from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, UserViewSet  # Import UserViewSet

# API Router
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'users', UserViewSet)  # Register users API

urlpatterns = [
    path('', include(router.urls)),  # Ensures all endpoints are under "/api/"
]
