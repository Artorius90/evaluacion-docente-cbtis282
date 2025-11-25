import sqlite3
import os

DB = 'evaluaciones.db'

# eliminar BD vieja si existe
if os.path.exists(DB):
    os.remove(DB)

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

-- ESTA ES LA TABLA CORRECTA PARA TU APLICACIÓN
CREATE TABLE evaluaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_nombre TEXT,
    matricula TEXT,
    grupo_id INTEGER,
    docente_id INTEGER,
    criterio TEXT,
    calificacion TEXT,
    comentario TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Datos de prueba opcionales
cur.executemany("INSERT INTO grupos (nombre) VALUES (?)", [
    ('Grupo A',),
    ('Grupo B',)
])

cur.executemany("INSERT INTO docentes (nombre) VALUES (?)", [
    ('Profesor Juan Pérez',),
    ('Profesora María López',)
])

cur.executemany("INSERT INTO materias (nombre, docente_id, grupo_id) VALUES (?, ?, ?)", [
    ('Matemáticas I', 1, 1),
    ('Historia II', 2, 1),
    ('Física I', 1, 2)
])

cur.executemany("INSERT INTO estudiantes (nombre, matricula, grupo_id) VALUES (?, ?, ?)", [
    ('Ana Gómez', 'A001', 1),
    ('Luis Morales', 'A002', 1),
    ('Carlos Ruiz', 'B001', 2),
    ('María Campos', 'B002', 2)
])

conn.commit()
conn.close()

print("✅ Base de datos creada correctamente con la estructura usada por la app.")
