from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LoginView,LogoutView, ProductViewSet, CartViewSet

router = DefaultRouter()
router.register(r'shop', UserViewSet)
router.register(r'products', ProductViewSet)
router.register(r'carts', CartViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),

]
