from django.contrib import admin
from leads_data import models

# Register your models here.
admin.site.register(models.DocumentSpace)
admin.site.register(models.DataFile)
admin.site.register(models.ResponseFile)
admin.site.register(models.Student)
admin.site.register(models.Response)

