from django.contrib import admin

# Register your models here.
from . import models
admin.site.register(models.Query)
admin.site.register(models.Entity)
