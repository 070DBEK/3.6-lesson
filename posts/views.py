import logging
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly

from .models import Post, Comment, PostLike, Tag, Category
from command.pagination import CustomPagination
from .serializers import (
    PostSerializer, CommentSerializer, PostLikeSerializer,
    TagSerializer, CategorySerializer
)
from .permissions import (
    IsAdminOrReadOnly,
    IsPostAuthorOrAdminOrReadOnly,
    IsCommentAuthorOrPostAuthorOrAdmin,
    IsLikeOwnerOrReadOnly,
    IsAdminOnly
)

logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminOnly()]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        return [IsPostAuthorOrAdminOrReadOnly()]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.all()
        slug = self.request.query_params.get('post_slug')
        if slug:
            post = get_object_or_404(Post, slug=slug)
            queryset = queryset.filter(post=post)
        return queryset

    def perform_create(self, serializer):
        slug = self.request.data.get('slug', None)
        parent_id = self.request.data.get('parent', None)
        if slug:
            post = get_object_or_404(Post, slug=slug)
        else:
            post = None
        parent_comment = None
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
        serializer.save(author=self.request.user, post=post, parent=parent_comment)


class ReplyCommentView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, parent_id):
        parent_comment = get_object_or_404(Comment, id=parent_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, parent=parent_comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostLikeViewSet(viewsets.ModelViewSet):
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = [IsAuthenticated, IsLikeOwnerOrReadOnly]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class AuthorPosts(APIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        posts = Post.objects.filter(author=user)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class CategoryPosts(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(category=category)


class TagPosts(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Post.objects.filter(tags=tag)


class LikePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        value = request.data.get("value")
        if value not in ["like", "dislike"]:
            return Response({"error": "Invalid value. Use 'like' or 'dislike'."}, status=400)

        like, created = PostLike.objects.get_or_create(user=request.user, post=post)
        if not created:
            if like.value == value:
                like.delete()
                return Response({"message": "Reaction removed"}, status=200)
            like.value = value
            like.save()
            serializer = PostLikeSerializer(like)
            return Response({"message": f"Reaction changed to {value}", "data": serializer.data}, status=200)

        like.value = value
        like.save()
        serializer = PostLikeSerializer(like)
        return Response({"message": f"{value} added", "data": serializer.data}, status=201)
