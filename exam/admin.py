from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *
# Register your models here.

@admin.register(CourseQuestion)
class CourseQuestionAdmin(ImportExportModelAdmin):
    list_display = ('comprehension', 'question', 'examiner_answer', 'student_answer')
    search_fields = ['comprehension', 'question', 'examiner_answer']
    # list_filter = ('question_id__title', 'question_id__code')  # Assuming title and code are fields in the related model


@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin):
    list_display = ('title', 'code', 'description')

@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    list_display = ('user',)

@admin.register(StudentCourseRegistration)
class StudentCourseRegistrationAdmin(ImportExportModelAdmin):
    list_display = ('student', 'course')

@admin.register(Exam)
class ExamAdmin(ImportExportModelAdmin):
    list_display = ('course','questions', 'duration')