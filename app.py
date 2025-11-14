from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_file
import sqlite3
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_super_segura_cbtis282'
DATABASE = "evaluaciones.db"

# ----------------------------------------------------
# 🔹 Función para conectar a la base de datos
# ----------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ----------------------------------------------------
# 🔹 Página principal
# ----------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

# ----------------------------------------------------
# 🔹 Obtener grupo del estudiante por matrícula
# ----------------------------------------------------
@app.route('/grupo_estudiante/<matricula>', methods=['GET'])
def obtener_grupo_estudiante(matricula):
    conn = get_db_connection()
    query = '''
        SELECT g.id, g.nombre
        FROM estudiantes e
        JOIN grupos g ON e.grupo_id = g.id
        WHERE e.matricula = ?
    '''
    grupo = conn.execute(query, (matricula,)).fetchone()
    conn.close()

    if grupo:
        return jsonify(dict(grupo))
    else:
        return jsonify({"error": "No se encontró estudiante"}), 404

# ----------------------------------------------------
# 🔹 Obtener docentes del grupo
# ----------------------------------------------------
@app.route('/docentes/<int:grupo_id>', methods=['GET'])
def obtener_docentes_por_grupo(grupo_id):
    conn = get_db_connection()
    query = '''
        SELECT DISTINCT d.id, d.nombre
        FROM docentes d
        JOIN materias m ON d.id = m.docente_id
        WHERE m.grupo_id = ?
    '''
    docentes = conn.execute(query, (grupo_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in docentes])

# ----------------------------------------------------
# 🔹 Mostrar formulario de evaluación
# ----------------------------------------------------
@app.route('/evaluacion')
def mostrar_formulario():
    return render_template('evaluacion.html')

