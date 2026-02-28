# views.py
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from django.db import transaction
from .models import *
from .Serializers import *

class LoginViewSet(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        print(f"LOGIN DEBUG: username={username}, password={password}")
        user = authenticate(username=username, password=password)
        if user:
            print(f"LOGIN DEBUG: Django auth user found: id={user.id}, is_staff={user.is_staff}")
            return Response({
                'message': 'Login successful', 
                'user_id': user.id, 
                'is_staff': user.is_staff,
                'token': 'dummy-token'
            }, status=status.HTTP_200_OK)
        else:
            print("LOGIN DEBUG: Django auth failed")
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterViewSet(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Registration successful',
                'user_id': user.id,
                'username': user.username,
                'token': 'dummy-token'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class SalesViewSet(viewsets.ModelViewSet):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # Get the product and requested quantity
                product_id = request.data.get('product')
                quantity = int(request.data.get('quantity', 0))
                
                # Check if product exists
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    return Response(
                        {'error': 'Product not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Check if enough stock is available
                if product.quantity < quantity:
                    return Response(
                        {'error': f'Insufficient stock. Available: {product.quantity}, Requested: {quantity}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Create the sale
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                
                # Update product stock
                product.quantity -= quantity
                product.save()
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # Get the existing sale
                instance = self.get_object()
                old_quantity = instance.quantity
                
                # Get new data
                product_id = request.data.get('product', instance.product_id)
                new_quantity = int(request.data.get('quantity', instance.quantity))
                
                # Check if product exists
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    return Response(
                        {'error': 'Product not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Calculate stock adjustment
                quantity_difference = new_quantity - old_quantity
                
                # Check if enough stock for the increase
                if quantity_difference > 0 and product.quantity < quantity_difference:
                    return Response(
                        {'error': f'Insufficient stock. Available: {product.quantity}, Needed: {quantity_difference}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Update the sale
                serializer = self.get_serializer(instance, data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                
                # Update product stock
                product.quantity -= quantity_difference
                product.save()
                
                return Response(serializer.data)
                
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # Get the sale
                instance = self.get_object()
                
                # Restore product stock
                product = instance.product
                product.quantity += instance.quantity
                product.save()
                
                # Delete the sale
                self.perform_destroy(instance)
                
                return Response(
                    {'message': 'Sale deleted and stock restored'}, 
                    status=status.HTTP_204_NO_CONTENT
                )
                
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer