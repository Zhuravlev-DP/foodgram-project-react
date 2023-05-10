from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from api.serializers.recipes import IngredientSerializer, TagSerializer
from recipes.models import Ingredient, Tag
from api.filters import IngredientSearch



class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearch,)
    search_fields = ('^name',)
    permission_classes = (AllowAny,)
    pagination_class = None

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None