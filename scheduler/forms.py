from django.forms import ModelForm
from .models import *
from django import forms


class RoomForm(ModelForm):
    class Meta:
        model = Room
        labels = {
            "r_number": "Room ID",
            "seating_capacity": "Seating Capacity"
        }
        fields = ['r_number', 'seating_capacity']
        widgets = {
            'r_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. R101'}),
            'seating_capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 60'}),
        }


class InstructorForm(ModelForm):
    class Meta:
        model = Instructor
        labels = {
            "uid": "Teacher ID",
            "name": "Full Name"
        }
        fields = ['uid', 'name']
        widgets = {
            'uid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. T001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Dr. Smith'}),
        }


class MeetingTimeForm(ModelForm):
    class Meta:
        model = MeetingTime
        fields = ['pid', 'time', 'day']
        widgets = {
            'pid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MT1'}),
            'time': forms.Select(attrs={'class': 'form-control'}),
            'day': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            "pid": "Slot ID",
            "time": "Time Slot",
            "day": "Day of Week"
        }


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['course_number', 'course_name', 'max_numb_students', 'instructors']
        labels = {
            "course_number": "Course Code",
            "course_name": "Course Name",
            "max_numb_students": "Max Students",
            "instructors": "Assigned Teachers"
        }
        widgets = {
            'course_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CS101'}),
            'course_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Data Structures'}),
            'max_numb_students': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 60'}),
            'instructors': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class DepartmentForm(ModelForm):
    class Meta:
        model = Department
        fields = ['dept_name', 'courses']
        labels = {
            "dept_name": "Department Name",
            "courses": "Courses Offered"
        }
        widgets = {
            'dept_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Science'}),
            'courses': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class SectionForm(ModelForm):
    class Meta:
        model = Section
        fields = ['section_id', 'department', 'num_class_in_week']
        labels = {
            "section_id": "Section ID",
            "department": "Department",
            "num_class_in_week": "Classes Per Week"
        }
        widgets = {
            'section_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CS-A'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'num_class_in_week': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 20'}),
        }
