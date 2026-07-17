"""
analysis.py
===========
Generates help desk reporting metrics from the ticket database:
  - Ticket volume by category
  - Average resolution time by priority (a basic SLA view)
  - Ticket volume over time (by month)

This mirrors the kind of reporting a real help desk manager reviews
to spot recurring problem areas and staffing needs. Charts are saved
as PNG files in the reports/ folder, and a summary is printed to the
console and written to reports/summary.txt.

Run it with:
    python analysis.py
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = "data/helpdesk.db"
REPORTS_DIR = "reports"

conn = sqlite3.connect(DB_PATH)

# ------------------------------------------------------------------
# Load tickets into a DataFrame with category names joined in
# ------------------------------------------------------------------
query = """
    SELECT t.ticket_id, c.category_name, t.priority, t.status,
           t.created_at, t.resolved_at
    FROM tickets t
    JOIN categories c ON t.category_id = c.category_id
"""
df = pd.read_sql_query(query, conn)
conn.close()

df["created_at"] = pd.to_datetime(df["created_at"])
df["resolved_at"] = pd.to_datetime(df["resolved_at"])

# Resolution time in hours (NaN for still-open tickets)
df["resolution_hours"] = (df["resolved_at"] - df["created_at"]).dt.total_seconds() / 3600

summary_lines = []


def log(line=""):
    """Print to console and also collect for the summary text file."""
    print(line)
    summary_lines.append(line)


log("=" * 60)
log("IT HELP DESK - TICKET METRICS SUMMARY")
log("=" * 60)

# ------------------------------------------------------------------
# 1. Ticket volume by category
# ------------------------------------------------------------------
volume_by_category = df["category_name"].value_counts()

log("\nTicket Volume by Category")
log("-" * 40)
for category, count in volume_by_category.items():
    log(f"  {category:<28} {count}")

plt.figure(figsize=(8, 5))
volume_by_category.sort_values().plot(kind="barh", color="#2c7fb8")
plt.title("Ticket Volume by Category")
plt.xlabel("Number of Tickets")
plt.tight_layout()
plt.savefig(f"{REPORTS_DIR}/volume_by_category.png")
plt.close()

# ------------------------------------------------------------------
# 2. Average resolution time by priority (only closed tickets)
# ------------------------------------------------------------------
closed = df.dropna(subset=["resolution_hours"])
avg_resolution_by_priority = (
    closed.groupby("priority")["resolution_hours"]
    .mean()
    .reindex(["Critical", "High", "Medium", "Low"])  # keep a logical order
)

log("\nAverage Resolution Time by Priority (hours)")
log("-" * 40)
for priority, hours in avg_resolution_by_priority.items():
    if pd.notna(hours):
        log(f"  {priority:<10} {hours:.1f} hrs")

plt.figure(figsize=(6, 5))
avg_resolution_by_priority.plot(kind="bar", color="#de2d26")
plt.title("Average Resolution Time by Priority")
plt.ylabel("Hours")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{REPORTS_DIR}/resolution_time_by_priority.png")
plt.close()

# ------------------------------------------------------------------
# 3. Ticket volume by month
# ------------------------------------------------------------------
df["month"] = df["created_at"].dt.to_period("M").astype(str)
volume_by_month = df.groupby("month").size()

log("\nTicket Volume by Month")
log("-" * 40)
for month, count in volume_by_month.items():
    log(f"  {month:<10} {count}")

plt.figure(figsize=(8, 5))
volume_by_month.plot(kind="line", marker="o", color="#31a354")
plt.title("Ticket Volume Over Time")
plt.ylabel("Tickets Opened")
plt.xlabel("Month")
plt.tight_layout()
plt.savefig(f"{REPORTS_DIR}/volume_by_month.png")
plt.close()

# ------------------------------------------------------------------
# 4. Open queue snapshot
# ------------------------------------------------------------------
open_count = (df["status"] != "Closed").sum()
total_count = len(df)

log("\nCurrent Queue Snapshot")
log("-" * 40)
log(f"  Total tickets:  {total_count}")
log(f"  Open/active:    {open_count}")
log(f"  Closed:         {total_count - open_count}")

log("\nCharts saved to reports/: volume_by_category.png, "
    "resolution_time_by_priority.png, volume_by_month.png")

# ------------------------------------------------------------------
# Write the text summary to a file too
# ------------------------------------------------------------------
with open(f"{REPORTS_DIR}/summary.txt", "w") as f:
    f.write("\n".join(summary_lines))
