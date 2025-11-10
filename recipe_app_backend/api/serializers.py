from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from .models import Recipe


# PUBLIC_INTERFACE
class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        User = get_user_model()
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
        )


# PUBLIC_INTERFACE
class LoginSerializer(serializers.Serializer):
    """Serializer to validate username and password for login."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs.get("username"), password=attrs.get("password"))
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        attrs["user"] = user
        return attrs


# PUBLIC_INTERFACE
class UserSerializer(serializers.ModelSerializer):
    """Public user info serializer."""

    class Meta:
        model = get_user_model()
        fields = ("id", "username")


# PUBLIC_INTERFACE
class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model, includes author read-only info."""

    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "title",
            "description",
            "ingredients",
            "steps",
            "image_url",
            "author",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "author", "created_at", "updated_at")
