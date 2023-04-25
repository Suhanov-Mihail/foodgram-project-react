from django.contrib import admin

from recipes.models import (Tag, Ingridient, IngridientInRecipe,
                            Recipe, Favorite, ShoppingList)


class RecipeIngredientsInline(admin.TabularInline):

    model = IngridientInRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    list_display = [
        'pk', 'name', 'author', 'text', 'cooking_time']
    search_fields = ['name', 'author', 'cooking_time', 'text']
    list_filter = ['name', 'author', 'tags']
    empty_value_display = '-empty-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = ['pk', 'name', 'color', 'slug']
    search_fields = ['name', 'color', 'slug']


@admin.register(Ingridient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = ['pk', 'name', 'measurement_unit']
    search_fields = ['name', 'measurement_unit']
    list_filter = ['name', 'measurement_unit']


@admin.register(IngridientInRecipe)
class IngridientInRecipeAdmin(admin.ModelAdmin):

    list_display = ['pk', 'recipe', 'ingridient', 'amount']
    search_fields = ['recipe', 'ingridient']
    list_filter = ['recipe', 'ingridient']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):

    list_display = ['pk', 'user', 'recipe']
    search_fields = ['user', 'recipe']
    list_filter = ['user', 'recipe']


@admin.register(ShoppingList)
class ShoppingCartAdmin(admin.ModelAdmin):

    list_display = ['pk', 'user', 'recipe']
    search_fields = ['user', 'recipe']
    list_filter = ['user', 'recipe']
