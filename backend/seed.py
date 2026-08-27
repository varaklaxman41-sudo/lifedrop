"""
Lifedrop - Database Seeder Utility
Run this script to reset or populate sample donors, emergency requests, and inventory.
Usage: python backend/seed.py [--reset]
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.db import get_db_connection, init_db, DB_PATH

def reset_and_seed():
    print(f"Connecting to database at: {DB_PATH}")
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("Removed existing lifedrop.db for a clean seed.")
        except Exception as e:
            print(f"Note: Could not remove old DB file: {e}")

    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM donors')
    donors_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM requests')
    requests_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM inventory')
    inventory_count = cursor.fetchone()[0]

    conn.close()

    print("\n[+] Database Seeding Complete:")
    print(f"   - Verified Donors: {donors_count}")
    print(f"   - Active Requests: {requests_count}")
    print(f"   - Inventory Groups: {inventory_count}")

if __name__ == '__main__':
    reset_and_seed()
