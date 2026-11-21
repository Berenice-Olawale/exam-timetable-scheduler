
"""
Timetable Visualization Module

This module:
1. Displays an examination timetable as a table.
2. Creates a calendar-style visualization.
3. Saves the timetable visualization as a PNG image.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt


def normalize_timetable(timetable):
    """
    Convert timetable assignments into a consistent format.
    """

    records = []

    for course, assignment in timetable.items():

        time_slot = assignment["time_slot"]
        room = assignment["room"]

        day, time = time_slot.rsplit("_", 1)

        records.append({
            "Course": course,
            "Day": day,
            "Time": time,
            "Room": room
        })

    return pd.DataFrame(records)


def display_timetable(timetable):
    """
    Display the examination timetable as a table.
    """

    df = normalize_timetable(timetable)

    if df.empty:
        print("No timetable available.")
        return df

    df = df.sort_values(
        by=["Day", "Time"]
    ).reset_index(drop=True)

    print("\nEXAMINATION TIMETABLE")
    print("=" * 50)

    print(df.to_string(index=False))

    return df


def plot_timetable(timetable, save_path="results/timetable.png"):
    """
    Create and save a calendar-style timetable.
    """

    df = normalize_timetable(timetable)

    if df.empty:
        print("No timetable available to visualize.")
        return

    days_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    days = [
        day for day in days_order
        if day in df["Day"].unique()
    ]

    times = sorted(df["Time"].unique())

    fig, ax = plt.subplots(
        figsize=(12, 6)
    )

    ax.set_xlim(0, len(days))
    ax.set_ylim(0, len(times))

    ax.set_xticks(range(len(days)))
    ax.set_yticks(range(len(times)))

    ax.set_xticklabels(days)
    ax.set_yticklabels(times)

    ax.set_xlabel("Days")
    ax.set_ylabel("Examination Times")

    ax.set_title("Examination Timetable")

    ax.invert_yaxis()

    for x, day in enumerate(days):

        for y, time in enumerate(times):

            exams = df[
                (df["Day"] == day) &
                (df["Time"] == time)
            ]

            if not exams.empty:

                text = ""

                for _, exam in exams.iterrows():

                    text += (
                        f'{exam["Course"]}\n'
                        f'{exam["Room"]}\n\n'
                    )

            else:
                text = "-"

            ax.text(
                x + 0.5,
                y + 0.5,
                text,
                ha="center",
                va="center",
                fontsize=10
            )

            ax.add_patch(
                plt.Rectangle(
                    (x, y),
                    1,
                    1,
                    fill=False,
                    edgecolor="black"
                )
            )

    plt.tight_layout()

    os.makedirs(
        os.path.dirname(save_path) or ".",
        exist_ok=True
    )

    plt.savefig(
        save_path,
        dpi=300,
        bbox_inches="tight"
    )

    print(f"\nVisualization saved to: {save_path}")

    plt.show()


if __name__ == "__main__":

    
    sample_timetable = {
        "CS101": {
            "time_slot": "Monday_09:00",
            "room": "Room_A"
        },

        "CS102": {
            "time_slot": "Monday_13:00",
            "room": "Room_B"
        },

        "CS103": {
            "time_slot": "Tuesday_09:00",
            "room": "Room_A"
        },

        "CS104": {
            "time_slot": "Tuesday_13:00",
            "room": "Room_B"
        }
    }

    display_timetable(sample_timetable)

    plot_timetable(sample_timetable)
