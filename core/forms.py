from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, StudentProfile, Homework, LeaveRequest, HomeworkSubmission
class StudentRegistrationForm(UserCreationForm):
    guardian_name = forms.CharField(required=False)
    guardian_phone = forms.CharField(required=False)
    class Meta:
        model = User
        fields = ('username','first_name','last_name','email','password1','password2')
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                guardian_name=self.cleaned_data.get('guardian_name',''),
                guardian_phone=self.cleaned_data.get('guardian_phone',''),
            )
        return user
class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ('course','title','description','due_date')
class SubmissionForm(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = ('text','file')
class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ('start_date','end_date','reason')
