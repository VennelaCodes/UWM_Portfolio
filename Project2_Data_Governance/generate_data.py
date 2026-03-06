"""
Project 2: Data Governance & Reporting Optimization Project
Generates multi-source datasets that need consolidation and standardization.
"""

import csv
import random
import datetime
import os

random.seed(99)

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

REGIONS = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]
TEAMS = [f"Team_{chr(65+i)}" for i in range(8)]
MONTHS = [f"2024-{m:02d}" for m in range(1, 13)]


def generate_source_a():
    """Source A: Team performance system - weekly data."""
    filepath = os.path.join(OUTPUT_DIR, "source_a_team_performance.csv")
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["week_ending", "team_name", "region", "loans_processed",
                          "loans_closed", "avg_turnaround_days", "escalations",
                          "client_calls_handled"])
        for month in MONTHS:
            for week in range(1, 5):
                for team in TEAMS:
                    region = random.choice(REGIONS)
                    processed = random.randint(80, 200)
                    closed = int(processed * random.uniform(0.35, 0.55))
                    turnaround = round(random.uniform(18, 42), 1)
                    escalations = random.randint(2, 25)
                    calls = random.randint(150, 500)
                    week_date = f"{month}-{min(7*week, 28):02d}"
                    writer.writerow([week_date, team, region, processed, closed,
                                     turnaround, escalations, calls])
    print(f"Generated Source A -> {filepath}")


def generate_source_b():
    """Source B: Client satisfaction surveys - monthly data."""
    filepath = os.path.join(OUTPUT_DIR, "source_b_satisfaction.csv")
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["survey_month", "Team", "REGION", "avg_csat_score",
                          "nps_score", "responses", "complaint_count"])
        for month in MONTHS:
            for team in TEAMS:
                region = random.choice(REGIONS)
                csat = round(random.uniform(3.2, 4.8), 2)
                nps = random.randint(20, 80)
                responses = random.randint(30, 150)
                complaints = random.randint(0, 15)
                writer.writerow([month, team, region, csat, nps, responses, complaints])
    print(f"Generated Source B -> {filepath}")


def generate_source_c():
    """Source C: Operational efficiency logs - daily aggregates."""
    filepath = os.path.join(OUTPUT_DIR, "source_c_efficiency.csv")
    start = datetime.date(2024, 1, 1)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "team_id", "region_name", "applications_received",
                          "applications_reviewed", "avg_review_time_hrs",
                          "rework_count", "system_downtime_min"])
        for day_offset in range(365):
            date = start + datetime.timedelta(days=day_offset)
            if date.weekday() >= 5:  # skip weekends
                continue
            for team in TEAMS:
                region = random.choice(REGIONS)
                received = random.randint(10, 50)
                reviewed = int(received * random.uniform(0.7, 1.0))
                review_time = round(random.uniform(1.5, 6.0), 2)
                rework = random.randint(0, 5)
                downtime = random.randint(0, 30)
                writer.writerow([date.isoformat(), team, region, received,
                                  reviewed, review_time, rework, downtime])
    print(f"Generated Source C -> {filepath}")


if __name__ == "__main__":
    generate_source_a()
    generate_source_b()
    generate_source_c()
    print("\nMulti-source data generation complete!")
