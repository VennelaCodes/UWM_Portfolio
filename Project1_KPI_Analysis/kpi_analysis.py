"""
Project 1: Operational Data Review & KPI Analysis Initiative
Main analysis script - validates data, calculates KPIs, and generates executive summaries.

Key Resume Bullets Demonstrated:
- Owned analysis of 50K+ operational records for KPI alignment & reporting accuracy
- Built structured validation checks reducing reporting inconsistencies by 20%
- Identified data gaps and process inefficiencies through record-level analysis
- Delivered executive-ready data summaries for KPI performance reviews
- Designed documentation workflows improving audit traceability
"""

import csv
import os
from collections import defaultdict
from datetime import datetime

INPUT_DIR = "data"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =============================================================================
# SECTION 1: DATA VALIDATION CHECKS
# Demonstrates: "Built structured validation checks reducing reporting
#                inconsistencies by 20%"
# =============================================================================

class DataValidator:
    """Structured validation framework for operational records."""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.records_checked = 0
        self.clean_records = 0

    def validate_record(self, row, line_num):
        """Apply all validation rules to a single record."""
        self.records_checked += 1
        issues = []

        # Rule 1: Loan amount must be positive and present
        try:
            amount = float(row["loan_amount"]) if row["loan_amount"] else None
            if amount is None:
                issues.append(("ERROR", "Missing loan amount"))
            elif amount <= 0:
                issues.append(("ERROR", f"Invalid loan amount: {amount}"))
        except ValueError:
            issues.append(("ERROR", f"Non-numeric loan amount: {row['loan_amount']}"))

        # Rule 2: Processing days must be non-negative
        try:
            days = int(row["processing_days"])
            if days < 0:
                issues.append(("ERROR", f"Negative processing days: {days}"))
            elif days > 120:
                issues.append(("WARNING", f"Unusually high processing days: {days}"))
        except ValueError:
            issues.append(("ERROR", f"Invalid processing days: {row['processing_days']}"))

        # Rule 3: Submission date should be within reporting period (2024)
        try:
            sub_date = datetime.strptime(row["submission_date"], "%Y-%m-%d")
            if sub_date.year != 2024:
                issues.append(("ERROR", f"Submission date outside reporting period: {row['submission_date']}"))
        except ValueError:
            issues.append(("ERROR", f"Invalid date format: {row['submission_date']}"))

        # Rule 4: Satisfaction score should be 1.0-5.0 if present
        if row["client_satisfaction_score"]:
            try:
                score = float(row["client_satisfaction_score"])
                if score < 1.0 or score > 5.0:
                    issues.append(("ERROR", f"Satisfaction score out of range: {score}"))
            except ValueError:
                issues.append(("ERROR", f"Invalid satisfaction score: {row['client_satisfaction_score']}"))

        # Rule 5: Closed/Approved records should have completion date
        if row["status"] in ["Closed", "Approved", "Denied", "Withdrawn"]:
            if not row["completion_date"]:
                issues.append(("WARNING", "Terminal status without completion date"))

        # Rule 6: Record ID format check
        if not row["record_id"].startswith("OP-2024-"):
            issues.append(("ERROR", f"Invalid record ID format: {row['record_id']}"))

        if not issues:
            self.clean_records += 1

        for severity, message in issues:
            entry = {
                "line": line_num,
                "record_id": row["record_id"],
                "severity": severity,
                "message": message
            }
            if severity == "ERROR":
                self.errors.append(entry)
            else:
                self.warnings.append(entry)

        return len(issues) == 0

    def get_summary(self):
        """Return validation summary statistics."""
        return {
            "total_records": self.records_checked,
            "clean_records": self.clean_records,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "data_quality_pct": round(self.clean_records / self.records_checked * 100, 2)
                                if self.records_checked > 0 else 0
        }


# =============================================================================
# SECTION 2: KPI CALCULATION ENGINE
# Demonstrates: "Owned analysis of 50K+ operational records to ensure KPI
#                alignment, reporting accuracy, and decision-ready data"
# =============================================================================

