"""
=============================================================
  diagnostics.py - The Diagnostic Engine (Core Feature!)
=============================================================
  This is the BRAIN of the entire project.
  
  It analyzes campaign metrics and automatically detects problems.
  
  HOW IT WORKS (Rule-Based System):
  1. We define RULES (thresholds for what's "bad")
  2. We check each metric against those rules
  3. If a metric crosses the bad threshold → issue detected
  4. Each issue has pre-written ROOT CAUSES and RECOMMENDATIONS
  
  Think of it like a doctor's checklist:
  - Blood pressure too high? → check for heart disease
  - Sugar too high? → check for diabetes
  Here: CTR too low? → check creative or targeting
  
  HEALTH SCORE:
  - Starts at 100
  - Each issue deducts points based on severity
  - Final score = overall campaign health (0-100)
"""

# -------------------------------------------------------
# THRESHOLDS (The Rules)
# These numbers define what is "bad" for each metric
# In real advertising, these vary by industry - these are averages
# -------------------------------------------------------
THRESHOLDS = {
    "ctr": {
        "critical": 0.5,    # Below 0.5% = very bad
        "warning": 1.0,     # Below 1.0% = concerning
        "good": 2.0,        # Above 2.0% = healthy
    },
    "cpc": {
        "warning": 5.0,     # Above $5/click = expensive
        "critical": 10.0,   # Above $10/click = very expensive
    },
    "conversion_rate": {
        "critical": 1.0,    # Below 1% = very bad
        "warning": 2.0,     # Below 2% = concerning
        "good": 5.0,        # Above 5% = excellent
    },
    "budget_remaining_pct": {
        "exhausted": 5.0,   # Less than 5% budget left
        "low": 20.0,        # Less than 20% budget left
    },
    "drop_threshold": 30,   # 30% drop = sudden performance drop
}

