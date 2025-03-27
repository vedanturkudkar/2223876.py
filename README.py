# 2223876.py

import pandas as pd
import re

attendance_data = pd.DataFrame({
    "student_id": [101, 101, 101, 101, 101, 102, 102, 102, 102, 103, 103, 103, 103, 103, 104, 104, 104, 104, 104],
    "attendance_date": [
        "2024-03-01", "2024-03-02", "2024-03-03", "2024-03-04", "2024-03-05",
        "2024-03-02", "2024-03-03", "2024-03-04", "2024-03-05",
        "2024-03-05", "2024-03-06", "2024-03-07", "2024-03-08", "2024-03-09",
        "2024-03-01", "2024-03-02", "2024-03-03", "2024-03-04", "2024-03-05"
    ],
    "status": ["Absent", "Absent", "Absent", "Absent", "Present",
               "Absent", "Absent", "Absent", "Absent",
               "Absent", "Absent", "Absent", "Absent", "Absent",
               "Present", "Present", "Absent", "Present", "Present"]
})


attendance_data["attendance_date"] = pd.to_datetime(attendance_data["attendance_date"])


students_data = pd.DataFrame({
    "student_id": [101, 102, 103, 104, 105],
    "student_name": ["Alice Johnson", "Bob Smith", "Charlie Brown", "David Lee", "Eva White"],
    "parent_email": ["alice_parent@example.com", "bob_parent@example.com",
                     "invalid_email.com", "invalid_email.com", "eva_white@example.com"]
})


def find_absence_streaks(df):
    results = []
    df = df.sort_values(by=["student_id", "attendance_date"])

    for student, group in df.groupby("student_id"):
        group = group.reset_index(drop=True)
        absences = group[group["status"] == "Absent"]
        
        streaks = []
        current_streak = []

        for i in range(len(absences)):
            if i == 0 or (absences.iloc[i]["attendance_date"] - absences.iloc[i-1]["attendance_date"]).days == 1:
                current_streak.append(absences.iloc[i])
            else:
                streaks.append(current_streak)
                current_streak = [absences.iloc[i]]
        
        if current_streak:
            streaks.append(current_streak)

        latest_valid_streak = None
        for streak in streaks:
            if len(streak) > 3:
                latest_valid_streak = streak

        if latest_valid_streak:
            results.append({
                "student_id": student,
                "absence_start_date": latest_valid_streak[0]["attendance_date"],
                "absence_end_date": latest_valid_streak[-1]["attendance_date"],
                "total_absent_days": len(latest_valid_streak)
            })

    return pd.DataFrame(results)

absence_streaks = find_absence_streaks(attendance_data)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

final_df = pd.merge(absence_streaks, students_data, on="student_id", how="left")

final_df["email"] = final_df["parent_email"].apply(lambda x: x if is_valid_email(x) else None)

final_df["msg"] = final_df.apply(lambda row: 
    f"Dear Parent, your child {row['student_name']} was absent from {row['absence_start_date'].date()} to {row['absence_end_date'].date()} for {row['total_absent_days']} days. Please ensure their attendance improves."
    if row["email"] else None, axis=1)

final_df = final_df.drop(columns=["parent_email"])

print(final_df)
