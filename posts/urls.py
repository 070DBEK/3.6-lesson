from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    TagViewSet,
    PostViewSet,
    CommentViewSet,
    PostLikeViewSet,
    ReplyCommentView,
    CategoryPosts,
    TagPosts,
    AuthorPosts,
    LikePostView
)


router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'likes', PostLikeViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('comments/<int:parent_id>/replies/', ReplyCommentView.as_view(), name='comment-reply'),
    path('tags/<slug:slug>/posts/', TagPosts.as_view(), name='tag-posts'),
    path('users/<str:username>/posts/', AuthorPosts.as_view(), name='author-posts'),
    path('posts/<slug:slug>/like/', LikePostView.as_view(), name='post-like-toggle'),
    path('categories/<slug:slug>/posts/', CategoryPosts.as_view(), name='category-posts'),
]
