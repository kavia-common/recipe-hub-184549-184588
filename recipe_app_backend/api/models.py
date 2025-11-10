from django.db import models
from django.contrib.auth import get_user_model


class Recipe(models.Model):
    """
    Represents a recipe created by a user.

    Fields:
    - title: short title of the recipe
    - description: a brief overview of the recipe
    - ingredients: newline-separated list or JSON-like text of ingredients
    - steps: instructions for preparing the recipe
    - image_url: optional URL to an image
    - author: FK to auth.User, the creator
    - created_at, updated_at: timestamps
    """
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    ingredients = models.TextField(help_text="List ingredients, one per line or JSON-like text.")
    steps = models.TextField(help_text="Cooking steps and instructions.")
    image_url = models.URLField(blank=True, null=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="recipes")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} by {self.author}"
