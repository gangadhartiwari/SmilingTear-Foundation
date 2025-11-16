import sqlite3

DB_NAME = "smilingtears.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # Volunteer Applications table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS volunteer_applications (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        phone TEXT,
        city TEXT,
        interests TEXT,
        message TEXT,
        timestamp TEXT,
        status TEXT
    )
    """)

    # Donations table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donation_id TEXT,
        transaction_id TEXT,
        amount REAL,
        program TEXT,
        donor_name TEXT,
        donor_email TEXT,
        donor_phone TEXT,
        is_anonymous INTEGER,
        timestamp TEXT,
        status TEXT
    )
    """)

    # Contact Submissions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS contact_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        message TEXT,
        timestamp TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()
