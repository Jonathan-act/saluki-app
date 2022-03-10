from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import CSRFProtect
import psycopg2
import datetime

#Conexión a BD
try:
    con = psycopg2.connect(
        host= 'ec2-52-44-209-165.compute-1.amazonaws.com',
        port = '5432',
        user='aldejcokjdndqp',
        password='2e48b0b2ed59ccea7e90b725082e6f4bbc454ee364df66c465acb799a0a862c7',
        database='dcfcqu1l37rf0n',
        keepalives=1,
        keepalives_idle=1,
        keepalives_interval=1,
        keepalives_count=15
    )
    print('Conexión exitosa')
    cursor = con.cursor()
except Exception as ex:
    print(ex)

app = Flask(__name__)

app.secret_key = "mykeyfromsalukiapp"
csrf = CSRFProtect(app)


#LOG, LOGOUT----------------------------------------------------------------------------------------------------------------------------------
@app.route('/')
def inicio():
    return render_template('login.html')

@app.route('/log', methods=['POST'])
def log():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        email = email.lower()
        cursor.execute(
            "select v.correo_veterinario, v.nombre_veterinario, v.apellido_veterinario, e.nombre_especialidad from veterinario v, especialidad e where v.correo_veterinario= %s and v.contrasena_veterinario=%s and v.id_especialidad=e.id_especialidad", (email, password)
        )
        user = cursor.fetchone() 

        if user != None:
            if user[0] == email:
                print(user)
                session['correo_veterinario'] = user[0]
                session['nombre_veterinario'] = user[1] + ' ' + user[2]
                session['titulo_veterinario'] = user[3]
                print(user[3])
                return redirect(url_for('vet_agenda'))
            else:
                message = "Credenciales incorrectas o usuario no registrado"
                flash(message)
                return redirect('/')
        else:
            message = "Credenciales incorrectas o usuario no registrado"
            flash(message)
            return redirect('/')

@app.route('/log_usr', methods=['POST'])
def log_usr():
    if request.method == 'POST':
        email = request.form['email_usr']
        password = request.form['pass_usr']
        email = email.lower()
        cursor.execute(
            "select correo_usuario, nombre_usuario, apellido_usuario from usuario where correo_usuario= %s and contrasena_usuario=%s", (
                email, password)
        )
        user = cursor.fetchone()

        if user != None:
            if user[0] == email:
                session['correo_usuario'] = user[0]
                session['nombre_usuario'] = user[1] + ' ' + user[2]
                cursor.execute(
                    " select id_mascota from mascota where correo_usuario = '{0}' limit 1".format(
                        user[0])
                )
                mascota = cursor.fetchall()                
                url = '/usr_resumen/' + str(mascota[0][0])
                print(url)
                return redirect(url)
            else:
                message = "Credenciales incorrecta o usuario no registrado"
                flash(message)
                return redirect('/')
        else:
            message = "Credenciales incorrecta o usuario no registrado"
            flash(message)
            return redirect('/')

@app.route('/logout')
def logout():
    if 'correo_veterinario' in session:
        session.pop('correo_veterinario')
    return redirect(url_for('inicio'))


#RENDERS VETERINARIOS----------------------------------------------------------------------------------------------------------------------------
@app.route('/vet_agenda')
def vet_agenda():
    if 'correo_veterinario' in session:
        correo_veterinario = session['correo_veterinario']
    else:
        return redirect(url_for('inicio'))
    vet = correo_veterinario
    cursor.execute(
        "select * from agenda where correo_veterinario = '{0}' and fecha_agenda = current_date order by fecha_agenda desc".format(
            vet)
    )
    horas = cursor.fetchall()
    cursor.execute(
        " select nombre_agenda, nombre_mascota, hora_agenda from agenda where correo_veterinario='{0}' and fecha_agenda = current_date and hora_agenda > current_time limit 1 ".format(
            correo_veterinario)
    )
    p_paciente = cursor.fetchall()
    if p_paciente == []:
        p_paciente = [[(''), ('No hay más pacientes hoy'), ('')]]
    return render_template('./veterinario/vet_agenda.html', horas=horas, paciente=p_paciente[0])

