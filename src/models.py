from dataclasses import dataclass, field
from typing import List, Dict, Tuple


@dataclass
class Student:
    """Represents a student."""
    student_id: str


@dataclass
class Course:
    """Represents a course and its enrolled students."""
    course_id: str
    student_ids: List[str] = field(default_factory=list)


@dataclass
class Room:
    """Represents an examination room."""
    room_id: str
    capacity: int


@dataclass
class TimeSlot:
    """Represents an examination day and starting time."""
    day: str
    start_time: str

    def to_string(self) -> str:
        return f"{self.day}_{self.start_time}"


@dataclass
class ExamDataset:
    """Stores all examination data."""

    courses: List[Course]
    students: List[Student]
    rooms: List[Room]
    time_slots: List[TimeSlot]

    def to_scheduler_inputs(self) -> Tuple[Dict, Dict, List[str]]:
        """
        Converts the dataset into the format expected
        by the optimization engine.
        """

        courses_dict = {
            course.course_id: course.student_ids
            for course in self.courses
        }

        rooms_dict = {
            room.room_id: room.capacity
            for room in self.rooms
        }

        time_slots_list = [
            slot.to_string()
            for slot in self.time_slots
        ]

        return courses_dict, rooms_dict, time_slots_list