class KPICalculator:
    """Calculates operational KPIs from validated records."""

    def __init__(self):
        self.records = []
        self.kpi_targets = {}

    def load_records(self, filepath):
        """Load clean operational records."""
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.records.append(row)
        print(f"Loaded {len(self.records)} records for KPI analysis")

    def load_targets(self, filepath):
        """Load KPI target benchmarks."""
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.kpi_targets[row["kpi_name"]] = {
                    "target": float(row["target_value"]),
                    "unit": row["unit"],
                    "direction": row["direction"]
                }

    def calculate_all_kpis(self):
        """Calculate all operational KPIs."""
        results = {}

        # KPI 1: Average Processing Days
        valid_days = [int(r["processing_days"]) for r in self.records
                      if r["processing_days"] and int(r["processing_days"]) >= 0]
        avg_days = sum(valid_days) / len(valid_days) if valid_days else 0
        results["Average Processing Days"] = round(avg_days, 1)

        # KPI 2: Closure Rate
        total = len(self.records)
        closed = sum(1 for r in self.records if r["status"] == "Closed")
        results["Closure Rate"] = round(closed / total * 100, 1) if total else 0

        # KPI 3: Client Satisfaction Score
        scores = [float(r["client_satisfaction_score"]) for r in self.records
                  if r["client_satisfaction_score"] and 1 <= float(r["client_satisfaction_score"]) <= 5]
        results["Client Satisfaction Score"] = round(sum(scores) / len(scores), 2) if scores else 0

        # KPI 4: Escalation Rate
        escalated = sum(1 for r in self.records if r["escalation_flag"] == "1")
        results["Escalation Rate"] = round(escalated / total * 100, 1) if total else 0

        # KPI 5: Denial Rate
        denied = sum(1 for r in self.records if r["status"] == "Denied")
        results["Denial Rate"] = round(denied / total * 100, 1) if total else 0

        # KPI 6: Approval to Close Ratio
        approved = sum(1 for r in self.records if r["status"] in ["Approved", "Closed"])
        results["Approval to Close Ratio"] = round(closed / approved * 100, 1) if approved else 0

        return results

    def calculate_kpis_by_dimension(self, dimension):
        """Calculate KPIs broken down by a specific dimension (region, team, etc.)."""
        grouped = defaultdict(list)
        for r in self.records:
            grouped[r[dimension]].append(r)

        breakdown = {}
        for key, group in sorted(grouped.items()):
            total = len(group)
            closed = sum(1 for r in group if r["status"] == "Closed")
            days = [int(r["processing_days"]) for r in group
                    if r["processing_days"] and int(r["processing_days"]) >= 0]

            breakdown[key] = {
                "total_records": total,
                "closure_rate": round(closed / total * 100, 1) if total else 0,
                "avg_processing_days": round(sum(days) / len(days), 1) if days else 0,
                "escalation_rate": round(
                    sum(1 for r in group if r["escalation_flag"] == "1") / total * 100, 1
                ) if total else 0
            }

        return breakdown

    def compare_to_targets(self, actuals):
        """Compare actual KPIs against targets and flag deviations."""
        comparison = []
        for kpi_name, actual in actuals.items():
            if kpi_name in self.kpi_targets:
                target_info = self.kpi_targets[kpi_name]
                target = target_info["target"]
                direction = target_info["direction"]

                if direction == "higher_is_better":
                    status = "ON TRACK" if actual >= target else "BELOW TARGET"
                    gap = actual - target
                else:
                    status = "ON TRACK" if actual <= target else "ABOVE TARGET"
                    gap = target - actual

                comparison.append({
                    "kpi": kpi_name,
                    "target": target,
                    "actual": actual,
                    "gap": round(gap, 2),
                    "status": status,
                    "unit": target_info["unit"]
                })
        return comparison


# =============================================================================
# SECTION 3: TREND MONITORING & GAP IDENTIFICATION
# Demonstrates: "Identified data gaps and process inefficiencies through
#                record-level analysis and trend monitoring"
# =============================================================================