@app.route('/vet_resumen/<string:id>')
def vet_resumen(id):
    if 'correo_veterinario' in session:
        correo_veterinario = session['correo_veterinario']
    else:
        return redirect(url_for('inicio'))
    #info mascota
    cursor.execute(
        "select nombre_mascota, id_especie, raza_mascota, id_mascota, (current_date - fecha_nacimiento_mascota)/365, caracter_mascota from mascota where id_mascota = {0}".format(
            id)
    )
    info_mascota = cursor.fetchall()
    #info dueño
    cursor.execute(
        " select u.nombre_usuario, u.apellido_usuario, u.telefono_usuario from usuario u, mascota m where m.id_mascota={0} and u.correo_usuario=m.correo_usuario".format(
            id)
    )
    info_dueño = cursor.fetchall()
    if info_dueño == []:
        info_dueño = [[('Dueño no'), ('registrado'), ('00000000')]]

    #info consultas
    cursor.execute(
        "select * from consulta where id_mascota = {0} ".format(id)
    )
    info_consulta = cursor.fetchall()
    if info_consulta == []:
        info_consulta = []
    vacunas = []
    operaciones = []
    alergias = []
    enfermedades = []
    for info in info_consulta:
        if info[5] != '':
            vacunas.append(info[5])
        if info[4] != '':
            operaciones.append(info[4])
        if info[6] != '':
            alergias.append(info[6])
        if info[7] != '':
            enfermedades.append(info[7])

    cursor.execute(
        " select nombre_agenda, nombre_mascota, hora_agenda from agenda where correo_veterinario='{0}' and fecha_agenda = current_date and hora_agenda > current_time limit 1 ".format(
            correo_veterinario)
    )
    p_paciente = cursor.fetchall()
    if p_paciente == []:
        p_paciente = [[(''), ('No hay más pacientes hoy'), ('')]]
    return render_template('./veterinario/vet_resumen.html', mascota=info_mascota[0], dueño=info_dueño[0], vacunas=vacunas, operaciones=operaciones, enfermedades=enfermedades, alergias=alergias, paciente=p_paciente[0])

@app.route('/vet_registrar_usuario')
def vet_registrar_usuario():
    if 'correo_veterinario' in session:
        correo_veterinario = session['correo_veterinario']
    else:
        return redirect(url_for('inicio'))
    cursor.execute("select id_ciudad, nombre_ciudad from ciudad")
    ciudades = cursor.fetchall()
    cursor.execute(
        " select nombre_agenda, nombre_mascota, hora_agenda from agenda where correo_veterinario='{0}' and fecha_agenda = current_date and hora_agenda > current_time limit 1 ".format(
            correo_veterinario)
    )
    p_paciente = cursor.fetchall()
    if p_paciente == []:
        p_paciente = [[(''), ('No hay más pacientes hoy'), ('')]]
    return render_template('./veterinario/vet_nuevo_usuario.html', ciudades=ciudades, paciente=p_paciente[0])

@app.route('/vet_registro_clinico/<string:id>')
def registro_clinico(id):
    if 'correo_veterinario' in session:
        correo_veterinario = session['correo_veterinario']
    else:
        return redirect(url_for('inicio'))
    cursor.execute(
        " select nombre_mascota, (current_date - fecha_nacimiento_mascota)/365, id_mascota, caracter_mascota from mascota where id_mascota = '{0}' ".format(
            id)
    )
    info_mascota = cursor.fetchall()

    #prox paciente
    cursor.execute(
        " select nombre_agenda, nombre_mascota, hora_agenda from agenda where correo_veterinario='{0}' and fecha_agenda = current_date and hora_agenda > current_time limit 1 ".format(
            correo_veterinario)
    )
    p_paciente = cursor.fetchall()
    if p_paciente == []:
        p_paciente = [[(''), ('No hay más pacientes hoy'), ('')]]
    return render_template('./veterinario/vet_registro_clinico.html', paciente=p_paciente[0], info=info_mascota[0])

@app.route('/vet_registro_mascota')
def registro_mascota():
    if 'correo_veterinario' in session:
        correo_veterinario = session['correo_veterinario']
    else:
        return redirect(url_for('inicio'))
    cursor.execute(
        "select id_especie from especie"
    )
    especies = cursor.fetchall()
    cursor.execute(
        " select nombre_agenda, nombre_mascota, hora_agenda from agenda where correo_veterinario='{0}' and fecha_agenda = current_date and hora_agenda > current_time limit 1 ".format(
            correo_veterinario)
    )
    p_paciente = cursor.fetchall()
    if p_paciente == []:
        p_paciente = [[(''), ('No hay más pacientes hoy'), ('')]]
    return render_template('./veterinario/vet_nueva_mascota.html', especies=especies, paciente=p_paciente[0])


