import os
from functools import wraps
from flask import Flask, request, jsonify, g
import mysql.connector, jwt

app=Flask(__name__)
def db(): return mysql.connector.connect(host=os.getenv("DB_HOST"),user=os.getenv("DB_USER"),password=os.getenv("DB_PASSWORD"),database=os.getenv("DB_NAME"))
def secured(fn):
    @wraps(fn)
    def wrapper(*a,**kw):
        value=request.headers.get("Authorization","")
        if not value.startswith("Bearer "): return jsonify(error="Authentication required"),401
        try: g.user_id=int(jwt.decode(value[7:],os.getenv("JWT_SECRET"),algorithms=["HS256"])["sub"])
        except Exception: return jsonify(error="Invalid or expired token"),401
        return fn(*a,**kw)
    return wrapper

@app.get("/health")
def health(): return {"status":"healthy","service":"account-service"}

@app.get("/")
@secured
def accounts():
    conn=db(); cur=conn.cursor(dictionary=True)
    cur.execute("SELECT id,account_number,account_type,balance,created_at FROM accounts WHERE user_id=%s ORDER BY account_type",(g.user_id,))
    rows=cur.fetchall()
    for r in rows: r["balance"]=float(r["balance"]); r["created_at"]=r["created_at"].isoformat()
    cur.close(); conn.close(); return jsonify(rows)

@app.get("/<account_type>")
@secured
def account(account_type):
    kind=account_type.upper()
    if kind not in ("SAVINGS","PERSONAL"): return jsonify(error="Account type not found"),404
    conn=db(); cur=conn.cursor(dictionary=True)
    cur.execute("SELECT id,account_number,account_type,balance,created_at FROM accounts WHERE user_id=%s AND account_type=%s",(g.user_id,kind)); row=cur.fetchone()
    if row:
        row["balance"]=float(row["balance"]); row["created_at"]=row["created_at"].isoformat()
        cur.execute("SELECT transaction_type,amount,description,created_at FROM transactions WHERE account_id=%s ORDER BY created_at DESC LIMIT 10",(row["id"],)); tx=cur.fetchall()
        for t in tx: t["amount"]=float(t["amount"]); t["created_at"]=t["created_at"].isoformat()
        row["transactions"]=tx
    cur.close(); conn.close()
    return jsonify(row) if row else (jsonify(error="Account not found"),404)
