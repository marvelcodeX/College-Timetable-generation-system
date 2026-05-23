from django.db import models

TIME_SLOTS = (
    ('9:30 - 10:30', '9:30 - 10:30'),
    ('10:30 - 11:30', '10:30 - 11:30'),
    ('11:30 - 12:30', '11:30 - 12:30'),
    ('12:30 - 1:30', '12:30 - 1:30'),
    ('2:30 - 3:30', '2:30 - 3:30'),
    ('3:30 - 4:30', '3:30 - 4:30'),
    ('4:30 - 5:30', '4:30 - 5:30'),
)

DAYS_OF_WEEK = (
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
)


class Room(models.Model):
    r_number = models.CharField(max_length=6, unique=True)
    seating_capacity = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.r_number} (Cap: {self.seating_capacity})'


class Instructor(models.Model):
    uid = models.CharField(max_length=6, unique=True)
    name = models.CharField(max_length=25)

    def __str__(self):
        return f'{self.name} ({self.uid})'


class MeetingTime(models.Model):
    pid = models.CharField(max_length=4, primary_key=True)
    time = models.CharField(max_length=50, choices=TIME_SLOTS, default='11:30 - 12:30')
    day = models.CharField(max_length=15, choices=DAYS_OF_WEEK)

    class Meta:
        unique_together = ('time', 'day')

    def __str__(self):
        return f'{self.day} {self.time}'


class Course(models.Model):
    course_number = models.CharField(max_length=5, primary_key=True)
    course_name = models.CharField(max_length=40)
    max_numb_students = models.IntegerField(default=30)
    instructors = models.ManyToManyField(Instructor)

    def __str__(self):
        return f'{self.course_name} ({self.course_number})'


class Department(models.Model):
    dept_name = models.CharField(max_length=50)
    courses = models.ManyToManyField(Course)

    def __str__(self):
        return self.dept_name


class Section(models.Model):
    section_id = models.CharField(max_length=25, primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    num_class_in_week = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.section_id} ({self.department})'
