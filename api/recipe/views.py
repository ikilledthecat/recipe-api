from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient

from recipe.serializers import TagSerializer, IngredientSerializer


class ListAPIViewSet(
        viewsets.GenericViewSet,
        mixins.ListModelMixin,
        mixins.CreateModelMixin):
    """List viewset with create and list end points"""
    pass


class BaseSecurity:
    """Common security config"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class DefaultUserQuerySet:
    """Common operations using querysets"""

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new tag"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseSecurity, DefaultUserQuerySet, ListAPIViewSet):
    """Manage Tags in database"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BaseSecurity, DefaultUserQuerySet, ListAPIViewSet):
    """Manage Tags in database"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
