import os, uuid
from datetime import date, timedelta
from typing import Literal, Optional                                     
from pathlib import Path

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="Douceur Bakery API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DB connection ──────────────────────────────────────────
from psycopg2 import pool as pg_pool

_pool = None

def get_conn():
    global _pool
    if _pool is None:
        _pool = pg_pool.SimpleConnectionPool(1, 5, os.environ["DATABASE_URL"])
    return _pool.getconn()

def query(sql, params=(), fetchone=False, fetchall=False, commit=False):
    conn = get_conn()
    try:
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, params)
                if commit:
                    return None
                if fetchone:
                    res = cur.fetchone()
                    return dict(res) if res else None
                if fetchall:
                    return [dict(r) for r in cur.fetchall()]
    finally:
        _pool.putconn(conn) 

# ── Schemas ────────────────────────────────────────────────
class ProductCreate(BaseModel):
    name: str
    category: str
    cost_price: float
    selling_price: float
    low_stock_threshold: int = 10

class InventoryCreate(BaseModel):
    product_id: int
    type: Literal["IN", "OUT"]
    quantity: int
    note: Optional[str] = ""
    date: Optional[str] = None

class SaleCreate(BaseModel):
    amount:       float
    payment_type: str = "เงินสด"
    sale_type:    str = "ทั่วไป"
    date:         Optional[str] = None

class ExpenseCreate(BaseModel):
    description: str
    amount: float
    date: Optional[str] = None