#RENDERS USUARIOS/DUEÑOS DE MASCOTAS--------------------------------------------------------------------------------------------------
@app.route('/usr_resumen/<string:id>')
def usr_resumen(id):
    if 'correo_usuario' in session:
        correo_usuario = session['correo_usuario']
    else:
        return redirect(url_for('inicio'))

    #Listar mascotas
    cursor.execute(
        " select nombre_mascota, id_mascota from mascota where correo_usuario = '{0}' ".format(
            correo_usuario)
    )
    mascotas = cursor.fetchall()

    #info mascota
    cursor.execute(
        "select nombre_mascota, id_especie, raza_mascota, id_mascota, (current_date - fecha_nacimiento_mascota)/365, caracter_mascota from mascota where id_mascota = {0}".format(
            id)
    )
    info_mascota = cursor.fetchall()
    #info dueño
    cursor.execute(
        " select u.nombre_usuario, u.apellido_usuario, u.telefono_usuario from usuario u, mascota m where m.id_mascota={0} and u.correo_usuario=m.correo_usuario".format(
            id)
    )
    info_dueño = cursor.fetchall()
    if info_dueño == []:
        info_dueño = [[('Dueño no'), ('registrado'), ('00000000')]]

    #info consultas
    cursor.execute(
        "select * from consulta where id_mascota = {0} ".format(id)
    )
    info_consulta = cursor.fetchall()
    if info_consulta == []:
        info_consulta = []
    vacunas = []
    operaciones = []
    alergias = []
    enfermedades = []
    for info in info_consulta:
        if info[5] != '':
            vacunas.append(info[5])
        if info[4] != '':
            operaciones.append(info[4])
        if info[6] != '':
            alergias.append(info[6])
        if info[7] != '':
            enfermedades.append(info[7])
    print(enfermedades)
    return render_template('./usuario/usr_resumen.html', mascotas=mascotas, mascota=info_mascota[0], dueño=info_dueño[0], vacunas=vacunas, operaciones=operaciones, enfermedades=enfermedades, alergias=alergias)

@app.route('/usr_registro_mascota')
def usr_registro_mascota():
    if 'correo_usuario' in session:
        correo_usuario = session['correo_usuario']
    else:
        return redirect(url_for('inicio'))

    #Listar mascotas
    cursor.execute(
        " select nombre_mascota, id_mascota from mascota where correo_usuario = '{0}' ".format(
            correo_usuario)
    )
    mascotas = cursor.fetchall()

    cursor.execute(
        "select id_especie from especie"
    )
    especies = cursor.fetchall()
    return render_template('./usuario/usr_nueva_mascota.html', especies=especies, mascotas=mascotas, usr=correo_usuario)

@app.route('/agendar_hora')
def agendar_hora():
    if 'correo_usuario' in session:
        correo_usuario = session['correo_usuario']
    else:
        return redirect(url_for('inicio'))

    #listar veterinarios
    cursor.execute(
        'select v.nombre_veterinario, v.apellido_veterinario, e.nombre_especialidad, v.correo_veterinario from veterinario v, especialidad e where v.id_especialidad = e.id_especialidad'
    )
    veterinarios = cursor.fetchall()

    #Listar mascotas
    cursor.execute(
        " select nombre_mascota, id_mascota from mascota where correo_usuario = '{0}' ".format(
            correo_usuario)
    )
    mascotas = cursor.fetchall()
    return render_template('./usuario/usr_solicitar_hora.html', mascotas = mascotas, veterinarios = veterinarios)

@app.route('/usr_registro_clinico/<string:id>')
def usr_registro_clinico(id):
    if 'correo_usuario' in session:
        correo_usuario = session['correo_usuario']
    else:
        return redirect(url_for('inicio'))

    #Listar mascotas
    cursor.execute(
        " select nombre_mascota, id_mascota from mascota where correo_usuario = '{0}' ".format(
            correo_usuario)
    )
    mascotas = cursor.fetchall()

    #Info mascota
    cursor.execute(
        " select nombre_mascota, (current_date - fecha_nacimiento_mascota)/365, id_mascota, caracter_mascota from mascota where id_mascota = '{0}' ".format(
            id)
    )
    info_mascota = cursor.fetchall()

    return render_template('./usuario/usr_registro_clinico.html', mascotas = mascotas, info = info_mascota[0])


