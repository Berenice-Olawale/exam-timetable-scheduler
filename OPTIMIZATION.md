
# Optimization Model — Exam Timetable Scheduler

## 1. Overview

The Exam Timetable Scheduler uses Integer Linear Programming (ILP) to automatically generate an examination timetable while satisfying scheduling requirements.

The optimization engine is implemented in Python using the PuLP library, with the CBC solver used to find an optimal solution.

The model assigns each course to exactly one examination room and one available time slot while preventing room conflicts, student scheduling conflicts, and room capacity violations.

It also considers student convenience by minimizing the number of examination days and penalizing multiple examinations on the same day.

## 2. Optimization Variables

### 2.1 Exam Assignment Variable

The main decision variable is:

x[c,r,t] = 1 if course c is assigned to room r at time slot t; otherwise 0.

This is a binary decision variable.

### 2.2 Student Exam-Day Variable

y[s,d] = 1 if student s has at least one examination on day d; otherwise 0.

This variable is used to calculate the number of days students need to attend examinations.

### 2.3 Multiple Examination Variable

z[s,d] = 1 if student s has two or more examinations on day d; otherwise 0.

This variable allows the optimization model to penalize multiple examinations on the same day.

## 3. Hard Constraints

Hard constraints are requirements that every valid timetable must satisfy.

### 3.1 Every Course Must Be Scheduled Exactly Once

Each course must be assigned to exactly one room and one time slot.

Sum over all rooms and time slots:

x[c,r,t] = 1

### 3.2 Room Exclusivity

A room cannot accommodate more than one examination at the same time.

Sum over all courses:

x[c,r,t] <= 1

### 3.3 Room Capacity

The number of students enrolled in a course cannot exceed the capacity of its assigned room.

If the number of students in a course exceeds a room's capacity, the corresponding assignment variable is fixed to zero.

### 3.4 Student Conflict Prevention

A student cannot take two examinations simultaneously.

For every student and time slot, the total number of assigned examinations involving that student must not exceed one.

Sum over the student's enrolled courses and all rooms:

x[c,r,t] <= 1

## 4. Soft Constraints

Soft constraints improve the quality of the timetable without making otherwise feasible schedules impossible.

### 4.1 Minimize Examination Days

The model minimizes the number of days on which each student has an examination.

The student-day variable is linked to the examinations scheduled for that student on each day.

### 4.2 Penalize Multiple Examinations Per Day

The model introduces a penalty whenever a student has two or more examinations on the same day.

A higher penalty is used to discourage this situation.

## 5. Objective Function

The objective function minimizes student inconvenience:

Minimize:

Z = 100 * Sum(z[s,d]) + Sum(y[s,d])

Where:

- z[s,d] represents students with multiple examinations on a day.
- y[s,d] represents students with at least one examination on a day.
- 100 is the penalty weight for multiple examinations.
- 1 is the penalty weight for each examination day.

The higher penalty encourages the solver to avoid scheduling multiple examinations for the same student on one day before minimizing the total number of student examination days.

This is a weighted optimization approach.

## 6. Solver Implementation

The optimization model is implemented using:

- Python
- PuLP
- CBC (Coin-or Branch and Cut) solver

The model uses binary decision variables and is solved as a minimization problem.

The solver searches for a feasible assignment that satisfies all hard constraints while minimizing the objective function.

## 7. Input Validation

Before optimization begins, the system checks:

- Courses have been provided.
- Rooms have been provided.
- Time slots have been provided.
- Room capacities are positive integers.
- Every course has enrolled students.
- Enrolment data uses lists of student IDs.
- Duplicate student IDs are not present within a course.
- Duplicate time slots are not present.
- Every course can fit into at least one available room.

Invalid input is rejected with an explanatory error message.

## 8. Infeasibility Handling

The system checks the solver status after optimization.

Possible outcomes include:

- Optimal: A valid optimal timetable has been found.
- Infeasible: No valid timetable exists with the supplied resources and constraints.
- Unbounded: The optimization model is unbounded.
- Other solver status: An optimal solution was not found.

If the problem is infeasible, the system reports the situation instead of generating an invalid timetable.

## 9. Timetable Extraction

After an optimal solution is found, the system extracts the selected binary assignments.

For every course, it identifies the room and time slot whose assignment variable has a value greater than 0.5.

The resulting timetable contains:

- Course ID
- Assigned room
- Examination time slot
- Examination day
- Number of enrolled students

## 10. Testing

The optimization engine is tested using Python's unittest framework.

The automated tests verify:

1. Successful timetable generation.
2. Prevention of simultaneous examinations for the same student.
3. Prevention of room double-booking.
4. Compliance with room capacities.
5. Rejection of oversized courses.
6. Detection and reporting of infeasible schedules.

Run the tests with:

```bash
python -m unittest discover -s tests -v
```

## 11. Conclusion

The optimization engine provides an automated approach to examination timetable generation using Integer Linear Programming.

By combining hard scheduling constraints with weighted soft constraints, the system generates valid timetables while considering student convenience.

The use of PuLP and CBC provides a flexible optimization framework that can be extended to larger datasets and additional scheduling requirements.
