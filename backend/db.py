"""
Lifedrop - SQLite Database Manager & Schema Initialization
"""

import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lifedrop.db')

def get_db_connection():
    """Create and return a database connection with dictionary-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initialize database tables and default seed data if not existing."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Donors Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donors (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            city TEXT NOT NULL,
            area TEXT,
            phone TEXT NOT NULL,
            email TEXT,
            age INTEGER,
            weight REAL,
            available BOOLEAN DEFAULT 1,
            verified BOOLEAN DEFAULT 1,
            total_donations INTEGER DEFAULT 0,
            last_donation TEXT,
            is_emergency_contact BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Requests Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id TEXT PRIMARY KEY,
            patient_name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            units INTEGER DEFAULT 1,
            hospital TEXT NOT NULL,
            city TEXT NOT NULL,
            urgency TEXT DEFAULT 'Standard',
            contact_name TEXT NOT NULL,
            contact_phone TEXT NOT NULL,
            notes TEXT,
            status TEXT DEFAULT 'Searching',
            donors_contacted INTEGER DEFAULT 0,
            donors_confirmed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Request Timeline Events Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS request_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT NOT NULL,
            time TEXT NOT NULL,
            event TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (request_id) REFERENCES requests (id) ON DELETE CASCADE
        )
    ''')

    # 4. Inventory Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            blood_group TEXT PRIMARY KEY,
            units_available INTEGER DEFAULT 0,
            daily_demand INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Stable',
            capacity_pct INTEGER DEFAULT 50,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 5. Broadcast Notifications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS broadcast_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT NOT NULL,
            donor_id TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'Sent',
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (request_id) REFERENCES requests (id) ON DELETE CASCADE,
            FOREIGN KEY (donor_id) REFERENCES donors (id) ON DELETE CASCADE
        )
    ''')

    # 6. Chat Logs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            intent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Seed Default Blood Inventory for Shivamogga Blood Banks
    cursor.execute('SELECT COUNT(*) FROM inventory')
    if cursor.fetchone()[0] == 0:
        default_inventory = [
            ('O+', 86, 28, 'Stable', 75),
            ('O-', 12, 22, 'Critical', 20),
            ('A+', 64, 18, 'Stable', 68),
            ('A-', 14, 11, 'Low', 35),
            ('B+', 78, 24, 'Stable', 80),
            ('B-', 9, 8, 'Critical', 18),
            ('AB+', 38, 9, 'Stable', 65),
            ('AB-', 5, 6, 'Critical', 15),
        ]
        cursor.executemany('''
            INSERT INTO inventory (blood_group, units_available, daily_demand, status, capacity_pct)
            VALUES (?, ?, ?, ?, ?)
        ''', default_inventory)

    # Seed Default Verified Donors in Shivamogga
    cursor.execute('SELECT COUNT(*) FROM donors')
    if cursor.fetchone()[0] == 0:
        default_donors = [
            ('DON-101', 'Prajwal Gowda', 'O+', 'Shivamogga', 'Durgigudi', '+91 98450 11223', 'prajwal.g@example.com', 26, 68.0, 1, 1, 4, '2026-06-12', 1),
            ('DON-102', 'Sahana Hegde', 'O-', 'Shivamogga', 'Gopala', '+91 98451 22334', 'sahana.h@example.com', 24, 55.0, 1, 1, 6, '2026-05-18', 1),
            ('DON-103', 'Manjunath Rao', 'A+', 'Shivamogga', 'Vinoba Nagara', '+91 98452 33445', 'manju.r@example.com', 32, 74.0, 1, 1, 3, '2026-07-01', 1),
            ('DON-104', 'Ananya Shenoy', 'B+', 'Shivamogga', 'Vidyanagara', '+91 98453 44556', 'ananya.s@example.com', 25, 54.0, 1, 1, 2, '2026-06-25', 1),
            ('DON-105', 'Darshan Kumar', 'AB+', 'Shivamogga', 'Tilak Nagara', '+91 98454 55667', 'darshan.k@example.com', 29, 76.0, 1, 1, 5, '2026-04-10', 1),
            ('DON-106', 'Megha Kulkarni', 'A-', 'Shivamogga', 'Gandhi Nagara', '+91 98455 66778', 'megha.k@example.com', 28, 59.0, 1, 1, 3, '2026-05-30', 1),
            ('DON-107', 'Chethan Acharya', 'B-', 'Shivamogga', 'Kuvempu Road', '+91 98456 77889', 'chethan.a@example.com', 27, 63.0, 1, 1, 4, '2026-06-05', 1),
            ('DON-108', 'Rakshith Shetty', 'AB-', 'Shivamogga', 'Sagara Road / Alkola', '+91 98457 88990', 'rakshith.s@example.com', 31, 71.0, 1, 1, 2, '2026-07-15', 1),
            ('DON-109', 'Naveen Kumar', 'O+', 'Shivamogga', 'Bhadravathi', '+91 98458 99001', 'naveen.b@example.com', 30, 70.0, 1, 1, 5, '2026-06-10', 1),
            ('DON-110', 'Deepa Bhat', 'O-', 'Shivamogga', 'Sagara', '+91 98459 00112', 'deepa.b@example.com', 27, 56.0, 1, 1, 3, '2026-05-20', 1),
        ]
        cursor.executemany('''
            INSERT INTO donors (id, name, blood_group, city, area, phone, email, age, weight, available, verified, total_donations, last_donation, is_emergency_contact)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', default_donors)

    # Seed Default Emergency Request in Shivamogga
    cursor.execute('SELECT COUNT(*) FROM requests')
    if cursor.fetchone()[0] == 0:
        default_requests = [
            ('REQ-1001', 'Sharadamma Patil', 'O-', 2, 'McGann Teaching Hospital & SIMS', 'Shivamogga', 'Emergency', 'Ramesh Patil', '+91 98450 11223', 'Emergency trauma care at McGann Hospital - urgent O- transfusion required', 'In Progress', 4, 1),
            ('REQ-1002', 'Venkatesh Murthy', 'B+', 1, 'Sahyadri Narayana Hospital', 'Shivamogga', 'Urgent', 'Suresh Murthy', '+91 98451 22334', 'Cardiac surgery blood requirement at Sahyadri Narayana Hospital', 'Searching', 3, 0),
            ('REQ-1003', 'Rashmi K', 'A+', 1, 'Nanjappa Hospital', 'Shivamogga', 'Emergency', 'Kiran Kumar', '+91 98452 33445', 'Maternity emergency at Nanjappa Hospital Tilak Nagar', 'Searching', 2, 0)
        ]
        cursor.executemany('''
            INSERT INTO requests (id, patient_name, blood_group, units, hospital, city, urgency, contact_name, contact_phone, notes, status, donors_contacted, donors_confirmed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', default_requests)

        # Timeline events
        timeline_events = [
            ('REQ-1001', '10:30 AM', 'Emergency blood request created for O- at McGann Teaching Hospital & SIMS, Shivamogga'),
            ('REQ-1001', '10:32 AM', 'Automated emergency alert dispatched to matching O- donors across Shivamogga & Gopala'),
            ('REQ-1001', '10:45 AM', 'Donor Sahana Hegde (DON-102) accepted request & en route to McGann Hospital'),
            ('REQ-1002', '11:15 AM', 'Urgent blood request created for B+ at Sahyadri Narayana Hospital, Harakere'),
            ('REQ-1002', '11:18 AM', 'Alert dispatched to registered donors in Vidyanagara & Kuvempu Road'),
            ('REQ-1003', '11:45 AM', 'Emergency request logged for A+ at Nanjappa Hospital, Tilak Nagara'),
        ]
        cursor.executemany('''
            INSERT INTO request_timeline (request_id, time, event)
            VALUES (?, ?, ?)
        ''', timeline_events)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print(f"Database initialized successfully at {DB_PATH}")
