from django.contrib.auth import get_user_model
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (Favorite, Ingridient, IngridientInRecipe,
                            Recipe, Tag, ShoppingList)
from users.serializers import MineUserSerializer


User = get_user_model()


class IngridientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов"""

    class Meta:
        model = Ingridient
        fields = ['id', 'name', 'measurement_unit']


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэга"""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class RecipeIngridientsSerializer(serializers.ModelSerializer):
    """Ингридиент в рецепте"""
    name = serializers.StringRelatedField(
        source='ingridient.name'
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingridient.measurement_unit'
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingridient',
        queryset=Ingridient.objects.all()
    )

    class Meta:
        model = IngridientInRecipe
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeListSerializer(serializers.ModelSerializer):
    """Получение рецепта"""
    ingridients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    author = MineUserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingridients(self, obj):
        return RecipeIngridientsSerializer(
            IngridientInRecipe.objects.filter(recipe=obj).all(), many=True
        ).data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(user=user, recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingridients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time', )


class IngridientCreateRecipeSerializez(serializers.ModelSerializer):
    """Сериализатор для ингридиентов при создании рецепта"""
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='ingridient',
        queryset=Ingridient.objects.all()
    )
    amount = serializers.IntegerField(
        write_only=True,
        min_value=1
    )

    class Meta:
        model = IngridientInRecipe
        fields = ['recipe', 'id', 'amount']


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов"""
    author = MineUserSerializer(read_only=True)
    ingridients = serializers.PrimaryKeyRelatedField(
        queryset=Ingridient.objects.all(),
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()
    author = MineUserSerializer(read_only=True)

    def validated_data(self, value):
        if len(value) < 1:
            raise serializers.ValidationError(
                'Необходимо добавить минимум один ингридиент')
        return value

    def create(self, validated_data):
        ingridients = validated_data.pop('ingridients')
        recipe = Recipe.objects.create(**validated_data)

        create_ingridients = [
            IngridientInRecipe(
                recipe=recipe,
                ingridient=ingridient['ingridient'],
                amount=ingridient['amount']
            )
            for ingridient in ingridients
        ]
        IngridientInRecipe.objects.bulk_create(
            create_ingridients
        )
        return recipe

    def update(self, instance, validated_data):
        ingridients = validated_data.pop('ingridients', None)
        if ingridients is not None:
            instance.ingridients.clear()

            create_ingridients = [
                IngridientInRecipe(
                    recipe=instance,
                    ingridient=ingridient['ingridient'],
                    amount=ingridient['amount']
                )
                for ingridient in ingridients
            ]
        IngridientInRecipe.objects.bulk_create(
            create_ingridients
        )
        return super().update(instance, validated_data)

    def to_representation(self, obj):
        """Возвращаем прдеставление в таком же виде, как и GET-запрос."""
        self.fields.pop('ingridients')
        representation = super().to_representation(obj)
        representation['ingridients'] = RecipeIngridientsSerializer(
            IngridientInRecipe.objects.filter(recipe=obj).all(), many=True
        ).data
        return representation

    class Meta:
        model = Recipe
        fields = ('ingridients', 'tags', 'image', 'name',
                  'text', 'cooking_time', 'author', )


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор избранного рецепта"""
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        if Favorite.objects.filter(user=user,
                                   recipe__id=recipe_id).exists():
            raise ValidationError(
                'Рецепт уже добавлен в избранное!'
            )
        return data


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок"""
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        if ShoppingList.objects.filter(user=user,
                                       recipe__id=recipe_id).exists():
            raise ValidationError(
                'Рецепт уже добавлен в корзину!'
            )
        return data
