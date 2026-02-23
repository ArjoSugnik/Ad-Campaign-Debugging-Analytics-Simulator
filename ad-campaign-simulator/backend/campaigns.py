"""
=============================================================
  campaigns.py - Campaign Data Logic
=============================================================
  This file handles creating, reading, and deleting campaigns.
  
  CRUD = Create, Read, Update, Delete
  These are the 4 basic operations for any database app.
  
  KEY CONCEPT: Auto-calculating metrics
  When a user enters: budget, impressions, clicks, conversions
  We automatically calculate: CTR, CPC, Conversion Rate
"""

from database import get_db_connection


def calculate_metrics(budget, impressions, clicks, conversions):
    """
    Calculates the 3 key advertising metrics automatically.
    
    CTR (Click Through Rate):
      - What % of people who SAW the ad actually CLICKED it?
      - Formula: (clicks / impressions) * 100
      - Good CTR: above 2% for most ads
      
    CPC (Cost Per Click):
      - How much does each click COST us?
      - Formula: budget / clicks
      - Lower CPC = more efficient spending
      
    Conversion Rate:
      - What % of people who CLICKED actually CONVERTED (bought/signed up)?
      - Formula: (conversions / clicks) * 100
      - Good conversion rate: 2-5% is average
    """
    # Avoid division by zero errors
    ctr = round((clicks / impressions * 100), 2) if impressions > 0 else 0
    cpc = round((budget / clicks), 2) if clicks > 0 else 0
    conversion_rate = round((conversions / clicks * 100), 2) if clicks > 0 else 0

    return ctr, cpc, conversion_rate


def create_campaign(data):
    """
    Saves a new campaign to the database.
    
    Steps:
    1. Extract values from the request data
    2. Calculate metrics
    3. Insert into database
    4. Return the saved campaign
    """
    # Extract values (use .get() with defaults to prevent crashes)
    name = data.get("name", "Unnamed Campaign")
    budget = float(data.get("budget", 0))
    impressions = int(data.get("impressions", 0))
    clicks = int(data.get("clicks", 0))
    conversions = int(data.get("conversions", 0))

    # Auto-calculate the 3 metrics
    ctr, cpc, conversion_rate = calculate_metrics(budget, impressions, clicks, conversions)

    # Save to database
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO campaigns (name, budget, impressions, clicks, conversions, ctr, cpc, conversion_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, budget, impressions, clicks, conversions, ctr, cpc, conversion_rate))

    conn.commit()

    # Get the ID that was just auto-generated
    new_id = cursor.lastrowid
    conn.close()

    # Return the complete campaign object
    return get_campaign_by_id(new_id)


def get_all_campaigns():
    """
    Fetches ALL campaigns from the database.
    Returns a list of dictionaries.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM campaigns ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to plain Python dictionaries
    return [dict(row) for row in rows]


def get_campaign_by_id(campaign_id):
    """
    Fetches ONE specific campaign by its ID.
    Returns None if not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def delete_campaign(campaign_id):
    """
    Deletes a campaign from the database.
    Returns True if deleted, False if not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # First check if it exists
    cursor.execute("SELECT id FROM campaigns WHERE id = ?", (campaign_id,))
    if not cursor.fetchone():
        conn.close()
        return False

    # Delete it
    cursor.execute("DELETE FROM campaigns WHERE id = ?", (campaign_id,))
    # Also delete its performance logs
    cursor.execute("DELETE FROM performance_logs WHERE campaign_id = ?", (campaign_id,))
    conn.commit()
    conn.close()
    return True
