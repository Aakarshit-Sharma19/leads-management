from typing import Optional

from django import http
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.views.generic import ListView

from document_spaces import forms
from leads_data.models import DocumentSpace, DataFile, Student


class SpaceFollowUpView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    context_object_name = 'students'
    template_name = "pages/spaces/follow-up.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.space: 'Optional[DocumentSpace]' = None
        self.data_file: 'Optional[DataFile]' = None

    def test_func(self):
        try:
            if self.request.user.is_space_owner:
                self.space = DocumentSpace.objects.get(id=self.kwargs['space_id'], owner=self.request.user)
            else:
                self.space = DocumentSpace.objects.get(Q(id=self.kwargs['space_id']) &
                                                       (Q(managers=self.request.user) | Q(writers=self.request.user)))
            return True
        except DocumentSpace.DoesNotExist:
            return False

    def get_queryset(self):
        try:
            self.data_file = DataFile.objects.get(pk=self.kwargs['file_id'])
        except DataFile.DoesNotExist:
            raise http.Http404()
        return Student.objects.filter(data_file_id=self.kwargs['file_id'], resolved=False)

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs = super().get_context_data(object_list=object_list, **kwargs)
        kwargs.update({
            'space': self.space,
            'data_file': self.data_file,
            'resolve_form': forms.ResolveEntryForm()
        })
        return kwargs
