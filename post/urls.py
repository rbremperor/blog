from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import register_view, home, PostViewSet, login_view, logout_view, ProfileViewSet

router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register('profile', ProfileViewSet, basename='profile')


post_create = PostViewSet.as_view({'get': 'create', 'post': 'create'})
post_update = PostViewSet.as_view({'get': 'retrieve', 'post': 'update'})  # Update view
post_delete = PostViewSet.as_view({'post': 'destroy'})  # Delete view
add_comment = PostViewSet.as_view({'post': 'add_comment'})
like_post = PostViewSet.as_view({'post': 'like_post'})
# delete_comment = PostViewSet.as_view({'post': 'delete_comment'})

profile_detail = ProfileViewSet.as_view({'get': 'retrieve'})
profile_follow = ProfileViewSet.as_view({'post': 'follow'})

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register_view, name='register'),
    path('home/', home, name='home'),
    path('publish/', post_create, name='post-create'),
    path('posts/<int:pk>/edit/', post_update, name='post-update'),  # Edit URL
    path('posts/<int:pk>/delete/', post_delete, name='post-delete'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('posts/<int:pk>/comment/', add_comment, name='add_comment'),
    path('posts/<int:pk>/like/', like_post, name='like_post'),
    path('profile/<int:pk>/', profile_detail, name='profile-detail'),
    path('profile/<int:pk>/follow/', profile_follow, name='profile-follow'),

]