#FUNCIONES----------------------------------------------------------------------------------------------------------------------------
@app.route('/buscar_mascota', methods=['POST'])
def buscar_mascota():
    if request.method == 'POST':
        id_mascota = request.form['id_mascota']
        cursor.execute(
            " select true from mascota where id_mascota = {0} ".format(
                id_mascota)
        )
        res = cursor.fetchall()
        if res == [(True,)]:
            url = '/vet_resumen/' + id_mascota
            return redirect(url)
        else:
            success_message = "Mascota no registrada"
            flash(success_message)
            return redirect('/vet_agenda')

@app.route('/registrar_usuario', methods=["POST"])
def registrar_usuario():
    if request.method == "POST":
        correo_usuario = request.form['email']
        nombre_usuario = request.form['nombre']
        apellido_usuario = request.form['apellido']
        telefono_usuario = request.form['telefono']
        ciudad_usuario = request.form['ciudad']
        contraseña_usuario = request.form['pass']
    correo_usuario = correo_usuario.lower()
    cursor.execute(
        " select true from usuario where correo_usuario = '{0}' ".format(
            correo_usuario)
    )
    usuario = cursor.fetchall()
    if usuario == [(True,)]:
        message = "Este correo electronico esta en uso, por favor ingrese otro."
        flash(message)
        cursor.execute("select id_ciudad, nombre_ciudad from ciudad")
        ciudades = cursor.fetchall()
        return render_template('./veterinario/vet_nuevo_usuario.html', ciudades=ciudades, nombre=nombre_usuario, apellido=apellido_usuario, telefono=telefono_usuario, pas=contraseña_usuario)
    else:
        cursor.execute(
            "insert into usuario values (%s, %s, %s, %s, %s, %s)", (correo_usuario, ciudad_usuario,
                                                                    nombre_usuario, apellido_usuario, contraseña_usuario, telefono_usuario)
        )
        con.commit()
        return redirect(url_for('vet_agenda'))

@app.route('/registrar_mascota', methods=['POST'])
def registrar_mascota_vet():
    if request.method == 'POST':
        id_mascota = request.form['id_mascota']
        correo_usuario = request.form['correo_usuario']
        nombre_mascota = request.form['nombre_mascota']
        caracter_mascota = request.form['caracter_mascota']
        fecha_nacimiento = request.form['fecha_nacimiento']
        especie_mascota = request.form['especie_mascota']
        raza_mascota = request.form['raza_mascota']
    correo_usuario = correo_usuario.lower()
    cursor.execute(
        " select 1 from mascota where id_mascota = {0} ".format(id_mascota)
    )
    mascota = cursor.fetchall()
    if mascota == [(1,)]:
        message = "La ID ingresada ya esta en uso, por favor ingrese una distinta"
        flash(message)
        cursor.execute(
            "select id_especie from especie"
        )
        especies = cursor.fetchall()
        return render_template('./veterinario/vet_nueva_mascota.html', correo=correo_usuario, nombre=nombre_mascota, caracter=caracter_mascota, raza=raza_mascota, fecha=fecha_nacimiento, especies=especies)
    else:
        cursor.execute(
            "insert into mascota values (%s, %s, %s, %s, %s, %s, %s)", (id_mascota, especie_mascota,
                                                                        correo_usuario, nombre_mascota, fecha_nacimiento, raza_mascota, caracter_mascota)
        )
        con.commit()
        return redirect('vet_resumen/{0}'.format(id_mascota))

@app.route('/registrar_mascota_usr', methods=['POST'])
def registrar_mascota_usr():
    if request.method == 'POST':
        id_mascota = request.form['id_mascota']
        correo_usuario = request.form['correo_usuario']
        nombre_mascota = request.form['nombre_mascota']
        caracter_mascota = request.form['caracter_mascota']
        fecha_nacimiento = request.form['fecha_nacimiento']
        especie_mascota = request.form['especie_mascota']
        raza_mascota = request.form['raza_mascota']
    correo_usuario = correo_usuario.lower()
    cursor.execute(
        " select 1 from mascota where id_mascota = {0} ".format(id_mascota)
    )
    mascota = cursor.fetchall()
    if mascota == [(1,)]:
        message = "La ID ingresada ya esta en uso, por favor ingrese una distinta"
        flash(message)
        cursor.execute(
            "select id_especie from especie"
        )
        especies = cursor.fetchall()
        return render_template('./usuario/usr_nueva_mascota.html', correo=correo_usuario, nombre=nombre_mascota, caracter=caracter_mascota, raza=raza_mascota, fecha=fecha_nacimiento, especies=especies)
    else:
        cursor.execute(
            "insert into mascota values (%s, %s, %s, %s, %s, %s, %s)", (id_mascota, especie_mascota,
                                                                        correo_usuario, nombre_mascota, fecha_nacimiento, raza_mascota, caracter_mascota)
        )
        con.commit()
        return redirect('usr_resumen/{0}'.format(id_mascota))

