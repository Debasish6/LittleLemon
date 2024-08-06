from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order,OrderItem,Booking
from django.contrib.auth.models import User

class CategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','title']

class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = MenuItem
        fields = ['id','title','price','featured','category','category_id']

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields ='__all__'
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class CartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Cart
        fields = ['id','user','menuitem','quantity','unit_price','price']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id','menuitem','quantity','unit_price','price']
        
class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(read_only = True, many = True)
    class Meta:
        model = Order
        fields = ['id','user','delivery_crew','status','order_items','total','date']

class OrderDetailSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(read_only = True, many = True)
    class Meta:
        model = Order
        fields = ['order_items', ]