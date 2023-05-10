from rest_framework import filters
from recipes.models import Ingredient


class IngredientSearch(filters.SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)