"""
seed_data.py
============
Builds the SQLite database (helpdesk.db) from schema.sql and fills it
with realistic sample IT help desk tickets.

Why sample data instead of a blank database?
A portfolio project with an empty database doesn't show anything.
Populating it with ~60 realistic tickets across common IT support
categories (Windows troubleshooting, network, printers, Active
Directory, software installs, hardware) lets the analytics script
and the CLI tool actually demonstrate something meaningful.

Run this once before using ticketing_system.py or analysis.py:
    python seed_data.py
"""

import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "data/helpdesk.db"

# ------------------------------------------------------------------
# 1. Connect to the database and create the tables from schema.sql
# ------------------------------------------------------------------
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

with open("schema.sql", "r") as f:
    cursor.executescript(f.read())

# Wipe any existing data so this script can be re-run safely
cursor.execute("DELETE FROM tickets")
cursor.execute("DELETE FROM categories")
cursor.execute("DELETE FROM users")
conn.commit()

# ------------------------------------------------------------------
# 2. Seed users (fictional employees across a few departments)
# ------------------------------------------------------------------
users = [
    ("Alicia Ramos", "Finance", "aramos@company.com"),
    ("Brian Kim", "Operations", "bkim@company.com"),
    ("Carla Nguyen", "Dispatch", "cnguyen@company.com"),
    ("David Ortiz", "HR", "dortiz@company.com"),
    ("Elena Petrova", "Finance", "epetrova@company.com"),
    ("Frank Sullivan", "IT", "fsullivan@company.com"),
    ("Grace Lee", "Dispatch", "glee@company.com"),
    ("Hassan Ali", "Operations", "hali@company.com"),
    ("Isabel Cruz", "HR", "icruz@company.com"),
    ("Jamal Watson", "Field Services", "jwatson@company.com"),
    ("Karen Byrd", "Dispatch", "kbyrd@company.com"),
    ("Luis Fernandez", "Field Services", "lfernandez@company.com"),
]
cursor.executemany(
    "INSERT INTO users (full_name, department, email) VALUES (?, ?, ?)",
    users,
)

# ------------------------------------------------------------------
# 3. Seed categories
# ------------------------------------------------------------------
categories = [
    "Hardware",
    "Network",
    "Printer",
    "Account/Active Directory",
    "Software Install",
    "Email/M365",
    "Asset Request",
    "VPN/Remote Access",
]
cursor.executemany(
    "INSERT INTO categories (category_name) VALUES (?)",
    [(c,) for c in categories],
)
conn.commit()

# Pull back the auto-generated IDs so we can reference them below
cursor.execute("SELECT user_id FROM users")
user_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT category_id, category_name FROM categories")
category_rows = cursor.fetchall()
category_ids = {name: cid for cid, name in category_rows}

# ------------------------------------------------------------------
# 4. Seed realistic tickets
# ------------------------------------------------------------------
# Each entry: (category, subject, description, resolution_notes, priority)
# priority weighting and resolution time ranges (in hours) are set per
# category further down to mimic real-world SLA patterns:
#   - Account lockouts / VPN issues -> resolved fast (people can't work at all)
#   - Asset requests -> resolved slower (procurement/approval delays)

