from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row 
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirmPassword')
        
        if not username:
            return render_template("register.html", error="Username is required")
        if not email:
            return render_template("register.html", error="Email is required")
        if not password:
            return render_template("register.html", error="Password is required")
        if not confirmPassword:
            return render_template("register.html", error="Please confirm your password")
        if password != confirmPassword:
            return render_template("register.html", error="Passwords do not match")

        try:
            conn = get_db_connection()
            print(conn)
            conn.execute(
                "INSERT INTO admin (username, email, password) VALUES (?, ?, ?)",
                (username, email, password),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            return render_template("register.html", error=f"Database error: {e}")

        # Redirect to login after successful registration
        return redirect(url_for("login"))

    # Render the registration form on GET request
    return render_template("register.html")

    

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
















if __name__ == "__main__":
    app.run(debug=True)