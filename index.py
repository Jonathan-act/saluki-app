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

@app.route('/log_cli', methods=['POST'])
def log_cli():
    if request.method == 'POST':
        email = request.form['email_cli']
        password = request.form['pass_cli']
        email = email.lower()
        cursor.execute(
            "select correo_clinica, nombre_clinica from clinica where correo_clinica= %s and contrasena_clinica=%s", (
                email, password)
        )
        user = cursor.fetchone()

        if user != None:
            if user[0] == email:
                session['correo_clinica'] = user[0]
                session['nombre_clinica'] = user[1]                              
                url = '/cli_inicio'
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

#RENDERS CLINICA----------------------------------------------------------------------------------------------------------------------------
@app.route('/cli_inicio')
def cli_inicio():
    ##total vacunas aplicadas
    cursor.execute(
        "select count(vacuna_consulta) from consulta where vacuna_consulta != ''"
    )
    vacunas_totales = cursor.fetchall()
    #vacuna más solicitada
    cursor.execute(
        "select vacuna_consulta, count(vacuna_consulta) as vacunas from consulta where  vacuna_consulta != '' group by vacuna_consulta order by vacunas desc limit 1"
    )
    vacuna_mas = cursor.fetchall()
    #menos solicitada
    cursor.execute(
        "select vacuna_consulta, count(vacuna_consulta) as vacunas from consulta where  vacuna_consulta != '' group by vacuna_consulta order by vacunas asc limit 1"
    )
    vacuna_menos = cursor.fetchall()
    #total cada vacuna
    cursor.execute(
        "select vacuna_consulta, count(vacuna_consulta) as vacunas from consulta where  vacuna_consulta != '' group by vacuna_consulta order by vacunas desc"
    )
    vacunas = cursor.fetchall()
    #==========================================================================================================================================
    #total vacunas aplicadas
    cursor.execute(
        "select count(operacion_consulta) from consulta where operacion_consulta != ''"
    )
    operaciones_totales = cursor.fetchall()
    #vacuna más solicitada
    cursor.execute(
        "select operacion_consulta, count(operacion_consulta) as vacunas from consulta where  operacion_consulta != '' group by operacion_consulta order by vacunas desc limit 1"
    )
    operacion_mas = cursor.fetchall()
    #menos solicitada
    cursor.execute(
        "select operacion_consulta, count(operacion_consulta) as vacunas from consulta where  operacion_consulta != '' group by operacion_consulta order by vacunas asc limit 1"
    )
    operacion_menos = cursor.fetchall()
    #total cada vacuna
    cursor.execute(
        "select operacion_consulta, count(operacion_consulta) as vacunas from consulta where  operacion_consulta != '' group by operacion_consulta order by vacunas desc"
    )
    operaciones = cursor.fetchall()

    #==========================================================================================================================================
    #ENFERMEDADES
    #más común
    cursor.execute(
        "select enfermedad_consulta, count(enfermedad_consulta) as vacunas from consulta where  enfermedad_consulta != '' group by enfermedad_consulta order by vacunas desc limit 1"
    )
    enfermedad_mas = cursor.fetchall()
    #menos común
    cursor.execute(
        "select enfermedad_consulta, count(enfermedad_consulta) as vacunas from consulta where  enfermedad_consulta != '' group by enfermedad_consulta order by vacunas asc limit 1"
    )
    enfermedad_menos = cursor.fetchall()
    #enfermedades
    cursor.execute(
        "select enfermedad_consulta, count(enfermedad_consulta) as vacunas from consulta where  enfermedad_consulta != '' group by enfermedad_consulta order by vacunas desc"
    )
    enfermedades = cursor.fetchall()

    #==========================================================================================================================================
    #ENFERMEDADES
    #más común
    cursor.execute(
        "select tratamiento_consulta, count(tratamiento_consulta) as vacunas from consulta where  tratamiento_consulta != '' group by tratamiento_consulta order by vacunas desc limit 1"
    )
    tratamiento_mas = cursor.fetchall()
    #menos común
    cursor.execute(
        "select tratamiento_consulta, count(tratamiento_consulta) as vacunas from consulta where  tratamiento_consulta != '' group by tratamiento_consulta order by vacunas asc limit 1"
    )
    tratamiento_menos = cursor.fetchall()
    #tratamientos
    cursor.execute(
        "select tratamiento_consulta, count(tratamiento_consulta) as vacunas from consulta where  tratamiento_consulta != '' group by tratamiento_consulta order by vacunas desc"
    )
    tratamientos = cursor.fetchall()

    return render_template('./clinica/cli_estadisticas.html', vacunas_totales=vacunas_totales[0], vacuna_mas = vacuna_mas[0], vacuna_menos = vacuna_menos[0], vacunas = vacunas, operaciones_totales = operaciones_totales[0], operacion_mas = operacion_mas[0], operacion_menos = operacion_menos[0], operaciones = operaciones, enfermedad_mas = enfermedad_mas[0], enfermedad_menos = enfermedad_menos[0], enfermedades = enfermedades, tratamiento_mas = tratamiento_mas[0], tratamiento_menos = tratamiento_menos[0], tratamientos = tratamientos)

