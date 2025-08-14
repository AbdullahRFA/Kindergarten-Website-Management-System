from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from .models import User, StudentProfile, Course, Homework, HomeworkSubmission, PaymentTransaction, BusLocation, Bus
from .forms import StudentRegistrationForm, HomeworkForm, SubmissionForm, LeaveRequestForm, StudentProfileForm


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