# -------------------------------------------------------
# ISSUE DEFINITIONS
# Each issue has:
# - type: machine-readable identifier
# - severity: critical / warning / info
# - title: human-readable name
# - description: what's happening
# - root_causes: WHY this might be happening
# - recommendations: WHAT TO DO about it
# -------------------------------------------------------
ISSUE_DEFINITIONS = {
    "LOW_CTR_CRITICAL": {
        "type": "LOW_CTR_CRITICAL",
        "severity": "critical",
        "title": "🔴 Critically Low Click-Through Rate",
        "description": "Your CTR is below 0.5%. This means almost nobody who sees your ad clicks on it.",
        "root_causes": [
            "Ad creative is not engaging or relevant to the audience",
            "Ad copy headline is weak or not attention-grabbing",
            "Wrong audience targeting - showing ads to wrong people",
            "Ad fatigue - same people seeing your ad too many times",
            "Poor ad placement or format mismatch",
            "Competitor ads are more attractive",
        ],
        "recommendations": [
            "A/B test new ad creatives with different images and headlines",
            "Review and refine your audience targeting parameters",
            "Add a stronger call-to-action (CTA) like 'Get 50% Off Today'",
            "Refresh ad creative every 2-3 weeks to fight ad fatigue",
            "Check if ad format matches placement (e.g., square for Instagram)",
            "Research competitor ads for inspiration (use Facebook Ad Library)",
        ],
        "score_deduction": 25,
    },
    "LOW_CTR_WARNING": {
        "type": "LOW_CTR_WARNING",
        "severity": "warning",
        "title": "🟡 Low Click-Through Rate",
        "description": "Your CTR is below 1.0%. There's room for improvement.",
        "root_causes": [
            "Ad creative could be more compelling",
            "Targeting might be slightly off",
            "Value proposition not clear enough",
        ],
        "recommendations": [
            "Test new headlines emphasizing benefits, not features",
            "Add social proof (e.g., '10,000 customers love us')",
            "Try different ad formats (carousel, video, static)",
        ],
        "score_deduction": 10,
    },
    "HIGH_CPC_CRITICAL": {
        "type": "HIGH_CPC_CRITICAL",
        "severity": "critical",
        "title": "🔴 Critically High Cost Per Click",
        "description": "Each click is costing more than $10. Your budget is burning fast.",
        "root_causes": [
            "High competition for the keywords/audience you're targeting",
            "Low Quality Score (Google) or Relevance Score (Facebook) - ads deemed irrelevant",
            "Bidding strategy too aggressive",
            "Targeting too narrow, inflating competition",
            "Ad extensions not being used (reduces Quality Score)",
        ],
        "recommendations": [
            "Improve ad Quality Score by aligning ad → keyword → landing page",
            "Test manual bidding vs. automated bidding strategies",
            "Expand audience targeting to reduce competition pressure",
            "Add negative keywords to filter irrelevant clicks",
            "Try long-tail keywords which typically have lower CPC",
            "Improve landing page relevance and load speed",
        ],
        "score_deduction": 20,
    },
    "HIGH_CPC_WARNING": {
        "type": "HIGH_CPC_WARNING",
        "severity": "warning",
        "title": "🟡 High Cost Per Click",
        "description": "CPC is above $5. Monitor to prevent budget waste.",
        "root_causes": [
            "Moderate competition in your targeting",
            "Quality Score could be improved",
        ],
        "recommendations": [
            "Review keyword bids and adjust down for low-converting ones",
            "Test enhanced CPC or target CPA bidding",
        ],
        "score_deduction": 8,
    },
    "LOW_CONVERSION_CRITICAL": {
        "type": "LOW_CONVERSION_CRITICAL",
        "severity": "critical",
        "title": "🔴 Critically Low Conversion Rate",
        "description": "Less than 1% of clicks convert. People click but don't complete the desired action.",
        "root_causes": [
            "Landing page doesn't match the ad's promise (message mismatch)",
            "Landing page loads slowly (each second of delay drops conversions ~7%)",
            "Checkout/signup process is too long or complicated",
            "Lack of trust signals (no reviews, no security badges)",
            "Mobile experience is poor (landing page not mobile-optimized)",
            "Wrong audience - clicks from people with no purchase intent",
            "Conversion tracking pixel/tag is broken (tracking failure)",
        ],
        "recommendations": [
            "Ensure landing page headline matches the ad copy exactly",
            "Test landing page load speed at PageSpeed Insights",
            "Simplify the conversion form - remove unnecessary fields",
            "Add trust signals: reviews, testimonials, security badges, guarantees",
            "Test mobile responsiveness on multiple devices",
            "Set up heatmaps (Hotjar/Microsoft Clarity) to see where users drop off",
            "Check that conversion tracking pixel fires correctly",
        ],
        "score_deduction": 25,
    },
    "LOW_CONVERSION_WARNING": {
        "type": "LOW_CONVERSION_WARNING",
        "severity": "warning",
        "title": "🟡 Below-Average Conversion Rate",
        "description": "Conversion rate is below 2%. Improving this would significantly boost ROI.",
        "root_causes": [
            "Landing page experience needs improvement",
            "Offer could be more compelling",
        ],
        "recommendations": [
            "Test different landing page layouts and CTAs",
            "Offer a stronger incentive (discount, free trial, guarantee)",
            "Add an exit-intent popup to capture hesitant visitors",
        ],
        "score_deduction": 10,
    },
    "TRACKING_FAILURE": {
        "type": "TRACKING_FAILURE",
        "severity": "critical",
        "title": "🔴 Possible Tracking Failure",
        "description": "Zero conversions with significant clicks is unusual. Your conversion tracking may be broken.",
        "root_causes": [
            "Conversion pixel/tag not installed on the Thank You page",
            "Tag Manager container not published after adding new tag",
            "Conversion event fires on wrong page",
            "Script blocked by browser ad blockers",
            "iOS 14+ privacy changes blocking conversion tracking",
            "Page redirect breaking the pixel fire",
        ],
        "recommendations": [
            "Use Google Tag Assistant or Facebook Pixel Helper browser extension to verify",
            "Check Tag Manager and ensure container is published",
            "Test conversion flow manually and watch for pixel fire in browser console",
            "Consider server-side tracking to bypass ad blockers",
            "Implement Meta CAPI or Google Enhanced Conversions for better tracking",
            "Review pixel placement - it must fire AFTER the conversion happens",
        ],
        "score_deduction": 30,
    },
    "BUDGET_EXHAUSTED": {
        "type": "BUDGET_EXHAUSTED",
        "severity": "critical",
        "title": "🔴 Budget Nearly Exhausted",
        "description": "Less than 5% of budget remaining. Ads may stop running soon.",
        "root_causes": [
            "Campaign budget set too low for the target audience size",
            "High CPC consuming budget faster than expected",
            "Campaign running too many ad sets or audiences simultaneously",
            "No daily budget cap set (monthly budget spent too quickly)",
        ],
        "recommendations": [
            "Increase budget or pause underperforming ad sets",
            "Set daily budget limits to pace spending evenly",
            "Pause campaigns with poor ROAS until budget is replenished",
            "Reduce audience size to make budget go further",
        ],
        "score_deduction": 15,
    },
    "BUDGET_LOW": {
        "type": "BUDGET_LOW",
        "severity": "warning",
        "title": "🟡 Budget Running Low",
        "description": "Less than 20% of budget remaining. Plan to replenish soon.",
        "root_causes": [
            "Budget pacing is ahead of schedule",
            "Higher than expected click volume",
        ],
        "recommendations": [
            "Review budget pacing in campaign settings",
            "Consider increasing budget if performance is good",
        ],
        "score_deduction": 5,
    },
}