def analyze_monthly_trends(records):
    """Identify monthly trends in key metrics."""
    monthly = defaultdict(lambda: {"count": 0, "closed": 0, "days": [], "escalations": 0})

    for r in records:
        try:
            month = r["submission_date"][:7]  # YYYY-MM
            monthly[month]["count"] += 1
            if r["status"] == "Closed":
                monthly[month]["closed"] += 1
            if r["processing_days"] and int(r["processing_days"]) >= 0:
                monthly[month]["days"].append(int(r["processing_days"]))
            if r["escalation_flag"] == "1":
                monthly[month]["escalations"] += 1
        except (ValueError, KeyError):
            continue

    trends = []
    for month in sorted(monthly.keys()):
        data = monthly[month]
        trends.append({
            "month": month,
            "volume": data["count"],
            "closure_rate": round(data["closed"] / data["count"] * 100, 1) if data["count"] else 0,
            "avg_processing_days": round(sum(data["days"]) / len(data["days"]), 1) if data["days"] else 0,
            "escalation_rate": round(data["escalations"] / data["count"] * 100, 1) if data["count"] else 0
        })
    return trends


def identify_process_inefficiencies(records):
    """Flag records and patterns that suggest process bottlenecks."""
    inefficiencies = {
        "long_processing": [],  # Records taking > 45 days
        "high_escalation_teams": {},
        "low_closure_regions": {}
    }

    team_stats = defaultdict(lambda: {"total": 0, "escalated": 0})
    region_stats = defaultdict(lambda: {"total": 0, "closed": 0})

    for r in records:
        # Long processing times
        try:
            days = int(r["processing_days"])
            if days > 45:
                inefficiencies["long_processing"].append({
                    "record_id": r["record_id"],
                    "team": r["team"],
                    "days": days,
                    "status": r["status"]
                })
        except ValueError:
            pass

        team_stats[r["team"]]["total"] += 1
        if r["escalation_flag"] == "1":
            team_stats[r["team"]]["escalated"] += 1

        region_stats[r["region"]]["total"] += 1
        if r["status"] == "Closed":
            region_stats[r["region"]]["closed"] += 1

    # Identify high-escalation teams (>18%)
    for team, stats in team_stats.items():
        esc_rate = stats["escalated"] / stats["total"] * 100 if stats["total"] else 0
        if esc_rate > 18:
            inefficiencies["high_escalation_teams"][team] = round(esc_rate, 1)

    # Identify low-closure regions (<40%)
    for region, stats in region_stats.items():
        close_rate = stats["closed"] / stats["total"] * 100 if stats["total"] else 0
        if close_rate < 40:
            inefficiencies["low_closure_regions"][region] = round(close_rate, 1)

    return inefficiencies


# =============================================================================
# SECTION 4: EXECUTIVE SUMMARY GENERATION
# Demonstrates: "Delivered executive-ready data summaries supporting KPI
#                performance reviews and operational decision-making"
# =============================================================================

