from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *
# Register your models here.


@admin.register(CourseQuestion)
class CourseQuestionAdmin(ImportExportModelAdmin):
    list_display = ('comprehension', 'question', 'examiner_answer', 'student_answer')
    search_fields = ['username', 'first_name', 'last_name']

@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin):
    list_display = ('title', 'code', 'description')