def run_diagnostics(campaign):
    """
    MAIN FUNCTION: Analyzes a campaign and returns all detected issues.
    
    This is the diagnostic engine. Think of it as running a health check.
    
    Returns a dictionary with:
    - health_score: 0-100 overall campaign health
    - issues: list of detected problems
    - recommendations: combined list of all recommendations
    - summary: one-line status message
    """
    issues = []
    score = 100  # Start perfect, deduct for issues

    ctr = campaign.get("ctr", 0) or 0
    cpc = campaign.get("cpc", 0) or 0
    conversion_rate = campaign.get("conversion_rate", 0) or 0
    budget = campaign.get("budget", 0) or 0
    clicks = campaign.get("clicks", 0) or 0
    conversions = campaign.get("conversions", 0) or 0

    # Estimate "budget spent" as CPC * clicks
    budget_spent = cpc * clicks
    budget_remaining_pct = ((budget - budget_spent) / budget * 100) if budget > 0 else 100

    # -------------------------------------------------------
    # RULE 1: Check CTR
    # -------------------------------------------------------
    if ctr < THRESHOLDS["ctr"]["critical"]:
        issue = ISSUE_DEFINITIONS["LOW_CTR_CRITICAL"].copy()
        issue["metric_value"] = ctr
        issue["threshold"] = THRESHOLDS["ctr"]["critical"]
        issues.append(issue)
        score -= issue["score_deduction"]

    elif ctr < THRESHOLDS["ctr"]["warning"]:
        issue = ISSUE_DEFINITIONS["LOW_CTR_WARNING"].copy()
        issue["metric_value"] = ctr
        issue["threshold"] = THRESHOLDS["ctr"]["warning"]
        issues.append(issue)
        score -= issue["score_deduction"]

    # -------------------------------------------------------
    # RULE 2: Check CPC
    # -------------------------------------------------------
    if cpc > THRESHOLDS["cpc"]["critical"]:
        issue = ISSUE_DEFINITIONS["HIGH_CPC_CRITICAL"].copy()
        issue["metric_value"] = cpc
        issue["threshold"] = THRESHOLDS["cpc"]["critical"]
        issues.append(issue)
        score -= issue["score_deduction"]

    elif cpc > THRESHOLDS["cpc"]["warning"]:
        issue = ISSUE_DEFINITIONS["HIGH_CPC_WARNING"].copy()
        issue["metric_value"] = cpc
        issue["threshold"] = THRESHOLDS["cpc"]["warning"]
        issues.append(issue)
        score -= issue["score_deduction"]

    # -------------------------------------------------------
    # RULE 3: Check Conversion Rate
    # -------------------------------------------------------
    if conversion_rate < THRESHOLDS["conversion_rate"]["critical"] and clicks > 50:
        issue = ISSUE_DEFINITIONS["LOW_CONVERSION_CRITICAL"].copy()
        issue["metric_value"] = conversion_rate
        issue["threshold"] = THRESHOLDS["conversion_rate"]["critical"]
        issues.append(issue)
        score -= issue["score_deduction"]

    elif conversion_rate < THRESHOLDS["conversion_rate"]["warning"] and clicks > 20:
        issue = ISSUE_DEFINITIONS["LOW_CONVERSION_WARNING"].copy()
        issue["metric_value"] = conversion_rate
        issue["threshold"] = THRESHOLDS["conversion_rate"]["warning"]
        issues.append(issue)
        score -= issue["score_deduction"]

    # -------------------------------------------------------
    # RULE 4: Tracking Failure Detection
    # Logic: if there are many clicks but ZERO conversions, something's wrong
    # -------------------------------------------------------
    if clicks > 100 and conversions == 0:
        issue = ISSUE_DEFINITIONS["TRACKING_FAILURE"].copy()
        issue["metric_value"] = 0
        issue["threshold"] = 1
        issues.append(issue)
        score -= issue["score_deduction"]

    # -------------------------------------------------------
    # RULE 5: Budget Exhaustion
    # -------------------------------------------------------
    if budget_remaining_pct < THRESHOLDS["budget_remaining_pct"]["exhausted"]:
        issue = ISSUE_DEFINITIONS["BUDGET_EXHAUSTED"].copy()
        issue["metric_value"] = budget_remaining_pct
        issue["threshold"] = THRESHOLDS["budget_remaining_pct"]["exhausted"]
        issues.append(issue)
        score -= issue["score_deduction"]

    elif budget_remaining_pct < THRESHOLDS["budget_remaining_pct"]["low"]:
        issue = ISSUE_DEFINITIONS["BUDGET_LOW"].copy()
        issue["metric_value"] = budget_remaining_pct
        issue["threshold"] = THRESHOLDS["budget_remaining_pct"]["low"]
        issues.append(issue)
        score -= issue["score_deduction"]

    # Clamp score between 0 and 100
    health_score = max(0, min(100, score))

    # Generate a summary label
    if health_score >= 80:
        summary = "✅ Campaign is performing well"
        status = "healthy"
    elif health_score >= 50:
        summary = "⚠️ Campaign has some issues that need attention"
        status = "warning"
    else:
        summary = "🚨 Campaign has critical issues requiring immediate action"
        status = "critical"

    # Collect all unique recommendations
    all_recommendations = []
    for issue in issues:
        for rec in issue.get("recommendations", []):
            if rec not in all_recommendations:
                all_recommendations.append(rec)

    return {
        "campaign_id": campaign.get("id"),
        "campaign_name": campaign.get("name"),
        "health_score": health_score,
        "status": status,
        "summary": summary,
        "issues": issues,
        "recommendations": all_recommendations,
        "metrics_analyzed": {
            "ctr": ctr,
            "cpc": cpc,
            "conversion_rate": conversion_rate,
            "budget_remaining_pct": round(budget_remaining_pct, 1),
        }
    }
