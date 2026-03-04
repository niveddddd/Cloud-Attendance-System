Cloud Attendance System ☁️📅
​A professional web-based attendance management system built with Python (Flask) and SQLite. This system allows administrators to manage student records, generate QR codes for touchless attendance, and export reports to Excel.
​🚀 Features
​Dual-Role Authentication: Separate dashboards for Administrators and Students.
​QR Code Attendance: Admins can generate a unique QR code for classes; students scan to mark attendance instantly.
​Student Management: Admin can register new students and delete existing records.
​Manual Override: Admin can manually add attendance records for any date.
​Excel Export: Download all attendance data into a .xlsx file with one click.
​Responsive UI: Modern interface built with Bootstrap 5 and custom CSS.
​🛠️ Tech Stack
​Backend: Python 3.x, Flask
​Database: SQLite3
​Libraries:
​qrcode & pillow (For QR generation)
​openpyxl (For Excel reports)
​gunicorn (For Cloud deployment)
​Frontend: HTML5, CSS3, Bootstrap 5
Cloud-Attendance-System
⚙️ Installation & Setup
Clone the repository (or open your project folder):
cd D:\CloudAttendance
Install dependencies:
pip install flask openpyxl qrcode pillow gunicorn
Run the application:
python app.py
Access the Portal:
Open your browser and go to http://127.0.0.1:5000.
🔑 Default Credentials
Admin admin 1234
Student (Created by Admin) (Set by Admin)
📲 How the QR System Works
​Admin logs in and clicks "Generate QR".
​The system creates a link: http://[Server-IP]:5000/qr-mark/[ClassName].
​Student scans the code with their mobile phone.
​The system verifies the student's session and records the attendance in the database for the current date.
​☁️ Deployment
​To deploy on Render:
​Push your code to GitHub.
​Connect the repository to Render.
​Set Build Command: pip install -r requirements.txt.
​Set Start Command: gunicorn app:app
