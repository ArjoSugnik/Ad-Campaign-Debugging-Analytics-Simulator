"""
=============================================================
  database.py - Database Setup & Connection
=============================================================
  This file handles everything related to our SQLite database.
  
  SQLite is like a simple spreadsheet saved as a file.
  No need to install a separate database server - it just works!
  
  Our database has ONE table: campaigns
"""

import sqlite3
import os

# Path where our database file will be saved
DB_PATH = os.path.join(os.path.dirname(__file__), "campaigns.db")


def get_db_connection():
    """
    Opens a connection to the database.
    
    Think of this like opening a spreadsheet file.
    row_factory makes rows return as dictionaries (key: value)
    instead of plain tuples - much easier to work with!
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Rows become dict-like objects
    return conn


def init_db():
    """
    Creates the database and tables if they don't exist yet.
    Safe to run multiple times - won't overwrite existing data.
    
    Our campaigns table stores:
    - id: auto-generated unique number
    - name: campaign name (text)
    - budget: total budget in dollars
    - impressions: how many people SAW the ad
    - clicks: how many people CLICKED the ad
    - conversions: how many people BOUGHT/SIGNED UP after clicking
    - ctr: Click Through Rate = clicks/impressions * 100
    - cpc: Cost Per Click = budget/clicks
    - conversion_rate: conversions/clicks * 100
    - created_at: when was this campaign added
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # CREATE TABLE IF NOT EXISTS means: only create if it doesn't already exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            budget          REAL NOT NULL,
            impressions     INTEGER NOT NULL,
            clicks          INTEGER NOT NULL,
            conversions     INTEGER NOT NULL,
            ctr             REAL,
            cpc             REAL,
            conversion_rate REAL,
            status          TEXT DEFAULT 'active',
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Performance log table - tracks history of changes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER NOT NULL,
            metric      TEXT NOT NULL,
            value       REAL NOT NULL,
            logged_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
        )
    """)

    conn.commit()  # Save changes
    conn.close()   # Close connection (good practice!)
    print(f"📂 Database ready at: {DB_PATH}")
