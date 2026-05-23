from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('help/', views.help_page, name='help'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Teachers
    path('dashboard/teachers/add/', views.add_instructor, name='add_instructor'),
    path('dashboard/teachers/', views.instructor_list, name='instructor_list'),
    path('dashboard/teachers/delete/<int:pk>/', views.delete_instructor, name='delete_instructor'),

    # Rooms
    path('dashboard/rooms/add/', views.add_room, name='add_room'),
    path('dashboard/rooms/', views.room_list, name='room_list'),
    path('dashboard/rooms/delete/<int:pk>/', views.delete_room, name='delete_room'),

    # Time Slots
    path('dashboard/timeslots/add/', views.add_timeslot, name='add_timeslot'),
    path('dashboard/timeslots/', views.timeslot_list, name='timeslot_list'),
    path('dashboard/timeslots/delete/<str:pk>/', views.delete_timeslot, name='delete_timeslot'),

    # Courses
    path('dashboard/courses/add/', views.add_course, name='add_course'),
    path('dashboard/courses/', views.course_list, name='course_list'),
    path('dashboard/courses/delete/<str:pk>/', views.delete_course, name='delete_course'),

    # Departments
    path('dashboard/departments/add/', views.add_department, name='add_department'),
    path('dashboard/departments/', views.department_list, name='department_list'),
    path('dashboard/departments/delete/<int:pk>/', views.delete_department, name='delete_department'),

    # Sections
    path('dashboard/sections/add/', views.add_section, name='add_section'),
    path('dashboard/sections/', views.section_list, name='section_list'),
    path('dashboard/sections/delete/<str:pk>/', views.delete_section, name='delete_section'),

    # Timetable Generation
    path('dashboard/generate/', views.generate_page, name='generate'),
    path('dashboard/timetable/', views.timetable, name='timetable'),
]
