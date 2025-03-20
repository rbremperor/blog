from django import template

register = template.Library()

@register.filter
def is_following(user, profile):
    return user.profile.is_following(profile)
