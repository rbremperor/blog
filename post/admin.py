from django.contrib import admin

from post.models import Comment, Post, Profile

# Register your models here.
admin.site.register(Comment)
admin.site.register(Post)
admin.site.register(Profile)
