"""
Project 3: Ad-hoc Reporting & Process Efficiency Project
Main script for ad-hoc report generation, validation, and performance tracking.

Key Resume Bullets Demonstrated:
- Delivered high-priority ad-hoc reporting requests under tight deadlines
- Built structured summary reports for daily, weekly, and monthly performance tracking
- Implemented pre-submission validation scripts minimizing downstream reporting errors
- Collaborated with cross-functional stakeholders to clarify reporting needs
"""

import csv
import os
from collections import defaultdict
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


# =============================================================================
# SECTION 1: AD-HOC REPORTING ENGINE
# Demonstrates: "Delivered high-priority ad-hoc reporting requests under
#                tight deadlines across multiple business units"
# =============================================================================

class AdhocReportingEngine:
    """Handles ad-hoc reporting requests with priority-based processing."""

    def __init__(self):
        self.daily_data = []
        self.weekly_data = []
        self.monthly_targets = []
        self.request_log = []

    def load_all_data(self):
        """Load all data sources."""
        # Daily performance
        with open(os.path.join(DATA_DIR, "daily_performance.csv"), "r") as f:
            self.daily_data = list(csv.DictReader(f))
        print(f"  Loaded {len(self.daily_data)} daily records")

        # Weekly summary
        with open(os.path.join(DATA_DIR, "weekly_summary.csv"), "r") as f:
            self.weekly_data = list(csv.DictReader(f))
        print(f"  Loaded {len(self.weekly_data)} weekly records")

        # Monthly targets
        with open(os.path.join(DATA_DIR, "monthly_targets.csv"), "r") as f:
            self.monthly_targets = list(csv.DictReader(f))
        print(f"  Loaded {len(self.monthly_targets)} monthly targets")

        # Request log
        with open(os.path.join(DATA_DIR, "adhoc_requests.csv"), "r") as f:
            self.request_log = list(csv.DictReader(f))
        print(f"  Loaded {len(self.request_log)} ad-hoc requests")

    def generate_performance_summary(self, business_unit, start_date, end_date):
        """Generate a performance summary for a specific business unit and date range."""
        filtered = [r for r in self.daily_data
                    if r["business_unit"] == business_unit
                    and start_date <= r["date"] <= end_date]

        if not filtered:
            return None

        total_completed = sum(int(r["loans_completed"]) for r in filtered)
        total_pipeline = sum(int(r["loans_in_pipeline"]) for r in filtered)
        total_errors = sum(int(r["error_count"]) for r in filtered)
        avg_cycle = sum(float(r["avg_cycle_time_days"]) for r in filtered) / len(filtered)
        total_overtime = sum(float(r["overtime_hours"]) for r in filtered)

        return {
            "business_unit": business_unit,
            "period": f"{start_date} to {end_date}",
            "working_days": len(filtered),
            "total_loans_completed": total_completed,
            "avg_daily_pipeline": round(total_pipeline / len(filtered)),
            "avg_cycle_time_days": round(avg_cycle, 1),
            "total_errors": total_errors,
            "error_rate_pct": round(total_errors / max(total_completed, 1) * 100, 2),
            "total_overtime_hours": round(total_overtime, 1),
            "productivity": round(total_completed / len(filtered), 1)
        }

    def generate_exception_report(self, threshold_cycle_time=25, threshold_errors=5):
        """Identify days that exceeded performance thresholds."""
        exceptions = []
        for r in self.daily_data:
            reasons = []
            if float(r["avg_cycle_time_days"]) > threshold_cycle_time:
                reasons.append(f"Cycle time {r['avg_cycle_time_days']}d > {threshold_cycle_time}d")
            if int(r["error_count"]) > threshold_errors:
                reasons.append(f"Errors {r['error_count']} > {threshold_errors}")
            if reasons:
                exceptions.append({
                    "date": r["date"],
                    "business_unit": r["business_unit"],
                    "reasons": "; ".join(reasons),
                    "cycle_time": r["avg_cycle_time_days"],
                    "errors": r["error_count"]
                })
        return exceptions

    def generate_trend_analysis(self, business_unit):
        """Monthly trend analysis for a business unit."""
        monthly = defaultdict(lambda: {
            "completed": 0, "pipeline": 0, "errors": 0,
            "cycle_times": [], "days": 0
        })

        for r in self.daily_data:
            if r["business_unit"] != business_unit:
                continue
            month = r["date"][:7]
            monthly[month]["completed"] += int(r["loans_completed"])
            monthly[month]["pipeline"] += int(r["loans_in_pipeline"])
            monthly[month]["errors"] += int(r["error_count"])
            monthly[month]["cycle_times"].append(float(r["avg_cycle_time_days"]))
            monthly[month]["days"] += 1

        trends = []
        for month in sorted(monthly.keys()):
            data = monthly[month]
            trends.append({
                "month": month,
                "total_completed": data["completed"],
                "avg_daily_pipeline": round(data["pipeline"] / data["days"]),
                "avg_cycle_time": round(sum(data["cycle_times"]) / len(data["cycle_times"]), 1),
                "total_errors": data["errors"],
                "error_rate": round(data["errors"] / max(data["completed"], 1) * 100, 2)
            })
        return trends


