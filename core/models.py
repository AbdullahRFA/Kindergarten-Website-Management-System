from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("teacher", "Teacher"),
        ("student", "Student"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    def is_admin(self):
        return self.role == 'admin'
    def is_teacher(self):
        return self.role == 'teacher'
    def is_student(self):
        return self.role == 'student'
    
    
class ClassRoom(models.Model):
    name = models.CharField(max_length=64)
    grade = models.CharField(max_length=32, blank=True)
    def __str__(self):
        return f"{self.grade} - {self.name}" if self.grade else self.name
    
class Course(models.Model):
    title = models.CharField(max_length=128)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    teacher = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'teacher'})
    def __str__(self):
        return self.title

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    full_name = models.CharField(max_length=128, blank=True)
    designation = models.CharField(max_length=64, blank=True)
    office_email = models.EmailField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    national_id = models.CharField(max_length=32, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=24, blank=True)
    emergency_contact = models.CharField(max_length=24, blank=True)
    photo = models.ImageField(upload_to='admin_photos/', blank=True, null=True)
    bio = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    languages = models.TextField(blank=True)
    hobbies = models.TextField(blank=True)
    social_media = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    interests = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name or self.user.username



class TeaacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    full_name = models.CharField(max_length=128, blank=True)
    class_room = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=24, blank=True)
    photo = models.ImageField(upload_to='teacher_photos/', blank=True, null=True)
    qualification = models.CharField(max_length=256, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.full_name or self.user.username 
    
class StudentProfile(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('rejected', 'Rejected'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=128, blank=True)
    class_room = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=24, blank=True)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    guardian_name = models.CharField(max_length=128, blank=True)
    guardian_relation = models.CharField(max_length=64, blank=True)
    guardian_email = models.EmailField(blank=True)
    guardian_phone = models.CharField(max_length=24, blank=True)
    admission_date = models.DateField(default=timezone.now)
    admission_fee_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending')
    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"
    def __str__(self):
        return self.full_name or self.user.username 
    def get_full_name(self):
        return self.full_name or f"{self.user.first_name} {self.user.last_name}"    
class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(default=timezone.now)
    class Meta:
        unique_together = ('student', 'course')
ATTENDANCE_STATUS = (
    ('present', 'Present'),
    ('absent', 'Absent'),
    ('late', 'Late'),
)
class Attendance(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=8, choices=ATTENDANCE_STATUS)
    class Meta:
        unique_together = ('student', 'course', 'date')
class Homework(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.title
class HomeworkSubmission(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_submissions')
class ExamMark(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=128)
    marks = models.DecimalField(max_digits=6, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
LEAVE_STATUS = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
)
class LeaveRequest(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=LEAVE_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
class PaymentTransaction(models.Model):
    PROVIDER_CHOICES = (
        ('bkash', 'Bkash'),
        ('nagad', 'Nagad'),
    )
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    provider = models.CharField(max_length=16, choices=PROVIDER_CHOICES)
    status = models.CharField(max_length=16, default='initiated')
    transaction_id = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
class Bus(models.Model):
    identifier = models.CharField(max_length=64)
    route_name = models.CharField(max_length=128, blank=True)
    def __str__(self):
        return self.identifier
class BusLocation(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    lat = models.FloatField()
    lon = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-timestamp']
