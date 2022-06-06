from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


from django.conf import settings

from django.contrib.auth.models import User
from .models.product import Product, Review
from .models.order import Order, OrderItem, ShippingAddress


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only = True)
    _id = serializers.SerializerMethodField(read_only = True)
    isAdmin = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = User
        fields = ['id', '_id', 'username', 'email', 'name', 'isAdmin']

    def get__id(self, obj):                
        return obj.id

    def get_isAdmin(self, obj):
        return obj.is_staff

    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email
        return name


class UserSerializerWithToken(UserSerializer):
    tokens = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        # fields = '__all__'
        fields = ['id', '_id', 'username', 'email', 'name', 'isAdmin', 'tokens']

    def get_tokens(self, obj):
        refresh = RefreshToken.for_user(obj)
        access = RefreshToken.for_user(obj).access_token

        tokens = {
            "refresh": str(refresh),
            "access": str(access)
        }
        return tokens




class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = '__all__'



class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = '__all__'



class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'



class OrderSerializer(serializers.ModelSerializer):                        
    orderItems = serializers.SerializerMethodField(read_only = True)
    shippingAddress = serializers.SerializerMethodField(read_only = True)
    user = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = Order
        fields = '__all__'


    def get_orderItems(self, obj):                              
        items = obj.orderitem_set.all()                         
        serializer = OrderItemSerializer(items, many = True)    
        return serializer.data                                  

    def get_shippingAddress(self, obj):                         
        try:
            address = ShippingAddressSerializer(obj.shippingaddress, many = False).data    
        except:
            address = False                                     
        return address                                         

    def get_user(self, obj):                                    
        user = obj.user                                         
        serializer = UserSerializer(user, many=False)           
        return serializer.data                                 



