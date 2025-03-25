from rest_framework import serializers
from post.models import Post, Comment, Like, Profile
from django.contrib.auth.models import User


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    class Meta:
        model = Comment
        fields = ["id", "post", "author", "content", "created_time"]
        read_only_fields = ["id", "post", "author", "created_time"]


    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user:
            validated_data["author"] = request.user.profile
        return Comment.objects.create(**validated_data)

class LikeSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ["id", "author", 'post']
        extra_kwargs = {"post": {"read_only": True}}

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user:
            validated_data["author"] = request.user.profile
            return Like.objects.create(**validated_data)
        return Like.objects.create(**validated_data)

class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('title', 'content', 'author', 'comments', 'likes')

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user:
            validated_data["author"] = request.user.profile
        return Post.objects.create(**validated_data)

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    following_count = serializers.IntegerField(source='following.count', read_only=True)
    profile_picture_url = serializers.SerializerMethodField()  # Added this field

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'profile_picture', 'profile_picture_url', 'followers_count', 'following_count']

    def get_profile_picture_url(self, obj):
        """Returns the full URL of the profile picture"""
        request = self.context.get('request')
        if obj.profile_picture and request:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

    def validate_username(self, value):
        """Ensure username is unique"""
        user = self.instance.user
        if User.objects.filter(username=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Username is already taken")
        return value
