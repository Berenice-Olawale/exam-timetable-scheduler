# Exam Timetable Scheduler with Integer Linear Programming

**Advanced Programming — Project 23**  
**Team:** Berenice Olawale, Meriem Ben Zouitine, David Chika Chinedu  
**Repository:** https://github.com/Berenice-Olawale/exam-timetable-scheduler

## Overview

The Exam Timetable Scheduler is a Python command-line application that generates examination schedules using **Integer Linear Programming (ILP)**. It assigns each course to one available room and one examination time slot while respecting room capacity, room availability and student-conflict requirements.

The optimization model also considers student convenience. It penalizes a student having multiple examinations on the same day and minimizes the total number of student examination days.

## Main features

- Load examination data from JSON or three CSV files.
- Generate reproducible synthetic datasets for experiments.
- Validate course enrolments, rooms and time slots before optimization.
- Solve the scheduling model with PuLP and the CBC solver.
- Enforce four hard scheduling requirements:
  1. Every course is scheduled exactly once.
  2. A room hosts at most one exam in a time slot.
  3. A course is assigned only to a room with sufficient capacity.
  4. A student has at most one exam in a time slot.
- Optimize two soft objectives:
  1. Penalize students who have more than one exam on the same day.
  2. Minimize the number of days on which students have exams.
- Display the generated timetable and save a calendar-style PNG visualization.
- Run performance experiments and save measurements as CSV and a graph.
- Run unit and integration tests with Python's `unittest` framework.

## Project structure

```text
exam-timetable-scheduler/
├── main.py
├── requirements.txt
├── README.md
├── OPTIMIZATION.md
├── data/
│   ├── exams.json
│   ├── courses.csv
│   ├── rooms.csv
│   └── time_slots.csv
├── src/
│   ├── models.py
│   ├── data_loader.py
│   ├── data_generator.py
│   ├── scheduler.py
│   ├── visualizer.py
│   └── performance.py
├── tests/
│   ├── test_scheduler.py
│   └── test_integration.py
└── results/
    ├── timetable.png
    ├── performance_graph.png
    └── performance_results.csv
```

`constraints.py` is not listed because the current constraint implementation is contained in `src/scheduler.py`.

## Requirements

- Python 3.10 or newer
- PuLP 3.3.0
- CBC solver (available through the PuLP installation when supported by the environment)
- pandas
- matplotlib

## Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/Berenice-Olawale/exam-timetable-scheduler.git
cd exam-timetable-scheduler
```

Create and activate a virtual environment:

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running the scheduler

### 1. Use the default JSON dataset

The default command reads `data/exams.json`:

```bash
python main.py
```

To explicitly specify a JSON file:

```bash
python main.py --json data/exams.json
```

### 2. Use CSV input

Provide all three CSV files:

```bash
python main.py --courses data/courses.csv --rooms data/rooms.csv --slots data/time_slots.csv
```

The expected CSV columns are:

| File | Required columns |
|---|---|
| `courses.csv` | `course_id`, `student_id` |
| `rooms.csv` | `room_id`, `capacity` |
| `time_slots.csv` | `day`, `start_time` |

Each row in `courses.csv` represents one student enrolment in one course.

### 3. Generate a synthetic dataset

```bash
python main.py --synthetic
```

Customize the generated instance:

```bash
python main.py --synthetic --num-courses 20 --num-students 100 --num-rooms 6 --num-slots 12 --seed 42
```

The seed makes synthetic data generation reproducible.

### 4. Control visualization output

Skip chart generation:

```bash
python main.py --no-plot
```

Choose a different output path:

```bash
python main.py --output results/my_timetable.png
```

## Input data format

The JSON input file contains three top-level properties: `courses`, `rooms` and `time_slots`.

Example:

```json
{
  "courses": {
    "CS101": ["S001", "S002", "S003"],
    "CS102": ["S001", "S004"],
    "CS103": ["S002", "S005"]
  },
  "rooms": {
    "Room_A": 30,
    "Room_B": 20
  },
  "time_slots": [
    "Monday_09:00",
    "Monday_13:00",
    "Tuesday_09:00"
  ]
}
```

## Optimization model

The model uses binary decision variables:

- `x[c,r,t] = 1` when course `c` is assigned to room `r` at time slot `t`.
- `y[s,d] = 1` when student `s` has at least one exam on day `d`.
- `z[s,d] = 1` when student `s` has at least two exams on day `d`.

The current weighted objective is:

\[
\min Z = 100\sum_s\sum_d z_{s,d} + \sum_s\sum_d y_{s,d}
\]

The coefficient 100 gives a substantially higher penalty to multiple exams on one day than to an additional exam day. The complete mathematical formulation and constraint explanation are in [`OPTIMIZATION.md`](OPTIMIZATION.md).

## Running tests

Run all unit and integration tests:

```bash
python -m unittest discover -s tests -v
```

The test suite checks timetable generation, student conflicts, room double-booking, room capacity, oversized-course validation, infeasible schedules, required output fields and the scheduler-to-visualizer data flow.

## Performance experiments

Run the benchmark module:

```bash
python -m src.performance
```

The experiment script generates small, medium and large synthetic datasets, records solver status, objective value and execution time, and writes:

- `results/performance_results.csv`
- `results/performance_graph.png`

Benchmark timings depend on the machine, solver version, input instance and random data. The results in the repository are measurements from one recorded run, not universal runtime guarantees.

## Module responsibilities

| Module | Responsibility |
|---|---|
| `main.py` | Command-line interface and application workflow |
| `src/models.py` | Dataclasses representing students, courses, rooms, time slots and datasets |
| `src/data_loader.py` | JSON/CSV loading and dataset validation |
| `src/data_generator.py` | Reproducible synthetic dataset generation |
| `src/scheduler.py` | ILP variables, objective, constraints, solver execution and timetable extraction |
| `src/visualizer.py` | Tabular display and calendar-style timetable chart |
| `src/performance.py` | Benchmark execution, CSV export and performance graph |
| `tests/` | Unit and integration tests |

## Team contributions

| Team member | Main responsibility |
|---|---|
| Berenice Olawale | Scheduling engine and ILP model |
| Meriem Ben Zouitine | Data models, data loading and synthetic data generation |
| David Chika Chinedu | Testing, visualization and performance analysis |

## Limitations and possible extensions

The current model assumes that every exam has the same duration and that each course is assigned to one room. It does not yet model lecturer availability, consecutive examination preferences, split-room examinations or detailed explanations of infeasibility. Future work could add these requirements, compare CBC with another optimization solver, and evaluate larger datasets using repeated benchmark runs.

## License and academic use

This repository was developed as an Advanced Programming course project. Add the license or usage terms required by the course or team before redistributing the project.
