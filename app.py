from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("sitestrack.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

@app.route("/track", methods=["POST"])
def track_visit():
    data = request.json
    site = data.get("site")

    conn = sqlite3.connect("sitestrack.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO visits (site) VALUES (?)", (site,))
    conn.commit()
    conn.close()

    return {"message": "Visit recorded"}

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("sitestrack.db")
    cursor = conn.cursor()

    # Visits per site
    cursor.execute("""
        SELECT site, COUNT(*) as visits
        FROM visits
        GROUP BY site
    """)
    stats = cursor.fetchall()

    # Total visits
    cursor.execute("SELECT COUNT(*) FROM visits")
    total_visits = cursor.fetchone()[0]

    # Today's visits
    cursor.execute("""
        SELECT COUNT(*) FROM visits
        WHERE DATE(timestamp) = DATE('now')
    """)
    today_visits = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        stats=stats,
        total_visits=total_visits,
        today_visits=today_visits
    )

@app.route("/")
def home():
    return "SitesTrack is running"

if __name__ == "__main__":
    init_db()
    app.run(debug=True)