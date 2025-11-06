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

CREATE TABLE evaluaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grupo_id INTEGER,
    docente_id INTEGER,
    calificacion INTEGER,
    comentario TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (grupo_id) REFERENCES grupos(id),
    FOREIGN KEY (docente_id) REFERENCES docentes(id)
);
