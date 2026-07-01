# Douceur — Bakery & Dessert Management System

## โครงสร้างโปรเจค

```
douceur/
├── api/
│   └── index.py          ← FastAPI backend (in-memory, ไม่มี  DB)
├── frontend/
│   ├── assets/
│   │   ├── css/style.css ← shared styles
│   │   └── js/
│   │       ├── utils.js  ← helper functions
│   │       └── shell.js  ← sidebar/topbar template
│   ├── index.html        ← Dashboard
│   ├── products.html     ← จัดการสินค้า
│   ├── inventory.html    ← รับเข้า/จ่ายออกสต็อก
│   └── sales.html        ← รายรับ-รายจ่าย
├── requirements.txt
├── vercel.json
└── README.md
```

## รัน Local

### Backend
```bash
pip install fastapi uvicorn pydantic
uvicorn api.index:app --reload --port 8000
```

### Frontend
```bash
# เปิดผ่าน Live Server (VS Code) หรือ:
cd frontend
python -m http.server 3000
```

> **หมายเหตุ:** ตอนรัน local ต้องแก้ `const API = '/api'` ใน `utils.js`
> เป็น `const API = 'http://localhost:8000/api'`

## Deploy บน Vercel

```bash
npm i -g vercel
vercel login
vercel --prod
```

Vercel จะ route `/api/*` → FastAPI และ `/*` → static frontend อัตโนมัติ

## API Endpoints

| Method | Path | คำอธิบาย |
|--------|------|----------|
| GET    | /api/dashboard       | สรุปภาพรวมวันนี้ |
| GET    | /api/products        | รายการสินค้าทั้งหมด + สต็อก |
| POST   | /api/products        | เพิ่มสินค้า |
| PUT    | /api/products/:id    | แก้ไขสินค้า |
| DELETE | /api/products/:id    | ลบสินค้า |
| GET    | /api/inventory       | รายการรับเข้า/จ่ายออก |
| POST   | /api/inventory       | บันทึก IN หรือ OUT |
| GET    | /api/sales           | รายการขาย |
| POST   | /api/sales           | บันทึกการขาย (auto-OUT inventory) |
| GET    | /api/expenses        | รายจ่ายอื่นๆ |
| POST   | /api/expenses        | เพิ่มรายจ่าย |
| DELETE | /api/expenses/:id    | ลบรายจ่าย |

## Business Logic

- **Stock** = รวม IN − รวม OUT (คำนวณ real-time)
- **COGS** = quantity_sold × cost_price
- **Net Profit** = revenue − COGS − expenses
- บันทึก Sale จะ auto-สร้าง inventory OUT ให้อัตโนมัติ

## อยากเพิ่ม Database?

ตอน ready เพิ่ม NeonDB ให้เปลี่ยนแค่ `api/index.py`:
1. `pip install psycopg2-binary`
2. เปลี่ยน `products: list[dict] = [...]` → query จาก PostgreSQL
3. Logic ทุกอย่างเหมือนเดิม 100%
