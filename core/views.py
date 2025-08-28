from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import random
from datetime import datetime, timedelta
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone

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
from django.utils.timezone import now
from calendar import monthrange


from .models import User, StudentProfile, Course, Homework, HomeworkSubmission, PaymentTransaction, BusLocation, Bus, TeaacherProfile, LeaveRequest, Notification, Message, ExamMark,AdminProfile, ClassRoom, Enrollment

from .forms import StudentRegistrationForm, HomeworkForm, SubmissionForm, LeaveRequestForm, StudentProfileForm, TeacherProfileForm, AdminProfileForm, PasswordResetRequestForm, UserPasswordChangeForm, ClassRoomForm, CourseForm


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
        return render(request, 'admin/dashboard.html', {
            'pending': pending,
            'total_students': total_students,
            'total_teachers': total_teachers
        })

    elif user.role == 'teacher':
        # ✅ get all classes assigned to this teacher
        assigned_classes = ClassRoom.objects.filter(teacher=user)

        # ✅ get courses created for those classes
        courses = Course.objects.filter(teacher=user)

        return render(request, 'teacher/dashboard.html', {
            'assigned_classes': assigned_classes,
            'courses': courses
        })

    else:  # student
        student_profile = getattr(user, 'student_profile', None)
        return render(request, 'student/dashboard.html', {'profile': student_profile})
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
def create_course(request):
    if request.user.role != "teacher":
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user  # auto-assign logged-in teacher
            course.save()
            messages.success(request, "Course created successfully!")
            return redirect("teacher_courses")
    else:
        form = CourseForm()

    # limit classrooms to only those assigned to this teacher
    form.fields['classroom'].queryset = ClassRoom.objects.filter(teacher=request.user)

    return render(request, "teacher/create_course.html", {"form": form})

@login_required
def teacher_courses(request):
    if request.user.role != "teacher":
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    courses = Course.objects.filter(teacher=request.user).select_related("classroom")
    return render(request, "teacher/course_list.html", {"courses": courses})



@login_required
def create_homework(request, course_id=None):
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
            return redirect('course_homeworks', course_id=hw.course.id)
    else:
        form = HomeworkForm()

    # limit courses to teacher's courses only
    form.fields['course'].queryset = Course.objects.filter(teacher=request.user)

    # preselect if course_id given
    if course_id:
        form.fields['course'].initial = Course.objects.get(id=course_id)

    return render(request, 'teacher/create_homework.html', {'form': form})


@login_required
def course_homeworks(request, course_id):
    # Get the course object or return 404
    course = get_object_or_404(Course, id=course_id)
    
    # Check if user has permission to view this course's homeworks
    if request.user.role != 'teacher' or course.teacher != request.user:
        messages.error(request, "You don't have permission to view these homeworks.")
        return redirect('dashboard')
    
    # Get all homeworks for this course
    homeworks = Homework.objects.filter(course=course).order_by('-created_at')
    
    # Get submission counts for each homework and calculate total submissions
    total_submissions = 0
    active_homeworks_count = 0
    now = timezone.now()
    
    for homework in homeworks:
        homework.submission_count = HomeworkSubmission.objects.filter(homework=homework).count()
        homework.graded_count = HomeworkSubmission.objects.filter(homework=homework, grade__isnull=False).count()
        total_submissions += homework.submission_count
        
        # Check if homework is active (not overdue)
        if homework.due_date >= now.date():
            active_homeworks_count += 1
    
    context = {
        'course': course,
        'homeworks': homeworks,
        'now': now,
        'total_submissions': total_submissions,
        'active_homeworks_count': active_homeworks_count,
    }
    
    return render(request, 'teacher/course_homeworks.html', context)



@login_required
def teacher_homeworks(request):
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied')
        return redirect('dashboard')

    homeworks = Homework.objects.filter(created_by=request.user).select_related("course")
    return render(request, 'teacher/homework_list.html', {"homeworks": homeworks})

@login_required
def view_submissions(request, homework_id):
    if request.user.role != "teacher":
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    homework = get_object_or_404(Homework, id=homework_id, created_by=request.user)
    submissions = HomeworkSubmission.objects.filter(homework=homework).select_related("student")

    return render(request, "teacher/view_submissions.html", {
        "homework": homework,
        "submissions": submissions,
    })