# =============================================================================
# SECTION 2: STRUCTURED SUMMARY REPORTS
# Demonstrates: "Built structured summary reports for daily, weekly, and
#                monthly performance tracking"
# =============================================================================

class StructuredReportBuilder:
    """Generates standardized reports at daily, weekly, and monthly intervals."""

    def __init__(self, engine):
        self.engine = engine

    def build_daily_report(self, target_date):
        """Build daily performance report across all business units."""
        filepath = os.path.join(REPORTS_DIR, f"daily_report_{target_date}.csv")
        day_data = [r for r in self.engine.daily_data if r["date"] == target_date]

        if not day_data:
            return None

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Business Unit", "Pipeline", "Completed", "Completion %",
                              "Cycle Time (days)", "Errors", "Staff", "Overtime Hrs"])
            totals = {"pipeline": 0, "completed": 0, "errors": 0, "staff": 0, "overtime": 0}
            for r in day_data:
                pipeline = int(r["loans_in_pipeline"])
                completed = int(r["loans_completed"])
                comp_pct = round(completed / max(pipeline, 1) * 100, 1)
                totals["pipeline"] += pipeline
                totals["completed"] += completed
                totals["errors"] += int(r["error_count"])
                totals["staff"] += int(r["staff_count"])
                totals["overtime"] += float(r["overtime_hours"])
                writer.writerow([
                    r["business_unit"], pipeline, completed, comp_pct,
                    r["avg_cycle_time_days"], r["error_count"],
                    r["staff_count"], r["overtime_hours"]
                ])
            # Totals row
            writer.writerow([
                "TOTAL", totals["pipeline"], totals["completed"],
                round(totals["completed"] / max(totals["pipeline"], 1) * 100, 1),
                "", totals["errors"], totals["staff"], round(totals["overtime"], 1)
            ])
        return filepath

    def build_weekly_report(self, week_number):
        """Build weekly performance summary."""
        filepath = os.path.join(REPORTS_DIR, f"weekly_report_W{week_number:02d}.csv")
        week_data = [r for r in self.engine.weekly_data if r["week_number"] == str(week_number)]

        if not week_data:
            return None

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Business Unit", "Week Ending", "Processed", "Completed",
                              "Completion Rate %", "Avg Cycle Time", "Escalations",
                              "Client Contacts"])
            for r in week_data:
                writer.writerow([
                    r["business_unit"], r["week_ending"], r["total_processed"],
                    r["total_completed"], r["completion_rate"], r["avg_cycle_time"],
                    r["escalations"], r["client_contacts"]
                ])
        return filepath

    def build_monthly_report(self, target_month):
        """Build comprehensive monthly performance report with target comparison."""
        filepath = os.path.join(REPORTS_DIR, f"monthly_report_{target_month}.txt")

        bu_list = ["Underwriting", "Closing", "Client Services", "Compliance", "Operations"]

        with open(filepath, "w") as f:
            f.write("=" * 70 + "\n")
            f.write(f"  MONTHLY PERFORMANCE REPORT - {target_month}\n")
            f.write(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")

            for bu in bu_list:
                summary = self.engine.generate_performance_summary(
                    bu, f"{target_month}-01", f"{target_month}-31"
                )
                if not summary:
                    continue

                # Find target
                target = next((t for t in self.engine.monthly_targets
                              if t["month"] == target_month and t["business_unit"] == bu), None)

                f.write(f"\n  {bu.upper()}\n")
                f.write(f"  {'-' * 40}\n")
                f.write(f"  Working Days:        {summary['working_days']}\n")
                f.write(f"  Loans Completed:     {summary['total_loans_completed']:,}\n")
                f.write(f"  Avg Daily Pipeline:  {summary['avg_daily_pipeline']:,}\n")
                f.write(f"  Avg Cycle Time:      {summary['avg_cycle_time_days']} days")
                if target:
                    target_ct = float(target["target_cycle_time"])
                    status = "OK" if summary["avg_cycle_time_days"] <= target_ct else "OVER"
                    f.write(f" (target: {target_ct}, {status})")
                f.write("\n")
                f.write(f"  Error Rate:          {summary['error_rate_pct']}%")
                if target:
                    target_er = float(target["target_error_rate"])
                    status = "OK" if summary["error_rate_pct"] <= target_er else "HIGH"
                    f.write(f" (target: {target_er}%, {status})")
                f.write("\n")
                f.write(f"  Overtime Hours:      {summary['total_overtime_hours']}\n")
                f.write(f"  Daily Productivity:  {summary['productivity']} loans/day\n")

            f.write("\n" + "=" * 70 + "\n")
        return filepath

    def generate_all_structured_reports(self):
        """Generate sample reports at all frequencies."""
        print("\n  Generating sample daily reports...")
        dates = ["2024-03-15", "2024-06-15", "2024-09-15", "2024-12-15"]
        for d in dates:
            result = self.build_daily_report(d)
            if result:
                print(f"    -> {result}")

        print("\n  Generating sample weekly reports...")
        for week in [1, 13, 26, 39, 52]:
            result = self.build_weekly_report(week)
            if result:
                print(f"    -> {result}")

        print("\n  Generating monthly reports...")
        for m in range(1, 13):
            result = self.build_monthly_report(f"2024-{m:02d}")
            if result:
                print(f"    -> {result}")


# =============================================================================
# SECTION 3: PRE-SUBMISSION VALIDATION
# Demonstrates: "Implemented pre-submission validation scripts minimizing
#                downstream reporting errors"
# =============================================================================

class ReportValidator:
    """Validates reports before submission to catch errors early."""

    def __init__(self):
        self.validation_results = []

    def validate_csv_report(self, filepath):
        """Run validation checks on a CSV report file."""
        issues = []
        filename = os.path.basename(filepath)

        if not os.path.exists(filepath):
            issues.append(("CRITICAL", "File does not exist"))
            self.validation_results.append({"file": filename, "issues": issues})
            return False

        with open(filepath, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Check 1: File has header and data
        if len(rows) < 2:
            issues.append(("ERROR", "File has no data rows"))

        # Check 2: Consistent column count
        if rows:
            header_cols = len(rows[0])
            for i, row in enumerate(rows[1:], 2):
                if len(row) != header_cols:
                    issues.append(("ERROR", f"Row {i}: Expected {header_cols} columns, found {len(row)}"))

        # Check 3: No empty critical cells in first 3 columns
        for i, row in enumerate(rows[1:], 2):
            for j in range(min(3, len(row))):
                if not row[j].strip():
                    issues.append(("WARNING", f"Row {i}, Col {j+1}: Empty value in key column"))

        # Check 4: Numeric fields are valid
        for i, row in enumerate(rows[1:], 2):
            for j, val in enumerate(row):
                if val.strip() and val.replace(".", "").replace("-", "").isdigit():
                    try:
                        num = float(val)
                        if num < 0 and rows[0][j] not in ["gap", "variance"]:
                            issues.append(("WARNING", f"Row {i}: Negative value {val} in {rows[0][j]}"))
                    except ValueError:
                        pass

        # Check 5: No duplicate rows
        data_rows = [tuple(r) for r in rows[1:]]
        if len(data_rows) != len(set(data_rows)):
            issues.append(("ERROR", "Duplicate rows detected"))

        status = "PASS" if not any(i[0] == "ERROR" for i in issues) else "FAIL"
        self.validation_results.append({
            "file": filename,
            "status": status,
            "rows": len(rows) - 1,
            "issues": issues
        })
        return status == "PASS"

    def validate_all_reports(self, reports_dir):
        """Validate all CSV reports in the directory."""
        csv_files = [f for f in os.listdir(reports_dir) if f.endswith(".csv")]
        passed = 0
        failed = 0

        for filename in sorted(csv_files):
            filepath = os.path.join(reports_dir, filename)
            if self.validate_csv_report(filepath):
                passed += 1
            else:
                failed += 1

        return passed, failed

    def generate_validation_report(self):
        """Generate validation summary report."""
        filepath = os.path.join(OUTPUT_DIR, "pre_submission_validation.txt")

        with open(filepath, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("  PRE-SUBMISSION VALIDATION REPORT\n")
            f.write(f"  Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            total_pass = sum(1 for r in self.validation_results if r["status"] == "PASS")
            total_fail = sum(1 for r in self.validation_results if r["status"] == "FAIL")

            f.write(f"  Files Validated: {len(self.validation_results)}\n")
            f.write(f"  Passed: {total_pass}\n")
            f.write(f"  Failed: {total_fail}\n\n")

            for result in self.validation_results:
                icon = "PASS" if result["status"] == "PASS" else "FAIL"
                f.write(f"  [{icon}] {result['file']} ({result['rows']} rows)\n")
                for severity, message in result["issues"]:
                    f.write(f"        [{severity}] {message}\n")

            f.write("\n" + "=" * 60 + "\n")

        print(f"  Validation report -> {filepath}")
        return filepath


# =============================================================================
# SECTION 4: AD-HOC REQUEST TRACKING & ANALYSIS
# Demonstrates: "Collaborated with cross-functional stakeholders to clarify
#                reporting needs and refine deliverables"
# =============================================================================

def analyze_adhoc_requests(request_log):
    """Analyze ad-hoc request patterns to improve process efficiency."""
    filepath = os.path.join(OUTPUT_DIR, "adhoc_request_analysis.txt")

    # Metrics by business unit
    by_bu = defaultdict(lambda: {"total": 0, "completed": 0, "turnaround_hrs": []})
    by_priority = defaultdict(lambda: {"total": 0, "completed": 0, "turnaround_hrs": []})
    by_type = defaultdict(int)
    by_month = defaultdict(int)

    for r in request_log:
        bu = r["business_unit"]
        by_bu[bu]["total"] += 1
        by_type[r["request_type"]] += 1
        by_month[r["request_date"][:7]] += 1
        by_priority[r["priority"]]["total"] += 1

        if r["status"] == "Completed" and r["turnaround_hours"]:
            by_bu[bu]["completed"] += 1
            by_bu[bu]["turnaround_hrs"].append(int(r["turnaround_hours"]))
            by_priority[r["priority"]]["completed"] += 1
            by_priority[r["priority"]]["turnaround_hrs"].append(int(r["turnaround_hours"]))

    with open(filepath, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("  AD-HOC REQUEST ANALYSIS\n")
        f.write(f"  Period: 2024 | Total Requests: {len(request_log)}\n")
        f.write("=" * 60 + "\n\n")

        f.write("  BY BUSINESS UNIT:\n")
        f.write(f"  {'Unit':<20} {'Total':>6} {'Done':>6} {'Avg Hrs':>8} {'On-Time%':>9}\n")
        f.write(f"  {'-'*20} {'-'*6} {'-'*6} {'-'*8} {'-'*9}\n")
        for bu in sorted(by_bu.keys()):
            data = by_bu[bu]
            avg_hrs = (sum(data["turnaround_hrs"]) / len(data["turnaround_hrs"])
                      if data["turnaround_hrs"] else 0)
            on_time = round(data["completed"] / max(data["total"], 1) * 100, 1)
            f.write(f"  {bu:<20} {data['total']:>6} {data['completed']:>6} "
                    f"{avg_hrs:>7.1f} {on_time:>8.1f}%\n")

        f.write("\n  BY PRIORITY:\n")
        f.write(f"  {'Priority':<10} {'Total':>6} {'Avg Turnaround Hrs':>20}\n")
        f.write(f"  {'-'*10} {'-'*6} {'-'*20}\n")
        for priority in ["High", "Medium", "Low"]:
            data = by_priority[priority]
            avg = (sum(data["turnaround_hrs"]) / len(data["turnaround_hrs"])
                  if data["turnaround_hrs"] else 0)
            f.write(f"  {priority:<10} {data['total']:>6} {avg:>19.1f}\n")

        f.write("\n  MOST REQUESTED REPORT TYPES:\n")
        for rtype, count in sorted(by_type.items(), key=lambda x: -x[1]):
            f.write(f"    {rtype:<25} {count:>4} requests\n")

        f.write("\n  MONTHLY REQUEST VOLUME:\n")
        for month in sorted(by_month.keys()):
            bar = "#" * (by_month[month] // 2)
            f.write(f"    {month}  {by_month[month]:>3}  {bar}\n")

        f.write("\n  RECOMMENDATIONS:\n")
        f.write("  1. Most frequent request types should be automated as recurring reports.\n")
        f.write("  2. High-priority requests averaging >24h turnaround need process review.\n")
        f.write("  3. Consider self-service dashboards for top-requesting business units.\n")

        f.write("\n" + "=" * 60 + "\n")

    print(f"\n  Request analysis -> {filepath}")
    return filepath


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 60)
    print("  AD-HOC REPORTING & PROCESS EFFICIENCY PROJECT")
    print("=" * 60)

    # Step 1: Load data
    print("\n--- Step 1: Load Data ---")
    engine = AdhocReportingEngine()
    engine.load_all_data()

    # Step 2: Generate structured reports
    print("\n--- Step 2: Structured Report Generation ---")
    builder = StructuredReportBuilder(engine)
    builder.generate_all_structured_reports()

    # Step 3: Generate ad-hoc reports
    print("\n--- Step 3: Ad-hoc Report Examples ---")
    print("  Generating performance summaries for each business unit...")
    for bu in ["Underwriting", "Closing", "Client Services", "Compliance", "Operations"]:
        summary = engine.generate_performance_summary(bu, "2024-01-01", "2024-12-31")
        if summary:
            print(f"    {bu}: {summary['total_loans_completed']:,} completed, "
                  f"{summary['avg_cycle_time_days']}d avg cycle, "
                  f"{summary['error_rate_pct']}% error rate")

    print("\n  Generating exception report...")
    exceptions = engine.generate_exception_report()
    print(f"    Found {len(exceptions)} exception records")

    # Save exceptions
    exc_path = os.path.join(OUTPUT_DIR, "exception_report.csv")
    with open(exc_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Business Unit", "Reasons", "Cycle Time", "Errors"])
        for e in exceptions[:50]:  # Top 50
            writer.writerow([e["date"], e["business_unit"], e["reasons"],
                             e["cycle_time"], e["errors"]])
    print(f"    -> {exc_path}")

    print("\n  Generating trend analysis...")
    for bu in ["Underwriting", "Client Services"]:
        trends = engine.generate_trend_analysis(bu)
        print(f"    {bu} trends: {len(trends)} months analyzed")

    # Step 4: Pre-submission validation
    print("\n--- Step 4: Pre-submission Validation ---")
    validator = ReportValidator()
    passed, failed = validator.validate_all_reports(REPORTS_DIR)
    print(f"  Validated {passed + failed} reports: {passed} passed, {failed} failed")
    validator.generate_validation_report()

    # Step 5: Ad-hoc request analysis
    print("\n--- Step 5: Ad-hoc Request Pattern Analysis ---")
    analyze_adhoc_requests(engine.request_log)

    print("\n" + "=" * 60)
    print("  PROJECT COMPLETE - Reports in reports/, Analysis in output/")
    print("=" * 60)


if __name__ == "__main__":
    main()
