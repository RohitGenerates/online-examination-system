from django.contrib import admin
from .models import Subject, Question, Exam, ExamQuestion, StudentExam, StudentAnswer

class ExamQuestionInline(admin.TabularInline):
    model = ExamQuestion
    extra = 1

class StudentAnswerInline(admin.TabularInline):
    model = StudentAnswer
    extra = 0

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'subject', 'question_type', 'correct_answer', 'marks')
    list_filter = ('subject', 'question_type')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'created_by', 'start_time', 'end_time', 'is_published')
    list_filter = ('subject', 'created_by', 'is_published')
    inlines = [ExamQuestionInline]

@admin.register(StudentExam)
class StudentExamAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'start_time', 'end_time', 'is_completed', 'score')
    list_filter = ('exam', 'student', 'is_completed')
    inlines = [StudentAnswerInline]

admin.site.register(ExamQuestion)
admin.site.register(StudentAnswer)