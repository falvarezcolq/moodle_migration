from email import message
import lib.moodle_api as moodle
# user = moodle_api.User(username="miusuario")
# user.get_with_courses()


import os
from colorama import Fore, Style
# from encuesta_db.dbpostgresql import DBPostgresql
from lib.db import DB
from flask import Flask, jsonify, request,render_template,redirect
from flask_cors import CORS
import json


app = Flask(__name__)
#api=Api(app)
CORS(app)

# print(Fore.RED+"HOLA MUNDO  en ROJO")
# print(Style.RESET_ALL)


users=[]
user_dict={}

@app.route("/", methods=['GET'])
def index():
    data = request.args
    # print(data)
    # if 'type' in data:
    #     type = data['type']
    #     print(type)
    #     if type == 'failure':
    #         return render_template('home.html',failure=True)

    return render_template('home.html',failure=False)

@app.route('/revisar/', methods = ['GET'])
def get_review():
    gestion='ADMEMP20221'
    db = DB('administracion')    
    data = db.query_get_students(gestion)
    users=[]
   
    for item in data:
        dbuser=item[0]
        users.append(moodle.User(
            username=dbuser["id_estudiante"], 
            password=dbuser["dip"], 
            firstname =dbuser["firstname"],
            lastname =dbuser["lastname"], 
            email = dbuser["correo"], 
            materias = dbuser["materias"]
        ))
       

    # courses ={ "-A-I-2022": 885, "-B-I-2022": 884, }
    courses ={ "-A-I-2022": 7, "-B-I-2022": 6, }
    moodle_courses = moodle.CourseList()
    
    for c in moodle_courses:
        courses[c.shortname]=c.id

    i = 0
    
    for user in users:
        i=i+1
        print(i)
        if user.get_moodle_user():
            user.get_courses_from_moodle()
            user.update_courses(courses)
        else:
            print("usuario que no existe ")
            user.create()
            user.get_courses_from_moodle()
            user.update_courses(courses)
    
    return jsonify(courses)


@app.route('/estudiantes/', methods = ['GET'])
def get_students():

    courses={ "-A-I-2022": 7, "-B-I-2022": 6, }
    moodle_courses = moodle.CourseList()
    for c in moodle_courses:
        courses[c.shortname]=c.id

    gestion='ADMEMP20221'
    db = DB('administracion')    
    data = db.query_get_students(gestion)
    
    users=[]
    for item in data:
        dbuser=item[0]
        users.append(moodle.User(
            username=dbuser["id_estudiante"], 
            password=dbuser["dip"], 
            firstname =dbuser["firstname"],
            lastname =dbuser["lastname"], 
            email = dbuser["correo"], 
            materias = dbuser["materias"]
        ))
    message = ""
    init = 3000
    end= init + 1000 if init+1000  < len(users) else  len(users) 
    i = init
    contador = 0
    
    for user in users[init:end]:
        i=i+1
        print(i)
        if user.get_moodle_user():
            user.get_courses_from_moodle()
            m = user.update_courses(courses)
            if m != "":
                contador = contador + 1
                message = message + "\n" + str(i) + m
        else:
            print("Usuario nuevo ")
            user.create()   
            # user.get_courses_from_moodle()
            m = user.update_courses(courses)
            if m != "":
                contador = contador + 1
                message = message + "\n" + str(i) 
                message = message + "\nUsuario nuevo"
                message = message + m
    message = "Usuarios actualizados: " +str(contador)+ "\n" + message

    return render_template('student_report.html', message=message)




@app.route('/migrarestudiante/', methods = ['GET','POST'])
def migrate_students():
    message=""

    if request.method == 'POST':
        print("===========post======================")
        courses={ "-A-I-2022": 7, "-B-I-2022": 6, }
        moodle_courses = moodle.CourseList()
        for c in moodle_courses:
            courses[c.shortname]=c.id

        gestion='ADMEMP20221'
        db = DB('administracion') 
        ci=request.form['ci']  
        data = db.query_get_student_by_ci(gestion,ci)
        # for item in data:
        if len(data)>0:
            dbuser=data[0][0]
            user = moodle.User(
                username=dbuser["id_estudiante"], 
                password=dbuser["dip"], 
                firstname =dbuser["firstname"],
                lastname =dbuser["lastname"], 
                email = dbuser["correo"], 
                materias = dbuser["materias"]
            )
            if user.get_moodle_user():
                user.get_courses_from_moodle()
                m = user.update_courses(courses,mostrar=True)
                message = message + "\n" + m
            else:
                user.create()   
                m = user.update_courses(courses,mostrar=True)
                message = m
        else:
            message ="Estudiante no encontrado"

    return render_template('migrar_estudiante.html',message=message)

    


