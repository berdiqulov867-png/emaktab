import os
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB_NAME = "school_bot_pro_v20.db"

app = FastAPI(title="e-Kundalik API")

# Mini App va har qanday domendan ulanish uchun CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fio TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                tarix INTEGER DEFAULT 0,
                geo INTEGER DEFAULT 0,
                vazifa INTEGER DEFAULT 0,
                davomat TEXT DEFAULT 'Keldi',
                payment_status TEXT DEFAULT 'To''lanmagan',
                phone TEXT DEFAULT 'Kiritilmagan'
            )
        """)
        conn.commit()

init_db()

class StudentCreate(BaseModel):
    fio: str
    code: str

@app.get("/")
def home():
    return {"status": "ok", "message": "e-Kundalik API ishlamoqda!"}

@app.get("/api/students")
def get_all_students():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, fio, code, tarix, geo, vazifa, davomat, payment_status, phone FROM students")
        rows = cursor.fetchall()
        
        result = []
        for r in rows:
            avg = (r[3] + r[4] + r[5]) // 3
            result.append({
                "id": r[0], "fio": r[1], "code": r[2],
                "tarix": r[3], "geo": r[4], "vazifa": r[5],
                "avg": avg, "davomat": r[6],
                "payment_status": r[7], "phone": r[8]
            })
        return result

@app.post("/api/student/add")
def add_student(st: StudentCreate):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO students (fio, code) VALUES (?, ?)", (st.fio, st.code))
            conn.commit()
            return {"status": "success", "message": "O'quvchi qo'shildi"}
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Bu kod allaqachon mavjud!")
      
