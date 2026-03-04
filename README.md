# Cloud Attendance System ☁️📅

[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-orange)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-brightgreen)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A **professional web-based attendance management system** built with **Python (Flask)** and **SQLite**.  
This system allows administrators to manage student records, generate QR codes for touchless attendance, and export reports to Excel.

---

## 🚀 Features

- **Dual-Role Authentication**: Separate dashboards for **Administrators** and **Students**.  
- **QR Code Attendance**: Admins can generate a unique QR code for classes; students scan to mark attendance instantly.  
- **Student Management**: Admin can register new students and delete existing records.  
- **Manual Override**: Admin can manually add attendance records for any date.  
- **Excel Export**: Download all attendance data into a `.xlsx` file with one click.  
- **Responsive UI**: Modern interface built with **Bootstrap 5** and custom CSS.  

---

## 🛠️ Tech Stack

- **Backend**: Python 3.x, Flask  
- **Database**: SQLite3  
- **Libraries**:  
  - `qrcode` & `pillow` – QR code generation  
  - `openpyxl` – Excel reports  
  - `gunicorn` – Cloud deployment  
- **Frontend**: HTML5, CSS3, Bootstrap 5  

---

## ⚙️ Installation & Setup

1. **Clone the repository**:

```bash
git clone <your-repo-url>
cd Cloud-Attendance-System​Set Build Command: pip install -r requirements.txt.
​Set Start Command: gunicorn app:app
```
install dependencies
```bash
pip install flask openpyxl qrcode pillow gunicorn
