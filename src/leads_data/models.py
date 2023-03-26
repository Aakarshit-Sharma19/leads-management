from auditlog.registry import auditlog
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone


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
    web_content_link = models.URLField()
    file_id = models.CharField(max_length=100, null=False, blank=False, unique=True)
    file_name = models.CharField(max_length=100, unique=True)
    current_row = models.IntegerField(default=1)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f'Data File: {self.file_name}'


class ResponseFile(models.Model):
    data_file = models.OneToOneField(DataFile, related_name='response_file', on_delete=models.CASCADE)
    web_content_link = models.URLField()
    file_id = models.CharField(max_length=100, null=False, blank=False, unique=True)

    def __str__(self):
        return f'Response File: {self.data_file.file_name}'


class Student(models.Model):
    STATUS_CHOICES = (
        ("started", "Interaction Started"),
        ("not_interested", "Not Interested"),
        ("interested", "Interested"),
        ("denied", "Denied Admission"),
        ("confirmed", "Admission Confirmed"),
    )

    data_file = models.ForeignKey(DataFile, related_name='approached_individuals', on_delete=models.CASCADE)
    row_no = models.IntegerField(blank=False, null=False)
    name = models.CharField(max_length=50)
    parent_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=14)
    education = models.CharField(max_length=200)
    status = models.CharField(choices=STATUS_CHOICES, max_length=14, default="started")
    resolved = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['data_file', 'row_no'])
        ]

    def __str__(self):
        return f'Pending Student Response of file {self.data_file.file_name}: {self.name}'

    @property
    def is_resolvable(self):
        return self.status in ("denied", "confirmed")


class Response(models.Model):
    individual = models.ForeignKey(Student, related_name='responses', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Student Response of {self.individual.name}: {self.content[:10]}'


auditlog.register(DocumentSpace)
auditlog.register(DataFile)
auditlog.register(ResponseFile)
auditlog.register(Student)
auditlog.register(Response)