# ── Dashboard ──────────────────────────────────────────────
# ── Dashboard ──────────────────────────────────────────────
# ── Dashboard (เวอร์ชันสมบูรณ์ แก้บั๊กตัวแปรไม่ตรงกัน) ──
@app.get("/api/dashboard")
def get_dashboard(period_type: str = "daily", selected_date: str = None):
    today = date.today().isoformat()

    # 1. จัดการค่าเริ่มต้นของวันที่
    if not selected_date:
        if period_type == "daily":
            selected_date = today
        elif period_type == "monthly":
            selected_date = today[:7] # "YYYY-MM"
        elif period_type == "yearly":
            selected_date = today[:4] # "YYYY"

    # 2. ตั้งค่าเงื่อนไขเวลาสำหรับ Query SQL (ป้องกัน NameError)
    if period_type == "daily":
        sql_cond = "DATE(date) = %s"
        sql_cond_join = "DATE(s.date) = %s"
    elif period_type == "monthly":
        sql_cond = "TO_CHAR(date, 'YYYY-MM') = %s"
        sql_cond_join = "TO_CHAR(s.date, 'YYYY-MM') = %s"
    elif period_type == "yearly":
        sql_cond = "TO_CHAR(date, 'YYYY') = %s"
        sql_cond_join = "TO_CHAR(s.date, 'YYYY') = %s"
    else:
        raise HTTPException(400, "Invalid period type")

    # 3. ดึงยอดขายและรายจ่าย 
    revenue = query(f"SELECT COALESCE(SUM(total_price),0) AS v FROM Sales WHERE {sql_cond}", (selected_date,), fetchone=True)["v"]
    exp_amt = query(f"SELECT COALESCE(SUM(amount),0) AS v FROM Expenses WHERE {sql_cond}", (selected_date,), fetchone=True)["v"]
    cogs = query(f"SELECT COALESCE(SUM(s.quantity * p.cost_price),0) AS v FROM Sales s JOIN Products p ON s.product_id=p.id WHERE {sql_cond_join}", (selected_date,), fetchone=True)["v"]
    net_profit = float(revenue) - float(cogs) - float(exp_amt)

    best = query(f"SELECT p.name, SUM(s.quantity) AS qty FROM Sales s JOIN Products p ON s.product_id=p.id WHERE {sql_cond_join} GROUP BY p.name ORDER BY qty DESC LIMIT 1", (selected_date,), fetchone=True)

    breakdown = query(f"SELECT description AS label, SUM(amount) AS amount FROM Expenses WHERE {sql_cond} GROUP BY description ORDER BY amount DESC", (selected_date,), fetchall=True)

    # 4. สร้างข้อมูลกราฟแท่ง (ให้หน้าเว็บอ่านค่าแกน X ได้ถูกต้อง)
    chart_data = []
    if period_type == "daily":
        # กราฟ 7 วันล่าสุด
        base_date = date.fromisoformat(selected_date)
        for i in range(6, -1, -1):
            d = base_date - timedelta(days=i)
            d_str = d.isoformat()
            rev = query("SELECT COALESCE(SUM(total_price),0) AS v FROM Sales WHERE DATE(date)=%s", (d_str,), fetchone=True)["v"]
            exp = query("SELECT COALESCE(SUM(amount),0) AS v FROM Expenses WHERE DATE(date)=%s", (d_str,), fetchone=True)["v"]
            chart_data.append({"date": d_str, "revenue": float(rev), "expenses": float(exp)})
            
    elif period_type == "monthly":
        # กราฟ 7 เดือนล่าสุด
        year, month = map(int, selected_date.split("-"))
        for i in range(6, -1, -1):
            m = month - i
            y = year
            while m <= 0:
                m += 12
                y -= 1
            m_str = f"{y:04d}-{m:02d}"
            rev = query("SELECT COALESCE(SUM(total_price),0) AS v FROM Sales WHERE TO_CHAR(date, 'YYYY-MM')=%s", (m_str,), fetchone=True)["v"]
            exp = query("SELECT COALESCE(SUM(amount),0) AS v FROM Expenses WHERE TO_CHAR(date, 'YYYY-MM')=%s", (m_str,), fetchone=True)["v"]
            chart_data.append({"date": m_str, "revenue": float(rev), "expenses": float(exp)})
            
    elif period_type == "yearly":
        # กราฟ 7 ปีล่าสุด
        y = int(selected_date)
        for i in range(6, -1, -1):
            y_str = str(y - i)
            rev = query("SELECT COALESCE(SUM(total_price),0) AS v FROM Sales WHERE TO_CHAR(date, 'YYYY')=%s", (y_str,), fetchone=True)["v"]
            exp = query("SELECT COALESCE(SUM(amount),0) AS v FROM Expenses WHERE TO_CHAR(date, 'YYYY')=%s", (y_str,), fetchone=True)["v"]
            chart_data.append({"date": y_str, "revenue": float(rev), "expenses": float(exp)})

    low_stock = query("""
        SELECT p.id, p.name, p.category, p.low_stock_threshold,
               COALESCE(SUM(CASE WHEN i.type='IN'  THEN i.quantity ELSE 0 END),0)
             - COALESCE(SUM(CASE WHEN i.type='OUT' THEN i.quantity ELSE 0 END),0)
               AS current_stock
        FROM Products p LEFT JOIN Inventory i ON p.id=i.product_id
        GROUP BY p.id, p.name, p.category, p.low_stock_threshold
        HAVING (COALESCE(SUM(CASE WHEN i.type='IN' THEN i.quantity ELSE 0 END),0)
              - COALESCE(SUM(CASE WHEN i.type='OUT' THEN i.quantity ELSE 0 END),0))
               <= p.low_stock_threshold""", fetchall=True)

    return {
        "today": {
            "revenue":    float(revenue),
            "expenses":   float(exp_amt),
            "net_profit": round(net_profit, 2),
            "best_seller": {
                "name":     best["name"]  if best else "-",
                "quantity": int(best["qty"]) if best else 0,
            },
        },
        "low_stock":         low_stock,
        "weekly_chart":      chart_data,
        "expense_breakdown": [{"label": r["label"], "amount": float(r["amount"])} for r in breakdown],
    }
    
# ── Products ───────────────────────────────────────────────
@app.get("/api/products")
def list_products():
    return query("""
        SELECT p.*,
               COALESCE(SUM(CASE WHEN i.type='IN'  THEN i.quantity ELSE 0 END),0)
             - COALESCE(SUM(CASE WHEN i.type='OUT' THEN i.quantity ELSE 0 END),0)
               AS current_stock
        FROM Products p LEFT JOIN Inventory i ON p.id=i.product_id
        GROUP BY p.id ORDER BY p.id""", fetchall=True)

