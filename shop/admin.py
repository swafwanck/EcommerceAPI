from django.contrib import admin
from .models import Users , Product , Cart

class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'role')
    search_fields = ('user__username', 'name')
    list_filter = ('role',)
    ordering = ('user__username',)

admin.site.register(Users, UserAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'vendor')
    search_fields =('name', 'price','vendor')
    list_filter = ('price',)
    

admin.site.register(Product, ProductAdmin) 



class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'product_id', 'product_name', 'product_price', 'quantity', 'total_price')
    search_fields = ('customer__username', 'product__name')
    list_filter = ('product',) 
    ordering = ('-id',)


admin.site.register(Cart, CartAdmin)