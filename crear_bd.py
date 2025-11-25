import sqlite3
import os

DB = 'evaluaciones.db'

# eliminar BD vieja si existe (opcional)
if os.path.exists(DB):
    os.remove(DB)

conn = sqlite3.connect(DB)
cur = conn.cursor()

# tablas
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

-- criterios se guardan como texto (JSON)
CREATE TABLE evaluaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_id INTEGER,
    docente_id INTEGER,
    grupo_id INTEGER,
    criterios TEXT NOT NULL,
    comentarios TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
    FOREIGN KEY (docente_id) REFERENCES docentes(id),
    FOREIGN KEY (grupo_id) REFERENCES grupos(id)
);
""")

# datos de ejemplo
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

# estudiantes ejemplo (matrícula opcional)
cur.executemany("INSERT INTO estudiantes (nombre, matricula, grupo_id) VALUES (?, ?, ?)", [
    ('Ana Gómez', 'A001', 1),
    ('Luis Morales', 'A002', 1),
    ('Carlos Ruiz', 'B001', 2),
    ('María Campos', 'B002', 2)
])

conn.commit()
conn.close()

print("✅ Base de datos creada y lista con datos de prueba.")