@app.post("/api/sales", status_code=201)
def create_sale(b: SaleCreate):
    r = query("""
        INSERT INTO Sales (total_price, payment_type, sale_type, date)
        VALUES (%s,%s,%s,%s) RETURNING *""",
        (b.amount, b.payment_type, b.sale_type,
         b.date or date.today().isoformat()),
        fetchone=True)
    return r

@app.put("/api/products/{pid}")
def update_product(pid: int, b: ProductCreate):
    r = query("""
        UPDATE Products SET name=%s,category=%s,cost_price=%s,
        selling_price=%s,low_stock_threshold=%s WHERE id=%s RETURNING *""",
        (b.name,b.category,b.cost_price,b.selling_price,b.low_stock_threshold,pid),
        fetchone=True)
    if not r: raise HTTPException(404,"Not found")
    return r

@app.delete("/api/products/{pid}")
def delete_product(pid: int):
    query("DELETE FROM Products WHERE id=%s",(pid,),commit=True)
    return {"deleted": pid}

# ── Inventory ──────────────────────────────────────────────
@app.get("/api/inventory")
def list_inventory():
    return query("""
        SELECT i.*, p.name AS product_name, p.category
        FROM Inventory i JOIN Products p ON i.product_id=p.id
        ORDER BY i.id DESC LIMIT 50""", fetchall=True)

@app.post("/api/inventory", status_code=201)
def create_inventory(b: InventoryCreate):
    if b.type == "OUT":
        stock = query("""
            SELECT COALESCE(SUM(CASE WHEN type='IN' THEN quantity ELSE -quantity END),0) AS v
            FROM Inventory WHERE product_id=%s""", (b.product_id,), fetchone=True)["v"]
        if b.quantity > int(stock):
            raise HTTPException(400, f"สต็อกไม่พอ — มีแค่ {stock} ชิ้น")
    r = query("""
        INSERT INTO Inventory (product_id,type,quantity,note,date)
        VALUES (%s,%s,%s,%s,%s) RETURNING *""",
        (b.product_id,b.type,b.quantity,b.note or "",b.date or date.today().isoformat()),
        fetchone=True)
    return r

# ── Sales ──────────────────────────────────────────────────
@app.get("/api/sales")
def list_sales():
    return query("""
        SELECT s.*, p.name AS product_name FROM Sales s
        JOIN Products p ON s.product_id=p.id ORDER BY s.id DESC LIMIT 50""", fetchall=True)

@app.post("/api/sales", status_code=201)
def create_sale(b: SaleCreate):
    price = query("SELECT selling_price FROM Products WHERE id=%s",
                  (b.product_id,), fetchone=True)
    if not price: raise HTTPException(404,"Product not found")
    total = round(b.quantity * float(price["selling_price"]), 2)
    r = query("""
        INSERT INTO Sales (product_id,quantity,total_price,date)
        VALUES (%s,%s,%s,%s) RETURNING *""",
        (b.product_id,b.quantity,total,b.date or date.today().isoformat()),
        fetchone=True)
    # auto OUT inventory
    query("INSERT INTO Inventory (product_id,type,quantity,note,date) VALUES (%s,'OUT',%s,'ขายสินค้า (auto)',%s)",
          (b.product_id,b.quantity,b.date or date.today().isoformat()), commit=True)
    return r

# ── Expenses ───────────────────────────────────────────────
@app.get("/api/expenses")
def list_expenses():
    return query("SELECT * FROM Expenses ORDER BY id DESC LIMIT 50", fetchall=True)

@app.post("/api/expenses", status_code=201)
def create_expense(b: ExpenseCreate):
    return query("""
        INSERT INTO Expenses (description,amount,date)
        VALUES (%s,%s,%s) RETURNING *""",
        (b.description,b.amount,b.date or date.today().isoformat()), fetchone=True)

@app.delete("/api/expenses/{eid}")
def delete_expense(eid: int):
    query("DELETE FROM Expenses WHERE id=%s",(eid,),commit=True)
    return {"deleted": eid}