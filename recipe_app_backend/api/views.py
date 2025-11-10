from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status, permissions, generics, viewsets, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication

from .models import Recipe
from .serializers import (
    UserRegisterSerializer,
    LoginSerializer,
    RecipeSerializer,
)


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Allow unsafe methods only for the author; read-only for others/public.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, "author_id", None) == getattr(request.user, "id", None)


class DefaultPagination(PageNumberPagination):
    """Simple page-number pagination with a default page size."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# PUBLIC_INTERFACE
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health(request):
    """Health check endpoint."""
    return Response({"message": "Server is up!"})


# PUBLIC_INTERFACE
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def api_root(request):
    """
    Root endpoint listing available API routes.

    Returns a discoverable set of primary endpoints to help clients navigate.
    """
    return Response(
        {
            "health": "/api/health/",
            "docs": "/docs/",
            "redoc": "/redoc/",
            "auth": {
                "register": "/api/auth/register/",
                "login": "/api/auth/login/",
                "logout": "/api/auth/logout/",
            },
            "recipes": {
                "list": "/api/recipes/",
                "create": "/api/recipes/",
                "detail": "/api/recipes/{id}/",
                "update": "/api/recipes/{id}/",
                "delete": "/api/recipes/{id}/",
            },
        }
    )


# PUBLIC_INTERFACE
class RegisterView(generics.CreateAPIView):
    """Register a new user and return a token."""

    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        if resp.status_code == status.HTTP_201_CREATED:
            user = get_user_model().objects.get(pk=resp.data["id"])
            token, _ = Token.objects.get_or_create(user=user)
            resp.data = {"user": {"id": user.id, "username": user.username}, "token": token.key}
        return resp


# PUBLIC_INTERFACE
class LoginView(generics.GenericAPIView):
    """Login with username and password; returns auth token."""

    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"user": {"id": user.id, "username": user.username}, "token": token.key},
            status=status.HTTP_200_OK,
        )


# PUBLIC_INTERFACE
class LogoutView(generics.GenericAPIView):
    """Logout by deleting the user's token."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        Token.objects.filter(user=request.user).delete()
        return Response({"detail": "Logged out"}, status=status.HTTP_200_OK)


# PUBLIC_INTERFACE
class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet providing CRUD for recipes.

    - List and retrieve are public
    - Create/update/partial_update/destroy require authentication
    - Only the author can modify/delete a recipe
    - Supports filtering by title icontains and author username or id
    - Paginates results
    """

    queryset = Recipe.objects.select_related("author").all()
    serializer_class = RecipeSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "author__username"]
    ordering_fields = ["created_at", "title"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        title = self.request.query_params.get("title")
        author = self.request.query_params.get("author")
        if title:
            qs = qs.filter(title__icontains=title)
        if author:
            qs = qs.filter(Q(author__username__iexact=author) | Q(author__id__iexact=author))
        return qs
