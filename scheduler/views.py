from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import (RoomForm, InstructorForm, MeetingTimeForm,
                    CourseForm, DepartmentForm, SectionForm)
from .models import Room, Instructor, MeetingTime, Course, Department, Section
from .algorithm import generate_timetable


# ── Public Pages ──────────────────────────────────────────────

def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def help_page(request):
    return render(request, 'help.html')


# ── Dashboard ─────────────────────────────────────────────────

@login_required
def dashboard(request):
    context = {
        'num_teachers': Instructor.objects.count(),
        'num_rooms': Room.objects.count(),
        'num_timeslots': MeetingTime.objects.count(),
        'num_courses': Course.objects.count(),
        'num_departments': Department.objects.count(),
        'num_sections': Section.objects.count(),
    }
    return render(request, 'dashboard/home.html', context)


# ── CRUD Helpers ──────────────────────────────────────────────

def _crud_add(request, form_class, template, redirect_name, entity_name):
    """Generic add view for any model form."""
    form = form_class(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{entity_name} added successfully.')
        return redirect(redirect_name)
    return render(request, template, {'form': form})


def _crud_list(request, queryset, template, context_key):
    """Generic list view."""
    return render(request, template, {context_key: queryset})


def _crud_delete(request, model, pk, redirect_name, entity_name):
    """Generic delete view."""
    obj = model.objects.filter(pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, f'{entity_name} deleted.')
    return redirect(redirect_name)


# ── Teachers ──────────────────────────────────────────────────

@login_required
def add_instructor(request):
    return _crud_add(request, InstructorForm,
                     'dashboard/add_instructor.html', 'add_instructor', 'Teacher')

@login_required
def instructor_list(request):
    return _crud_list(request, Instructor.objects.all(),
                      'dashboard/instructor_list.html', 'instructors')

@login_required
def delete_instructor(request, pk):
    return _crud_delete(request, Instructor, pk, 'instructor_list', 'Teacher')


# ── Rooms ─────────────────────────────────────────────────────

@login_required
def add_room(request):
    return _crud_add(request, RoomForm,
                     'dashboard/add_room.html', 'add_room', 'Room')

@login_required
def room_list(request):
    return _crud_list(request, Room.objects.all(),
                      'dashboard/room_list.html', 'rooms')

@login_required
def delete_room(request, pk):
    return _crud_delete(request, Room, pk, 'room_list', 'Room')


# ── Time Slots ────────────────────────────────────────────────

@login_required
def add_timeslot(request):
    return _crud_add(request, MeetingTimeForm,
                     'dashboard/add_timeslot.html', 'add_timeslot', 'Time Slot')

@login_required
def timeslot_list(request):
    return _crud_list(request, MeetingTime.objects.all(),
                      'dashboard/timeslot_list.html', 'timeslots')

@login_required
def delete_timeslot(request, pk):
    return _crud_delete(request, MeetingTime, pk, 'timeslot_list', 'Time Slot')


# ── Courses ───────────────────────────────────────────────────

@login_required
def add_course(request):
    return _crud_add(request, CourseForm,
                     'dashboard/add_course.html', 'add_course', 'Course')

@login_required
def course_list(request):
    return _crud_list(request, Course.objects.all(),
                      'dashboard/course_list.html', 'courses')

@login_required
def delete_course(request, pk):
    return _crud_delete(request, Course, pk, 'course_list', 'Course')


# ── Departments ───────────────────────────────────────────────

@login_required
def add_department(request):
    return _crud_add(request, DepartmentForm,
                     'dashboard/add_department.html', 'add_department', 'Department')

@login_required
def department_list(request):
    return _crud_list(request, Department.objects.all(),
                      'dashboard/department_list.html', 'departments')

@login_required
def delete_department(request, pk):
    return _crud_delete(request, Department, pk, 'department_list', 'Department')


# ── Sections ──────────────────────────────────────────────────

@login_required
def add_section(request):
    return _crud_add(request, SectionForm,
                     'dashboard/add_section.html', 'add_section', 'Section')

@login_required
def section_list(request):
    return _crud_list(request, Section.objects.all(),
                      'dashboard/section_list.html', 'sections')

@login_required
def delete_section(request, pk):
    return _crud_delete(request, Section, pk, 'section_list', 'Section')


# ── Timetable Generation ─────────────────────────────────────

@login_required
def generate_page(request):
    """Show the generation launch page with data summary."""
    context = {
        'num_teachers': Instructor.objects.count(),
        'num_rooms': Room.objects.count(),
        'num_timeslots': MeetingTime.objects.count(),
        'num_courses': Course.objects.count(),
        'num_departments': Department.objects.count(),
        'num_sections': Section.objects.count(),
    }
    return render(request, 'dashboard/generate.html', context)


@login_required
def timetable(request):
    """Run the genetic algorithm and display results."""
    try:
        best_schedule, generations, is_perfect = generate_timetable()
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('generate')

    # Organize schedule into a grid: section → day → time → class
    sections = Section.objects.all()
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    times = MeetingTime.objects.values_list('time', flat=True).distinct()
    times = sorted(set(times))

    timetable_data = {}
    for section in sections:
        section_classes = [c for c in best_schedule.classes if c.section_id == section.section_id]
        grid = {}
        for day in days_order:
            grid[day] = {}
            for time in times:
                grid[day][time] = None

        for c in section_classes:
            day = c.meeting_time.day
            time = c.meeting_time.time
            grid[day][time] = {
                'course': str(c.course),
                'instructor': str(c.instructor),
                'room': str(c.room),
            }

        timetable_data[section] = grid

    context = {
        'timetable_data': timetable_data,
        'days': days_order,
        'times': times,
        'generations': generations,
        'is_perfect': is_perfect,
        'conflicts': best_schedule.num_conflicts,
    }
    return render(request, 'dashboard/timetable_result.html', context)

