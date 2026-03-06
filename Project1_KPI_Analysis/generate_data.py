"""
Project 1: Operational Data Review & KPI Analysis Initiative
Generates 50K+ synthetic operational records simulating a mortgage/loan processing environment.
"""

import csv
import random
import datetime
import os

random.seed(42)

# --- Configuration ---
NUM_RECORDS = 52000
OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Reference Data ---
REGIONS = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]
TEAMS = [f"Team_{chr(65+i)}" for i in range(10)]  # Team_A through Team_J
LOAN_TYPES = ["Conventional", "FHA", "VA", "Jumbo", "USDA"]
STATUSES = ["Submitted", "In Review", "Underwriting", "Approved", "Closed", "Denied", "Withdrawn"]
PROCESSORS = [f"Processor_{i:03d}" for i in range(1, 51)]

# Status weights (most should be Closed/Approved for realism)
STATUS_WEIGHTS = [0.08, 0.07, 0.10, 0.15, 0.45, 0.10, 0.05]

def random_date(start, end):
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + datetime.timedelta(days=random_days)

def generate_operational_records():
    """Generate 52K operational records with realistic mortgage processing data."""
    filepath = os.path.join(OUTPUT_DIR, "operational_records.csv")

    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2024, 12, 31)

    # Introduce intentional data quality issues (~5% of records) for validation demo
    error_count = 0

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "record_id", "submission_date", "loan_type", "loan_amount",
            "region", "team", "processor", "status", "processing_days",
            "client_satisfaction_score", "escalation_flag", "completion_date",
            "error_flag"
        ])

        for i in range(1, NUM_RECORDS + 1):
            record_id = f"OP-2024-{i:06d}"
            submission_date = random_date(start_date, end_date)
            loan_type = random.choice(LOAN_TYPES)

            # Loan amounts vary by type
            if loan_type == "Jumbo":
                loan_amount = round(random.uniform(500000, 2000000), 2)
            elif loan_type == "USDA":
                loan_amount = round(random.uniform(100000, 350000), 2)
            else:
                loan_amount = round(random.uniform(150000, 750000), 2)

            region = random.choice(REGIONS)
            team = random.choice(TEAMS)
            processor = random.choice(PROCESSORS)
            status = random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0]

            # Processing days depends on status
            if status in ["Closed", "Approved"]:
                processing_days = random.randint(15, 60)
            elif status == "Denied":
                processing_days = random.randint(10, 45)
            elif status == "Withdrawn":
                processing_days = random.randint(5, 30)
            else:
                processing_days = random.randint(1, 30)

            completion_date = ""
            if status in ["Closed", "Approved", "Denied", "Withdrawn"]:
                completion_date = (submission_date + datetime.timedelta(days=processing_days)).isoformat()

            satisfaction = round(random.uniform(1, 5), 1) if status == "Closed" else ""
            escalation = random.choices([0, 1], weights=[0.85, 0.15], k=1)[0]

            # Introduce data quality issues for ~5% of records
            error_flag = 0
            if random.random() < 0.05:
                error_flag = 1
                error_count += 1
                issue_type = random.choice(["missing_amount", "negative_days", "future_date", "invalid_score"])
                if issue_type == "missing_amount":
                    loan_amount = ""
                elif issue_type == "negative_days":
                    processing_days = -random.randint(1, 10)
                elif issue_type == "future_date":
                    submission_date = datetime.date(2025, random.randint(1, 6), random.randint(1, 28))
                elif issue_type == "invalid_score":
                    satisfaction = 7.5  # out of range

            writer.writerow([
                record_id, submission_date.isoformat(), loan_type, loan_amount,
                region, team, processor, status, processing_days,
                satisfaction, escalation, completion_date, error_flag
            ])

    print(f"Generated {NUM_RECORDS} records -> {filepath}")
    print(f"Intentional data quality issues: {error_count} records ({error_count/NUM_RECORDS*100:.1f}%)")

def generate_kpi_targets():
    """Generate KPI target reference data."""
    filepath = os.path.join(OUTPUT_DIR, "kpi_targets.csv")

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["kpi_name", "target_value", "unit", "frequency", "direction"])

        kpis = [
            ("Average Processing Days", 30, "days", "Monthly", "lower_is_better"),
            ("Closure Rate", 45, "percent", "Monthly", "higher_is_better"),
            ("Client Satisfaction Score", 4.0, "score_1_to_5", "Monthly", "higher_is_better"),
            ("Escalation Rate", 10, "percent", "Weekly", "lower_is_better"),
            ("Denial Rate", 12, "percent", "Monthly", "lower_is_better"),
            ("Approval to Close Ratio", 75, "percent", "Monthly", "higher_is_better"),
            ("Records Processed per Processor", 100, "count", "Monthly", "higher_is_better"),
            ("Data Quality Score", 95, "percent", "Weekly", "higher_is_better"),
        ]

        for kpi in kpis:
            writer.writerow(kpi)

    print(f"Generated KPI targets -> {filepath}")

if __name__ == "__main__":
    generate_operational_records()
    generate_kpi_targets()
    print("\nData generation complete!")