# @app.route('/estudiante/', methods = ['POST'])
# def get_estudiante():
#     cip=request.form['ci']
#     ru =request.form['ru']
#     gestion='ADMEMP20213'
#     datodb = DBPostgresql2('administracion')    
#     datodb1 = datodb.query_estudiante(cip, ru, gestion)
#     return jsonify(datodb1)

# @app.route('/guardar_evaluacion', methods = ['POST'])
# def post_guardar_evaluacion():
#     print("***********json************")
#     print(request.json)
#     print("***********form************")
#     print(request.form)
#     data = { "message":"se ha recibido con'exito"}
#     return jsonify(data)

#     # id_estudiante = request.form['id_estudiante']
#     # id_paralelo = request.form['id_paralelo']
#     # id_evaluacion = id_paralelo+"-"+id_estudiante
#     # datodb = DBPostgresql3('administracionx')   

#     # if datodb.existe_registro(id_evaluacion):
#     #     data = { "message":"La Materia ya fue evaluada"}
#     #     return jsonify(data)
#     # else:
#     #     datodb.save_test(id_evaluacion, request.form)
#         #     data = { "message":"Su evaluacion de la materia ya fue registrada exitosamente. ¡Gracias!"}
#         #     return jsonify(data)


# @app.route('/evaluador/', methods = ['POST'])
# def post_evaluador():
#     ci = request.form['ci']
#     gestion='ADMEMP20213'
#     datodb = DBPostgresql2('administracion')    
#     datodb1 = datodb.query(ci, gestion)
#     print(datodb1)
#     print(type(datodb1))
#     if len(datodb1) == 0:
#         return redirect('/?type=failure')

#     materias = [ x[0] for x in datodb1]
#     first = materias[0]
#     # full_name = first['nombres'] +" "+ first['paterno'] +" "+ first['materno']

#     materias_json = []
#     for x in materias:
#         data = {
#             "code":str_encrypt( json.dumps(x)),
#             "name":x['materia'],
#             "sigla":x['sigla']
#         }
#         materias_json.append(data)

#     return render_template('evaluador.html',lista=materias_json)
    

# @app.route('/formulario/', methods = ['GET'])
# def formulario():
#     data = request.args
#     if 'type' in data:
#         encrypt = data['type']
#         try:
#             materia_json = str_decrypt(encrypt) 
#             materia = json.loads(materia_json)
#             id_evaluacion = materia["id_paralelo"] +"-"+materia["id_estudiante"]
#             datodb = DBPostgresql3('administracionx')   

#             if datodb.existe_registro(id_evaluacion):
#                 return render_template("materiaevaluada.html",materia=materia)
            
#             return render_template("formulario.html",materia=materia,code=encrypt)
#         except:
#             return redirect('/')
#     return redirect('/') 


# @app.route('/save/<code>', methods = ['POST'])
# def save(code): 
#     # try:
#     materia_json = str_decrypt(code) 
#     materia = json.loads(materia_json)
#     id_evaluacion = materia["id_paralelo"] +"-"+ materia["id_estudiante"]
#     datodb = DBPostgresql3('administracionx')   

#     if datodb.existe_registro(id_evaluacion):
#         return render_template("materiaevaluada.html",materia=materia)
    
#     data=request.form
#     print(data)
#     values = [materia['id_estudiante'],
#                 materia['id_paralelo'],
#                 materia['id_materia'],
#                 materia["id_inscripcion"],
#                 materia['ci']]
#     miarray = [id_evaluacion] +  values + [ x[1] for x in data.items()] 
#     print(miarray)
#     print(len(miarray))
#     datodb.save_form(miarray )
#     return render_template("materia_form_success.html",materia=materia)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5010", debug=True)