ticket_templates = [
    ("Hardware", "Laptop won't power on",
     "User reports laptop screen stays black, charging light is on.",
     "Reseated battery and reset power circuit; laptop powered on normally.", "High"),
    ("Hardware", "Monitor flickering intermittently",
     "External monitor flickers every few minutes during use.",
     "Replaced HDMI cable; flickering stopped.", "Medium"),
    ("Hardware", "Laptop running extremely slow",
     "User reports laptop takes 10+ minutes to boot and freezes often.",
     "Cleared temp files, disabled unnecessary startup apps, ran disk cleanup.", "Medium"),
    ("Network", "No internet connection at desk",
     "User cannot reach any internal or external sites from their workstation.",
     "Found unplugged patch cable at wall jack; reseated and confirmed link light.", "High"),
    ("Network", "Intermittent WiFi drops in conference room B",
     "WiFi disconnects every 15-20 minutes during meetings.",
     "Identified AP overload; moved device to 5GHz band and reduced client count on AP.", "Medium"),
    ("Network", "Cannot access shared drive",
     "User gets 'network path not found' error accessing \\\\fileserver\\shared.",
     "VPN was not connected; reconnected VPN client and mapped drive successfully.", "Medium"),
    ("Printer", "Print jobs stuck in queue",
     "Documents sent to 3rd floor printer are stuck in queue, nothing prints.",
     "Cleared print spooler service and restarted; queue processed normally.", "Low"),
    ("Printer", "Printer showing offline",
     "Shared printer shows offline status on all workstations.",
     "Printer had lost DHCP lease; assigned static IP and re-added on print server.", "Medium"),
    ("Printer", "Toner replacement needed",
     "Print quality faded significantly, likely low toner.",
     "Replaced toner cartridge and ran test print; quality restored.", "Low"),
    ("Account/Active Directory", "Account locked out",
     "User locked out of Windows login after failed password attempts.",
     "Unlocked account in Active Directory Users and Computers, reset password on next logon.", "Critical"),
    ("Account/Active Directory", "New hire account provisioning",
     "New employee starting Monday needs AD account, email, and shared drive access.",
     "Created AD account, added to appropriate security groups, provisioned mailbox.", "Medium"),
    ("Account/Active Directory", "Password reset request",
     "User forgot password and needs reset before shift starts.",
     "Verified identity, reset password in AD, confirmed successful login.", "High"),
    ("Account/Active Directory", "Access denied to shared folder",
     "User needs access to Finance shared folder for new role.",
     "Added user to Finance-ReadWrite security group; access confirmed.", "Medium"),
    ("Software Install", "Need Adobe Acrobat installed",
     "User requires Adobe Acrobat Pro for contract review work.",
     "Deployed Adobe Acrobat Pro via software deployment tool; verified license activation.", "Low"),
    ("Software Install", "Excel crashing on open",
     "Excel crashes immediately when opening any file.",
     "Repaired Office 365 installation via Apps & Features; issue resolved.", "Medium"),
    ("Software Install", "Browser extension blocking site access",
     "User cannot access internal ticketing portal, browser shows blank page.",
     "Disabled conflicting ad-block extension; portal loaded correctly.", "Low"),
    ("Email/M365", "Not receiving external emails",
     "User not receiving emails from outside the organization since yesterday.",
     "Found external emails routed to quarantine by spam filter; released and adjusted rule.", "High"),
    ("Email/M365", "Outlook not syncing on mobile",
     "Outlook mobile app stopped syncing new mail on user's phone.",
     "Removed and re-added account profile on device; sync resumed.", "Low"),
    ("Email/M365", "Shared mailbox permission request",
     "User needs send-as permission on Dispatch shared mailbox.",
     "Granted send-as permission via Exchange admin center.", "Medium"),
    ("Asset Request", "New laptop request for field technician",
     "Field Services requesting a new ruggedized laptop for new hire.",
     "Processed asset request, imaged laptop with standard build, logged serial number in asset inventory.", "Low"),
    ("Asset Request", "Docking station request",
     "User requests docking station for dual-monitor setup at desk.",
     "Issued docking station from inventory, updated asset tag assignment.", "Low"),
    ("Asset Request", "Replace end-of-life desktop",
     "Desktop is 6+ years old and flagged for replacement in asset inventory.",
     "Deployed replacement desktop from standard image, decommissioned and wiped old unit per policy.", "Medium"),
    ("VPN/Remote Access", "VPN client won't connect",
     "User working remotely cannot establish VPN connection, times out.",
     "Reinstalled VPN client and reset stored credentials; connection succeeded.", "Critical"),
    ("VPN/Remote Access", "MFA push notifications not arriving",
     "User not receiving MFA push notifications when logging into VPN.",
     "Re-registered MFA device in authentication portal; notifications resumed.", "High"),
]

# Resolution time ranges (hours) per priority, used to generate resolved_at
resolution_hour_ranges = {
    "Critical": (0.5, 4),
    "High": (2, 12),
    "Medium": (6, 48),
    "Low": (12, 96),
}

random.seed(42)  # fixed seed so the dataset is reproducible

start_date = datetime(2026, 4, 1)
end_date = datetime(2026, 7, 10)
date_span_days = (end_date - start_date).days

rows_to_insert = []
ticket_count = 60

for i in range(ticket_count):
    template = random.choice(ticket_templates)
    category_name, subject, description, resolution_notes, priority = template

    user_id = random.choice(user_ids)
    category_id = category_ids[category_name]

    created_at = start_date + timedelta(
        days=random.randint(0, date_span_days),
        hours=random.randint(7, 17),  # business hours
    )

    # 90% of tickets are resolved/closed; 10% remain open to show a
    # realistic active queue in the reporting
    is_resolved = random.random() < 0.90

    if is_resolved:
        low, high = resolution_hour_ranges[priority]
        resolution_hours = random.uniform(low, high)
        resolved_at = created_at + timedelta(hours=resolution_hours)
        status = "Closed"
    else:
        resolved_at = None
        status = random.choice(["Open", "In Progress"])
        resolution_notes = None

    rows_to_insert.append((
        user_id,
        category_id,
        subject,
        description,
        priority,
        status,
        created_at.strftime("%Y-%m-%d %H:%M"),
        resolved_at.strftime("%Y-%m-%d %H:%M") if resolved_at else None,
        resolution_notes,
    ))

cursor.executemany(
    """
    INSERT INTO tickets
        (user_id, category_id, subject, description, priority,
         status, created_at, resolved_at, resolution_notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    rows_to_insert,
)

conn.commit()
conn.close()

print(f"Database seeded successfully: {DB_PATH}")
print(f"  - {len(users)} users")
print(f"  - {len(categories)} categories")
print(f"  - {ticket_count} tickets")
