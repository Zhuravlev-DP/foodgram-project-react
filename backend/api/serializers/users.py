from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from users.models import User, Follow

class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request_user = self.context.get('request').user
        if request_user.is_anonymous:
            return False
        return Follow.objects.filter(user=request_user, author=obj.id).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password')
        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, username):
        """Проверка на создание пользователя ME."""
        if username == 'me':
            raise serializers.ValidationError(
                'Пользователя с username = me нельзя создавать.',
                code=status.HTTP_400_BAD_REQUEST
            )
        return username


class FollowSerializer(CustomUserSerializer):
    # recipes = serializers.SerializerMethodField(read_only=True)
    # recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields
        # + ('recipes', 'recipes_count')

    # def get_recipes(self, obj):
    #     from api.serializers.recipes import RecipeInfoSerializer

    #     request = self.context.get('request')
    #     context = {'request': request}
    #     recipes_limit = request.query_params.get('recipes_limit')
    #     queryset = obj.recipes.all()
    #     if recipes_limit:
    #         queryset = queryset[:int(recipes_limit)]
    #     return RecipeInfoSerializer(queryset, context=context, many=True).data

    # def get_recipes_count(self, obj):
    #     return obj.recipes.count()