@app.route('/cli_veterinarios')
def cli_veterinarios():
    clinica = 'clinica.ubb@saluki.cl'
    cursor.execute(
        "select * from veterinario where correo_clinica = '{0}'".format(clinica)
    )
    veterinarios = cursor.fetchall()
    vet_estadisticas = [{}]
    for veterinario in veterinarios:
        #consultas últimos 7 días
        cursor.execute(
            "select count(id_agenda) from agenda where correo_veterinario='{0}' and fecha_agenda between current_date-7 and current_date".format(
                veterinario[0])
        )
        a_semanal = cursor.fetchall()
        #consultas ultimos 30 días
        cursor.execute(
            "select count(id_agenda) from agenda where correo_veterinario='{0}' and fecha_agenda between current_date-30 and current_date".format(veterinario[0])
        )
        a_mensual = cursor.fetchall()
        #consultas totales
        cursor.execute(
            "select count(id_agenda) from agenda where correo_veterinario='{0}'".format(
                veterinario[0])
        )
        a_total = cursor.fetchall()

        estadisticas = [{
            "correo_veterinario" : veterinario[0],
            "a_semanales": a_semanal[0][0],
            "a_mensuales": a_mensual[0][0],
            "a_totales": a_total[0][0]
        }]
        vet_estadisticas.append(estadisticas)
    #especialidades
    cursor.execute(
        "select * from especialidad"
    )
    especialidades = cursor.fetchall()
    print(vet_estadisticas)
    return render_template('./clinica/cli_veterinarios.html', veterinarios = veterinarios, estadisticas = vet_estadisticas, especialidades = especialidades)

@app.route('/cli_registrar_vet')
def cli_registrar_vet():
    #especialidades
    cursor.execute(
        "select * from especialidad"
    )
    especialidades = cursor.fetchall()
    #ciudades
    cursor.execute(
        "select * from ciudad"
    )
    ciudades = cursor.fetchall()
    return render_template('./clinica/cli_registrar_vet.html', especialidades = especialidades, ciudades = ciudades)

@app.route('/cli_clientes')
def cli_clientes():
    cursor.execute(
        "select u.nombre_usuario, u.apellido_usuario, u.correo_usuario, u.telefono_usuario, count(u.correo_usuario) as consultas from consulta c, usuario u, mascota m where c.id_mascota=m.id_mascota and m.correo_usuario=u.correo_usuario group by u.correo_usuario order by consultas desc"
    )
    clientes = cursor.fetchall()
    return render_template('./clinica/cli_clientes.html', clientes = clientes)

@app.route('/cli_mascotas')
def cli_mascotas():
    cursor.execute(
        "select m.id_mascota, m.nombre_mascota, m.id_especie, m.fecha_nacimiento_mascota, m.caracter_mascota, m.correo_usuario, count(c.id_consulta) as consultas from mascota m, consulta c where m.id_mascota=c.id_mascota group by m.id_mascota"
    )
    mascotas = cursor.fetchall()
    return render_template('./clinica/cli_mascotas.html', mascotas=mascotas)

