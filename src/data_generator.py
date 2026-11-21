"""
Synthetic Examination Data Generator.

Generates courses, students, rooms and examination
time slots for the examination timetable scheduler.
"""

import random

from src.models import (
    Student,
    Course,
    Room,
    TimeSlot,
    ExamDataset
)


def generate_dataset(
    num_courses,
    num_students,
    num_rooms=5,
    num_time_slots=10,
    min_enrollment=1,
    max_enrollment=5,
    seed=None
):
    """
    Generate a synthetic examination dataset.

    Returns an ExamDataset object.
    """

    # Validate input parameters
    if num_courses < 1:
        raise ValueError("At least one course is required.")

    if num_students < 1:
        raise ValueError("At least one student is required.")

    if num_rooms < 1:
        raise ValueError("At least one room is required.")

    if num_time_slots < 1:
        raise ValueError("At least one time slot is required.")

    if min_enrollment < 1:
        raise ValueError("Minimum enrollment must be at least 1.")

    if max_enrollment < min_enrollment:
        raise ValueError(
            "Maximum enrollment cannot be smaller than minimum enrollment."
        )

    if max_enrollment > num_students:
        raise ValueError(
            "Maximum enrollment cannot exceed the number of students."
        )

    # Use a local random generator for reproducible results
    rng = random.Random(seed)

    # Generate students
    students = [
        Student(student_id=f"S{i:03d}")
        for i in range(1, num_students + 1)
    ]

    student_ids = [
        student.student_id for student in students
    ]

    # Generate rooms
    rooms = [
        Room(
            room_id=f"Room_{chr(65 + i)}",
            capacity=30 + (i * 10)
        )
        for i in range(num_rooms)
    ]

    # Generate courses and student enrollments
    courses = []

    for i in range(1, num_courses + 1):

        enrollment_size = rng.randint(
            min_enrollment,
            max_enrollment
        )

        enrolled_students = rng.sample(
            student_ids,
            enrollment_size
        )

        course = Course(
            course_id=f"CS{i:03d}",
            student_ids=enrolled_students
        )

        courses.append(course)

    # Generate examination time slots
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday"
    ]

    hours = [
        "09:00",
        "11:00",
        "13:00",
        "15:00"
    ]

    available_slots = [
        TimeSlot(day=day, start_time=hour)
        for day in days
        for hour in hours
    ]

    if num_time_slots > len(available_slots):
        raise ValueError(
            f"Maximum available time slots is "
            f"{len(available_slots)}."
        )

    time_slots = rng.sample(
        available_slots,
        num_time_slots
    )

    # Sort slots into chronological order
    day_order = {
        day: index for index, day in enumerate(days)
    }

    time_slots.sort(
        key=lambda slot: (
            day_order[slot.day],
            slot.start_time
        )
    )

    # Return the complete dataset
    return ExamDataset(
        courses=courses,
        students=students,
        rooms=rooms,
        time_slots=time_slots
    )


def generate_scheduler_inputs(**kwargs):
    """
    Generate data directly in the format expected
    by the optimization engine.
    """

    dataset = generate_dataset(**kwargs)

    courses, rooms, time_slots = (
        dataset.to_scheduler_inputs()
    )

    return {
        "courses": courses,
        "rooms": rooms,
        "time_slots": time_slots
    }


if __name__ == "__main__":

    dataset = generate_dataset(
        num_courses=5,
        num_students=20,
        num_rooms=3,
        num_time_slots=5,
        seed=42
    )

    courses, rooms, time_slots = (
        dataset.to_scheduler_inputs()
    )

    print("GENERATED EXAMINATION DATA")
    print("=" * 40)

    print("\nCourses and Enrollments:")
    print(courses)

    print("\nRooms and Capacities:")
    print(rooms)

    print("\nAvailable Time Slots:")
    print(time_slots)

    print("\nNumber of Students:")
    print(len(dataset.students))
