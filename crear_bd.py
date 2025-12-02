import sqlite3
import os

DB = "evaluaciones.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.executescript("""
CREATE TABLE grupos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
);

CREATE TABLE docentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
);

CREATE TABLE materias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    docente_id INTEGER,
    grupo_id INTEGER,
    FOREIGN KEY (docente_id) REFERENCES docentes(id),
    FOREIGN KEY (grupo_id) REFERENCES grupos(id)
);

CREATE TABLE estudiantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    matricula TEXT,
    grupo_id INTEGER,
    FOREIGN KEY (grupo_id) REFERENCES grupos(id)
);

CREATE TABLE evaluaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_nombre TEXT,
    matricula TEXT,
    grupo_id INTEGER,
    docente_id INTEGER,
    criterio TEXT,
    calificacion TEXT,
    comentario TEXT
);
""")

conn.commit()
conn.close()

print("✅ Base de datos creada con estructura original.")
