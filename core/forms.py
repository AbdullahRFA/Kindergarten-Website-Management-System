from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import AdminProfile
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
User = get_user_model()

from .models import User, StudentProfile, Homework, LeaveRequest, HomeworkSubmission, TeaacherProfile, AdminProfile, ClassRoom, Course


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
        fields = ['course', 'title', 'description', 'due_date']

        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter homework title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter homework details'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'classroom']   # teacher will be auto-assigned in the view

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter course title'
            }),
            'classroom': forms.Select(attrs={
                'class': 'form-select'
            }),
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


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'full_name', 'class_room', 'date_of_birth', 'address', 'phone',
            'photo', 'guardian_name', 'guardian_relation', 'guardian_email',
            'guardian_phone'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'admission_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'full_name': 'Full Name',
            'class_room': 'Class Room',
            'date_of_birth': 'Date of Birth',
            'address': 'Address',
            'phone': 'Phone Number',
            'photo': 'Profile Photo',
            'guardian_name': "Guardian's Name",
            'guardian_relation': "Guardian's Relation",
            'guardian_email': "Guardian's Email",
            'guardian_phone': "Guardian's Phone Number"
        }       
        

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeaacherProfile
        fields = [
            'full_name', 'class_room', 'date_of_birth', 'address', 'phone',
            'photo', 'qualification', 'experience_years'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        labels = {
            'full_name': 'Full Name',
            'class_room': 'Class Room',
            'date_of_birth': 'Date of Birth',
            'address': 'Address',
            'phone': 'Phone Number',
            'photo': 'Profile Photo',
            'qualification': 'Qualification',
            'experience_years': 'Years of Experience'
        }


phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

class AdminProfileForm(forms.ModelForm):
    phone = forms.CharField(
        validators=[phone_validator],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Phone Number',
        max_length=24
    )
    emergency_contact = forms.CharField(
        validators=[phone_validator],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Emergency Contact',
        max_length=24
    )

    class Meta:
        model = AdminProfile
        fields = [
            'full_name',
            'designation',
            'office_email',
            'date_of_birth',
            'joining_date',
            'national_id',
            'address',
            'phone',
            'emergency_contact',
            'photo',
            'bio',
            'skills',
            'experience',
            'education',
            'languages',
            'hobbies',
            'social_media',
            'achievements',
            'certifications',
            'interests',
            'notes',
            'is_active',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'joining_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'experience': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'education': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'languages': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'hobbies': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'social_media': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'achievements': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'certifications': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'interests': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'office_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    label = "Registered Email"
    
    
class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Old Password'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter New Password'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'})
    )
    
    

class TeacherCreateForm(UserCreationForm):
    full_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    class_room = forms.Select(attrs={'class': 'form-select'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')  # ✅ Login credentials
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'teacher'   # ✅ Assign teacher role
        if commit:
            user.save()
            # create teacher profile automatically
            TeaacherProfile.objects.create(
                user=user,
                full_name=self.cleaned_data.get('full_name')
            )
        return user
    




class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = ['name', 'grade', 'curriculum', 'teacher', 'monthly_fee']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Class Name (e.g., Play, KG, One)'}),
            'grade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Grade (optional)'}),
            'curriculum': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter curriculum details'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'monthly_fee': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }