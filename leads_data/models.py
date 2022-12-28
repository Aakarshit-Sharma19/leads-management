from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


class DocumentSpace(models.Model):
    owner = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='owner_of_space')
    managers = models.ManyToManyField(get_user_model(), related_name='manager_of_spaces')
    writers = models.ManyToManyField(get_user_model(), related_name='writer_of_spaces')

    def __str__(self):
        return f'Space of {self.owner.get_full_name()}'
    def get_absolute_url(self):
        return reverse('spaces_overview', args=(self.pk,))
class DataFile(models.Model):
    space = models.ForeignKey(DocumentSpace, on_delete=models.CASCADE, related_name='files')
    file_id = models.CharField(max_length=35, null=False, blank=False)
    file_name = models.CharField(max_length=100)
    current_row = models.IntegerField(default=0)


class UpdatedFile(models.Model):
    data_file = models.OneToOneField(DataFile, related_name='updated_file', on_delete=models.CASCADE)
