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
        except: return "User already exists"
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
    # Change '127.0.0.1' to your Cloud URL when deploying
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
    return f"Attendance for {class_name} Marked Successfully via QR!"

# ---------------------------------------------------------
# STUDENT & EXCEL EXPORT
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

[span_33](start_span)@app.route("/logout") #[span_33](end_span)
def logout():
    [span_34](start_span)session.clear() #[span_34](end_span)
    [span_35](start_span)return redirect("/login") #[span_35](end_span)

# ---------------------------------------------------------
# 3. ADMIN CONTROLS (DASHBOARD, REGISTER, DELETE, MANUAL MARK)
# ---------------------------------------------------------
[span_36](start_span)@app.route("/admin-dashboard") #[span_36](end_span)
def admin_dashboard():
    [span_37](start_span)if session.get("role") != "admin": #[span_37](end_span)
        return redirect("/login")
    [span_38](start_span)conn = sqlite3.connect(DATABASE); c = conn.cursor() #[span_38](end_span)
    [span_39](start_span)c.execute("SELECT username, date FROM attendance") #[span_39](end_span)
    [span_40](start_span)data = c.fetchall(); conn.close() #[span_40](end_span)
    [span_41](start_span)return render_template("admin_dashboard.html", attendance=data) #[span_41](end_span)

[span_42](start_span)@app.route("/register", methods=["GET", "POST"]) #[span_42](end_span)
def register():
    [span_43](start_span)if session.get("role") != "admin": #[span_43](end_span)
        return redirect("/login")
    [span_44](start_span)if request.method == "POST": #[span_44](end_span)
        [span_45](start_span)username, password = request.form["username"], request.form["password"] #[span_45](end_span)
        [span_46](start_span)conn = sqlite3.connect(DATABASE); c = conn.cursor() #[span_46](end_span)
        try:
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                      (username, password, "student")[span_47](start_span)) #[span_47](end_span)
            conn.commit()
        [span_48](start_span)except: return "Username exists" #[span_48](end_span)
        [span_49](start_span)finally: conn.close() #[span_49](end_span)
        [span_50](start_span)return redirect("/admin-dashboard") #[span_50](end_span)
    [span_51](start_span)return render_template("register.html") #[span_51](end_span)

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
    username, date = request.form["username"], request.form["date"]
    conn = sqlite3.connect(DATABASE); c = conn.cursor()
    c.execute("INSERT INTO attendance (username, date) VALUES (?, ?)", (username, date))
    conn.commit(); conn.close()
    return redirect("/admin-dashboard")

# ---------------------------------------------------------
# 4. QR CODE FEATURE
# ---------------------------------------------------------
@app.route("/generate-qr/<class_name>")
def generate_qr(class_name):
    if session.get("role") != "admin": return redirect("/login")
    if not os.path.exists('static'): os.makedirs('static')
    # Change '127.0.0.1' to your Cloud URL when deploying to Render
    qr_data = f"http://127.0.0.1:5000/qr-mark/{class_name}"
    img = qrcode.make(qr_data)
    img.save("static/qr_code.png")
    return render_template("qr_display.html", class_name=class_name)

@app.route("/qr-mark/<class_name>")
def qr_mark(class_name):
    if "username" not in session: return redirect("/login")
    [span_52](start_span)username, today = session["username"], datetime.now().strftime("%Y-%m-%d") #[span_52](end_span)
    [span_53](start_span)conn = sqlite3.connect(DATABASE); c = conn.cursor() #[span_53](end_span)
    [span_54](start_span)c.execute("SELECT * FROM attendance WHERE username=? AND date=?", (username, today)) #[span_54](end_span)
    if c.fetchone():
        conn.close(); return "Already marked today!" [span_55](start_span)#
    c.execute("INSERT INTO attendance (username, date) VALUES (?, ?)", (username, today)) #[span_55](end_span)
    [span_56](start_span)conn.commit(); conn.close() #[span_56](end_span)
    return f"Attendance for {class_name} Marked Successfully via QR!"

# ---------------------------------------------------------
# 5. STUDENT FEATURES (MARKING & DASHBOARD)
# ---------------------------------------------------------
[span_57](start_span)@app.route("/student-dashboard") #[span_57](end_span)
def student_dashboard():
    [span_58](start_span)if session.get("role") != "student": #[span_58](end_span)
        return redirect("/login")
    [span_59](start_span)return render_template("student_dashboard.html") #[span_59](end_span)

[span_60](start_span)@app.route("/mark") #[span_60](end_span)
def mark():
    [span_61](start_span)if "username" not in session: return redirect("/login") #[span_61](end_span)
    [span_62](start_span)username, today = session["username"], datetime.now().strftime("%Y-%m-%d") #[span_62](end_span)
    [span_63](start_span)conn = sqlite3.connect(DATABASE); c = conn.cursor() #[span_63](end_span)
    [span_64](start_span)c.execute("SELECT * FROM attendance WHERE username=? AND date=?", (username, today)) #[span_64](end_span)
    if c.fetchone():
        conn.close(); return "Already marked today!" [span_65](start_span)#
    c.execute("INSERT INTO attendance (username, date) VALUES (?, ?)", (username, today)) #[span_65](end_span)
    [span_66](start_span)conn.commit(); conn.close() #[span_66](end_span)
    return "Attendance Marked Successfully!" [span_67](start_span)#

# ---------------------------------------------------------
# 6. DATA EXPORT (Excel)
# ---------------------------------------------------------
@app.route("/export") #[span_67](end_span)
def export():
    [span_68](start_span)if session.get("role") != "admin": #[span_68](end_span)
        return redirect("/login")
    [span_69](start_span)conn = sqlite3.connect(DATABASE); c = conn.cursor() #[span_69](end_span)
    [span_70](start_span)c.execute("SELECT username, date FROM attendance") #[span_70](end_span)
    [span_71](start_span)data = c.fetchall(); conn.close() #[span_71](end_span)
    [span_72](start_span)wb = Workbook() #[span_72](end_span)
    [span_73](start_span)ws = wb.active; ws.title = "Attendance" #[span_73](end_span)
    [span_74](start_span)ws.append(["Student Name", "Date"]) #[span_74](end_span)
    [span_75](start_span)for row in data: ws.append(row) #[span_75](end_span)
    [span_76](start_span)file_path = "attendance.xlsx"; wb.save(file_path) #[span_76](end_span)
    [span_77](start_span)return send_file(file_path, as_attachment=True) #[span_77](end_span)

[span_78](start_span)if __name__ == "__main__": #[span_78](end_span)
    [span_79](start_span)app.run(debug=True) #[span_79](end_span)
