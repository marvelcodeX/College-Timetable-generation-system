"""
Genetic Algorithm for College Timetable Generation.

Hard constraints (must be satisfied — fitness penalty):
  1. No instructor teaches two classes at the same time
  2. No room is double-booked at the same time
  3. No section has two classes at the same time
  4. Room capacity >= course enrollment

Soft constraints (optimization goals):
  5. Balanced spread of classes across the week for each section
"""

import random

# GA Parameters
POPULATION_SIZE = 25
MAX_GENERATIONS = 500
ELITE_COUNT = 2
TOURNAMENT_SIZE = 5
MUTATION_RATE = 0.10
CROSSOVER_RATE = 0.85


class ScheduleClass:
    """A single scheduled class — one gene in the chromosome."""

    __slots__ = ('section_id', 'department', 'course', 'instructor',
                 'meeting_time', 'room')

    def __init__(self, section_id, department, course):
        self.section_id = section_id
        self.department = department
        self.course = course
        self.instructor = None
        self.meeting_time = None
        self.room = None

    def __repr__(self):
        return (f"<Class {self.course} | {self.section_id} | "
                f"{self.meeting_time} | {self.room} | {self.instructor}>")


class TimetableData:
    """Loads all required data from the database once."""

    def __init__(self):
        from .models import Room, Instructor, MeetingTime, Course, Department, Section
        self.rooms = list(Room.objects.all())
        self.instructors = list(Instructor.objects.all())
        self.meeting_times = list(MeetingTime.objects.all())
        self.courses = list(Course.objects.all())
        self.departments = list(Department.objects.all())
        self.sections = list(Section.objects.all())

    def validate(self):
        """Check that we have enough data to attempt generation."""
        errors = []
        if not self.rooms:
            errors.append("No rooms defined.")
        if not self.meeting_times:
            errors.append("No time slots defined.")
        if not self.sections:
            errors.append("No sections defined.")
        if not self.courses:
            errors.append("No courses defined.")
        for section in self.sections:
            dept_courses = section.department.courses.all()
            if not dept_courses.exists():
                errors.append(f"Section '{section.section_id}': department '{section.department}' has no courses.")
        return errors


