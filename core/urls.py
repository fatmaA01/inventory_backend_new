from django.urls import path, include
from rest_framework import routers
from .views import *


router = routers.DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'sales', SalesViewSet)
router.register(r'user', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginViewSet.as_view(), name='login'),
    path('login', LoginViewSet.as_view(), name='login_no_slash'),
]