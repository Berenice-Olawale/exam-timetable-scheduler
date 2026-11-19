
import unittest
from contextlib import redirect_stdout
from io import StringIO

from src.scheduler import ExamScheduler


class TestExamScheduler(unittest.TestCase):

    def setUp(self):
        self.courses = {
            "CS101": ["S001", "S002", "S003"],
            "CS102": ["S001", "S004"],
            "CS103": ["S002", "S005"]
        }

        self.rooms = {
            "Room_A": 5,
            "Room_B": 3
        }

        self.time_slots = [
            "Monday_09:00",
            "Monday_13:00",
            "Tuesday_09:00"
        ]

    def test_valid_timetable_is_generated(self):
        scheduler = ExamScheduler(
            self.courses, self.rooms, self.time_slots
        )

        with redirect_stdout(StringIO()):
            timetable = scheduler.solve()

        self.assertIsNotNone(timetable)
        self.assertEqual(len(timetable), len(self.courses))

    def test_no_student_has_simultaneous_exams(self):
        scheduler = ExamScheduler(
            self.courses, self.rooms, self.time_slots
        )

        with redirect_stdout(StringIO()):
            timetable = scheduler.solve()

        self.assertIsNotNone(timetable)

        for i in range(len(timetable)):
            for j in range(i + 1, len(timetable)):
                exam_a = timetable[i]
                exam_b = timetable[j]

                if exam_a["time_slot"] == exam_b["time_slot"]:
                    students_a = set(self.courses[exam_a["course"]])
                    students_b = set(self.courses[exam_b["course"]])

                    self.assertTrue(
                        students_a.isdisjoint(students_b),
                        "A student has two exams at the same time."
                    )

    def test_no_room_is_double_booked(self):
        scheduler = ExamScheduler(
            self.courses, self.rooms, self.time_slots
        )

        with redirect_stdout(StringIO()):
            timetable = scheduler.solve()

        self.assertIsNotNone(timetable)

        bookings = [
            (exam["room"], exam["time_slot"])
            for exam in timetable
        ]

        self.assertEqual(len(bookings), len(set(bookings)))

    def test_room_capacity_is_respected(self):
        scheduler = ExamScheduler(
            self.courses, self.rooms, self.time_slots
        )

        with redirect_stdout(StringIO()):
            timetable = scheduler.solve()

        self.assertIsNotNone(timetable)

        for exam in timetable:
            room_capacity = self.rooms[exam["room"]]

            self.assertLessEqual(
                exam["student_count"],
                room_capacity
            )

    def test_oversized_course_is_rejected(self):
        invalid_courses = {
            "CS101": ["S001", "S002", "S003", "S004", "S005", "S006"]
        }

        scheduler = ExamScheduler(
            invalid_courses,
            self.rooms,
            self.time_slots
        )

        with self.assertRaises(ValueError):
            scheduler.validate_inputs()

    def test_infeasible_schedule_is_reported(self):
        conflicting_courses = {
            "CS101": ["S001"],
            "CS102": ["S001"]
        }

        one_room = {
            "Room_A": 5
        }

        one_time_slot = [
            "Monday_09:00"
        ]

        scheduler = ExamScheduler(
            conflicting_courses,
            one_room,
            one_time_slot
        )

        output = StringIO()

        with redirect_stdout(output):
            timetable = scheduler.solve()

        self.assertIsNone(timetable)
        self.assertIn("Infeasible", output.getvalue())


if __name__ == "__main__":
    unittest.main()