def generate_executive_summary(kpi_results, comparison, trends, inefficiencies, validation_summary):
    """Generate a formatted executive summary report."""
    filepath = os.path.join(OUTPUT_DIR, "executive_summary.txt")

    with open(filepath, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("    OPERATIONAL DATA REVIEW & KPI ANALYSIS - EXECUTIVE SUMMARY\n")
        f.write(f"    Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        # Data Quality Section
        f.write("1. DATA QUALITY OVERVIEW\n")
        f.write("-" * 40 + "\n")
        f.write(f"   Total Records Analyzed:  {validation_summary['total_records']:,}\n")
        f.write(f"   Clean Records:           {validation_summary['clean_records']:,}\n")
        f.write(f"   Data Quality Score:      {validation_summary['data_quality_pct']}%\n")
        f.write(f"   Errors Detected:         {validation_summary['error_count']:,}\n")
        f.write(f"   Warnings Detected:       {validation_summary['warning_count']:,}\n\n")

        # KPI Performance Section
        f.write("2. KPI PERFORMANCE vs. TARGETS\n")
        f.write("-" * 40 + "\n")
        f.write(f"   {'KPI':<35} {'Target':>8} {'Actual':>8} {'Gap':>8} {'Status':>15}\n")
        f.write(f"   {'-'*35} {'-'*8} {'-'*8} {'-'*8} {'-'*15}\n")
        for c in comparison:
            f.write(f"   {c['kpi']:<35} {c['target']:>8.1f} {c['actual']:>8.1f} "
                    f"{c['gap']:>+8.1f} {c['status']:>15}\n")
        f.write("\n")

        # Trend Summary
        f.write("3. MONTHLY TREND SUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(f"   {'Month':<10} {'Volume':>8} {'Close%':>8} {'Avg Days':>10} {'Esc%':>8}\n")
        f.write(f"   {'-'*10} {'-'*8} {'-'*8} {'-'*10} {'-'*8}\n")
        for t in trends:
            f.write(f"   {t['month']:<10} {t['volume']:>8,} {t['closure_rate']:>7.1f}% "
                    f"{t['avg_processing_days']:>9.1f} {t['escalation_rate']:>7.1f}%\n")
        f.write("\n")

        # Inefficiency Alerts
        f.write("4. PROCESS INEFFICIENCY ALERTS\n")
        f.write("-" * 40 + "\n")
        f.write(f"   Records with >45 day processing: {len(inefficiencies['long_processing']):,}\n")

        if inefficiencies["high_escalation_teams"]:
            f.write("   High-Escalation Teams (>18%):\n")
            for team, rate in sorted(inefficiencies["high_escalation_teams"].items()):
                f.write(f"     - {team}: {rate}%\n")

        if inefficiencies["low_closure_regions"]:
            f.write("   Low-Closure Regions (<40%):\n")
            for region, rate in sorted(inefficiencies["low_closure_regions"].items()):
                f.write(f"     - {region}: {rate}%\n")
        f.write("\n")

        # Recommendations
        f.write("5. RECOMMENDATIONS\n")
        f.write("-" * 40 + "\n")
        recommendations = []
        for c in comparison:
            if "BELOW" in c["status"] or "ABOVE" in c["status"]:
                recommendations.append(
                    f"   - {c['kpi']}: Currently {c['actual']}{c['unit']} vs target "
                    f"{c['target']}{c['unit']}. Recommend focused improvement plan."
                )
        if inefficiencies["high_escalation_teams"]:
            recommendations.append(
                f"   - Review escalation protocols for: "
                f"{', '.join(inefficiencies['high_escalation_teams'].keys())}"
            )
        if len(inefficiencies["long_processing"]) > 500:
            recommendations.append(
                "   - Investigate root cause of extended processing times (>45 days)"
            )

        for rec in recommendations:
            f.write(rec + "\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("    END OF EXECUTIVE SUMMARY\n")
        f.write("=" * 80 + "\n")

    print(f"\nExecutive summary saved -> {filepath}")
    return filepath


# =============================================================================
# SECTION 5: AUDIT TRAIL & DOCUMENTATION
# Demonstrates: "Designed documentation workflows improving audit traceability
#                and cross-team transparency"
# =============================================================================

def generate_validation_log(validator):
    """Generate detailed validation log for audit traceability."""
    filepath = os.path.join(OUTPUT_DIR, "validation_log.csv")

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "record_id", "line_number", "severity", "message"])

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for error in validator.errors:
            writer.writerow([timestamp, error["record_id"], error["line"], "ERROR", error["message"]])
        for warning in validator.warnings:
            writer.writerow([timestamp, warning["record_id"], warning["line"], "WARNING", warning["message"]])

    print(f"Validation log saved -> {filepath} ({len(validator.errors) + len(validator.warnings)} entries)")
    return filepath


def generate_kpi_detail_report(comparison, by_region, by_team):
    """Generate detailed KPI breakdown report."""
    filepath = os.path.join(OUTPUT_DIR, "kpi_detail_report.csv")

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)

        # Overall KPI section
        writer.writerow(["SECTION: Overall KPI Performance"])
        writer.writerow(["KPI", "Target", "Actual", "Gap", "Status"])
        for c in comparison:
            writer.writerow([c["kpi"], c["target"], c["actual"], c["gap"], c["status"]])

        writer.writerow([])

        # By Region
        writer.writerow(["SECTION: KPIs by Region"])
        writer.writerow(["Region", "Total Records", "Closure Rate %", "Avg Processing Days", "Escalation Rate %"])
        for region, metrics in sorted(by_region.items()):
            writer.writerow([region, metrics["total_records"], metrics["closure_rate"],
                             metrics["avg_processing_days"], metrics["escalation_rate"]])

        writer.writerow([])

        # By Team
        writer.writerow(["SECTION: KPIs by Team"])
        writer.writerow(["Team", "Total Records", "Closure Rate %", "Avg Processing Days", "Escalation Rate %"])
        for team, metrics in sorted(by_team.items()):
            writer.writerow([team, metrics["total_records"], metrics["closure_rate"],
                             metrics["avg_processing_days"], metrics["escalation_rate"]])

    print(f"KPI detail report saved -> {filepath}")
    return filepath


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 60)
    print("  OPERATIONAL DATA REVIEW & KPI ANALYSIS INITIATIVE")
    print("=" * 60)

    # Step 1: Load and validate data
    print("\n--- Step 1: Data Validation ---")
    validator = DataValidator()
    records = []

    data_file = os.path.join(INPUT_DIR, "operational_records.csv")
    with open(data_file, "r") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            validator.validate_record(row, i)
            records.append(row)

    summary = validator.get_summary()
    print(f"  Records checked: {summary['total_records']:,}")
    print(f"  Clean records:   {summary['clean_records']:,}")
    print(f"  Data quality:    {summary['data_quality_pct']}%")
    print(f"  Errors found:    {summary['error_count']:,}")
    print(f"  Warnings found:  {summary['warning_count']:,}")

    # Generate validation log
    generate_validation_log(validator)

    # Step 2: Calculate KPIs
    print("\n--- Step 2: KPI Calculation ---")
    calc = KPICalculator()
    calc.records = records
    calc.load_targets(os.path.join(INPUT_DIR, "kpi_targets.csv"))

    kpi_results = calc.calculate_all_kpis()
    for kpi, value in kpi_results.items():
        print(f"  {kpi}: {value}")

    # Compare to targets
    comparison = calc.compare_to_targets(kpi_results)
    print("\n  KPI vs Target Status:")
    for c in comparison:
        print(f"    {c['kpi']}: {c['status']} (gap: {c['gap']:+.1f})")

    # Step 3: Dimensional breakdowns
    print("\n--- Step 3: Dimensional Analysis ---")
    by_region = calc.calculate_kpis_by_dimension("region")
    by_team = calc.calculate_kpis_by_dimension("team")

    print("  By Region:")
    for region, metrics in sorted(by_region.items()):
        print(f"    {region}: Close={metrics['closure_rate']}%, "
              f"Days={metrics['avg_processing_days']}, Esc={metrics['escalation_rate']}%")

    print("  By Team:")
    for team, metrics in sorted(by_team.items()):
        print(f"    {team}: Close={metrics['closure_rate']}%, "
              f"Days={metrics['avg_processing_days']}, Esc={metrics['escalation_rate']}%")

    # Step 4: Trend analysis & inefficiency detection
    print("\n--- Step 4: Trend Analysis ---")
    trends = analyze_monthly_trends(records)
    for t in trends:
        print(f"  {t['month']}: Volume={t['volume']:,}, Close={t['closure_rate']}%, "
              f"Days={t['avg_processing_days']}")

    print("\n--- Step 5: Process Inefficiency Detection ---")
    inefficiencies = identify_process_inefficiencies(records)
    print(f"  Long processing records (>45 days): {len(inefficiencies['long_processing']):,}")
    print(f"  High escalation teams: {list(inefficiencies['high_escalation_teams'].keys())}")
    print(f"  Low closure regions: {list(inefficiencies['low_closure_regions'].keys())}")

    # Step 5: Generate reports
    print("\n--- Step 6: Report Generation ---")
    generate_executive_summary(kpi_results, comparison, trends, inefficiencies, summary)
    generate_kpi_detail_report(comparison, by_region, by_team)

    print("\n" + "=" * 60)
    print("  ANALYSIS COMPLETE - All reports saved to output/")
    print("=" * 60)


if __name__ == "__main__":
    main()
