import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from api.serializers.users import CustomUserSerializer
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart, Tag
)


class Base64ImageField(serializers.ImageField):
    """Кастомное поле кодирования изображения в base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='img.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор работы с ингредиентами."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('__all__',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор работы с тегами."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('__all__',)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор добавления/удаления рецепта в избранное."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user, recipe = data['user'], data['recipe']
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'error': 'Вы уже добавили этот рецепт в избранное'}
            )
        return data

    def to_representation(self, instance):
        context = {'request': self.context['request']}
        serializer = RecipeInfoSerializer(
            instance=instance.recipe,
            context=context
        )
        return serializer.data


class RecipeInfoSerializer(serializers.ModelSerializer):
    """Сериализатор отображения краткой информации о рецепте."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(FavoriteSerializer):
    """Сериализатор добавления/удаления рецепта в список покупок."""
    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart

    def validate(self, data):
        user, recipe = data['user'], data['recipe']
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'error': 'Вы уже добавили этот рецепт в список покупок'}
            )
        return data


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор описания ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', read_only=True)
    name = serializers.CharField(
        source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиента в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта.
    Валидирует ингредиенты ответ возвращает GetRecipeSerializer."""
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = AddIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def validate(self, data):
        ingredients = [item['ingredient'] for item in data['ingredients']]
        all_ingredients, unique_ingredients = (
            len(ingredients), len(set(ingredients)))

        if all_ingredients != unique_ingredients:
            raise serializers.ValidationError(
                {'error': 'Ингредиенты должны быть уникальными'}
            )
        return data

    def get_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            ) for ingredient in ingredients)

    def create(self, validated_data):
        user = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        self.get_ingredients(recipe, ingredients)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        RecipeIngredient.objects.filter(recipe=instance).delete()

        instance.tags.set(tags)
        self.get_ingredients(instance, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        context = {'request': self.context['request']}
        return GetRecipeSerializer(instance, context=context).data


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор отображения полной информации о рецепте."""
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(read_only=True, many=True,
                                             source='recipe_ingredient')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, object):
        request = self.context['request']
        if (not request) or (not request.user):
            return False
        user = request.user
        if user.is_anonymous:
            return False
        return object.favorite.filter(user=user).exists()

    # def get_is_favorite(self, obj):
    #     return FavoriteRecipe.objects.exist(user=user, recipe=resipe)
        # return Recipe.objects.filter(favorite__user=user)

    def get_is_in_shopping_cart(self, object):
        request = self.context['request']
        if (not request) or (not request.user):
            return False
        user = request.user
        if user.is_anonymous:
            return False
        return object.shopping_cart.filter(user=user).exists()
