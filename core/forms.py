from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, StudentProfile, Homework, LeaveRequest, HomeworkSubmission
class StudentRegistrationForm(UserCreationForm):
    guardian_name = forms.CharField(
        required=False,
        label="Guardian's Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter guardian’s full name'})
    )
    guardian_phone = forms.CharField(
        required=False,
        label="Guardian's Phone",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter guardian’s phone number'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email address'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                guardian_name=self.cleaned_data.get('guardian_name', ''),
                guardian_phone=self.cleaned_data.get('guardian_phone', ''),
            )
        return user


class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ('course', 'title', 'description', 'due_date')
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Homework title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed description'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'course': 'Course',
            'title': 'Title',
            'description': 'Description',
            'due_date': 'Due Date',
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = ('text', 'file')
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your submission'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'text': 'Submission Text',
            'file': 'Upload File',
        }


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ('start_date', 'end_date', 'reason')
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Explain your reason for leave'}),
        }
        labels = {
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'reason': 'Reason for Leave',
        }
