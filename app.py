from flask import Flask, render_template, request, redirect, session, send_file, url_for
import sqlite3
from datetime import datetime
from openpyxl import Workbook
import qrcode
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"
DATABASE = "attendance.db"

# ---------------------------------------------------------
# DATABASE INITIALIZATION
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        date TEXT)""")
    # Default Admin (Username: admin | Password: 1234)
    c.execute("DELETE FROM users WHERE username='admin'")
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
              ("admin", "1234", "admin"))
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect(DATABASE); c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone(); conn.close()
        if user:
            session["username"], session["role"] = username, user[0]
            return redirect("/admin-dashboard" if user[0] == "admin" else "/student-dashboard")
        return "Invalid Login"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------------------------------------------------
# ADMIN CONTROLS
# ---------------------------------------------------------
@app.route("/admin-dashboard")
def admin_dashboard():
    if session.get("role") != "admin": return redirect("/login")
    conn = sqlite3.connect(DATABASE); c = conn.cursor()
    c.execute("SELECT username, date FROM attendance")
    data = c.fetchall(); conn.close()
    return render_template("admin_dashboard.html", attendance=data)

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("role") != "admin": return redirect("/login")
    if request.method == "POST":
        un, pw = request.form["username"], request.form["password"]
        conn = sqlite3.connect(DATABASE); c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'student')", (un, pw))
            conn.commit()
        except: return "User exists"
        finally: conn.close()
        return redirect("/admin-dashboard")
    return render_template("register.html")

@app.route("/delete-student/<username>")
def delete_student(username):
    if session.get("role") != "admin": return redirect("/login")
    conn = sqlite3.connect(DATABASE); c = conn.cursor()
    c.execute("DELETE FROM users WHERE username=?", (username,))
    c.execute("DELETE FROM attendance WHERE username=?", (username,))
    conn.commit(); conn.close()
    return redirect("/admin-dashboard")

@app.route("/admin-mark", methods=["POST"])
def admin_mark():
    if session.get("role") != "admin": return redirect("/login")
    un, dt = request.form["username"], request.form["date"]
    conn = sqlite3.connect(DATABASE); c = conn.cursor()
    c.execute("INSERT INTO attendance (username, date) VALUES (?, ?)", (un, dt))
    conn.commit(); conn.close()
    return redirect("/admin-dashboard")

# ---------------------------------------------------------
# QR CODE FEATURE
# ---------------------------------------------------------
@app.route("/generate-qr/<class_name>")
def generate_qr(class_name):
    if session.get("role") != "admin": return redirect("/login")
    if not os.path.exists('static'): os.makedirs('static')
    # Use Local IP instead of 127.0.0.1 for mobile scanning
    qr_data = f"http://127.0.0.1:5000/qr-mark/{class_name}"
    img = qrcode.make(qr_data)
    img.save("static/qr_code.png")
    return render_template("qr_display.html", class_name=class_name)

@app.route("/qr-mark/<class_name>")
def qr_mark(class_name):
    if "username" not in session: return redirect("/login")
    un, today = session["username"], datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DATABASE); c = conn.cursor()
    c.execute("SELECT * FROM attendance WHERE username=? AND date=?", (un, today))
    if c.fetchone():
        conn.close(); return "Already marked today!"
    c.execute("INSERT INTO attendance (username, date) VALUES (?, ?)", (un, today))
    conn.commit(); conn.close()
    return f"Attendance for {class_name} Marked!"

# ---------------------------------------------------------
# STUDENT & EXPORT
# ---------------------------------------------------------
@app.route("/student-dashboard")
def student_dashboard():
    if session.get("role") != "student": return redirect("/login")
    return render_template("student_dashboard.html")

@app.route("/mark")
def mark():
    if "username" not in session: return redirect("/login")
    un, today = session["username"], datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DATABASE); c = conn.cursor()
    c.execute("SELECT * FROM attendance WHERE username=? AND date=?", (un, today))
    if c.fetchone():
        conn.close(); return "Already marked today!"
    c.execute("INSERT INTO attendance (username, date) VALUES (?, ?)", (un, today))
    conn.commit(); conn.close()
    return "Marked Successfully!"

@app.route("/export")
def export():
    if session.get("role") != "admin": return redirect("/login")
    conn = sqlite3.connect(DATABASE); c = conn.cursor()
    c.execute("SELECT username, date FROM attendance"); data = c.fetchall(); conn.close()
    wb = Workbook(); ws = wb.active; ws.append(["Student Name", "Date"])
    for row in data: ws.append(row)
    wb.save("attendance.xlsx")
    return send_file("attendance.xlsx", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
