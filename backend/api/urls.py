from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from api.views.users import CustomUserViewSet


router_v1 = DefaultRouter()
router_v1.register(r'users', CustomUserViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
    # path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
