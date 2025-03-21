from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Post, Comment, PostLike, Tag, Category
from .serializers import PostSerializer, CommentSerializer, PostLikeSerializer, TagSerializer, CategorySerializer
from .permissions import (
    IsAdminOrReadOnly,
    IsPostAuthorOrAdminOrReadOnly,
    IsCommentAuthorOrPostAuthorOrAdmin,
    IsLikeOwnerOrReadOnly,
    IsAdminOnly
)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsPostAuthorOrAdminOrReadOnly]

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthorOrPostAuthorOrAdmin]

class PostLikeViewSet(viewsets.ModelViewSet):
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = [IsAuthenticated, IsLikeOwnerOrReadOnly]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminOnly()]
