import random

from django.http import HttpRequest


def get_random_avatar_url(request: HttpRequest):
    if 'avatar_seed' in request.COOKIES:
        seed = request.COOKIES.get('avatar_seed')
    else:
        seed = 1
    return {
        "avatar_url": f"https://avatars.dicebear.com/api/bottts/{seed}.svg?size=36",
        "avatar_url_120": f"https://avatars.dicebear.com/api/bottts/{seed}.svg?size=120"
    }

def get_url_name(request: HttpRequest):
    return {
        'url_name': request.resolver_match.url_name
    }