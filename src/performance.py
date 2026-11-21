"""
Performance Analysis Module

This module benchmarks the examination scheduling system
using different dataset sizes.

It records:
- Number of courses
- Number of students
- Execution time
- Solution status
- Objective value, when available

It saves benchmark results to CSV and creates a graph.
"""

import os
import time
import csv
import matplotlib.pyplot as plt


def generate_dataset(
    num_courses,
    num_students,
    num_rooms=5,
    num_time_slots=10
):
    """
    Generate synthetic datasets for performance experiments.
    """

    students = [
        f"S{i:04d}"
        for i in range(1, num_students + 1)
    ]

    courses = {}

    for i in range(1, num_courses + 1):

        course_id = f"CS{i:03d}"

        start = ((i - 1) * 3) % num_students

        course_students = [
            students[(start + j) % num_students]
            for j in range(min(5, num_students))
        ]

        courses[course_id] = course_students

    rooms = {
        f"Room_{i}": 30 + (i * 10)
        for i in range(1, num_rooms + 1)
    }

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

    all_slots = [
        f"{day}_{hour}"
        for day in days
        for hour in hours
    ]

    time_slots = all_slots[:num_time_slots]

    return {
        "courses": courses,
        "rooms": rooms,
        "time_slots": time_slots
    }


def run_real_scheduler(courses, rooms, time_slots):
    """
    Run the actual ExamScheduler from scheduler.py.
    """

    from src.scheduler import ExamScheduler
    import pulp

    scheduler = ExamScheduler(
        courses,
        rooms,
        time_slots
    )

    timetable = scheduler.solve()

    status = pulp.LpStatus[scheduler.model.status]

    objective_value = None

    if scheduler.model.objective is not None:
        objective_value = pulp.value(
            scheduler.model.objective
        )

    return {
        "success": timetable is not None,
        "status": status,
        "objective_value": objective_value,
        "timetable": timetable
    }


def benchmark_solver(solver_function, dataset):
    """
    Measure the execution time of the solver.
    """

    start_time = time.perf_counter()

    result = solver_function(
        dataset["courses"],
        dataset["rooms"],
        dataset["time_slots"]
    )

    end_time = time.perf_counter()

    execution_time = end_time - start_time

    if result is None:
        result = {}

    return {
        "execution_time": execution_time,
        "status": result.get("status", "Unknown"),
        "objective_value": result.get("objective_value"),
        "success": result.get("success", False)
    }


def run_experiments(solver_function, experiments):
    """
    Run performance experiments for multiple dataset sizes.
    """

    results = []

    for experiment in experiments:

        name = experiment["name"]

        print(f"\nRunning experiment: {name}")
        print("-" * 40)

        dataset = generate_dataset(
            num_courses=experiment["courses"],
            num_students=experiment["students"],
            num_rooms=experiment["rooms"],
            num_time_slots=experiment["time_slots"]
        )

        try:

            benchmark = benchmark_solver(
                solver_function,
                dataset
            )

            record = {
                "experiment": name,
                "courses": experiment["courses"],
                "students": experiment["students"],
                "rooms": experiment["rooms"],
                "time_slots": experiment["time_slots"],
                "execution_time": benchmark["execution_time"],
                "status": benchmark["status"],
                "objective_value": benchmark["objective_value"],
                "success": benchmark["success"]
            }

        except Exception as error:

            record = {
                "experiment": name,
                "courses": experiment["courses"],
                "students": experiment["students"],
                "rooms": experiment["rooms"],
                "time_slots": experiment["time_slots"],
                "execution_time": None,
                "status": f"Error: {error}",
                "objective_value": None,
                "success": False
            }

        results.append(record)

        print(f"Courses: {record['courses']}")
        print(f"Students: {record['students']}")
        print(f"Execution time: {record['execution_time']}")
        print(f"Status: {record['status']}")
        print(f"Objective: {record['objective_value']}")

    return results


def save_results(
    results,
    filename="results/performance_results.csv"
):
    """
    Save performance results to a CSV file.
    """

    os.makedirs(
        os.path.dirname(filename) or ".",
        exist_ok=True
    )

    if not results:
        print("No results to save.")
        return

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys()
        )

        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to: {filename}")


def plot_performance(
    results,
    filename="results/performance_graph.png"
):
    """
    Plot execution time against the number of courses.
    """

    valid_results = [
        result for result in results
        if result["execution_time"] is not None
    ]

    if not valid_results:
        print("No valid performance results to plot.")
        return

    courses = [
        result["courses"]
        for result in valid_results
    ]

    times = [
        result["execution_time"]
        for result in valid_results
    ]

    os.makedirs(
        os.path.dirname(filename) or ".",
        exist_ok=True
    )

    plt.figure(figsize=(8, 5))

    plt.plot(
        courses,
        times,
        marker="o"
    )

    plt.title("Solver Performance")
    plt.xlabel("Number of Courses")
    plt.ylabel("Execution Time (seconds)")
    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    print(f"Graph saved to: {filename}")


def print_summary(results):
    """
    Display a summary of all performance experiments.
    """

    print("\nPERFORMANCE SUMMARY")
    print("=" * 70)

    for result in results:

        execution_time = result["execution_time"]

        if execution_time is None:
            execution_time = "Failed"

        print(
            f"{result['experiment']:12} | "
            f"Courses: {result['courses']:4} | "
            f"Students: {result['students']:5} | "
            f"Time: {execution_time} | "
            f"Status: {result['status']} | "
            f"Objective: {result['objective_value']}"
        )


if __name__ == "__main__":

    experiments = [
        {
            "name": "Small",
            "courses": 5,
            "students": 20,
            "rooms": 3,
            "time_slots": 5
        },
        {
            "name": "Medium",
            "courses": 15,
            "students": 75,
            "rooms": 5,
            "time_slots": 10
        },
        {
            "name": "Large",
            "courses": 30,
            "students": 200,
            "rooms": 8,
            "time_slots": 15
        }
    ]

    print("Starting performance experiments...")

    results = run_experiments(
        run_real_scheduler,
        experiments
    )

    print_summary(results)

    save_results(results)

    plot_performance(results)