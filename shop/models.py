from django.contrib.auth.models import User
from django.db import models

class Users(models.Model):
    ROLE_CHOICES = (
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Customer')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Users'



class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8 , decimal_places=2)
    vendor = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name


class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    vendor = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='carts')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


    def __str__(self):
        return self.product.name

    @property
    def product_name(self):
        return self.product.name

    @property
    def product_price(self):
        return self.product.price