class Schedule:
    """A chromosome — a complete timetable candidate."""

    def __init__(self, data):
        self.data = data
        self.classes = []
        self.fitness = -1
        self.num_conflicts = 0

    def initialize(self):
        """Create random schedule respecting section/course structure."""
        for section in self.data.sections:
            dept_courses = list(section.department.courses.all())
            if not dept_courses:
                continue

            n = section.num_class_in_week
            slots_available = len(self.data.meeting_times)
            classes_to_schedule = min(n, slots_available)

            # Distribute classes across courses
            per_course = max(1, classes_to_schedule // len(dept_courses))
            remainder = classes_to_schedule - per_course * len(dept_courses)

            for course in dept_courses:
                course_instructors = list(course.instructors.all())
                if not course_instructors:
                    continue

                count = per_course + (1 if remainder > 0 else 0)
                if remainder > 0:
                    remainder -= 1

                for _ in range(count):
                    sc = ScheduleClass(section.section_id, section.department, course)
                    sc.meeting_time = random.choice(self.data.meeting_times)
                    sc.room = random.choice(self.data.rooms)
                    sc.instructor = random.choice(course_instructors)
                    self.classes.append(sc)

        self.fitness = -1
        return self

    def calculate_fitness(self):
        """Evaluate fitness based on hard and soft constraint violations."""
        conflicts = 0

        for i in range(len(self.classes)):
            ci = self.classes[i]

            # Hard constraint: room capacity
            if ci.room.seating_capacity < ci.course.max_numb_students:
                conflicts += 1

            for j in range(i + 1, len(self.classes)):
                cj = self.classes[j]

                # Only check classes at the same time
                if ci.meeting_time.pk != cj.meeting_time.pk:
                    continue

                # Hard constraint: room double-booking
                if ci.room.pk == cj.room.pk:
                    conflicts += 1

                # Hard constraint: instructor double-booking
                if ci.instructor.pk == cj.instructor.pk:
                    conflicts += 1

                # Hard constraint: section double-booking
                if ci.section_id == cj.section_id:
                    conflicts += 1

        self.num_conflicts = conflicts
        self.fitness = 1.0 / (1.0 + conflicts)
        return self.fitness

    def get_fitness(self):
        if self.fitness < 0:
            self.calculate_fitness()
        return self.fitness


class Population:
    """A collection of schedule candidates."""

    def __init__(self, data, size):
        self.schedules = []
        for _ in range(size):
            self.schedules.append(Schedule(data).initialize())


class GeneticAlgorithm:
    """Evolves a population of schedules toward conflict-free timetables."""

    def __init__(self, data):
        self.data = data

    def evolve(self, population):
        """One generation: selection → crossover → mutation."""
        # Sort by fitness descending
        population.schedules.sort(key=lambda s: s.get_fitness(), reverse=True)

        new_pop = Population(self.data, 0)

        # Elitism: keep the best schedules
        for i in range(ELITE_COUNT):
            new_pop.schedules.append(population.schedules[i])

        # Fill the rest via crossover + mutation
        while len(new_pop.schedules) < POPULATION_SIZE:
            parent1 = self._tournament_select(population)
            parent2 = self._tournament_select(population)

            if random.random() < CROSSOVER_RATE:
                child = self._crossover(parent1, parent2)
            else:
                child = self._clone(parent1)

            self._mutate(child)
            new_pop.schedules.append(child)

        return new_pop

    def _tournament_select(self, population):
        """Tournament selection: pick the best from a random subset."""
        tournament = random.sample(population.schedules,
                                   min(TOURNAMENT_SIZE, len(population.schedules)))
        return max(tournament, key=lambda s: s.get_fitness())

    def _crossover(self, parent1, parent2):
        """Uniform crossover: each gene from either parent."""
        child = Schedule(self.data)
        child.classes = []

        size = min(len(parent1.classes), len(parent2.classes))
        for i in range(size):
            if random.random() < 0.5:
                child.classes.append(self._copy_class(parent1.classes[i]))
            else:
                child.classes.append(self._copy_class(parent2.classes[i]))

        # If parents differ in length, append remaining from the longer
        longer = parent1 if len(parent1.classes) >= len(parent2.classes) else parent2
        for i in range(size, len(longer.classes)):
            child.classes.append(self._copy_class(longer.classes[i]))

        return child

    def _mutate(self, schedule):
        """Random mutation: re-randomize genes with MUTATION_RATE probability."""
        for sc in schedule.classes:
            if random.random() < MUTATION_RATE:
                sc.meeting_time = random.choice(self.data.meeting_times)
            if random.random() < MUTATION_RATE:
                sc.room = random.choice(self.data.rooms)
            if random.random() < MUTATION_RATE:
                course_instructors = list(sc.course.instructors.all())
                if course_instructors:
                    sc.instructor = random.choice(course_instructors)

    def _clone(self, schedule):
        """Deep-copy a schedule."""
        clone = Schedule(self.data)
        clone.classes = [self._copy_class(c) for c in schedule.classes]
        return clone

    @staticmethod
    def _copy_class(sc):
        new_sc = ScheduleClass(sc.section_id, sc.department, sc.course)
        new_sc.instructor = sc.instructor
        new_sc.meeting_time = sc.meeting_time
        new_sc.room = sc.room
        return new_sc


def generate_timetable():
    """
    Main entry point: run the GA and return the best schedule found.
    Returns (schedule, generation_num, is_perfect) or raises ValueError.
    """
    data = TimetableData()
    errors = data.validate()
    if errors:
        raise ValueError("Cannot generate timetable:\n" + "\n".join(errors))

    population = Population(data, POPULATION_SIZE)
    ga = GeneticAlgorithm(data)

    best_schedule = None
    generation = 0

    for generation in range(1, MAX_GENERATIONS + 1):
        population = ga.evolve(population)
        population.schedules.sort(key=lambda s: s.get_fitness(), reverse=True)
        best = population.schedules[0]

        if best_schedule is None or best.get_fitness() > best_schedule.get_fitness():
            best_schedule = best

        # Perfect solution found
        if best.get_fitness() >= 1.0:
            return best, generation, True

    # Return best-effort result
    return best_schedule, generation, (best_schedule.get_fitness() >= 1.0)
