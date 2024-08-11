from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Users , Product, Cart

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Users
        fields = ['user', 'role', 'name']

    
class ProductSerializer(serializers.ModelSerializer):

    vendor = serializers.ReadOnlyField(source='vendor.name')

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'vendor']
        read_only_fields = ['vendor'] 
    


class CartSerializer(serializers.ModelSerializer):
    customer = serializers.ReadOnlyField(source='customer.username')
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')

    class Meta:
        model = Cart
        fields = ['id', 'customer','product_id','product_name', 'product_price', 'quantity','total_price',]