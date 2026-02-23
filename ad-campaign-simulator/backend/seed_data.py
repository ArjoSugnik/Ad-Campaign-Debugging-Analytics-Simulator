"""
=============================================================
  seed_data.py - Example Test Data
=============================================================
  This file loads example campaigns into the database.
  Great for testing and demonstrations!
  
  Each campaign demonstrates a different type of issue:
  - Campaign 1: Healthy campaign (no issues)
  - Campaign 2: Low CTR problem
  - Campaign 3: High CPC issue
  - Campaign 4: Tracking failure simulation
  - Campaign 5: Budget exhaustion
  - Campaign 6: Multiple critical issues
"""

from campaigns import create_campaign


def seed_example_campaigns():
    """Creates 6 example campaigns covering different scenarios."""

    example_campaigns = [
        # ---- HEALTHY CAMPAIGN ----
        {
            "name": "Spring Sale - Google Search (Healthy)",
            "budget": 5000.00,
            "impressions": 150000,
            "clicks": 4500,    # CTR = 3.0% (good!)
            "conversions": 180, # Conv rate = 4.0% (good!)
            # CPC = 5000/4500 = $1.11 (great!)
        },

        # ---- LOW CTR CAMPAIGN ----
        {
            "name": "Brand Awareness - Display Network (Low CTR)",
            "budget": 3000.00,
            "impressions": 500000,
            "clicks": 1000,    # CTR = 0.2% (very bad! below 0.5%)
            "conversions": 25,
            # This triggers LOW_CTR_CRITICAL
        },

        # ---- HIGH CPC CAMPAIGN ----
        {
            "name": "Competitor Keywords - Search (High CPC)",
            "budget": 8000.00,
            "impressions": 20000,
            "clicks": 600,     # CTR = 3.0% (good)
            "conversions": 18,
            # CPC = 8000/600 = $13.33 (very expensive!)
            # This triggers HIGH_CPC_CRITICAL
        },

        # ---- TRACKING FAILURE ----
        {
            "name": "Black Friday - Retargeting (Tracking Issue)",
            "budget": 4500.00,
            "impressions": 80000,
            "clicks": 2400,    # CTR = 3.0% (good)
            "conversions": 0,  # 0 conversions with 2400 clicks = suspicious!
            # This triggers TRACKING_FAILURE
        },

        # ---- BUDGET EXHAUSTED ----
        {
            "name": "Holiday Rush - Facebook (Budget Exhausted)",
            "budget": 1000.00,
            "impressions": 45000,
            "clicks": 990,     # CPC = $1000/990 = ~$1.01
            # Budget spent = $1.01 * 990 = ~$1000 (almost all gone!)
            "conversions": 30,
        },

        # ---- MULTIPLE CRITICAL ISSUES ----
        {
            "name": "New Product Launch - Broken Campaign",
            "budget": 2000.00,
            "impressions": 900000,  # Huge impressions
            "clicks": 900,          # CTR = 0.1% (terrible!)
            "conversions": 0,       # 0 conversions (tracking failure + low CTR)
            # CPC = 2000/900 = $2.22 (not terrible but everything else is)
        },
    ]

    count = 0
    for campaign_data in example_campaigns:
        create_campaign(campaign_data)
        count += 1
        print(f"  ✅ Created: {campaign_data['name']}")

    print(f"\n🌱 Seeded {count} example campaigns!")
    return count


if __name__ == "__main__":
    seed_example_campaigns()
