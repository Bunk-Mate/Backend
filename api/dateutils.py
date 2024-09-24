import datetime
from datetime import timedelta

SA = 5
SU = 6
HOLIDAYS = [
    "2024-02-03",  # Non - Instructional WD (Saturday)
    "2024-02-04",  # H (Sunday)
    "2024-02-10",  # H (Saturday)
    "2024-02-11",  # H (Sunday)
    "2024-02-17",  # Instructional WD (Saturday)
    "2024-02-18",  # H (Sunday)
    "2024-02-24",  # H (Saturday)
    "2024-02-25",  # H (Sunday)
    "2024-03-02",  # Non - Instructional WD (Saturday)
    "2024-03-03",  # H (Sunday)
    "2024-03-09",  # H (Saturday)
    "2024-03-10",  # H (Sunday)
    "2024-03-16",  # Instructional WD (Saturday)
    "2024-03-17",  # H (Sunday)
    "2024-03-23",  # H (Saturday)
    "2024-03-24",  # H (Sunday)
    "2024-03-28",  # Maundy Thursday H
    "2024-03-29",  # Good Friday H
    "2024-03-30",  # Non-Instructional WD (Saturday)
    "2024-03-31",  # Easter H (Sunday)
    "2024-04-06",  # Non - Instructional WD (Saturday)
    "2024-04-07",  # H (Sunday)
    "2024-04-10",  # Id-ul-Fitr (Ramzan)* H
    "2024-04-13",  # H (Saturday)
    "2024-04-14",  # Vishu/Ambedkar Jayanti H (Sunday)
    "2024-04-20",  # Instructional WD (Saturday)
    "2024-04-21",  # H (Sunday)
    "2024-04-27",  # H (Saturday)
    "2024-04-28",  # H (Sunday)
    "2024-05-01",  # May Day H
    "2024-05-04",  # Non - Instructional WD (Saturday)
    "2024-05-05",  # H (Sunday)
    "2024-05-11",  # H (Saturday)
    "2024-05-12",  # H (Sunday)
    "2024-05-18",  # Instructional WD (Saturday)
    "2024-05-19",  # H (Sunday)
    "2024-05-25",  # H (Saturday)
    "2024-05-26",  # H (Sunday)
    "2024-06-01",  # Non - Instructional WD (Saturday)
    "2024-06-02",  # H (Sunday)
    "2024-06-08",  # H (Saturday)
    "2024-06-09",  # H (Sunday)
    "2024-06-15",  # H (Saturday)
    "2024-06-16",  # H (Sunday)
    "2024-06-17",  # Bakrid H
    "2024-06-22",  # H (Saturday)
    "2024-06-23",  # H (Sunday)
    "2024-06-29",  # H (Saturday)
    "2024-06-30",
    "2024-10-02",
    "2024-10-31",
    "2024-12-25",
    "2025-01-02",
    "2025-01-02",
]  # H (Sunday)


def is_holiday(date: datetime.date):
    if date.strftime("%Y-%m-%d") in HOLIDAYS:
        return True
    else:
        return False


def working_days(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() not in [SA, SU] and not is_holiday(current_date):
            yield current_date
        current_date += timedelta(days=1)
