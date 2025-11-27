import sqlite3
import pandas as pd
import os

print("🔍 Iniciando importación...")  # ← Esta línea sirve para comprobar que el script se ejecuta

EXCEL_FILE = "datos_evaluacion.xlsx"
DB_FILE = "evaluaciones.db"

if not os.path.exists(EXCEL_FILE):
    print(f"❌ No se encontró el archivo {EXCEL_FILE}. Colócalo en la carpeta del proyecto.")
    exit()

if not os.path.exists(DB_FILE):
    print(f"❌ No se encontró el archivo {DB_FILE}. Crea primero la base de datos con crear_bd.py")
    exit()

conn = sqlite3.connect(DB_FILE)

hojas_tablas = {
    "Grupos": "grupos",
    "Docentes": "docentes",
    "Materias": "materias",
    "Estudiantes": "estudiantes",
}

for hoja, tabla in hojas_tablas.items():
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=hoja, dtype=str)
        if not df.empty:
            df = df.dropna(how="all")
            df.to_sql(tabla, conn, if_exists="replace", index=False)
            print(f"✅ Hoja '{hoja}' importada correctamente en tabla '{tabla}'.")
        else:
            print(f"⚠️ Hoja '{hoja}' está vacía, se omitió.")
    except ValueError:
        print(f"⚠️ No se encontró la hoja '{hoja}' en el Excel, se omitió.")
    except Exception as e:
        print(f"❌ Error al importar '{hoja}': {e}")

conn.close()
print("🎉 Importación completa.")

