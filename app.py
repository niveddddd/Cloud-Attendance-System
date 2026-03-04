from flask import Flask, render_template, request, redirect, session, send_file, url_for
import sqlite3
from datetime import datetime
from openpyxl import Workbook
import qrcode
import os

app = Flask(__name__)
[span_3](start_span)[span_4](start_span)app.secret_key = "supersecretkey" #[span_3](end_span)[span_4](end_span)
[span_5](start_span)DATABASE = "attendance.db" #[span_5](end_span)

# ---------------------------------------------------------
# 1. DATABASE INITIALIZATION
# ---------------------------------------------------------
def init_db():
    [span_6](start_span)[span_7](start_span)conn = sqlite3.connect(DATABASE) #[span_6](end_span)[span_7](end_span)
    [span_8](start_span)[span_9](start_span)c = conn.cursor() #[span_8](end_span)[span_9](end_span)
    
    # Users table: Stores admin and student credentials
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        [span_10](start_span)[span_11](start_span)role TEXT)""") #[span_10](end_span)[span_11](end_span)
    
    # Attendance table: Stores daily records
    c.execute("""CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        [span_12](start_span)date TEXT)""") #[span_12](end_span)
    
    # Ensure default Admin exists (Username: admin | Password: 1234)
    [span_13](start_span)c.execute("DELETE FROM users WHERE username='admin'") #[span_13](end_span)
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
              ("admin", "1234", "admin")[span_14](start_span)) #[span_14](end_span)
    
    [span_15](start_span)conn.commit() #[span_15](end_span)
    [span_16](start_span)[span_17](start_span)conn.close() #[span_16](end_span)[span_17](end_span)

init_db()

# ---------------------------------------------------------
# 2. AUTHENTICATION (LOGIN/LOGOUT)
# ---------------------------------------------------------
[span_18](start_span)@app.route("/", methods=["GET", "POST"]) #[span_18](end_span)
[span_19](start_span)@app.route("/login", methods=["GET", "POST"]) #[span_19](end_span)
def login():
    [span_20](start_span)if request.method == "POST": #[span_20](end_span)
        [span_21](start_span)username = request.form["username"] #[span_21](end_span)
        [span_22](start_span)password = request.form["password"] #[span_22](end_span)
        
        [span_23](start_span)conn = sqlite3.connect(DATABASE); c = conn.cursor() #[span_23](end_span)
        [span_24](start_span)c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password)) #[span_24](end_span)
        [span_25](start_span)user = c.fetchone(); conn.close() #[span_25](end_span)
        
        if user:
            [span_26](start_span)session["username"] = username #[span_26](end_span)
            [span_27](start_span)session["role"] = user[0] #[span_27](end_span)
            [span_28](start_span)if user[0] == "admin": #[span_28](end_span)
                [span_29](start_span)return redirect("/admin-dashboard") #[span_29](end_span)
            else:
                [span_30](start_span)return redirect("/student-dashboard") #[span_30](end_span)
        [span_31](start_span)return "Invalid Login" #[span_31](end_span)
    [span_32](start_span)return render_template("login.html") #[span_32](end_span)

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
