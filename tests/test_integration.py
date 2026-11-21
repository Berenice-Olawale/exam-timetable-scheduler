import unittest

from src.scheduler import ExamScheduler
from src.visualizer import normalize_timetable


class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.courses = {
            "CS101": ["S001", "S002"],
            "CS102": ["S003", "S004"],
            "CS103": ["S001", "S003"]
        }

        self.rooms = {
            "Room_A": 10,
            "Room_B": 20
        }

        self.time_slots = [
            "Monday_09:00",
            "Monday_13:00",
            "Tuesday_09:00"
        ]

    def test_scheduler_produces_timetable(self):
        scheduler = ExamScheduler(
            self.courses,
            self.rooms,
            self.time_slots
        )

        timetable = scheduler.solve()

        self.assertIsNotNone(timetable)
        self.assertEqual(len(timetable), len(self.courses))

    def test_timetable_contains_required_fields(self):
        scheduler = ExamScheduler(
            self.courses,
            self.rooms,
            self.time_slots
        )

        timetable = scheduler.solve()

        self.assertIsNotNone(timetable)

        for exam in timetable:
            self.assertIn("course", exam)
            self.assertIn("room", exam)
            self.assertIn("time_slot", exam)
            self.assertIn("day", exam)
            self.assertIn("student_count", exam)

    def test_visualizer_accepts_scheduler_output(self):
        scheduler = ExamScheduler(
            self.courses,
            self.rooms,
            self.time_slots
        )

        timetable = scheduler.solve()

        self.assertIsNotNone(timetable)

        timetable_dict = {
            exam["course"]: {
                "time_slot": exam["time_slot"],
                "room": exam["room"]
            }
            for exam in timetable
        }

        result = normalize_timetable(timetable_dict)

        self.assertEqual(len(result), len(self.courses))

    def test_all_courses_are_scheduled(self):
        scheduler = ExamScheduler(
            self.courses,
            self.rooms,
            self.time_slots
        )

        timetable = scheduler.solve()

        self.assertIsNotNone(timetable)

        scheduled_courses = {
            exam["course"]
            for exam in timetable
        }

        self.assertEqual(
            scheduled_courses,
            set(self.courses.keys())
        )


if __name__ == "__main__":
    unittest.main()