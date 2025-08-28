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
    
    
    path('forgot_password/', views.request_password_reset, name='forgot_password'),
    path('verify_otp/<str:email>/', views.verify_otp, name='verify_otp'),
    path('reset_password/<str:email>/', views.reset_password, name='reset_password'),
    
    path('change_password/', views.change_password, name='change_password'),
    path('password_change_complete/', views.password_change_complete, name='password_change_complete'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('student_profile/', views.student_profile, name='student_profile'),
    path('student_profile_and_edit/', views.student_profile_and_edit, name='student_profile_and_edit'),
    
    path('teacher_profile/', views.teacher_profile, name='teacher_profile'),
    path('teacher_profile_edit/', views.teacher_profile_edit, name='teacher_profile_edit'),
    
    path('admin_profile/', views.admin_profile, name='admin_profile'),
    path('admin_profile_edit/', views.admin_profile_edit, name='admin_profile_edit'),
    
    
       # Course
    path("teacher/courses/create/", views.create_course, name="create_course"),
    path("teacher/courses", views.teacher_courses, name="teacher_courses"),

    # Homework Management for Teachers 
    path("teacher/homework/create/<int:course_id>", views.create_homework, name="create_homework"),

    path("course/<int:course_id>/homeworks/", views.course_homeworks, name="course_homeworks"),
    path("teacher/teacher_homeworks/", views.teacher_homeworks, name="teacher_homeworks"),
    path("teacher/view_submissions/<int:homework_id>", views.view_submissions, name="view_submissions"),
    
    # Homework Management for Students
    path("student/homework/", views.student_homeworks, name="student_homeworks"),
    path("student/homework/<int:pk>/submit/", views.submit_homework, name="submit_homework"),
    
    
    
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('api/bus/locations/', views.bus_locations_json, name='bus_locations_json'),
    
    
    path("add_teacher_by_admin/", views.add_teacher_by_admin, name="add_teacher_by_admin"),
    path("manage_users_by_admin/", views.manage_users_by_admin, name="manage_users_by_admin"),
    path("edit_user_by_admin/<int:user_id>/edit/", views.edit_user_by_admin, name="edit_user_by_admin"),
    
    
    path("manage_classes_by_admin/", views.manage_classes_by_admin, name="manage_classes_by_admin"),
    path("add_class_by_admin/", views.add_class_by_admin, name="add_class_by_admin"),
    path("edit_class_by_admin/<int:class_id>/edit/", views.edit_class_by_admin, name="edit_class_by_admin"),
    
    path("classes/", views.available_classes, name="available_classes"),
    path("classes/apply/<int:class_id>/", views.apply_for_class, name="apply_for_class"),
    
    path("admissions_manage_by_admin/", views.admissions_manage_by_admin, name="admissions_manage_by_admin"),
    path("update_admission_status_by_admin/<int:student_id>/<str:action>/", views.update_admission_status_by_admin, name="update_admission_status_by_admin"),
    
    path("student/pay-fee/", views.pay_monthly_fee, name="pay_monthly_fee"),
    
    # Student
    path("student_fee-history/", views.student_fee_history, name="student_fee_history"),

    # Admin
    path("admin_fee-history/", views.admin_fee_history, name="admin_fee_history"),
    
    path("fee_report_by_admin/", views.fee_report_by_admin, name="fee_report_by_admin"),
    
    
    
    path("class/<int:class_id>/details/", views.class_details, name="class_details"),
    path("course/<int:course_id>/details/", views.course_details, name="course_details"),
    path("course/<int:course_id>/enroll/", views.enroll_course, name="enroll_course"),
    
]
