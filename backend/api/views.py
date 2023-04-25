from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.response import Response

from recipes.models import (Ingridient, Tag, Recipe,
                            Favorite, ShoppingList, IngridientInRecipe)
from users.serializers import RecipeShortSerializer
from .filters import RecipeFilter
from .serializers import (IngridientSerializer, TagSerializer,
                          RecipeCreateUpdateSerializer, RecipeListSerializer)
from .permissions import IsAuthorOrAdminPermissoin


class IngridientViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset для просмотра ингридиентовч"""
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['^name']


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset для просмотра тега"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset для рецептов"""
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrAdminPermissoin]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        """Добавление или удаление для списка избранного"""
        if request.method == 'POST':
            self.add_to(Favorite, request.user, pk)
        else:
            return self.remove_form(Favorite, request.user, pk)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        """Добавление или удаление для списка покупок"""
        if request.method == 'POST':
            self.add_to(ShoppingList, request.user, pk)
        else:
            return self.remove_form(ShoppingList, request.user, pk)

    def add_to(self, model, user, pk):
        """Метод для добавления."""
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_form(self, model, user, pk):
        """Метод для удаления."""
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачивание списка покупок"""
        shopping_cart = ShoppingList.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        buy_list = IngridientInRecipe.objects.filter(
            recipe__in=recipes).values(
            'ingredient').annotate(amount=Sum('amount'))
        buy_list_text = 'Список покупок с сайта Foodgram:\n\n'
        for item in buy_list:
            ingredient = Ingridient.objects.get(pk=item['ingredient'])
            amount = item['amount']
            buy_list_text += (
                f'{ingredient.name}, {amount} '
                f'{ingredient.measurement_unit}\n'
            )
        response = HttpResponse(buy_list_text, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )
        return response