# ----------------------------------------------------
# 🔹 Guardar evaluación (evita duplicados)
# ----------------------------------------------------
@app.route("/evaluar", methods=["POST"])
def evaluar():
    data = request.get_json()

    matricula = data.get("matricula")
    docente_id = data.get("docente_id")
    grupo_id = data.get("grupo_id")
    criterios = data.get("criterios")
    comentario = data.get("comentario", "")
    estudiante_nombre = data.get("estudiante_nombre")

    # 🚫 Lista de palabras prohibidas
    palabras_prohibidas = [
        "pendejo", "culero", "mamona", "mamón", "idiota", "estúpido", "imbécil",
        "puto", "puta", "mierda", "cabrón", "chingada", "chingar", "verga"
    ]
    comentario_limpio = comentario.lower()
    if any(p in comentario_limpio for p in palabras_prohibidas):
        return jsonify({
            "status": "error",
            "mensaje": "Tu comentario contiene lenguaje inapropiado. Por favor modifícalo antes de enviarlo."
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Verificar si el estudiante ya evaluó (sin importar al docente)
    cursor.execute("""
        SELECT COUNT(*) FROM evaluaciones
        WHERE matricula = ?
    """, (matricula,))
    ya_evaluado = cursor.fetchone()[0] > 0

    if ya_evaluado:
        conn.close()
        return jsonify({
            "status": "error",
            "mensaje": "Ya enviaste tus evaluaciones anteriormente. Solo se permite una participación por estudiante."
        }), 400

    # ✅ Guardar cada criterio
    for criterio, calificacion in criterios.items():
        cursor.execute("""
            INSERT INTO evaluaciones (estudiante_nombre, matricula, grupo_id, docente_id, criterio, calificacion, comentario)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (estudiante_nombre, matricula, grupo_id, docente_id, criterio, calificacion, comentario))

    conn.commit()
    conn.close()

    return jsonify({"status": "success", "mensaje": "Evaluación guardada exitosamente."})


@app.route("/verificar_evaluacion", methods=["POST"])
def verificar_evaluacion():
    data = request.get_json()
    matricula = data.get("matricula")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM evaluaciones WHERE matricula = ?", (matricula,))
        ya_evaluado = cursor.fetchone()[0] > 0
        conn.close()

        return jsonify({"ya_evaluado": ya_evaluado})
    except Exception as e:
        print("❌ Error al verificar evaluación:", e)
        return jsonify({"error": "Error interno del servidor"}), 500

# ----------------------------------------------------
# 🔹 Login del administrador
# ----------------------------------------------------
@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin282':
            session['admin'] = True
            flash('Acceso concedido', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Contraseña incorrecta', 'error')
            return redirect(url_for('login_admin'))

    return render_template('login_admin.html')

# ----------------------------------------------------
# 🔹 Panel del administrador
# ----------------------------------------------------
@app.route('/admin')
def admin_panel():
    if not session.get('admin'):
        flash('Debes iniciar sesión para acceder al panel.', 'error')
        return redirect(url_for('login_admin'))

    conn = get_db_connection()

    resultados = conn.execute('''
        SELECT g.nombre AS grupo, d.nombre AS docente, 
               AVG(
                   CASE 
                       WHEN e.calificacion = 'Muy bueno' THEN 5
                       WHEN e.calificacion = 'Bueno' THEN 4
                       WHEN e.calificacion = 'Regular' THEN 3
                       WHEN e.calificacion = 'Malo' THEN 2
                       WHEN e.calificacion = 'Muy malo' THEN 1
                   END
               ) AS promedio
        FROM evaluaciones e
        JOIN grupos g ON e.grupo_id = g.id
        JOIN docentes d ON e.docente_id = d.id
        GROUP BY g.id, d.id
    ''').fetchall()

    comentarios = conn.execute('''
        SELECT DISTINCT d.nombre AS docente, g.nombre AS grupo, e.comentario
        FROM evaluaciones e
        JOIN grupos g ON e.grupo_id = g.id
        JOIN docentes d ON e.docente_id = d.id
        WHERE e.comentario IS NOT NULL AND TRIM(e.comentario) != ''
        ORDER BY d.nombre
    ''').fetchall()

    grupos = conn.execute("SELECT nombre FROM grupos ORDER BY nombre").fetchall()
    docentes = conn.execute("SELECT nombre FROM docentes ORDER BY nombre").fetchall()

    conn.close()

    return render_template('admin.html', resultados=resultados, comentarios=comentarios, grupos=grupos, docentes=docentes)

# ----------------------------------------------------
# 🔹 Exportar a Excel
# ----------------------------------------------------
@app.route('/exportar_excel')
def exportar_excel():
    conn = get_db_connection()

    query = '''
        SELECT 
            g.nombre AS Grupo,
            d.nombre AS Docente,
            ROUND(AVG(
                CASE 
                    WHEN e.calificacion = 'Muy bueno' THEN 5
                    WHEN e.calificacion = 'Bueno' THEN 4
                    WHEN e.calificacion = 'Regular' THEN 3
                    WHEN e.calificacion = 'Malo' THEN 2
                    WHEN e.calificacion = 'Muy malo' THEN 1
                END
            ), 2) AS Promedio
        FROM evaluaciones e
        JOIN grupos g ON e.grupo_id = g.id
        JOIN docentes d ON e.docente_id = d.id
        GROUP BY g.nombre, d.nombre
        ORDER BY g.nombre, d.nombre
    '''
    df_promedios = pd.read_sql_query(query, conn)

    def interpretar_promedio(valor):
        if valor >= 4.5:
            return "Muy bueno"
        elif valor >= 3.5:
            return "Bueno"
        elif valor >= 2.5:
            return "Regular"
        elif valor >= 1.5:
            return "Malo"
        else:
            return "Muy malo"

    df_promedios["Interpretación"] = df_promedios["Promedio"].apply(interpretar_promedio)

    query_comentarios = '''
        SELECT 
            g.nombre AS Grupo,
            d.nombre AS Docente,
            e.comentario AS Comentario
        FROM evaluaciones e
        JOIN grupos g ON e.grupo_id = g.id
        JOIN docentes d ON e.docente_id = d.id
        WHERE e.comentario IS NOT NULL AND TRIM(e.comentario) != ''
        ORDER BY g.nombre, d.nombre
    '''
    df_comentarios = pd.read_sql_query(query_comentarios, conn)
    conn.close()

    file_path = "reporte_docentes.xlsx"
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df_promedios.to_excel(writer, sheet_name='Promedios', index=False)
        df_comentarios.to_excel(writer, sheet_name='Comentarios', index=False)

    return send_file(file_path, as_attachment=True)
# ----------------------------------------------------
# 🔹 Reporte: Estudiantes que ya realizaron la evaluación
# ----------------------------------------------------
@app.route("/reporte_evaluaciones")
def reporte_evaluaciones():
    if not session.get('admin'):
        flash('Debes iniciar sesión para acceder al reporte.', 'error')
        return redirect(url_for('login_admin'))

    conn = get_db_connection()

    # Obtener los estudiantes que ya evaluaron al menos un docente
    query = """
        SELECT DISTINCT e.matricula, e.estudiante_nombre, g.nombre AS grupo
        FROM evaluaciones e
        JOIN grupos g ON e.grupo_id = g.id
        ORDER BY g.nombre, e.estudiante_nombre
    """
    datos = conn.execute(query).fetchall()
    conn.close()

    return render_template("reporte_evaluaciones.html", datos=datos)

@app.route("/borrar_todo", methods=["POST"])
def borrar_todo():
    # Verificar que el admin esté en sesión
    if "admin" not in session:
        return redirect(url_for("login_admin"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM evaluaciones")
    conn.commit()
    conn.close()

    flash("Todas las evaluaciones fueron eliminadas.", "info")
    return redirect(url_for("admin_panel"))

# ----------------------------------------------------
# 🔹 Logout administrador
# ----------------------------------------------------
@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('login_admin'))
    # Verificar que el admin esté en sesión
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM evaluaciones")
    conn.commit()
    conn.close()

    return redirect(url_for("admin"))
# ----------------------------------------------------
# 🔹 Ejecución
# ----------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
