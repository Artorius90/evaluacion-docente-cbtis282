import sqlite3

DB_FILE = "evaluaciones.db"

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# Listar tablas
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = cur.fetchall()
print("📋 Tablas en la base de datos:", [t[0] for t in tablas])

# Mostrar las primeras 5 filas de cada tabla
for tabla in [t[0] for t in tablas]:
    print(f"\n--- Contenido de la tabla '{tabla}' ---")
    cur.execute(f"SELECT * FROM {tabla} LIMIT 5;")
    filas = cur.fetchall()
    for fila in filas:
        print(fila)

conn.close()
