"""
ticketing_system.py
====================
A simple command-line IT help desk ticketing tool.

This simulates the core workflow of a real ticketing system like
ServiceNow: logging a new ticket, updating its status as it's worked,
searching/filtering existing tickets, and closing a ticket with
resolution notes.

Run it with:
    python ticketing_system.py

Make sure you've run seed_data.py first so the database exists.
"""

import sqlite3
from datetime import datetime

DB_PATH = "data/helpdesk.db"


def get_connection():
    """Open a connection to the database with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def print_menu():
    print("\n===== IT HELP DESK TICKETING SYSTEM =====")
    print("1. View all open tickets")
    print("2. Create a new ticket")
    print("3. Update ticket status")
    print("4. Close a ticket (add resolution notes)")
    print("5. Search tickets by category")
    print("6. View ticket details")
    print("7. Exit")


def view_open_tickets(conn):
    """Show every ticket that isn't Closed, most recent first."""
    query = """
        SELECT t.ticket_id, u.full_name, c.category_name, t.subject,
               t.priority, t.status, t.created_at
        FROM tickets t
        JOIN users u ON t.user_id = u.user_id
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.status != 'Closed'
        ORDER BY t.created_at DESC
    """
    rows = conn.execute(query).fetchall()

    if not rows:
        print("\nNo open tickets. Queue is clear!")
        return

    print(f"\n{'ID':<5}{'Requester':<18}{'Category':<26}{'Priority':<10}{'Status':<14}{'Created'}")
    print("-" * 95)
    for row in rows:
        ticket_id, name, category, subject, priority, status, created_at = row
        print(f"{ticket_id:<5}{name:<18}{category:<26}{priority:<10}{status:<14}{created_at}")


def create_ticket(conn):
    """Prompt the tech for details and insert a new ticket."""
    cursor = conn.cursor()

    print("\n--- New Ticket ---")

    # Show available users so the tech can pick a valid ID
    users = cursor.execute("SELECT user_id, full_name, department FROM users").fetchall()
    for uid, name, dept in users:
        print(f"  {uid}: {name} ({dept})")
    user_id = input("Requester user ID: ").strip()

    categories = cursor.execute("SELECT category_id, category_name FROM categories").fetchall()
    for cid, cname in categories:
        print(f"  {cid}: {cname}")
    category_id = input("Category ID: ").strip()

    subject = input("Subject: ").strip()
    description = input("Description: ").strip()

    priority = ""
    while priority not in ("Low", "Medium", "High", "Critical"):
        priority = input("Priority (Low/Medium/High/Critical): ").strip().title()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute(
        """
        INSERT INTO tickets
            (user_id, category_id, subject, description, priority, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'Open', ?)
        """,
        (user_id, category_id, subject, description, priority, created_at),
    )
    conn.commit()
    print(f"\nTicket #{cursor.lastrowid} created successfully.")


def update_status(conn):
    """Change a ticket's status (e.g. Open -> In Progress)."""
    ticket_id = input("\nTicket ID to update: ").strip()
    new_status = ""
    while new_status not in ("Open", "In Progress", "Resolved", "Closed"):
        new_status = input("New status (Open/In Progress/Resolved/Closed): ").strip().title()

    conn.execute(
        "UPDATE tickets SET status = ? WHERE ticket_id = ?",
        (new_status, ticket_id),
    )
    conn.commit()
    print(f"Ticket #{ticket_id} status updated to '{new_status}'.")


def close_ticket(conn):
    """Close a ticket and record what fixed the issue.

    This resolution_notes field is what feeds the knowledge base --
    recurring fixes get written up as proper KB articles later.
    """
    ticket_id = input("\nTicket ID to close: ").strip()
    resolution_notes = input("Resolution notes (what fixed it): ").strip()
    resolved_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn.execute(
        """
        UPDATE tickets
        SET status = 'Closed', resolution_notes = ?, resolved_at = ?
        WHERE ticket_id = ?
        """,
        (resolution_notes, resolved_at, ticket_id),
    )
    conn.commit()
    print(f"Ticket #{ticket_id} closed.")


def search_by_category(conn):
    """List every ticket, closed or not, in a chosen category."""
    categories = conn.execute("SELECT category_id, category_name FROM categories").fetchall()
    for cid, cname in categories:
        print(f"  {cid}: {cname}")
    category_id = input("Category ID to search: ").strip()

    query = """
        SELECT t.ticket_id, t.subject, t.status, t.priority, t.created_at
        FROM tickets t
        WHERE t.category_id = ?
        ORDER BY t.created_at DESC
    """
    rows = conn.execute(query, (category_id,)).fetchall()

    if not rows:
        print("No tickets found in that category.")
        return

    print(f"\n{'ID':<5}{'Subject':<40}{'Status':<14}{'Priority':<10}{'Created'}")
    print("-" * 95)
    for ticket_id, subject, status, priority, created_at in rows:
        print(f"{ticket_id:<5}{subject:<40}{status:<14}{priority:<10}{created_at}")


def view_ticket_details(conn):
    """Show the full record for a single ticket, including resolution."""
    ticket_id = input("\nTicket ID to view: ").strip()

    query = """
        SELECT t.ticket_id, u.full_name, u.department, c.category_name,
               t.subject, t.description, t.priority, t.status,
               t.created_at, t.resolved_at, t.resolution_notes
        FROM tickets t
        JOIN users u ON t.user_id = u.user_id
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.ticket_id = ?
    """
    row = conn.execute(query, (ticket_id,)).fetchone()

    if not row:
        print("Ticket not found.")
        return

    (tid, name, dept, category, subject, description, priority,
     status, created_at, resolved_at, resolution_notes) = row

    print(f"\n--- Ticket #{tid} ---")
    print(f"Requester:   {name} ({dept})")
    print(f"Category:    {category}")
    print(f"Subject:     {subject}")
    print(f"Description: {description}")
    print(f"Priority:    {priority}")
    print(f"Status:      {status}")
    print(f"Created:     {created_at}")
    print(f"Resolved:    {resolved_at or '—'}")
    print(f"Resolution:  {resolution_notes or '—'}")


def main():
    conn = get_connection()

    actions = {
        "1": view_open_tickets,
        "2": create_ticket,
        "3": update_status,
        "4": close_ticket,
        "5": search_by_category,
        "6": view_ticket_details,
    }

    while True:
        print_menu()
        choice = input("Select an option: ").strip()

        if choice == "7":
            print("Goodbye.")
            break
        elif choice in actions:
            actions[choice](conn)
        else:
            print("Invalid option, try again.")

    conn.close()


if __name__ == "__main__":
    main()
