import sqlite3
import os

DB = "evaluaciones.db"

# Eliminar BD anterior
if os.path.exists(DB):
    os.remove(DB)

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Crear tablas correctas
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
    matricula TEXT NOT NULL,
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
    comentario TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (grupo_id) REFERENCES grupos(id),
    FOREIGN KEY (docente_id) REFERENCES docentes(id)
);
""")

# Datos ejemplo
cur.executemany("INSERT INTO grupos (nombre) VALUES (?)", [
    ('3A',),
    ('3B',),
    ('4A',),
    ('4B',)
])

cur.executemany("INSERT INTO docentes (nombre) VALUES (?)", [
    ('Profesor Juan Pérez',),
    ('Profesora María López',),
    ('Ing. Roberto Medina',)
])

cur.executemany("INSERT INTO materias (nombre, docente_id, grupo_id) VALUES (?, ?, ?)", [
    ('Matemáticas I', 1, 1),
    ('Historia II', 2, 1),
    ('Física I', 3, 2)
])

cur.executemany("INSERT INTO estudiantes (nombre, matricula, grupo_id) VALUES (?, ?, ?)", [
    ('Ana Gómez', '23301052820113', 1),
    ('Luis Morales', '23301052820114', 1),
    ('Carlos Ruiz', '23301052820115', 2),
    ('María Campos', '23301052820116', 2)
])

conn.commit()
conn.close()

print("✅ Base de datos corregida y lista.")

