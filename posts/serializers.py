from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Tag, Post, Comment, PostLike


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']
        extra_kwargs = {
            'slug': {'read_only': True}
        }


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category', queryset=Category.objects.all(), write_only=True
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        source='tags', queryset=Tag.objects.all(), many=True, write_only=True
    )
    summary = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'summary',
            'author', 'category', 'category_id',
            'tags', 'tag_ids',
            'created_at', 'updated_at', 'status',
            'featured_image', 'likes_count', 'comments_count', 'is_liked'
        ]
        extra_kwargs = {
            'slug': {'read_only': True},
            'featured_image': {'required': False, 'allow_null': True},
        }

    def get_summary(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content

    def get_likes_count(self, obj):
        return obj.likes.filter(value='like').count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user, value='like').exists()
        return False

    def create(self, validated_data):
        request = self.context.get('request')
        tag_ids = validated_data.pop('tags', [])
        category_id = validated_data.pop('category', None)
        post = Post.objects.create(author=request.user, **validated_data)
        if tag_ids:
            post.tags.set(tag_ids)
        if category_id:
            post.category = category_id
            post.save()

        return post


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    post = PostSerializer(read_only=True)

    slug = serializers.SlugRelatedField(
        queryset=Post.objects.all(),
        slug_field='slug',
        write_only=True,
        required=False
    )

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at', 'slug']


class PostLikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = PostLike
        fields = ['id', 'post', 'user', 'value', 'created_at']
        read_only_fields = ['id', 'created_at']
