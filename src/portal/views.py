import random

from auditlog.models import LogEntry
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.views.generic import TemplateView, FormView

from portal.forms import DeleteOlderLogEntriesForm


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "pages/index.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['log_entries'] = LogEntry.objects.all()[:50]
        kwargs['form'] = DeleteOlderLogEntriesForm()
        return kwargs

    def get(self, request, *args, **kwargs):
        response = super(IndexView, self).get(request, *args, **kwargs)
        # For random avatar in the header
        if 'avatar_seed' not in request.COOKIES:
            seed = random.randint(0, 10000)
            request.COOKIES['seed'] = seed
            response.set_cookie('avatar_seed', seed)
        return response


class RecentActivityView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    def test_func(self):
        return self.request.user.is_superuser

    template_name = 'pages/recent-activity.html'
    form_class = DeleteOlderLogEntriesForm

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['log_entries'] = LogEntry.objects.all()
        return kwargs

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        LogEntry.objects.filter(Q(timestamp__lte=form.cleaned_data['timeframe'])).delete()
        messages.success(self.request, "Entries deleted successfully")
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
