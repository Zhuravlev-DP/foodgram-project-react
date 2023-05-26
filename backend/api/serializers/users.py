from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status

from users.models import User, Follow


class CustomUserSerializer(UserSerializer):
    """Сериализатор отображения информации о пользователе."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, object):
        """Проверка подписан ли пользователь на автора."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user,
            author=object.id
        ).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор обработки запросов создания пользователя."""
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, username):
        """Валидация создание пользователя с юзернеймом 'me'."""
        if username == 'me':
            raise serializers.ValidationError(
                'Пользователя с username = me нельзя создавать.',
                code=status.HTTP_400_BAD_REQUEST
            )
        return username


class FollowSerializer(CustomUserSerializer):
    """Сериализатор добавления/удаления подписки, просмотра подписок."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        """Получить рецепты."""
        from api.serializers.recipes import RecipeInfoSerializer

        request = self.context.get('request')
        context = {'request': request}
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = obj.recipes.all()
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return RecipeInfoSerializer(queryset, context=context, many=True).data

    def get_recipes_count(self, obj):
        """Получить количество рецептов."""
        return obj.recipes.count()