@login_required
def student_homeworks(request):
    if request.user.role != "student":
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    student = request.user.student_profile
    homeworks = Homework.objects.filter(course__classroom=student.class_room).order_by("-created_at")

    return render(request, "student/homework_list.html", {"homeworks": homeworks})


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
    
    
# Edit user (admin, teacher, student) - only by admin
@login_required
def edit_user_by_admin(request, user_id):
    if request.user.role != "admin":   # ✅ only admins can edit
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    user = get_object_or_404(User, id=user_id)

    # ✅ Select correct profile + form depending on role
    if user.role == "admin":
        profile = getattr(user, 'admin_profile', None)
        if not profile:
            profile = AdminProfile.objects.create(user=user)
        ProfileFormClass = AdminProfileForm

    elif user.role == "teacher":    
        profile = getattr(user, 'teacher_profile', None)
        if not profile:
            profile = TeaacherProfile.objects.create(user=user)
        ProfileFormClass = TeacherProfileForm

    elif user.role == "student":
        profile = getattr(user, 'student_profile', None)
        if not profile:
            profile = StudentProfile.objects.create(user=user)
        ProfileFormClass = StudentProfileForm

    else:
        messages.error(request, "Unknown role. Cannot edit this user.")
        return redirect("manage_users")

    # ✅ Handle POST/GET form
    if request.method == "POST":
        form = ProfileFormClass(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, f"{user.username}'s profile updated successfully!")
            return redirect("manage_users")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileFormClass(instance=profile)

    return render(request, "admin/edit_user.html", {
        "user_obj": user,
        "form": form,
        "profile": profile,
    })






@login_required
def manage_classes_by_admin(request):
    if request.user.role != "admin":
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    classes = ClassRoom.objects.all()
    return render(request, "admin/manage_classes.html", {"classes": classes})


@login_required
def add_class_by_admin(request):
    if request.user.role != "admin":
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ClassRoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Class added successfully!")
            return redirect("manage_classes_by_admin")
    else:
        form = ClassRoomForm()

    return render(request, "admin/add_class.html", {"form": form})


@login_required
def edit_class_by_admin(request, class_id):
    if request.user.role != "admin":
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    classroom = get_object_or_404(ClassRoom, id=class_id)
    if request.method == "POST":
        form = ClassRoomForm(request.POST, instance=classroom)
        if form.is_valid():
            form.save()
            messages.success(request, "Class updated successfully!")
            return redirect("manage_classes_by_admin")
    else:
        form = ClassRoomForm(instance=classroom)

    return render(request, "admin/edit_class.html", {"form": form, "classroom": classroom})



@login_required
def available_classes(request):
    if not request.user.is_student():
        messages.error(request, "Only students can view available classes.")
        return redirect("dashboard")

    classes = ClassRoom.objects.all()
    return render(request, "student/available_classes.html", {"classes": classes})

@login_required
def apply_for_class(request, class_id):
    if not request.user.is_student():
        messages.error(request, "Only students can apply for classes.")
        return redirect("dashboard")

    student_profile, created = StudentProfile.objects.get_or_create(user=request.user)
    classroom = get_object_or_404(ClassRoom, id=class_id)

    student_profile.class_room = classroom
    student_profile.status = "pending"   # ✅ wait for admin approval
    student_profile.admission_fee_paid = False
    student_profile.save()

    messages.success(request, f"You have applied for admission into {classroom.name}. Please wait for approval.")
    return redirect("student_profile")



@login_required
def admissions_manage_by_admin(request):
    if not request.user.is_admin():
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    pending_students = StudentProfile.objects.filter(status="pending")
    active_students = StudentProfile.objects.filter(status="active")
    rejected_students = StudentProfile.objects.filter(status="rejected")

    return render(request, "admin/manage_admissions.html", {
        "pending_students": pending_students,
        "active_students": active_students,
        "rejected_students": rejected_students,
    })
    
@login_required
def update_admission_status_by_admin(request, student_id, action):
    if not request.user.is_admin():
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    student = get_object_or_404(StudentProfile, id=student_id)

    if action == "approve":
        student.status = "active"
        student.admission_fee_paid = True  

        # 🔹 Assign monthly fee from class
        if student.class_room:
            student.monthly_fee = student.class_room.monthly_fee

        student.save()
        messages.success(request, f"{student.get_full_name()} approved! Monthly fee set to {student.monthly_fee}.")

    elif action == "reject":
        student.status = "rejected"
        student.save()
        messages.warning(request, f"{student.get_full_name()} has been rejected.")

    return redirect("manage_admissions")


@login_required
def pay_monthly_fee(request):
    if not request.user.is_student():
        messages.error(request, "Only students can pay fees.")
        return redirect("dashboard")

    student = request.user.student_profile

    if not student.class_room:
        messages.error(request, "You are not assigned to any class. Contact admin.")
        return redirect("dashboard")

    amount = student.class_room.monthly_fee  # ✅ Correct place

    if request.method == "POST":
        tx = PaymentTransaction.objects.create(
            student=student,
            amount=amount,
            provider="bkash",  # or user choice
            status="success",  # you can make it "initiated" until confirmed
            transaction_id=f"TXN-{random.randint(100000, 999999)}"
        )
        messages.success(request, f"Monthly fee of {amount} paid successfully!")
        return redirect("student_fee_history")

    return render(request, "student/pay_fee.html", {"student": student, "amount": amount})


