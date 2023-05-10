from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from api.views.users import CustomUserViewSet
from api.views.recipes import IngredientViewSet, TagViewSet


router_v1 = DefaultRouter()
router_v1.register(r'users', CustomUserViewSet)
router_v1.register(r'ingredients', IngredientViewSet)
# router_v1.register(r'recipes', RecipeViewSet)
router_v1.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
    # path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
