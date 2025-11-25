from flask import Flask,render_template,request,session,redirect,url_for
import mysql.connector

app=Flask(__name__)
db=mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="allocation"
)
app.secret_key="your_key"

conn=db.cursor()

@app.route("/")
def home():
    return render_template("homepage.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]

        conn.execute(
            "SELECT * FROM details WHERE name=%s AND password=%s",
            (name, password)
        )
        admin = conn.fetchone()

        if admin:
            # 🔥 Save student name in session
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
    # Check if already booked
    conn.execute("SELECT * FROM booked WHERE room=%s", (room,))
    booked_room = conn.fetchone()
    if booked_room:
        return f"Room {room} is already booked!"
    return render_template("booking.html", room=room)

@app.route("/confirm_booking", methods=["POST"])
def confirm_booking():
    student = session.get("student_name")   # ← FIXED
    room = request.form["room"]
    gender = request.form["gender"]
    room_type = request.form["room_type"]
    session_year = "2024/2025"

    # Double check
    conn.execute("SELECT * FROM booked WHERE room=%s", (room,))
    exists = conn.fetchone()

    if exists:
        return render_template("already_booked.html", room=room)

    # Save booking
    conn.execute(
        "INSERT INTO booked (student_name, room, gender, room_type, session_year) VALUES (%s,%s,%s,%s,%s)",
        (student, room, gender, room_type, session_year)
    )
    db.commit()

    return render_template("success.html", room=room)

@app.route("/bedspaces")
def bedspaces():
    return render_template("bedspaces.html")
        
          
if __name__=="__main__":
    app.run(debug=True)