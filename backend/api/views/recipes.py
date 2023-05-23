from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen.canvas import Canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientSearch, RecipeFilter
from api.paginations import LimitPageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers.recipes import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer
)
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет обработки запросов получения ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearch,)
    search_fields = ('^name',)
    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет обработки запросов получения тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет обработки запросов рецептов.
    Создание/получение/редактирование/удаление рецептов.
    Добавление/удаление рецепта в избранное и список покупок.
    Скачивание файла со списком покупок."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitPageNumberPagination

    def action_post_delete(self, pk, serializer_class):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object = serializer_class.Meta.model.objects.filter(
            user=user,
            recipe=recipe
        )

        if self.request.method == 'POST':
            serializer = serializer_class(
                data={'user': user.id, 'recipe': pk},
                context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if object.exists():
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Этого рецепта не было в cписке'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        """Добавляет/удалет рецепт в избранное."""
        return self.action_post_delete(pk, FavoriteSerializer)

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk):
        """Добавляет/удалет рецепт в список покупок."""
        return self.action_post_delete(pk, ShoppingCartSerializer)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Загружает файл .pdf со списком покупок."""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            "attachment; filename='shopping_cart.pdf'"
        )
        canvas = Canvas(response)
        font_arial = ttfonts.TTFont('Arial', 'data/arial.ttf')
        pdfmetrics.registerFont(font_arial)
        canvas.setFont('Arial', 14)

        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values_list(
            'ingredient__name',
            'amount',
            'ingredient__measurement_unit'
        )

        shopping_list = {}
        for name, amount, unit in ingredients:
            if name not in shopping_list:
                shopping_list[name] = {'amount': amount, 'unit': unit}
            else:
                shopping_list[name]['amount'] += amount
        height = 700

        canvas.drawString(100, 750, 'Список покупок')
        for number, (name, data) in enumerate(shopping_list.items(), start=1):
            canvas.drawString(
                80,
                height,
                f"{number}. {name} – {data['amount']} {data['unit']}"
            )
            height -= 25
        canvas.showPage()
        canvas.save()
        return response