#RENDERS VETERINARIOS----------------------------------------------------------------------------------------------------------------------------
@app.route('/vet_agenda')
def vet_agenda():
    if 'correo_veterinario' in session:
        correo_veterinario = session['correo_veterinario']
    else:
        return redirect(url_for('inicio'))
    vet = correo_veterinario
    cursor.execute(
        "select * from agenda where correo_veterinario = '{0}' and fecha_agenda = current_date order by hora_agenda asc".format(
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
    #consultas totales
    cursor.execute(
        " select count(distinct fecha_consulta) from consulta where id_mascota = '{0}' ".format(id)
    )
    consultas_totales = cursor.fetchall()
    #especies
    cursor.execute(
        "select id_especie from especie"
    )
    especies = cursor.fetchall()
    #info mascota
    cursor.execute(
        "select nombre_mascota, id_especie, raza_mascota, id_mascota, (current_date - fecha_nacimiento_mascota)/365, caracter_mascota, fecha_nacimiento_mascota from mascota where id_mascota = {0}".format(
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
    #if info_consulta == []:
    #    info_consulta = []
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
    return render_template('./veterinario/vet_resumen.html', mascota=info_mascota[0], dueño=info_dueño[0], vacunas=vacunas, operaciones=operaciones, enfermedades=enfermedades, alergias=alergias, paciente=p_paciente[0], consultas_totales = consultas_totales[0], id = id, especies = especies)

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

@app.route('/historial_completo/<string:id>')
def historial_completo(id):
    if 'correo_veterinario' in session:
        correo_veterinario = session['correo_veterinario']
        usuario = False
    elif 'correo_usuario' in session:
        correo_veterinario = session['correo_usuario']
        usuario = True
    else:
        return redirect(url_for('inicio'))
    #mostrar porx paciente
    cursor.execute(
        " select nombre_agenda, nombre_mascota, hora_agenda from agenda where correo_veterinario='{0}' and fecha_agenda = current_date and hora_agenda > current_time limit 1 ".format(
            correo_veterinario)
    )
    p_paciente = cursor.fetchall()
    if p_paciente == []:
        p_paciente = [[(''), ('No hay más pacientes hoy'), ('')]]
    #mostrar todas las consultas
    cursor.execute(
        'select * from consulta where id_mascota = {0} order by fecha_consulta desc'.format(id)
    )
    consultas = cursor.fetchall()
    return render_template('./veterinario/historial_completo.html', consultas = consultas, mascota = consultas[0] ,paciente = p_paciente[0], usuario = usuario)

#RENDERS USUARIOS/DUEÑOS DE MASCOTAS--------------------------------------------------------------------------------------------------
@app.route('/usr_resumen/<string:id>')
def usr_resumen(id):
    if 'correo_usuario' in session:
        correo_usuario = session['correo_usuario']
        cursor.execute(
            "select 1 from mascota where id_mascota = '{0}' and correo_usuario = '{1}'".format(id, correo_usuario)
            )
        res = cursor.fetchall()
        print(res)
        if res == [(1,)]:
            #Listar mascotas
            cursor.execute(
                " select nombre_mascota, id_mascota from mascota where correo_usuario = '{0}' ".format(
                    correo_usuario)
            )
            mascotas = cursor.fetchall()

            #especies
            cursor.execute(
                "select id_especie from especie"
            )
            especies = cursor.fetchall()

            #info mascota
            cursor.execute(
                "select nombre_mascota, id_especie, raza_mascota, id_mascota, (current_date - fecha_nacimiento_mascota)/365, caracter_mascota, fecha_nacimiento_mascota from mascota where id_mascota = {0}".format(
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
            return render_template('./usuario/usr_resumen.html', mascotas=mascotas, mascota=info_mascota[0], dueño=info_dueño[0], vacunas=vacunas, operaciones=operaciones, enfermedades=enfermedades, alergias=alergias, especies=especies)
    else:
        #return redirect(url_for('inicio'))
        return 'Esta no es tu mascota amigo mio'

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

@app.route('/registrar_usuario', methods=['POST'])
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

#eliminar hora
@app.route('/eliminar_hrs/<string:id>')
def eliminar_hrs(id):
    cursor.execute(
        "delete from agenda where id_agenda = '{0}' ".format(id)
        )
    con.commit()
    return redirect('/vet_agenda')

#modificar hora
@app.route('/modificar_hrs', methods=['POST'])
def modificar_hrs():
    if 'correo_veterinario' in session:
        veterinario = session['correo_usuario']
    if request.method == 'POST':
        id = request.form['id']
        hora = request.form['hora']
        fecha = request.form['fecha']
    #verificar disponibilidad de hora
    cursor.execute(
        "select 1 from agenda where correo_veterinario = '{0}' and fecha_agenda = '{1}' and hora_agenda = '{2}' limit 1".format(
            veterinario, fecha, hora)
    )
    res = cursor.fetchall()
    print(res)
    if res == [(1,)]:
        message = "Hora no disponible, por favor selecciona otra."
        flash(message)
    else:
        #modificar hora
        cursor.execute(
            "update agenda set hora_Agenda = '{0}', fecha_agenda = '{1}' where id_agenda = '{2}'".format(hora, fecha, id)
            )
        con.commit()
        return redirect('/vet_agenda')

#actualizar registros
@app.route('/actualizar_registros', methods=['POST'])
def actualizar_registros():
    if request.method == 'POST':
        id = request.form['id']
        id_mascota = request.form['id_mascota']
        alergia = request.form['alergia']
        vacuna = request.form['vacuna']
        tratamiento = request.form['tratamiento']
        operacion = request.form['operacion']
        enfermedad = request.form['enfermedad']
        comentario = request.form['comentario']
    cursor.execute(
        "update consulta set comentario_consulta = '{1}', operacion_consulta = '{2}', vacuna_consulta = '{3}', alergia_consulta = '{4}', enfermedad_consulta = '{5}', tratamiento_consulta = '{6}' where id_consulta = '{0}'".format(
            id, comentario, operacion, vacuna, alergia, enfermedad, tratamiento)
    )
    con.commit()
    url = '/historial_completo/' + id_mascota
    return redirect(url)
    
#actualizar info mascota
@app.route('/actualizar_informacion_mascota', methods=['POST'])
def actualizar_informacion_mascota():
    if request.method == 'POST':
        id_mascota = request.form['id_mascota']
        caracter = request.form['caracter']
        nombre = request.form['nombre']
        raza = request.form['raza']
        especie = request.form['especie']
        fecha_nacimiento = request.form['fecha_nacimiento']
        usr = request.form['usr']
    print(id_mascota, caracter)
    cursor.execute(
        "update mascota set caracter_mascota = '{0}', nombre_mascota = '{2}', raza_mascota='{3}', fecha_nacimiento_mascota = '{4}', id_especie='{5}' where id_mascota = '{1}'".format(caracter, id_mascota, nombre, raza, fecha_nacimiento, especie)
    )
    con.commit()
    if usr == 'usr':
        url = '/usr_resumen/'+id_mascota
        return redirect(url)
    else:
        url = '/vet_resumen/'+id_mascota
        return redirect(url)
    
#registrar veterinario
@app.route('/registrar_vet', methods=['POST'])
def registrar_vet():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        especialidad = request.form['especialidad']
        telefono = request.form['telefono']
        ciudad = request.form['ciudad']
    correo_clinica = 'clinica.ubb@saluki.cl'
    cursor.execute(
        "insert into veterinario (correo_veterinario, id_especialidad, id_ciudad, nombre_veterinario, apellido_veterinario, contrasena_veterinario, telefono_veterinario, correo_clinica) values ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')".format(correo, especialidad, ciudad, nombre, apellido, contrasena, telefono, correo_clinica)
    )
    con.commit()
    return redirect('/cli_veterinarios')

@app.route('/eliminar_vet/<string:id>')
def eliminar_route(id):
    cursor.execute(
        "update veterinario set correo_clinica = '' where correo_veterinario = '{0}'".format(id)
    )
    con.commit()
    return redirect('/cli_veterinarios')

@app.route('/actualizar_vet', methods=['POST'])
def actualizar_vet():
    if request.method == 'POST':
        especialidad = request.form['especialidad']
        telefono = request.form['telefono']
        correo = request.form['correo']
    return 'hola que tal'

#tecnologias del proyecto
@app.route('/info')
def info():
    return render_template('info.html')

#error 404
@app.errorhandler(404)
def not_found(error):
    return render_template('not_found.html')
    
#BORRAR ANTES DEL MERGE A PRODUCCIÓN
if __name__ == '__main__':
    app.run(port=3000, debug=True)
