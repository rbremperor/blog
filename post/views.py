from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.decorators import action

from post.models import Post, Like, Comment, Profile
from post.forms import RegisterForm, PostForm, LoginForm
from post.serializers import PostSerializer, CommentSerializer, LikeSerializer, ProfileSerializer


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home/')
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})



def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)  # Verify credentials

            if user is not None:
                login(request, user)  # Log in the user
                return redirect('/home/')
            else:
                form.add_error(None, "Invalid username or password")  # Show error if login fails
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('login')


def home(request):
    posts = Post.objects.prefetch_related("comments").all()
    for post in posts:
        post.liked = post.likes.filter(author=request.user.profile).exists()
    return render(request, "home.html", {"posts": posts})


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get_renderer_context(self):
        """Dynamically switch renderer based on request type."""
        if self.request.accepted_renderer.format == "html":
            return {"template_name": self.get_template_name()}
        return {}

    def get_template_name(self):
        """Returns the correct template for each action."""
        if self.action == "list":
            return "posts.html"
        elif self.action == "create":
            return "publish.html"
        elif self.action in ["retrieve", "update"]:
            return "edit_post.html"
        return None

    def list(self, request, *args, **kwargs):
        user_profile = Profile.objects.get(user=self.request.user)  # Get the Profile instance
        queryset = Post.objects.filter(author=user_profile)  # ✅ Filter by Profile
        return render(request, "posts.html", {"posts": queryset})

    def create(self, request, *args, **kwargs):
        """Create a new post (HTML form for browser)."""
        if request.method == "POST":
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user.profile
                post.save()
                return redirect("/home/")

        form = PostForm()
        return render(request, "publish.html", {"form": form})

    def retrieve(self, request, pk=None):
        """Retrieve a single post (HTML for browser, JSON for API)."""
        post = get_object_or_404(Post, pk=pk)
        form = PostForm(instance=post)
        return render(request, "edit_post.html", {"form": form, "post": post})

    def update(self, request, pk=None):
        """Update a post (HTML for browser)."""
        post = get_object_or_404(Post, pk=pk, author=request.user.profile)
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                form.save()
                return redirect("post-list")
        else:
            form = PostForm(instance=post)
        return render(request, "edit_post.html", {"form": form, "post": post})

    def destroy(self, request, pk=None):
        """Delete a post (JSON only)."""
        post = get_object_or_404(Post, pk=pk, author=request.user.profile)
        post.delete()
        return redirect('post-list')

    @action(detail=True, methods=['post'], renderer_classes=[JSONRenderer])
    def add_comment(self, request, pk=None):
        """Add a comment (JSON API only)."""
        post = get_object_or_404(Post, pk=pk)
        serializer = CommentSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(post=post, author=request.user.profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], renderer_classes=[JSONRenderer])
    def like_post(self, request, pk=None):
        """Like/unlike a post (JSON API only)."""
        post = get_object_or_404(Post, pk=pk)
        user = request.user

        if not user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_403_FORBIDDEN)

        existing_like = Like.objects.filter(post=post, author=user.profile).first()  # Fix here

        if existing_like:
            existing_like.delete()
            return Response({
                "message": "Unliked",
                "liked": False,
                "likes_count": post.likes.count()
            }, status=status.HTTP_200_OK)

        Like.objects.create(post=post, author=user.profile)  # Fix here
        return Response({
            "message": "Liked",
            "liked": True,
            "likes_count": post.likes.count()
        }, status=status.HTTP_201_CREATED)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    renderer_classes = (TemplateHTMLRenderer,)

    def retrieve(self, request, pk=None):
        """Retrieve a single user profile."""
        profile = get_object_or_404(Profile, user__pk=pk)
        return render(request, "profile.html", {"profile": profile})

    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        user_profile = request.user.profile
        target_profile = get_object_or_404(Profile, pk=pk)

        if user_profile.is_following(target_profile):
            user_profile.unfollow(target_profile)
            return Response({"message": "Unfollowed"}, status=status.HTTP_200_OK)

        user_profile.follow(target_profile)
        return Response({"message": "Followed"}, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return Profile.objects.exclude(user=self.request.user)