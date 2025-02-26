from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser

# Custom User Model
class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'  # Allows logging in with email instead of username
    REQUIRED_FIELDS = ['username']  # Keeps 'username' required but not for login

    def __str__(self):
        return self.email

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

# Shoe Size Model
class ShoeSize(models.Model):
    size = models.CharField(max_length=10, unique=True)  # Example: "US 9", "EU 42", "UK 8"

    def __str__(self):
        return self.size

# Product Model
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default="No description available")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    shoe_sizes = models.ManyToManyField(ShoeSize, related_name="products")  # ✅ Allow multiple shoe sizes
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

# Cart Model
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")  
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")  
    number_of_items = models.PositiveIntegerField(default=1)  
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # ✅ Remove blank/null
    image_url = models.URLField(max_length=500, blank=True, null=True)  
    description = models.TextField()  
    product_size = models.ForeignKey(ShoeSize, on_delete=models.CASCADE, related_name="cart_items")  # ✅ Reference ShoeSize
    created_at = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        if self.product:  
            self.image_url = self.product.image_url  
            self.description = self.product.description  
            self.total_price = self.product.price * self.number_of_items  # Auto-calculate total price
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.number_of_items}) - Size: {self.product_size}"