@app.route('/agregar_registro', methods=['POST'])
def agregar_registro():
    if request.method == 'POST':
        id = request.form['id_mascota']
        alergia = request.form['alergia']
        vacuna = request.form['vacuna']
        operacion = request.form['operacion']
        enfermedad = request.form['enfermedad']
        tratamiento = request.form['tratamiento']
        comentario = request.form['comentario']
        fecha = datetime.date.today()

    cursor.execute(
        "insert into consulta (id_mascota, fecha_consulta, operacion_consulta, vacuna_consulta, alergia_consulta, enfermedad_consulta, tratamiento_consulta, comentario_consulta) values ( %s, %s, %s, %s, %s, %s, %s, %s)", (
            id, fecha, operacion, vacuna, alergia, enfermedad, tratamiento, comentario)
    )
    con.commit()
    url = "/vet_resumen/"+id
    return redirect(url)

@app.route('/usr_agregar_registro', methods=['POST'])
def usr_agregar_registro():
    if request.method == 'POST':
        id = request.form['id_mascota']
        alergia = request.form['alergia']
        vacuna = request.form['vacuna']
        operacion = request.form['operacion']
        enfermedad = request.form['enfermedad']
        tratamiento = request.form['tratamiento']
        comentario = request.form['comentario']
        fecha = datetime.date.today()

    cursor.execute(
        "insert into consulta (id_mascota, fecha_consulta, operacion_consulta, vacuna_consulta, alergia_consulta, enfermedad_consulta, tratamiento_consulta, comentario_consulta) values ( %s, %s, %s, %s, %s, %s, %s, %s)", (
            id, fecha, operacion, vacuna, alergia, enfermedad, tratamiento, comentario)
    )
    con.commit()
    url = "/usr_resumen/"+id
    return redirect(url)

#agendar hora
@app.route('/hrs_disponibles', methods=['POST'])
def hrs_disponibles():
    if 'correo_usuario' in session:
        correo_usuario = session['correo_usuario']
    else:
        return redirect(url_for('inicio'))
    if request.method == 'POST':
        veterinario = request.form['veterinario']
        fecha = request.form['fecha']
        hora = request.form['hora']
        dueno = request.form['dueno']
        telefono = request.form['telefono']
        mascota = request.form['mascota']
        caracter = request.form['caracter']
    print(veterinario, fecha, hora, dueno, telefono, mascota, caracter)

    #verificar disponibilidad de hora
    cursor.execute(
        """select 1 from agenda where correo_veterinario = '{0}' and fecha_agenda = '{1}' and hora_agenda = '{2}' limit 1;""".format(veterinario, fecha, hora)
    )
    res = cursor.fetchall()
    print(res)
    if res == [(1,)]:
        message = "Hora no disponible, por favor selecciona otra."
        flash(message)
        #listar veterinarios
        cursor.execute(
            'select v.nombre_veterinario, v.apellido_veterinario, e.nombre_especialidad, v.correo_veterinario from veterinario v, especialidad e where v.id_especialidad = e.id_especialidad'
        )
        veterinarios = cursor.fetchall()

        #Listar mascotas
        cursor.execute(
            " select nombre_mascota, id_mascota from mascota where correo_usuario = '{0}' ".format(
                correo_usuario)
        )
        mascotas = cursor.fetchall()
        return render_template('./usuario/usr_solicitar_hora.html', mascotas=mascotas, veterinarios=veterinarios, dueno = dueno, telefono = telefono, mascota = mascota,  caracter = caracter)

    else:
        cursor.execute(
            'insert into agenda (correo_veterinario, fecha_agenda, hora_agenda, nombre_agenda, telefono_agenda, nombre_mascota, caracter_agenda) values (%s, %s, %s, %s, %s, %s, %s)', (
                veterinario, fecha, hora, dueno, telefono, mascota, caracter)
        )
        con.commit()
        message = "Listo! tu hora  esta agendada."
        flash(message)
    return redirect('/agendar_hora')

@app.route('/info')
def info():
    return render_template('info.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('not_found.html')
    
