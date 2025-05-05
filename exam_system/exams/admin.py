from django.contrib import admin
from .models import Question, Exam, StudentExamResult

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'marks')
    search_fields = ('text',)

class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'department', 'semester', 'duration', 'passing_score')
    list_filter = ('department', 'semester')
    search_fields = ('title', 'subject')

class StudentExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'obtained_marks', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('student__user__username', 'exam__title')

admin.site.register(Question, QuestionAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(StudentExamResult, StudentExamResultAdmin)