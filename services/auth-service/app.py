import os, datetime, random
from flask import Flask, request, jsonify
import mysql.connector
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

def db():
    return mysql.connector.connect(host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME"))

def account_number():
    return "91" + "".join(str(random.randint(0,9)) for _ in range(10))

@app.get("/health")
def health(): return {"status":"healthy","service":"auth-service"}

@app.post("/register")
def register():
    data=request.get_json(silent=True) or {}
    required=("full_name","email","phone","password")
    if any(not data.get(k) for k in required): return jsonify(error="All registration fields are required"),400
    if len(data["password"]) < 8: return jsonify(error="Password must contain at least 8 characters"),400
    conn=db(); cur=conn.cursor()
    try:
        cur.execute("INSERT INTO users(full_name,email,phone,password_hash) VALUES(%s,%s,%s,%s)",
                    (data["full_name"].strip(),data["email"].strip().lower(),data["phone"].strip(),generate_password_hash(data["password"])))
        uid=cur.lastrowid
        cur.execute("INSERT INTO accounts(user_id,account_number,account_type,balance) VALUES(%s,%s,'SAVINGS',1000.00)",(uid,account_number()))
        cur.execute("INSERT INTO accounts(user_id,account_number,account_type,balance) VALUES(%s,%s,'PERSONAL',500.00)",(uid,account_number()))
        conn.commit(); return jsonify(message="Registration successful"),201
    except mysql.connector.IntegrityError:
        conn.rollback(); return jsonify(error="Email already registered"),409
    finally: cur.close(); conn.close()

@app.post("/login")
def login():
    data=request.get_json(silent=True) or {}
    conn=db(); cur=conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s",((data.get("email") or "").strip().lower(),)); user=cur.fetchone()
    cur.close(); conn.close()
    if not user or not check_password_hash(user["password_hash"],data.get("password", "")):
        return jsonify(error="Invalid email or password"),401
    token=jwt.encode({"sub":str(user["id"]),"name":user["full_name"],"exp":datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=8)},os.getenv("JWT_SECRET"),algorithm="HS256")
    return jsonify(token=token,user={"id":user["id"],"full_name":user["full_name"],"email":user["email"]})
