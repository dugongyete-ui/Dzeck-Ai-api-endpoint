from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = "drama.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS dramas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER,
            genre TEXT,
            description TEXT,
            poster TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/api/dramas")
def get_dramas():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM dramas")
    rows = c.fetchall()
    conn.close()

    dramas = []
    for r in rows:
        dramas.append({
            "id": r[0],
            "title": r[1],
            "year": r[2],
            "genre": r[3],
            "description": r[4],
            "poster": r[5]
        })
    return jsonify(dramas)

@app.post("/api/dramas")
def add_drama():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO dramas (title, year, genre, description, poster)
        VALUES (?, ?, ?, ?, ?)
    """, (data["title"], data["year"], data["genre"], data["description"], data["poster"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Drama added"}), 201

@app.delete("/api/dramas/<int:id>")
def delete_drama(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM dramas WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Drama deleted"})
