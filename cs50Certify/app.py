from flask import Flask, render_template, request, redirect, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import sqlite3
from web3 import Web3

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

DATABASE = "database.db" 

GANACHE_URL = 'http://127.0.0.1:7545'  # Ganache default RPC server
CONTRACT_ADDRESS = '0x8d706AFdAccC1eb33a58d953C5FC50E314700A5B'  # Replace with your deployed contract address on Ganache
ABI = []

web3 = Web3(Web3.HTTPProvider(GANACHE_URL))
contract = web3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)

@app.route('/verify', methods=['GET', 'POST'])
def verify_degree():
    message = ""

    if request.method == 'POST':
        # MetaMask connection assumption
        try:
            user_account = web3.eth.accounts[0]  # Assuming MetaMask is connected and this is the account
        except IndexError:
            message = "MetaMask is not connected. Please connect MetaMask before proceeding."
            return render_template('form.html', message=message)

        # Form inputs
        name = request.form.get('name').strip().upper()
        university = request.form.get('university').strip().upper()
        degree_name = request.form.get('degreeName').strip().upper()
        year = request.form.get('year').strip().upper()
        roll_no = request.form.get('rollNo').strip().upper()
        reg_no = request.form.get('regNo').strip().upper()

        # Hash the degree data
        data = f"{name}{university}{degree_name}{year}{roll_no}{reg_no}"
        degree_hash = web3.keccak(text=data).hex()

        # Interact with the smart contract
        try:
            # Check if the degree exists
            exists = contract.functions.isDegreeExists(degree_hash).call()

            if exists:
                # Verify the degree
                tx = contract.functions.verifyDegree(degree_hash).transact({
                    'from': user_account,
                    'value': web3.to_wei(0.001, 'ether')  # Transaction fee
                })
                receipt = web3.eth.wait_for_transaction_receipt(tx)

                if receipt['status'] == 1:
                    message = "Degree is verified on the blockchain."
                else:
                    message = "Degree verification failed."
            else:
                message = "Degree has not been uploaded to the blockchain."
        except Exception as e:
            message = f"Error occurred: {str(e)}"

    return render_template('verify.html')


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

@app.route('/verify')
def verify():
    return render_template('verify.html')

if __name__ == "__main__":
    app.run(debug=True)
