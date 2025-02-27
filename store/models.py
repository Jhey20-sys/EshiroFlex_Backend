from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser

# Custom User Model (if needed)
class User(AbstractUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['username'] 

    def __str__(self):
        return self.email
    
# Category Model
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

# Product Model
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default="No description available")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null = False, related_name="products")
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name
