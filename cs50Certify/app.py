from flask import Flask, render_template, request, redirect, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import sqlite3

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

DATABASE = "database.db" 

def get_db():
    if not hasattr(g, "db"):
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "db"):
        g.db.close()


def ensure_admin():
    db = get_db()
    cursor = db.cursor()
    username = "admin"
    email = "admin@admin.com"
    password = "admin"
    
    cursor.execute("SELECT * FROM admin WHERE username = ?", (username,))
    admin_exists = cursor.fetchone()
    
    if admin_exists:
        print("Admin already exists in the database.")
    else:
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO admin (username, email, password) VALUES (?, ?, ?)", 
                       (username, email, hashed_password))
        db.commit()
        print("Admin added successfully!")

with app.app_context():
    ensure_admin()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username:
            return render_template("login.html", error="Username is required")
        if not password:
            return render_template("login.html", error="Password is required")
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM admin WHERE username = ?", (username,))
        admin_exists = cursor.fetchone()

        if admin_exists and check_password_hash(admin_exists["password"], password):
            session["admin"] = admin_exists["id"]
            return redirect("/")  
        else:
            return render_template("login.html", error="Invalid credentials")
     
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
