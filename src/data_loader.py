"""
Examination Data Loader.

Loads examination datasets from CSV and JSON files,
validates the information and converts it into
the format expected by the optimization engine.
"""

import csv
import json

from pathlib import Path

from src.models import (
    Student,
    Course,
    Room,
    TimeSlot,
    ExamDataset
)


def validate_dataset(dataset):
    """Validate an examination dataset."""

    if not dataset.courses:
        raise ValueError("The dataset contains no courses.")

    if not dataset.rooms:
        raise ValueError("The dataset contains no rooms.")

    if not dataset.time_slots:
        raise ValueError("The dataset contains no time slots.")

    # Validate course IDs and enrollments
    course_ids = [
        course.course_id for course in dataset.courses
    ]

    if len(course_ids) != len(set(course_ids)):
        raise ValueError("Duplicate course IDs found.")

    student_ids = {
        student.student_id for student in dataset.students
    }

    for course in dataset.courses:

        if not course.course_id:
            raise ValueError("A course has a missing ID.")

        if not course.student_ids:
            raise ValueError(
                f"Course {course.course_id} has no enrolled students."
            )

        if len(course.student_ids) != len(set(course.student_ids)):
            raise ValueError(
                f"Duplicate enrollments in {course.course_id}."
            )

        for student_id in course.student_ids:

            if student_id not in student_ids:
                raise ValueError(
                    f"Unknown student ID: {student_id}"
                )

    # Validate rooms
    room_ids = [
        room.room_id for room in dataset.rooms
    ]

    if len(room_ids) != len(set(room_ids)):
        raise ValueError("Duplicate room IDs found.")

    for room in dataset.rooms:

        if not room.room_id:
            raise ValueError("A room has a missing ID.")

        if (
            not isinstance(room.capacity, int)
            or isinstance(room.capacity, bool)
            or room.capacity <= 0
        ):
            raise ValueError(
                f"Invalid capacity for room {room.room_id}."
            )

    # Validate time slots
    slot_names = [
        slot.to_string() for slot in dataset.time_slots
    ]

    if len(slot_names) != len(set(slot_names)):
        raise ValueError("Duplicate time slots found.")

    for slot in dataset.time_slots:

        if not slot.day or not slot.start_time:
            raise ValueError("A time slot has missing information.")

    return dataset


def load_json_data(filename):
    """
    Load examination data from a JSON file.

    Expected structure:

    {
        "courses": {
            "CS101": ["S001", "S002"],
            "CS102": ["S003"]
        },
        "rooms": {
            "Room_A": 30,
            "Room_B": 40
        },
        "time_slots": [
            "Monday_09:00",
            "Tuesday_13:00"
        ]
    }
    """

    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("JSON data must contain an object.")

    required = {"courses", "rooms", "time_slots"}

    missing = required - set(data.keys())

    if missing:
        raise ValueError(
            f"Missing JSON sections: {', '.join(sorted(missing))}"
        )

    if not all(isinstance(data[key], dict) for key in ("courses", "rooms")):
        raise ValueError("Courses and rooms must be JSON objects.")

    if not isinstance(data["time_slots"], list):
        raise ValueError("Time slots must be a JSON list.")

    courses = [
        Course(
            course_id=course_id,
            student_ids=student_list
        )
        for course_id, student_list in data["courses"].items()
    ]

    rooms = [
        Room(
            room_id=room_id,
            capacity=capacity
        )
        for room_id, capacity in data["rooms"].items()
    ]

    time_slots = []

    for slot in data["time_slots"]:

        if not isinstance(slot, str) or "_" not in slot:
            raise ValueError(
                f"Invalid time slot format: {slot}"
            )

        day, start_time = slot.rsplit("_", 1)

        time_slots.append(
            TimeSlot(day=day, start_time=start_time)
        )

    # Collect all unique enrolled students
    student_ids = sorted({
        student_id
        for course in courses
        for student_id in course.student_ids
    })

    students = [
        Student(student_id=student_id)
        for student_id in student_ids
    ]

    dataset = ExamDataset(
        courses=courses,
        students=students,
        rooms=rooms,
        time_slots=time_slots
    )

    return validate_dataset(dataset)


def load_csv_data(
    courses_file,
    rooms_file,
    time_slots_file
):
    """
    Load examination data from three CSV files.

    courses.csv:
        course_id,student_id

    rooms.csv:
        room_id,capacity

    time_slots.csv:
        day,start_time
    """

    # Load courses and student enrollments
    course_enrollments = {}

    with open(courses_file, "r", encoding="utf-8-sig", newline="") as file:

        reader = csv.DictReader(file)

        if not {"course_id", "student_id"}.issubset(reader.fieldnames or []):
            raise ValueError(
                "courses.csv must contain course_id and student_id columns."
            )

        for row in reader:

            course_id = (row.get("course_id") or "").strip()
            student_id = (row.get("student_id") or "").strip()

            if not course_id or not student_id:
                raise ValueError(
                    "Missing course ID or student ID in courses.csv."
                )

            course_enrollments.setdefault(course_id, [])

            if student_id in course_enrollments[course_id]:
                raise ValueError(
                    f"Duplicate enrollment: {course_id}, {student_id}"
                )

            course_enrollments[course_id].append(student_id)

    courses = [
        Course(
            course_id=course_id,
            student_ids=student_ids
        )
        for course_id, student_ids in course_enrollments.items()
    ]

    # Load rooms
    rooms = []

    with open(rooms_file, "r", encoding="utf-8-sig", newline="") as file:

        reader = csv.DictReader(file)

        if not {"room_id", "capacity"}.issubset(reader.fieldnames or []):
            raise ValueError(
                "rooms.csv must contain room_id and capacity columns."
            )

        for row in reader:

            room_id = (row.get("room_id") or "").strip()
            capacity = (row.get("capacity") or "").strip()

            if not room_id or not capacity:
                raise ValueError("Missing room information.")

            try:
                capacity = int(capacity)
            except ValueError:
                raise ValueError(
                    f"Invalid capacity for room {room_id}."
                )

            rooms.append(
                Room(room_id=room_id, capacity=capacity)
            )

    # Load examination time slots
    time_slots = []

    with open(time_slots_file, "r", encoding="utf-8-sig", newline="") as file:

        reader = csv.DictReader(file)

        if not {"day", "start_time"}.issubset(reader.fieldnames or []):
            raise ValueError(
                "time_slots.csv must contain day and start_time columns."
            )

        for row in reader:

            day = (row.get("day") or "").strip()
            start_time = (row.get("start_time") or "").strip()

            if not day or not start_time:
                raise ValueError("Missing time slot information.")

            time_slots.append(
                TimeSlot(day=day, start_time=start_time)
            )

    # Collect unique students from all enrollments
    student_ids = sorted({
        student_id
        for course in courses
        for student_id in course.student_ids
    })

    students = [
        Student(student_id=student_id)
        for student_id in student_ids
    ]

    dataset = ExamDataset(
        courses=courses,
        students=students,
        rooms=rooms,
        time_slots=time_slots
    )

    return validate_dataset(dataset)


def to_scheduler_inputs(dataset):
    """Convert a validated dataset to scheduler inputs."""

    courses, rooms, time_slots = (
        dataset.to_scheduler_inputs()
    )

    return {
        "courses": courses,
        "rooms": rooms,
        "time_slots": time_slots
    }


if __name__ == "__main__":

    print("Data loader module is ready.")
    print("Use load_json_data() or load_csv_data() to load datasets.")
