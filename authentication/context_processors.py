import random

def get_random_avatar_url(request):
    return {
        "avatar_url": f"https://avatars.dicebear.com/api/adventurer-neutral/{random.randint(0, 1000)}.svg?b=%23deddda&size=36"
    }