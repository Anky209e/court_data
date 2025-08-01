from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from bs_hc_scrap import fetch_case_data, get_case_types_and_years
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-in-production")

# Fetch case types and years once at startup
CASE_TYPES, CASE_YEARS = get_case_types_and_years()

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS queries (
    id INTEGER PRIMARY KEY,
    case_type TEXT,
    case_number TEXT,
    case_year TEXT,
    case_type_status TEXT,
    parties TEXT,
    listing_date_court_no TEXT,
    pdf_links TEXT
)
"""

def ensure_table():
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute(DB_SCHEMA)
    conn.commit()
    conn.close()

def log_query(case_type, case_number, case_year, case_type_status, parties, listing_date_court_no, pdf_links):
    ensure_table()
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute("""
        INSERT INTO queries (
            case_type, case_number, case_year, case_type_status, parties, listing_date_court_no, pdf_links
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        case_type, case_number, case_year, case_type_status, parties, listing_date_court_no, pdf_links
    ))
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    has_data = False
    error = None
    not_found = None
    if request.method == "POST":
        case_type = request.form["case_type"]
        case_number = request.form["case_number"]
        case_year = request.form["case_year"]
        try:
            parsed, _ = fetch_case_data(case_type, case_number, case_year)
            # Only log if data is found (e.g., at least one field is non-empty or PDFs found)
            if parsed and (parsed.get("case_type_status") or parsed.get("parties") or parsed.get("listing_date_court_no") or parsed.get("latest_order_pdfs")):
                pdf_links = json.dumps(parsed.get("latest_order_pdfs", []))
                log_query(
                    case_type, case_number, case_year,
                    parsed.get("case_type_status", ""),
                    parsed.get("parties", ""),
                    parsed.get("listing_date_court_no", ""),
                    pdf_links
                )
                result = parsed
            else:
                not_found = {
                    "case_type": case_type,
                    "case_number": case_number,
                    "case_year": case_year
                }
        except Exception as e:
            error = f"Error: {str(e)}"
            flash(error, "danger")
    # Ensure table exists before SELECT
    ensure_table()
    try:
        conn = sqlite3.connect("db.sqlite3")
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM queries")
        has_data = c.fetchone()[0] > 0
        conn.close()
    except Exception as e:
        has_data = False
        flash(f"Database error: {str(e)}", "danger")
    return render_template(
        "index.html",
        case_types=CASE_TYPES,
        case_years=CASE_YEARS,
        result=result,
        has_data=has_data,
        not_found=not_found
    )

@app.route("/dashboard")
def dashboard():
    ensure_table()
    try:
        conn = sqlite3.connect("db.sqlite3")
        c = conn.cursor()
        c.execute("""
            SELECT id, case_type, case_number, case_year, case_type_status, parties, listing_date_court_no, pdf_links
            FROM queries ORDER BY id DESC
        """)
        rows = c.fetchall()
        conn.close()
    except Exception as e:
        rows = []
        flash(f"Database error: {str(e)}", "danger")
    return render_template("dashboard.html", queries=rows)

@app.route("/query/<int:query_id>")
def query_detail(query_id):
    ensure_table()
    try:
        conn = sqlite3.connect("db.sqlite3")
        c = conn.cursor()
        c.execute("""
            SELECT case_type, case_number, case_year, case_type_status, parties, listing_date_court_no, pdf_links
            FROM queries WHERE id=?
        """, (query_id,))
        row = c.fetchone()
        conn.close()
        if not row:
            flash("Query not found.", "danger")
            return redirect(url_for("dashboard"))
        pdf_links = json.loads(row[6] or "[]")
    except Exception as e:
        flash(f"Database error: {str(e)}", "danger")
        return redirect(url_for("dashboard"))
    return render_template("query_detail.html", query=row, pdf_links=pdf_links)

@app.template_filter('fromjson')
def fromjson_filter(s):
    import json
    return json.loads(s)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)