
from rest_framework import viewsets, status
from rest_framework.response import Response


from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken , AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

import requests
import logging
from django.urls import reverse
from rest_framework.request import Request



from .models import Users , Product , Cart
from .serializers import UserProfileSerializer , UserSerializer, ProductSerializer ,CartSerializer

logger = logging.getLogger(__name__)





class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request: Request, *args, **kwargs):
        name = request.data.get('name')
        email = request.data.get('email')
        role = request.data.get('role','Customer')
        password = request.data.get('password')
        username = request.data.get('username')
        
        if not name or not email or not password or not username:
            return Response({'error': 'Please provide name, email, username, and password'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'error': 'A user with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, password=password, email=email)
        customer = Users.objects.create(user=user, name=name, role=role)
        
        login_url = request.build_absolute_uri(reverse('token_obtain_pair'))
        
        return Response({
            'id': customer.user.id,
            'name': customer.name,
            'email': customer.user.email,
            'role': customer.role,
            'login_url': login_url
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_staff:
            return Response({
                'error': "You cannot edit this profile."
            }, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_staff:
            return Response({
                'error': "You cannot delete this profile."
            }, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({"message": "Logged out successfully."}, status=status.HTTP_204_NO_CONTENT)
        
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


    def perform_create(self, serializer):
        user = self.request.user
        try:
            vendor_profile = Users.objects.get(user=user)
            if vendor_profile.role != 'Vendor':
                raise PermissionDenied("You can't create the product. Only vendors can create products.")
            serializer.save(vendor=vendor_profile)

        except Users.DoesNotExist:
            logger.error("User does not exist: %s", user)
            raise PermissionDenied("User does not exist or is not a vendor.")

        except PermissionDenied as e:
            raise e

        except Exception as e:
            logger.error("Unexpected error: %s", str(e))
            raise Exception("Unexpected error occurred.")

    def update(self, request, *args, **kwargs):
        user = request.user
        if not self._is_vendor(user):
            return Response({"error": "Only vendors can update products."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if not self._is_vendor(user):
            return Response({"error": "Only vendors can delete products."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def _is_vendor(self, user):
        try:
            vendor_profile = Users.objects.get(user=user)
            return vendor_profile.role == 'Vendor'
        except Users.DoesNotExist:
            return False



class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user)

    def create(self, request, *args, **kwargs):
        if not self._is_customer(request.user):
            return Response({'error': 'Only customers can add items to the cart.'}, status=status.HTTP_403_FORBIDDEN)

        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        total_price = product.price * quantity

        cart_item, created = Cart.objects.get_or_create(
            customer=request.user,
            product=product,
            defaults={'vendor': product.vendor}
        )
        cart_item.quantity = quantity
        cart_item.total_price = total_price
        cart_item.vendor = product.vendor 
        cart_item.save()

        serializer = CartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if not self._is_customer(request.user):
            return Response({'error': 'Only customers can update items in the cart.'}, status=status.HTTP_403_FORBIDDEN)

        quantity = int(request.data.get('quantity'))
        product_id = kwargs.get('pk')

        try:
            cart_item = Cart.objects.get(customer=request.user, product__id=product_id)
            cart_item.quantity = quantity
            cart_item.total_price = cart_item.product.price * quantity
            cart_item.save()
        except Cart.DoesNotExist:
            return Response({'error': 'Product not in cart.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if not self._is_customer(request.user):
            return Response({'error': 'Only customers can remove items from the cart.'}, status=status.HTTP_403_FORBIDDEN)

        cart_id = kwargs.get('pk')

        try:
            cart_item = Cart.objects.get(pk=cart_id, customer=request.user)
            cart_item.delete()
        except Cart.DoesNotExist:
            return Response({'error': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'Product removed from cart.'}, status=status.HTTP_204_NO_CONTENT)

    def _is_customer(self, user):
        try:
            user_profile = Users.objects.get(user=user)
            return user_profile.role == 'Customer'
        except Users.DoesNotExist:
            return False