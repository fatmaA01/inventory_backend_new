from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class SalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sales
        fields = '__all__'  

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    Password = serializers.CharField(write_only=True, required=False)  # Handle both field names
    
    class Meta:
        model = User
        fields = ['username', 'password', 'Password', 'email', 'name', 'phone', 'address', 'role']
        extra_kwargs = {
            'email': {'required': False},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('Password', None)  # Remove if exists
        
        if not password:
            raise serializers.ValidationError({'password': 'Password is required'})
        
        user = User(**validated_data)
        user.set_password(password)  # Hash the password
        if not user.role:
            user.role = 'customer'  # Default role
        user.save()
        return user

