from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views.recipes import IngredientViewSet, RecipeViewSet, TagViewSet
from api.views.users import CustomUserViewSet


router_v1 = DefaultRouter()
router_v1.register(r'users', CustomUserViewSet)
router_v1.register(r'ingredients', IngredientViewSet)
router_v1.register(r'recipes', RecipeViewSet)
router_v1.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
