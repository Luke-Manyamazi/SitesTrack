from flask import Flask, render_template, request, jsonify
import sqlite3

DB_PATH = "sitestrack.db"

app = Flask(__name__)


# ----------------------------
# INIT DATABASE (SAAS MODEL)
# ----------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Sites table (NEW)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT DEFAULT 'uncategorized',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Visits table (UPGRADED)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id INTEGER,
            ip_address TEXT,
            country TEXT,
            device TEXT,
            user_agent TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ----------------------------
# TRACK VISITS (UPGRADED)
# ----------------------------
@app.route("/track", methods=["POST"])
def track_visit():
    data = request.get_json()

    site = data.get("site")
    category = data.get("category", "uncategorized")

    if not site:
        return jsonify({"error": "site is required"}), 400

    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "").lower()

    # ----------------------------
    # DEVICE DETECTION
    # ----------------------------
    if "mobile" in user_agent:
        device = "Mobile"
    elif "tablet" in user_agent or "ipad" in user_agent:
        device = "Tablet"
    else:
        device = "Desktop"

    # ----------------------------
    # COUNTRY (PLACEHOLDER FOR NOW)
    # Later we plug in IP API
    # ----------------------------
    country = "Unknown"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure site exists
    cursor.execute("""
        INSERT OR IGNORE INTO sites (name, category)
        VALUES (?, ?)
    """, (site, category))

    # Get site ID
    cursor.execute("SELECT id FROM sites WHERE name = ?", (site,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return jsonify({"error": "site not found after insert"}), 500

    site_id = result[0]

    # Insert visit (FULL ANALYTICS DATA)
    cursor.execute("""
        INSERT INTO visits (site_id, ip_address, country, device, user_agent)
        VALUES (?, ?, ?, ?, ?)
    """, (site_id, ip, country, device, user_agent))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Visit recorded",
        "site": site,
        "category": category,
        "device": device,
        "country": country
    })


# ----------------------------
# DASHBOARD (ANALYTICS ENGINE)
# ----------------------------
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ----------------------------
    # SITE PERFORMANCE (BAR CHART)
    # ----------------------------
    cursor.execute("""
        SELECT s.name, s.category, COUNT(v.id) as visits
        FROM sites s
        LEFT JOIN visits v ON s.id = v.site_id
        GROUP BY s.id
        ORDER BY visits DESC
    """)
    stats = cursor.fetchall()

    # ----------------------------
    # TOTAL VISITS
    # ----------------------------
    cursor.execute("SELECT COUNT(*) FROM visits")
    total_visits = cursor.fetchone()[0]

    # ----------------------------
    # TODAY VISITS
    # ----------------------------
    cursor.execute("""
        SELECT COUNT(*) FROM visits
        WHERE DATE(timestamp) = DATE('now')
    """)
    today_visits = cursor.fetchone()[0]

    # ----------------------------
    # UNIQUE SITES
    # ----------------------------
    cursor.execute("SELECT COUNT(*) FROM sites")
    unique_sites = cursor.fetchone()[0]

    # ----------------------------
    # TOP SITE
    # ----------------------------
    cursor.execute("""
        SELECT s.name, COUNT(v.id) as c
        FROM sites s
        LEFT JOIN visits v ON s.id = v.site_id
        GROUP BY s.id
        ORDER BY c DESC
        LIMIT 1
    """)
    top_site = cursor.fetchone()

    top_site_name = top_site[0] if top_site else "None"
    top_site_visits = top_site[1] if top_site else 0

    # ----------------------------
    # AVERAGE VISITS
    # ----------------------------
    avg_visits = (total_visits / unique_sites) if unique_sites else 0

    # =========================================================
    # 📊 NEW ANALYTICS ADDITIONS
    # =========================================================

    # ----------------------------
    # DEVICE ANALYTICS (PIE CHART)
    # ----------------------------
    cursor.execute("""
        SELECT device, COUNT(*)
        FROM visits
        GROUP BY device
    """)
    device_stats = cursor.fetchall()

    # ----------------------------
    # COUNTRY ANALYTICS (PIE CHART)
    # ----------------------------
    cursor.execute("""
        SELECT country, COUNT(*)
        FROM visits
        GROUP BY country
    """)
    country_stats = cursor.fetchall()

    # ----------------------------
    # HOURLY TRAFFIC (LINE CHART)
    # ----------------------------
    cursor.execute("""
        SELECT strftime('%H', timestamp) as hour, COUNT(*)
        FROM visits
        GROUP BY hour
        ORDER BY hour
    """)
    hourly_stats = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",

        # existing
        stats=stats,
        total_visits=total_visits,
        today_visits=today_visits,
        unique_sites=unique_sites,
        top_site_name=top_site_name,
        top_site_visits=top_site_visits,
        avg_visits=avg_visits,

        # new analytics
        device_stats=device_stats,
        country_stats=country_stats,
        hourly_stats=hourly_stats
    )


# ----------------------------
# HOME
# ----------------------------
@app.route("/")
def home():
    return "SitesTrack Analytics Running"


# ----------------------------
# START APP
# ----------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)