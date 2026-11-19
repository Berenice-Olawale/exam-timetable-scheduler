
import pulp
from collections import defaultdict


class ExamScheduler:
    """
    Exam Timetable Scheduler using Integer Linear Programming.

    Hard constraints:
    1. Every exam is scheduled exactly once.
    2. A room cannot host two exams simultaneously.
    3. Room capacity must accommodate all students.
    4. A student cannot have two exams simultaneously.

    Soft constraints:
    1. Avoid multiple exams for the same student on one day.
    2. Minimize the number of days on which students have exams.
    """

    def __init__(self, courses, rooms, time_slots):

        self.courses = courses
        self.rooms = rooms
        self.time_slots = time_slots

        # Extract unique days from time slot names.
        self.days = list(dict.fromkeys(
            slot.split("_")[0] for slot in time_slots
        ))

        # Create the optimization problem.
        self.model = pulp.LpProblem(
            "Exam_Timetable_Scheduler",
            pulp.LpMinimize
        )

        # Binary assignment variables.
        self.x = pulp.LpVariable.dicts(
            "exam_assignment",
            (self.courses, self.rooms, self.time_slots),
            cat=pulp.LpBinary
        )

        # Binary variable: 1 if a student has an exam on a day.
        self.student_day = pulp.LpVariable.dicts(
            "student_day",
            (
                list(set(
                    student
                    for course in courses
                    for student in courses[course]
                )),
                self.days
            ),
            cat=pulp.LpBinary
        )

        # Binary variable: 1 if a student has multiple exams on a day.
        self.multiple_exams = pulp.LpVariable.dicts(
            "multiple_exams",
            (
                list(set(
                    student
                    for course in courses
                    for student in courses[course]
                )),
                self.days
            ),
            cat=pulp.LpBinary
        )

    def add_objective(self):
        """
        Minimize student inconvenience.

        Penalty 1: Multiple exams on the same day.
        Penalty 2: Number of days with exams.
        """

        multiple_exam_penalty = 100
        exam_day_penalty = 1

        students = list(self.student_day.keys())

        self.model += (
            multiple_exam_penalty * pulp.lpSum(
                self.multiple_exams[student][day]
                for student in students
                for day in self.days
            )
            +
            exam_day_penalty * pulp.lpSum(
                self.student_day[student][day]
                for student in students
                for day in self.days
            )
        ), "Minimize_Student_Inconvenience"

    def add_constraints(self):

        # Constraint 1:
        # Every exam must be assigned exactly once.
        for course in self.courses:

            self.model += (
                pulp.lpSum(
                    self.x[course][room][slot]
                    for room in self.rooms
                    for slot in self.time_slots
                ) == 1,
                f"Exam_Assignment_{course}"
            )

        # Constraint 2:
        # A room cannot host two exams simultaneously.
        for room in self.rooms:

            for slot in self.time_slots:

                self.model += (
                    pulp.lpSum(
                        self.x[course][room][slot]
                        for course in self.courses
                    ) <= 1,
                    f"Room_Conflict_{room}_{slot}"
                )

        # Constraint 3:
        # Room capacity must accommodate all enrolled students.
        for course in self.courses:

            student_count = len(self.courses[course])

            for room in self.rooms:

                if student_count > self.rooms[room]:

                    for slot in self.time_slots:

                        self.model += (
                            self.x[course][room][slot] == 0,
                            f"Room_Capacity_{course}_{room}_{slot}"
                        )

        # Constraint 4:
        # A student cannot have two exams at the same time.
        all_students = list(self.student_day.keys())

        for student in all_students:

            enrolled_courses = [
                course
                for course in self.courses
                if student in self.courses[course]
            ]

            for slot in self.time_slots:

                self.model += (
                    pulp.lpSum(
                        self.x[course][room][slot]
                        for course in enrolled_courses
                        for room in self.rooms
                    ) <= 1,
                    f"Student_Conflict_{student}_{slot}"
                )

        # Constraint 5:
        # Link student_day variables to actual exam assignments.
        for student in all_students:

            enrolled_courses = [
                course
                for course in self.courses
                if student in self.courses[course]
            ]

            for day in self.days:

                day_slots = [
                    slot for slot in self.time_slots
                    if slot.split("_")[0] == day
                ]

                exams_on_day = pulp.lpSum(
                    self.x[course][room][slot]
                    for course in enrolled_courses
                    for room in self.rooms
                    for slot in day_slots
                )

                # student_day = 1 if at least one exam occurs that day.
                self.model += (
                    exams_on_day >= self.student_day[student][day],
                    f"Student_Day_Lower_{student}_{day}"
                )

                self.model += (
                    exams_on_day <= len(enrolled_courses)
                    * self.student_day[student][day],
                    f"Student_Day_Upper_{student}_{day}"
                )

                # Constraint 6:
                # Detect multiple exams on the same day.
                if len(enrolled_courses) > 1:

                    self.model += (
                        exams_on_day <= 1 + (
                            len(enrolled_courses) - 1
                        ) * self.multiple_exams[student][day],
                        f"Multiple_Exams_Upper_{student}_{day}"
                    )

                    self.model += (
                        exams_on_day >= 2 * self.multiple_exams[student][day],
                        f"Multiple_Exams_Lower_{student}_{day}"
                    )

                else:

                    self.model += (
                        self.multiple_exams[student][day] == 0,
                        f"No_Multiple_Exams_{student}_{day}"
                    )

    def solve(self):

        self.add_objective()
        self.add_constraints()

        solver = pulp.PULP_CBC_CMD(msg=True)

        self.model.solve(solver)

        status = pulp.LpStatus[self.model.status]

        print("\nSolver Status:", status)

        if status != "Optimal":
            print("No optimal timetable was found.")
            return None

        timetable = []

        for course in self.courses:

            for room in self.rooms:

                for slot in self.time_slots:

                    value = pulp.value(
                        self.x[course][room][slot]
                    )

                    if value is not None and value > 0.5:

                        timetable.append({
                            "course": course,
                            "room": room,
                            "time_slot": slot,
                            "day": slot.split("_")[0],
                            "student_count": len(self.courses[course])
                        })

        return timetable
