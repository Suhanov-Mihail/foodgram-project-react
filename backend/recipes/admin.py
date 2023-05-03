from django.contrib import admin

from recipes.models import (Tag, TagRecipe, Ingredient, IngredientInRecipe,
                            Recipe, Favorite, ShoppingList)


class RecipeIngredientsInline(admin.TabularInline):

    model = IngredientInRecipe
    extra = 1


class RecipeTagInLine(admin.TabularInline):

    model = TagRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    list_display = [
        'pk', 'name', 'author', 'text', 'cooking_time']
    search_fields = ['name', 'author', 'cooking_time', 'text']
    list_filter = ['name', 'author', 'tags']
    empty_value_display = '-empty-'
    inlines = [RecipeIngredientsInline, RecipeTagInLine]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = ['pk', 'name', 'color', 'slug']
    search_fields = ['name', 'color', 'slug']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = ['pk', 'name', 'measurement_unit']
    search_fields = ['name', 'measurement_unit']
    list_filter = ['name', 'measurement_unit']


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):

    list_display = ['pk', 'recipe', 'ingredient', 'amount']
    search_fields = ['recipe', 'ingredient']
    list_filter = ['recipe', 'ingredient']


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
