from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, ClassRoom, Course, StudentProfile, Enrollment, Attendance, Homework, HomeworkSubmission, ExamMark, LeaveRequest, PaymentTransaction, Message, Notification, Bus, BusLocation

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

# Register other models
admin.site.register(ClassRoom)
admin.site.register(Course)
admin.site.register(StudentProfile)
admin.site.register(Enrollment)
admin.site.register(Attendance)
admin.site.register(Homework)
admin.site.register(HomeworkSubmission)
admin.site.register(ExamMark)
admin.site.register(LeaveRequest)
admin.site.register(PaymentTransaction)
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(Bus)
admin.site.register(BusLocation)
