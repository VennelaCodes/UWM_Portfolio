"""
Project 3: Ad-hoc Reporting & Process Efficiency Project
Generates datasets for ad-hoc reporting scenarios across multiple business units.
"""

import csv
import random
import datetime
import os

random.seed(77)

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BUSINESS_UNITS = ["Underwriting", "Closing", "Client Services", "Compliance", "Operations"]
PRIORITIES = ["High", "Medium", "Low"]
REQUEST_TYPES = ["Performance Summary", "Exception Report", "Trend Analysis",
                 "Compliance Audit", "Volume Tracker", "Custom Metric"]


def generate_adhoc_requests():
    """Generate ad-hoc reporting request log."""
    filepath = os.path.join(OUTPUT_DIR, "adhoc_requests.csv")
    start = datetime.date(2024, 1, 1)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["request_id", "request_date", "business_unit", "requester",
                          "request_type", "priority", "deadline_date",
                          "completion_date", "status", "turnaround_hours"])

        for i in range(1, 201):
            req_date = start + datetime.timedelta(days=random.randint(0, 364))
            bu = random.choice(BUSINESS_UNITS)
            requester = f"{bu[:3].upper()}-{random.choice(['Manager', 'Director', 'VP', 'Lead'])}"
            req_type = random.choice(REQUEST_TYPES)
            priority = random.choices(PRIORITIES, weights=[0.3, 0.5, 0.2], k=1)[0]

            if priority == "High":
                deadline_days = random.randint(1, 3)
            elif priority == "Medium":
                deadline_days = random.randint(3, 7)
            else:
                deadline_days = random.randint(5, 14)

            deadline = req_date + datetime.timedelta(days=deadline_days)
            completed = random.random() < 0.92
            if completed:
                turnaround_hrs = random.randint(2, deadline_days * 24)
                comp_date = req_date + datetime.timedelta(hours=turnaround_hrs)
                status = "Completed"
            else:
                turnaround_hrs = ""
                comp_date = ""
                status = random.choice(["In Progress", "Pending Info"])

            writer.writerow([
                f"ADH-{i:04d}", req_date.isoformat(), bu, requester,
                req_type, priority, deadline.isoformat(),
                comp_date if comp_date else "", status,
                turnaround_hrs
            ])
    print(f"Generated ad-hoc requests -> {filepath}")


def generate_daily_performance():
    """Generate daily performance tracking data."""
    filepath = os.path.join(OUTPUT_DIR, "daily_performance.csv")
    start = datetime.date(2024, 1, 1)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "business_unit", "loans_in_pipeline",
                          "loans_completed", "avg_cycle_time_days",
                          "error_count", "staff_count", "overtime_hours"])

        for day_offset in range(365):
            date = start + datetime.timedelta(days=day_offset)
            if date.weekday() >= 5:
                continue
            for bu in BUSINESS_UNITS:
                pipeline = random.randint(50, 300)
                completed = random.randint(10, 80)
                cycle_time = round(random.uniform(5, 35), 1)
                errors = random.randint(0, 8)
                staff = random.randint(15, 50)
                overtime = round(random.uniform(0, 20), 1)
                writer.writerow([date.isoformat(), bu, pipeline, completed,
                                  cycle_time, errors, staff, overtime])
    print(f"Generated daily performance -> {filepath}")


def generate_weekly_summary():
    """Generate weekly summary tracking data."""
    filepath = os.path.join(OUTPUT_DIR, "weekly_summary.csv")

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["week_number", "week_ending", "business_unit",
                          "total_processed", "total_completed", "completion_rate",
                          "avg_cycle_time", "escalations", "client_contacts"])

        start = datetime.date(2024, 1, 5)  # First Friday
        for week in range(52):
            week_end = start + datetime.timedelta(weeks=week)
            for bu in BUSINESS_UNITS:
                processed = random.randint(200, 800)
                completed = int(processed * random.uniform(0.6, 0.95))
                comp_rate = round(completed / processed * 100, 1)
                cycle_time = round(random.uniform(8, 30), 1)
                escalations = random.randint(2, 25)
                contacts = random.randint(100, 600)
                writer.writerow([week + 1, week_end.isoformat(), bu,
                                  processed, completed, comp_rate,
                                  cycle_time, escalations, contacts])
    print(f"Generated weekly summary -> {filepath}")


def generate_monthly_targets():
    """Generate monthly target benchmarks."""
    filepath = os.path.join(OUTPUT_DIR, "monthly_targets.csv")

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["month", "business_unit", "target_completion_rate",
                          "target_cycle_time", "target_error_rate", "target_escalation_rate"])

        for m in range(1, 13):
            for bu in BUSINESS_UNITS:
                writer.writerow([
                    f"2024-{m:02d}", bu,
                    random.randint(80, 95),
                    round(random.uniform(12, 22), 1),
                    round(random.uniform(1, 5), 1),
                    round(random.uniform(3, 10), 1)
                ])
    print(f"Generated monthly targets -> {filepath}")


if __name__ == "__main__":
    generate_adhoc_requests()
    generate_daily_performance()
    generate_weekly_summary()
    generate_monthly_targets()
    print("\nAd-hoc reporting data generation complete!")
