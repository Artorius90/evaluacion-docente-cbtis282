from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_super_segura_cbtis282'  # 🔐 Clave necesaria para sesiones y flash
DATABASE = "evaluaciones.db"

# --- Conexión a la base de datos ---
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Página principal ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Obtener grupo del estudiante por matrícula ---
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

# --- Obtener docentes del grupo ---
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

# --- Guardar evaluación ---
@app.route('/evaluacion')
def mostrar_formulario():
    return render_template('evaluacion.html')
@app.route('/evaluar', methods=['POST'])
def evaluar_docente():
    data = request.get_json()
    estudiante_nombre = data.get('estudiante_nombre')
    matricula = data.get('matricula')
    grupo_id = data.get('grupo_id')
    docente_id = data.get('docente_id')
    criterios = data.get('criterios')
    comentario = data.get('comentario', '')

    if not (estudiante_nombre and matricula and grupo_id and docente_id and criterios):
        return jsonify({"error": "Faltan datos"}), 400

    conn = get_db_connection()

    # Guardar estudiante si no existe
    cur = conn.execute("SELECT id FROM estudiantes WHERE matricula = ?", (matricula,))
    estudiante = cur.fetchone()
    if estudiante:
        estudiante_id = estudiante['id']
    else:
        cur = conn.execute(
            "INSERT INTO estudiantes (nombre, matricula, grupo_id) VALUES (?, ?, ?)",
            (estudiante_nombre, matricula, grupo_id)
        )
        estudiante_id = cur.lastrowid

    # Insertar evaluación
    for criterio, calificacion in criterios.items():
        conn.execute('''
            INSERT INTO evaluaciones (estudiante_id, docente_id, grupo_id, criterio, calificacion, comentario, fecha)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (estudiante_id, docente_id, grupo_id, criterio, calificacion, comentario, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Evaluación registrada con éxito"}), 201
# --- Panel de administrador ---
import pandas as pd
from flask import send_file

@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        password = request.form.get('password')
        # 🔑 Puedes cambiar aquí la contraseña
        if password == 'admin282':
            session['admin'] = True
            flash('Acceso concedido', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Contraseña incorrecta', 'error')
            return redirect(url_for('login_admin'))

    return render_template('login_admin.html')
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

# Exportar excel
@app.route('/exportar_excel')
def exportar_excel():
    import pandas as pd
    from flask import send_file

    conn = get_db_connection()

    # Consulta para calcular promedios por docente y grupo
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

    # Agregar interpretación textual del promedio
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

    # Consulta para comentarios
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

    # Guardar ambos en un solo archivo Excel (dos hojas)
    file_path = "reporte_docentes.xlsx"
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df_promedios.to_excel(writer, sheet_name='Promedios', index=False)
        df_comentarios.to_excel(writer, sheet_name='Comentarios', index=False)

    return send_file(file_path, as_attachment=True)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('login_admin'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)





