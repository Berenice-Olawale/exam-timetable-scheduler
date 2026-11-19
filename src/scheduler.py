
import pulp


class ExamScheduler:
    """
    Exam Timetable Scheduler using Integer Linear Programming.

    Hard constraints:
    1. Every exam must be scheduled exactly once.
    2. A room cannot host two exams simultaneously.
    3. Room capacity must accommodate all enrolled students.
    4. A student cannot have two exams at the same time.
    """

    def __init__(self, courses, rooms, time_slots):

        self.courses = courses
        self.rooms = rooms
        self.time_slots = time_slots

        # Create the optimization problem
        self.model = pulp.LpProblem(
            "Exam_Timetable_Scheduler",
            pulp.LpMinimize
        )

        # Binary decision variables:
        # x[course][room][slot] = 1 if an exam is assigned there,
        # otherwise 0.
        self.x = pulp.LpVariable.dicts(
            "exam_assignment",
            (self.courses, self.rooms, self.time_slots),
            cat=pulp.LpBinary
        )

    def add_objective(self):
        """
        Zero objective for now.
        Soft constraint penalties will be introduced later.
        """
        self.model += 0

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
        all_students = set(
            student
            for course in self.courses
            for student in self.courses[course]
        )

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

    def solve(self):

        self.add_objective()
        self.add_constraints()

        # Run the CBC optimization solver.
        solver = pulp.PULP_CBC_CMD(msg=True)

        self.model.solve(solver)

        status = pulp.LpStatus[self.model.status]

        print("\nSolver Status:", status)

        if status != "Optimal":
            print("No optimal timetable was found.")
            return None

        # Extract the optimized timetable.
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
                            "student_count": len(self.courses[course])
                        })

        return timetable
