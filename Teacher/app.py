import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = "teacher_secret_key"
DB_PATH = "db.sqlite"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            gender TEXT,
            address TEXT,
            department TEXT NOT NULL,
            qualification TEXT,
            subject TEXT,
            experience INTEGER,
            date_of_joining TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    conn = get_db_connection()
    teachers = conn.execute("SELECT * FROM teachers").fetchall()
    conn.close()
    return render_template("home.html", teachers=teachers)

@app.route("/teacher/add/", methods=["GET", "POST"])
def add_teacher():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        gender = request.form.get("gender")
        address = request.form.get("address")
        department = request.form.get("department")
        qualification = request.form.get("qualification")
        subject = request.form.get("subject")
        experience = request.form.get("experience", 0)
        date_of_joining = request.form.get("date_of_joining")

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO teachers (name, email, phone, gender, address, department, qualification, subject, experience, date_of_joining)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, phone, gender, address, department, qualification, subject, experience, date_of_joining))
        conn.commit()
        conn.close()
        
        flash("Teacher added successfully!", "success")
        return redirect(url_for("details"))
        
    return render_template("add_students.html")

@app.route("/teacher/edit/<int:id>/", methods=["GET", "POST"])
def edit_teacher(id):
    conn = get_db_connection()
    teacher = conn.execute("SELECT * FROM teachers WHERE id = ?", (id,)).fetchone()

    if not teacher:
        conn.close()
        flash("Teacher record not found.", "danger")
        return redirect(url_for("details"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        gender = request.form.get("gender")
        address = request.form.get("address")
        department = request.form.get("department")
        qualification = request.form.get("qualification")
        subject = request.form.get("subject")
        experience = request.form.get("experience")
        date_of_joining = request.form.get("date_of_joining")

        conn.execute('''
            UPDATE teachers 
            SET name=?, email=?, phone=?, gender=?, address=?, department=?, qualification=?, subject=?, experience=?, date_of_joining=?
            WHERE id=?
        ''', (name, email, phone, gender, address, department, qualification, subject, experience, date_of_joining, id))
        conn.commit()
        conn.close()
        
        flash("Teacher details updated successfully!", "info")
        return redirect(url_for("details"))

    conn.close()
    return render_template("edit_students.html", teacher=teacher)

@app.route("/teacher/delete/<int:id>/", methods=["GET", "POST"])
def delete_teacher(id):
    conn = get_db_connection()
    teacher = conn.execute("SELECT * FROM teachers WHERE id = ?", (id,)).fetchone()

    if not teacher:
        conn.close()
        flash("Teacher record not found.", "danger")
        return redirect(url_for("details"))

    if request.method == "POST":
        conn.execute("DELETE FROM teachers WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        flash("Teacher deleted successfully.", "warning")
        return redirect(url_for("details"))

    conn.close()
    return render_template("delete_teacher.html", teacher=teacher)

@app.route("/teacher/details/")
def details():
    conn = get_db_connection()
    teachers = conn.execute("SELECT * FROM teachers").fetchall()
    conn.close()
    return render_template("details.html", teachers=teachers)

@app.route("/teacher/dashboard/")
def dashboard():
    conn = get_db_connection()
    total_teachers = conn.execute("SELECT COUNT(*) FROM teachers").fetchone()[0]
    dept_data = conn.execute("SELECT department, COUNT(*) as count FROM teachers GROUP BY department").fetchall()
    exp_data = conn.execute("SELECT name, experience FROM teachers ORDER BY experience DESC LIMIT 7").fetchall()
    conn.close()

    dept_labels = [row["department"] for row in dept_data]
    dept_counts = [row["count"] for row in dept_data]

    exp_labels = [row["name"] for row in exp_data]
    exp_years = [row["experience"] for row in exp_data]

    return render_template("dashboard.html", 
                           total_teachers=total_teachers,
                           dept_labels=dept_labels,
                           dept_counts=dept_counts,
                           exp_labels=exp_labels,
                           exp_years=exp_years)

if __name__ == "__main__":
    app.run(debug=True)