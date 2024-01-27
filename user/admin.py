from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *


# Register your models here.
@admin.register(User)
class UsersAdmin(ImportExportModelAdmin):
    list_display = ('username','email', 'first_name', 'last_name')
    search_fields = ['username', 'first_name', 'last_name']
