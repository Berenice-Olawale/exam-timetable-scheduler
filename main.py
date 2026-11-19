from src.scheduler import ExamScheduler


def main():

    # Number of students enrolled in each course
    courses = {
        "CS101": ["S001", "S002", "S003"],
        "CS102": ["S001", "S004"],
        "CS103": ["S002", "S005"]
    }

    # Room capacities
    rooms = {
        "Room_A": 5,
        "Room_B": 3
    }

    # Available examination slots
    time_slots = [
        "Monday_09:00",
        "Monday_13:00",
        "Tuesday_09:00"
    ]

    scheduler = ExamScheduler(
        courses,
        rooms,
        time_slots
    )

    timetable = scheduler.solve()

    if timetable:
        print("\nGENERATED EXAM TIMETABLE")
        print("-" * 55)

        for exam in timetable:
            print(
                f"Course: {exam['course']} | "
                f"Room: {exam['room']} | "
                f"Time: {exam['time_slot']}"
            )


if __name__ == "__main__":
    main()
