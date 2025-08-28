from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import random
from datetime import datetime, timedelta
from django.contrib.auth import update_session_auth_hash


from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views as auth_views
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from .models import User, StudentProfile, Course, Homework, HomeworkSubmission, PaymentTransaction, BusLocation, Bus, TeaacherProfile, LeaveRequest, Notification, Message, ExamMark,AdminProfile
from .forms import StudentRegistrationForm, HomeworkForm, SubmissionForm, LeaveRequestForm, StudentProfileForm, TeacherProfileForm, AdminProfileForm, PasswordResetRequestForm, UserPasswordChangeForm


def homepage(request):
    return render(request, 'homepage.html')
def about(request):
    return render(request, 'about.html')
def contact(request):
    return render(request, 'contact.html')

def SRS(request):
    return render(request, 'SRS.html')


def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration submitted — pending approval.')
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'auth/register.html', {'form': form})

def forgot_password(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            User = get_user_model()
            user = User.objects.filter(email=email).first()  # ✅ Correct
            
            if user:
                send_otp(email)
                messages.success(request, "OTP has been sent to your email.")
                return redirect('verify_otp', email=email)
            else:
                messages.error(request, "❌ No user found with this email.")
    else:
        form = PasswordResetRequestForm()
    return render(request, "password_reset_and_change/request_password_reset.html", {'form': form})



# Temporary OTP Storage
otp_storage = {}

# Send OTP to Email
def send_otp(email):
    otp = random.randint(100000, 999999)
    otp_storage[email] = {
        'otp': otp,
        'timestamp': datetime.now()
    }

    subject = "Password Reset OTP - KWMS"
    message = f"Hello,\n\nYour OTP for password reset is: {otp}\n\nDo not share this OTP with anyone."
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

# Password Reset Request View
def request_password_reset(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            User = get_user_model()
            
            # Correct usage of .first()
            user = User.objects.filter(email=email).first()
            
            if user:  # If user exists
                send_otp(email)
                messages.success(request, "OTP has been sent to your email.")
                return redirect('verify_otp', email=email)
            else:
                messages.error(request, "❌ No user found with this email.")
    else:
        form = PasswordResetRequestForm()
    
    return render(request, "password_reset_and_change/request_password_reset.html", {'form': form})

# OTP Verification View
def verify_otp(request, email):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        data = otp_storage.get(email)

        if data:
            otp_valid = str(data['otp']) == entered_otp
            otp_expired = datetime.now() > data['timestamp'] + timedelta(minutes=5)

            if otp_valid and not otp_expired:
                del otp_storage[email]
                messages.success(request, "OTP verified successfully. Set a new password.")
                return redirect('reset_password', email=email)
            elif otp_expired:
                del otp_storage[email]
                messages.error(request, "OTP has expired. Please request a new one.")
            else:
                messages.error(request, "Invalid OTP. Please try again.")
        else:
            messages.error(request, "No OTP found for this email.")
    return render(request, "password_reset_and_change/verify_otp.html", {'email': email})

# Password Reset View
def reset_password(request, email):
    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password == confirm_password:
            User = get_user_model()
            try:
                user = User.objects.get(email=email)
                user.password = make_password(new_password)
                user.save()
                messages.success(request, "Password reset successfully. Please login.")
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, "User not found.")
        else:
            messages.error(request, "Passwords do not match. Try again.")
    return render(request, "password_reset_and_change/reset_password.html", {'email': email})





@login_required(login_url='login_user')
# @user_passes_test(check_admin)
def change_password(request):
    if request.method == 'POST':
        form = UserPasswordChangeForm(data=request.POST, user=request.user)  # ✅ Corrected form initialization
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # ✅ Keep user logged in
            messages.success(request, "Your password was successfully updated!")
            return redirect('password_change_complete')  # ✅ Redirect instead of re-rendering
    else:
        form = UserPasswordChangeForm(user=request.user)

    return render(request, 'password_reset_and_change/change_password.html', {'form': form})

def password_change_complete(request):
    return render(request, 'password_reset_and_change/password_change_complete.html')







@login_required
def dashboard(request):
    user = request.user
    if user.role == 'admin':
        pending = StudentProfile.objects.filter(status='pending').count()
        total_students = StudentProfile.objects.filter(status='active').count()
        total_teachers = User.objects.filter(role='teacher').count()
        return render(request, 'admin/dashboard.html', {'pending': pending, 'total_students': total_students, 'total_teachers': total_teachers})
    elif user.role == 'teacher':
        courses = Course.objects.filter(teacher=user)
        return render(request, 'teacher/dashboard.html', {'courses': courses})
    else:
        student_profile = getattr(user, 'student_profile', None)
        return render(request, 'student/dashboard.html', {'profile': student_profile})


@login_required
def admin_profile(request):
     # Ensure the user has a profile, else create one
    profile, created = AdminProfile.objects.get_or_create(user=request.user)
    print(request.user)
    return render(request, 'admin/admin_profile.html', {
        'profile': profile
    })

@login_required
def admin_profile_edit(request):
    profile = get_object_or_404(AdminProfile, user=request.user)
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('admin_profile')
    else:
        form = AdminProfileForm(instance=profile)
    return render(request, 'admin/admin_profile_edit.html', {'form': form, 'profile': profile})

@login_required
def teacher_profile(request):
     # Ensure the user has a profile, else create one
    profile, created = TeaacherProfile.objects.get_or_create(user=request.user)
    print(request.user)
    return render(request, 'teacher/teacher_profile.html', {
        'profile': profile
    })

@login_required
def teacher_profile_edit(request):
    profile = get_object_or_404(TeaacherProfile, user=request.user)
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('teacher_profile')
    else:
        form = TeacherProfileForm(instance=profile)
    return render(request, 'teacher/teacher_profile_edit.html', {'form': form, 'profile': profile})  

@login_required
def student_profile(request):
    # Ensure the user has a profile, else create one
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    print(request.user)
    return render(request, 'student/student_profile.html', {
        'profile': profile
    })

@login_required
def student_profile_and_edit(request):
    # Ensure the user has a profile, else create one
    profile, created = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('student_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentProfileForm(instance=profile)

    return render(request, 'student/student_profile_edit.html', {
        'form': form,
        'profile': profile
    })

@login_required
def create_homework(request):
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied')
        return redirect('dashboard')
    if request.method == 'POST':
        form = HomeworkForm(request.POST)
        if form.is_valid():
            hw = form.save(commit=False)
            hw.created_by = request.user
            hw.save()
            messages.success(request,'Homework created')
            return redirect('dashboard')
    else:
        form = HomeworkForm()
    return render(request, 'teacher/create_homework.html', {'form': form})
@login_required
def submit_homework(request, pk):
    hw = get_object_or_404(Homework, pk=pk)
    student_profile = request.user.student_profile
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.homework = hw
            sub.student = student_profile
            sub.save()
            messages.success(request, 'Submitted')
            return redirect('dashboard')
    else:
        form = SubmissionForm()
    return render(request, 'student/submit_homework.html', {'form': form, 'homework': hw})
@login_required
def initiate_payment(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        tx = PaymentTransaction.objects.create(
            student=getattr(request.user, 'student_profile', None),
            amount=amount,
            provider='bkash',
            status='initiated'
        )
        return redirect(reverse('payment_status', args=[tx.id]))
    return render(request, 'payment/initiate.html')
def payment_callback(request):
    tx_id = request.POST.get('transaction_id')
    status = request.POST.get('status')
    try:
        tx = PaymentTransaction.objects.get(transaction_id=tx_id)
        tx.status = status
        tx.save()
        if status == 'success' and tx.student:
            tx.student.status = 'pending'
            tx.student.save()
    except PaymentTransaction.DoesNotExist:
        pass
    return HttpResponse('OK')
@login_required
def bus_locations_json(request):
    buses = Bus.objects.all()
    data = []
    for bus in buses:
        loc = BusLocation.objects.filter(bus=bus).order_by('-timestamp').first()
        if loc:
            data.append({'bus': bus.identifier, 'lat': loc.lat, 'lon': loc.lon, 'time': loc.timestamp.isoformat()})
    return JsonResponse({'locations': data})



# Add teacher by admin
from django.contrib.admin.views.decorators import staff_member_required
from .forms import TeacherCreateForm

@login_required
def add_teacher_by_admin(request):
    if request.user.role != "admin":   # only admins allowed
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    if request.method == "POST":
        form = TeacherCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher account created successfully!")
            return redirect("dashboard")
    else:
        form = TeacherCreateForm()
    return render(request, "admin/add_teacher.html", {"form": form})



# Show all user (admin, teacher, student)
@login_required
def manage_users_by_admin(request):
    if request.user.role != "admin":   # ✅ only admins allowed
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    admins = User.objects.filter(role="admin")
    teachers = User.objects.filter(role="teacher")
    students = User.objects.filter(role="student")

    return render(request, "admin/manage_users.html", {
        "admins": admins,
        "teachers": teachers,
        "students": students,
    })