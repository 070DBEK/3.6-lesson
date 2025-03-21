from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Tag, Post, Comment, PostLike


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    category = CategorySerializer()
    tags = TagSerializer(many=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'author', 'category', 'tags',
            'created_at', 'updated_at', 'status', 'featured_image', 'likes_count', 'comments_count'
        ]

    def get_likes_count(self, obj):
        return obj.likes.filter(value='like').count()

    def get_comments_count(self, obj):
        return obj.comments.count()


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']


class PostLikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = PostLike
        fields = ['id', 'post', 'user', 'value', 'created_at']
