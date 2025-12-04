from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
import os

app = Flask(__name__)

# Read environment variables safely
MYSQL_HOST = os.getenv("MYSQLHOST")
MYSQL_USER = os.getenv("MYSQLUSER")
MYSQL_PASSWORD = os.getenv("MYSQLPASSWORD")
MYSQL_DATABASE = os.getenv("MYSQLDATABASE")
MYSQL_PORT = int(os.getenv("MYSQLPORT", 3306))  # default to 3306 if missing

# Convert port to integer safely
try:
    MYSQL_PORT = int(MYSQL_PORT)
except ValueError:
    MYSQL_PORT = 3306

# Connect to remote MySQL
try:
    db = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        port=MYSQL_PORT
    )
    conn = db.cursor()
except mysql.connector.Error as e:
    print("Error connecting to MySQL:", e)
    conn = None  # avoid crashing; your routes should handle this

app.secret_key = "your_key"

@app.route("/")
def home():
    return render_template("homepage.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]

        if conn:
            conn.execute(
                "SELECT * FROM details WHERE name=%s AND password=%s",
                (name, password)
            )
            admin = conn.fetchone()
        else:
            admin = None

        if admin:
            session["student_name"] = name
            return render_template("bedspaces.html")
        else:
            return render_template("login.html", error="Invalid details")

    return render_template("login.html")

@app.route("/select-room", methods=["POST"])
def select_room():
    gender = request.form.get("gender")
    room = request.form.get("room")

    if not gender or not room:
        return render_template("bedspaces.html", error="Please select both fields")

    page = f"{gender}-{room}.html"
    return render_template(page)

@app.route("/booking")
def booking():
    room = request.args.get("room")
    if conn:
        conn.execute("SELECT * FROM booked WHERE room=%s", (room,))
        booked_room = conn.fetchone()
    else:
        booked_room = None

    if booked_room:
        return f"Room {room} is already booked!"
    return render_template("booking.html", room=room)

@app.route("/confirm_booking", methods=["POST"])
def confirm_booking():
    student = session.get("student_name")
    room = request.form["room"]
    gender = request.form["gender"]
    room_type = request.form["room_type"]
    session_year = "2024/2025"

    if conn:
        conn.execute("SELECT * FROM booked WHERE room=%s", (room,))
        exists = conn.fetchone()
    else:
        exists = None

    if exists:
        return render_template("already_booked.html", room=room)

    if conn:
        conn.execute(
            "INSERT INTO booked (student_name, room, gender, room_type, session_year) VALUES (%s,%s,%s,%s,%s)",
            (student, room, gender, room_type, session_year)
        )
        db.commit()

    return render_template("success.html", room=room)

@app.route("/bedspaces")
def bedspaces():
    return render_template("bedspaces.html")


if __name__ == "__main__":
    app.run(debug=False)

