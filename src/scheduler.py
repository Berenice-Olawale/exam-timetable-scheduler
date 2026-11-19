
import pulp


class ExamScheduler:
    """
    Exam Timetable Scheduler using Integer Linear Programming.

    Hard constraints:
    1. Every exam is scheduled exactly once.
    2. A room cannot host two exams simultaneously.
    3. Room capacity must accommodate all enrolled students.
    4. A student cannot have two exams at the same time.

    Soft constraints:
    1. Avoid multiple exams for a student on the same day.
    2. Minimize the number of student exam-days.
    """

    def __init__(self, courses, rooms, time_slots):

        self.courses = courses
        self.rooms = rooms
        self.time_slots = time_slots

        self.students = sorted({
            student
            for course_students in courses.values()
            for student in course_students
        })

        self.days = list(dict.fromkeys(
            slot.split("_")[0] for slot in time_slots
        ))

        self.model = pulp.LpProblem(
            "Exam_Timetable_Scheduler",
            pulp.LpMinimize
        )

        self.x = pulp.LpVariable.dicts(
            "exam_assignment",
            (self.courses, self.rooms, self.time_slots),
            cat=pulp.LpBinary
        )

        self.student_day = pulp.LpVariable.dicts(
            "student_day",
            (self.students, self.days),
            cat=pulp.LpBinary
        )

        self.multiple_exams = pulp.LpVariable.dicts(
            "multiple_exams",
            (self.students, self.days),
            cat=pulp.LpBinary
        )

    def validate_inputs(self):
        """
        Validate input data before building the optimization model.
        """

        if not self.courses:
            raise ValueError("No courses were provided.")

        if not self.rooms:
            raise ValueError("No rooms were provided.")

        if not self.time_slots:
            raise ValueError("No time slots were provided.")

        if any(not isinstance(capacity, int) or capacity <= 0
               for capacity in self.rooms.values()):
            raise ValueError("Room capacities must be positive integers.")

        for course, students in self.courses.items():

            if not isinstance(students, list):
                raise ValueError(
                    f"Enrolment for {course} must be a list of student IDs."
                )

            if not students:
                raise ValueError(
                    f"Course {course} has no enrolled students."
                )

            if len(students) != len(set(students)):
                raise ValueError(
                    f"Course {course} contains duplicate student IDs."
                )

        if len(self.time_slots) != len(set(self.time_slots)):
            raise ValueError("Duplicate time slots were provided.")

        # Check whether every course can fit into at least one room.
        for course, students in self.courses.items():

            largest_room = max(self.rooms.values())

            if len(students) > largest_room:
                raise ValueError(
                    f"Course {course} has {len(students)} students, "
                    f"but the largest room only holds {largest_room}."
                )

        print("Input validation successful.")

    def add_objective(self):
        """
        Minimize student inconvenience.
        """

        multiple_exam_penalty = 100
        exam_day_penalty = 1

        self.model += (
            multiple_exam_penalty * pulp.lpSum(
                self.multiple_exams[student][day]
                for student in self.students
                for day in self.days
            )
            +
            exam_day_penalty * pulp.lpSum(
                self.student_day[student][day]
                for student in self.students
                for day in self.days
            )
        ), "Minimize_Student_Inconvenience"

    def add_constraints(self):

        # Constraint 1: Every exam must be assigned exactly once.
        for course in self.courses:

            self.model += (
                pulp.lpSum(
                    self.x[course][room][slot]
                    for room in self.rooms
                    for slot in self.time_slots
                ) == 1,
                f"Exam_Assignment_{course}"
            )

        # Constraint 2: A room cannot host two exams simultaneously.
        for room in self.rooms:

            for slot in self.time_slots:

                self.model += (
                    pulp.lpSum(
                        self.x[course][room][slot]
                        for course in self.courses
                    ) <= 1,
                    f"Room_Conflict_{room}_{slot}"
                )

        # Constraint 3: Room capacity.
        for course in self.courses:

            student_count = len(self.courses[course])

            for room in self.rooms:

                if student_count > self.rooms[room]:

                    for slot in self.time_slots:

                        self.model += (
                            self.x[course][room][slot] == 0,
                            f"Room_Capacity_{course}_{room}_{slot}"
                        )

        # Constraint 4: No student can have two exams simultaneously.
        for student in self.students:

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

        # Constraint 5: Identify days when students have exams.
        for student in self.students:

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

                self.model += (
                    exams_on_day >= self.student_day[student][day],
                    f"Student_Day_Lower_{student}_{day}"
                )

                self.model += (
                    exams_on_day <= len(enrolled_courses)
                    * self.student_day[student][day],
                    f"Student_Day_Upper_{student}_{day}"
                )

                # Constraint 6: Penalize multiple exams on one day.
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

    def solve(self):

        try:
            self.validate_inputs()

        except ValueError as error:
            print("\nInput Validation Error:", error)
            return None

        self.add_objective()
        self.add_constraints()

        print("\nStarting optimization...")

        solver = pulp.PULP_CBC_CMD(msg=True)

        try:
            self.model.solve(solver)

        except pulp.PulpSolverError as error:
            print("\nSolver Error:", error)
            return None

        status = pulp.LpStatus[self.model.status]

        print("\nSolver Status:", status)

        if status == "Infeasible":
            print(
                "No feasible timetable exists with the supplied "
                "courses, rooms, and time slots."
            )
            return None

        if status == "Unbounded":
            print("The optimization model is unbounded.")
            return None

        if status != "Optimal":
            print("The solver did not find an optimal solution.")
            return None

        print(
            "Objective Value:",
            pulp.value(self.model.objective)
        )

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
