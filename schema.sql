-- ============================================================
-- IT Help Desk Ticketing System - Database Schema
-- ============================================================
-- This defines three tables:
--   1. users     -> the employees who submit tickets
--   2. categories -> the type of IT issue (Hardware, Network, etc.)
--   3. tickets    -> the actual help desk tickets, linked to the
--                    above two tables by foreign keys
-- ============================================================

-- Table of end users who can submit tickets
CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name   TEXT NOT NULL,
    department  TEXT NOT NULL,
    email       TEXT NOT NULL
);

-- Table of ticket categories, used to group and report on issue types
CREATE TABLE IF NOT EXISTS categories (
    category_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE
);

-- Main tickets table
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    category_id     INTEGER NOT NULL,
    subject         TEXT NOT NULL,
    description     TEXT,
    priority        TEXT NOT NULL CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),
    status          TEXT NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Resolved', 'Closed')),
    created_at      TEXT NOT NULL,      -- ISO date the ticket was opened
    resolved_at     TEXT,               -- ISO date the ticket was resolved (NULL if still open)
    resolution_notes TEXT,              -- what fixed the issue (feeds the knowledge base)
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
);
