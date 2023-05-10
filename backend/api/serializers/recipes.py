from rest_framework import serializers

from recipes.models import Ingredient, Tag

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        # read_only_fields = ('__all__',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        # read_only_fields = ('__all__',)