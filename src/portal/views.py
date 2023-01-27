import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "pages/index.html"

    def get(self, request, *args, **kwargs):
        response = super(IndexView, self).get(request, *args, **kwargs)
        # For random avatar in the header
        if 'avatar_seed' not in request.COOKIES:
            seed = random.randint(0, 10000)
            request.COOKIES['seed'] = seed
            response.set_cookie('avatar_seed', seed)
        return response
