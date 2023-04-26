from typing import Optional

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Exists, OuterRef

User = get_user_model()


class Tag(models.Model):
    """Модель тега"""
    name = models.CharField(
        max_length=50,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет',
        validators=[RegexValidator(regex=r'^#([A-Fa-f0-9]{6})$')]
    )
    slug = models.SlugField(
        max_length=30,
        verbose_name='Слаг',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingridient(models.Model):
    """Модель ингридиента"""
    name = models.CharField(
        max_length=50,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Мера измерения'
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class RecipeQueryset(models.QuerySet):

    def add_user_annotations(self, user_id: Optional[int]):
        return self.annotate(
            is_favorite=Exists(
                Favorite.objects.filter(
                    user_id=user_id, recipe_pk=OuterRef('pk')
                )
            ),
        )


class Recipe(models.Model):
    """Модель рецепта"""
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingridients = models.ManyToManyField(
        Ingridient,
        through='IngridientInRecipe',
        through_fields=('recipe', 'ingridient'),
        related_name='recipes',
        verbose_name='Ингридиенты в рецепте',
    )
    text = models.TextField(
        verbose_name='Рецепт приготовления'
    )
    image = models.ImageField(
        verbose_name='Фото готовой еды',
        upload_to='recipes/image/'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        through_fields=('recipe', 'tag'),
        related_name='recipes',
        verbose_name='Тег рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления'
    )

    objects = RecipeQueryset.as_manager()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngridientInRecipe(models.Model):
    """Модель ингридиента в рецепте"""
    amount = models.PositiveIntegerField(
        verbose_name='Количество'
    )
    ingridient = models.ForeignKey(
        Ingridient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Ингридиент в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'

    def __str__(self):
        return f'{self.ingridient} в {self.recipe}'


class TagRecipe(models.Model):
    """Тег в рецепте"""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.tag}{self.recipe}'


class Favorite(models.Model):
    """Модель избранного рецепта"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_user_recipe'
            )
        ]
        verbose_name = 'Объект избранного'
        verbose_name_plural = 'Объекты избранного'

    def __str__(self):
        return f'Избранный {self.recipe} {self.user}'


class ShoppingList(models.Model):
    """Модель списка покупок"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shoppinglist_user_recipe'
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
