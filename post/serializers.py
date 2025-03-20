from rest_framework import serializers
from post.models import Post, Comment, Like, Profile


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

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'profile_picture', 'followers_count', 'following_count']
