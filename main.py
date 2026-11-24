"""Command-line entry point for the Exam Timetable Scheduler."""

import argparse
from pathlib import Path

from src.data_loader import load_csv_data, load_json_data
from src.data_generator import generate_dataset
from src.scheduler import ExamScheduler
from src.visualizer import display_timetable, plot_timetable


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate an examination timetable using Integer Linear Programming."
    )

    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--json",
        dest="json_file",
        help="Path to a JSON file containing courses, rooms and time slots.",
    )
    source.add_argument(
        "--synthetic",
        action="store_true",
        help="Generate a synthetic dataset instead of loading files.",
    )

    parser.add_argument("--courses", help="CSV file containing course_id,student_id.")
    parser.add_argument("--rooms", help="CSV file containing room_id,capacity.")
    parser.add_argument("--slots", help="CSV file containing day,start_time.")

    parser.add_argument("--num-courses", type=int, default=10)
    parser.add_argument("--num-students", type=int, default=50)
    parser.add_argument("--num-rooms", type=int, default=5)
    parser.add_argument("--num-slots", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)

    parser.add_argument(
        "--output",
        default="results/timetable.png",
        help="Path for the generated timetable image (default: results/timetable.png).",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Do not generate the timetable image.",
    )
    return parser


def load_inputs(args):
    """Load or generate a dataset and return scheduler-compatible inputs."""
    if args.synthetic:
        dataset = generate_dataset(
            num_courses=args.num_courses,
            num_students=args.num_students,
            num_rooms=args.num_rooms,
            num_time_slots=args.num_slots,
            seed=args.seed,
        )
        return dataset.to_scheduler_inputs()

    csv_values = (args.courses, args.rooms, args.slots)
    if args.synthetic and any(csv_values):
        raise ValueError("--synthetic cannot be combined with CSV input options.")
    if args.json_file and any(csv_values):
        raise ValueError("--json cannot be combined with CSV input options.")
    if any(csv_values):
        if not all(csv_values):
            raise ValueError(
                "CSV input requires all three options: --courses, --rooms and --slots."
            )
        dataset = load_csv_data(
            args.courses,
            args.rooms,
            args.slots,
        )
        return dataset.to_scheduler_inputs()

    json_file = args.json_file or "data/exams.json"
    dataset = load_json_data(json_file)
    return dataset.to_scheduler_inputs()


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        courses, rooms, time_slots = load_inputs(args)
        print("EXAM TIMETABLE SCHEDULER")
        print("=" * 60)
        print(
            f"Loaded {len(courses)} courses, "
            f"{len(rooms)} rooms and {len(time_slots)} time slots."
        )

        scheduler = ExamScheduler(courses, rooms, time_slots)
        timetable = scheduler.solve()

        if timetable is None:
            return 1

        print("\nGENERATED EXAMINATION TIMETABLE")
        print("=" * 60)
        timetable_for_visualizer = {
            exam["course"]: {
                "time_slot": exam["time_slot"],
                "room": exam["room"],
                "student_count": exam["student_count"],
            }
            for exam in timetable
        }
        display_timetable(timetable_for_visualizer)

        if not args.no_plot:
            plot_timetable(
                timetable_for_visualizer,
                save_path=args.output,
            )

        return 0

    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
