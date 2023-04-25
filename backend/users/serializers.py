from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from djoser.serializers import UserSerializer, UserCreateSerializer
from recipes.models import Recipe
from .models import User, Subscribe


class MineCreateUserSerializers(UserCreateSerializer):
    """Сериализатор для модели User для регистрации"""
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password', )


class MineUserSerializer(UserSerializer):
    """Сериализотор для просмотра модели User"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user

        if user.is_anonymous:
            return False

        return Subscribe.objects.filter(user=user, author=obj).exists()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', )


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для короткого вывода рецепта"""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки на автора"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = SerializerMethodField(read_only=True)
    recipes = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, author):
        return author.recipes.count()

    def get_recipes(self, author):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data