@login_required
def student_fee_history(request):
    if not request.user.is_student():
        messages.error(request, "Only students can view fee history.")
        return redirect("dashboard")

    student = request.user.student_profile
    payments = PaymentTransaction.objects.filter(student=student).order_by("-created_at")

    return render(request, "student/fee_history.html", {"payments": payments, "student": student})


@login_required
def admin_fee_history(request):
    if not request.user.is_admin():
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    payments = PaymentTransaction.objects.select_related("student").order_by("-created_at")
    return render(request, "admin/fee_history.html", {"payments": payments})




@login_required
def fee_report_by_admin(request):
    if not request.user.is_admin():
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    today = now().date()
    start_of_month = today.replace(day=1)
    end_of_month = today.replace(day=monthrange(today.year, today.month)[1])

    students = StudentProfile.objects.filter(status="active").select_related("class_room")

    report = []
    for student in students:
        has_paid = PaymentTransaction.objects.filter(
            student=student,
            status="success",
            created_at__date__gte=start_of_month,
            created_at__date__lte=end_of_month
        ).exists()

        report.append({
            "student": student,
            "class_name": student.class_room.name if student.class_room else "Not Assigned",
            "monthly_fee": student.class_room.monthly_fee if student.class_room else 0,
            "has_paid": has_paid
        })

    return render(request, "admin/fee_report.html", {"report": report, "month": today.strftime("%B %Y")})


@login_required
def class_details(request, class_id):
    # Get the classroom object or return 404
    classroom = get_object_or_404(ClassRoom, id=class_id)
    
    # Check if user has permission to view this class
    if request.user.role == 'teacher' and classroom.teacher != request.user:
        messages.error(request, "You don't have permission to view this class.")
        return redirect('dashboard')
    
    # Students can only view classes they're enrolled in
    if request.user.role == 'student':
        student_profile = getattr(request.user, 'student_profile', None)
        if not student_profile or student_profile.class_room != classroom:
            messages.error(request, "You don't have permission to view this class.")
            return redirect('dashboard')
    
    # Get all courses for this classroom
    courses = Course.objects.filter(classroom=classroom)
    
    # Get all students in this classroom
    students = StudentProfile.objects.filter(class_room=classroom, status='active')
    
    # Get teacher profile if available
    teacher_profile = None
    if classroom.teacher:
        teacher_profile = getattr(classroom.teacher, 'teacher_profile', None)
    
    context = {
        'classroom': classroom,
        'courses': courses,
        'students': students,
        'teacher_profile': teacher_profile,
    }
    
    return render(request, 'teacher/class_details.html', context)



@login_required
def enroll_course(request, course_id):
    if not request.user.is_student():
        messages.error(request, "Only students can enroll in courses.")
        return redirect('dashboard')
    
    course = get_object_or_404(Course, id=course_id)
    student_profile = getattr(request.user, 'student_profile', None)
    
    if not student_profile:
        messages.error(request, "Student profile not found.")
        return redirect('dashboard')
    
    # Check if student is already enrolled
    if Enrollment.objects.filter(student=student_profile, course=course).exists():
        messages.warning(request, "You are already enrolled in this course.")
        return redirect('course_details', course_id=course.id)
    
    # Create enrollment
    Enrollment.objects.create(student=student_profile, course=course)
    messages.success(request, f"You have successfully enrolled in {course.title}.")
    
    return redirect('teacher/course_details', course_id=course.id)

@login_required
def course_details(request, course_id):
    # Get the course object or return 404
    course = get_object_or_404(Course, id=course_id)
    
    # Check if user has permission to view this course
    if request.user.role == 'teacher' and course.teacher != request.user:
        messages.error(request, "You don't have permission to view this course.")
        return redirect('dashboard')
    
    # Students can only view courses in their class
    if request.user.role == 'student':
        student_profile = getattr(request.user, 'student_profile', None)
        if not student_profile or student_profile.class_room != course.classroom:
            messages.error(request, "You don't have permission to view this course.")
            return redirect('dashboard')
    
    # Get all homeworks for this course
    homeworks = Homework.objects.filter(course=course).order_by('-created_at')
    
    # Get all enrollments for this course
    enrollments = Enrollment.objects.filter(course=course).select_related('student')
    
    # Get teacher profile if available
    teacher_profile = None
    if course.teacher:
        teacher_profile = getattr(course.teacher, 'teacher_profile', None)
    
    # Check if current student is enrolled
    is_enrolled = False
    if request.user.role == 'student':
        student_profile = getattr(request.user, 'student_profile', None)
        if student_profile:
            is_enrolled = Enrollment.objects.filter(student=student_profile, course=course).exists()
    
    context = {
        'course': course,
        'homeworks': homeworks,
        'enrollments': enrollments,
        'teacher_profile': teacher_profile,
        'is_enrolled': is_enrolled,
        'now': timezone,  # Add current time for homework due date comparison
    }
    
    return render(request, 'teacher/course_details.html', context)