from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('',views.homepage, name='homepage'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('SRS/', views.SRS, name='SRS'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register_student, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('student_profile/', views.student_profile, name='student_profile'),
    path('student_profile_and_edit/', views.student_profile_and_edit, name='student_profile_and_edit'),
    
    path('teacher_profile/', views.teacher_profile, name='teacher_profile'),
    path('teacher_profile_edit/', views.teacher_profile_edit, name='teacher_profile_edit'),
    
    path('teacher/homework/create/', views.create_homework, name='create_homework'),
    path('student/homework/<int:pk>/submit/', views.submit_homework, name='submit_homework'),
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('api/bus/locations/', views.bus_locations_json, name='bus_locations_json'),
]
