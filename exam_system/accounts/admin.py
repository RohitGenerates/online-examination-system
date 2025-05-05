from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Teacher

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'status')
    list_filter = ('status',)
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('status',)}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Student)
admin.site.register(Teacher)