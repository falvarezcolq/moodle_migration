import psycopg2
#from psycopg2.extras import Json
#from psycopg2.extras import to_json
import json
import re

class DB:

    def __init__(self, dbadm):
       
        self._connect = psycopg2.connect(
            host='', 
            database='',
            user='', 
            password='',
            port="",
        )
        self._cur = self._connect.cursor()
        # print('Conexión establecida con éxito')

    def __del__(self):
        self._connect.close()
        self._cur.close()
    
    def _launch_query(self, query, cip, gestio):
        self._cur.execute(query, (gestio,cip,))
        auxreg = self._cur.fetchall()
        print ("*********************************************")
        print(auxreg)
        return (auxreg)


    def get_all(self):
        return self.get_by_filters()

    def query(self,cip, gestio):
        query =("""select row_to_json(row) from 

		i.id_paralelo as "id_paralelo", i.control as "id_materia",
		i.id_inscripcion as "id_inscripcion",
		dip as "ci", d.paterno as "paterno", d.materno as "materno", d.nombres as "nombres", 
        m.sigla as "sigla", m.materia as "materia" from inscritos i, estudiantes e, dpersonales d, materias m 
        where i.id_inscripcion=%s and i.id_estudiante=e.id_estudiante 
        and e.id_persona=d.id_persona and d.dip=%s and i.control=m.id_materia) row;""")
        return self._launch_query(query, cip, gestio)

    def query_estudiante(self,cip,ru, gestio):
        query =("""select row_to_json(row) from (select i.id_estudiante as "id_estudiante", 
		i.id_paralelo as "id_paralelo", i.control as "id_materia",
		i.id_inscripcion as "id_inscripcion",
		dip as "ci", d.paterno as "paterno", d.materno as "materno", d.nombres as "nombres", 
        m.sigla as "sigla", m.materia as "materia" from inscritos i, estudiantes e, dpersonales d, materias m 
        where i.id_inscripcion=%s and i.id_estudiante=e.id_estudiante 
        and e.id_persona=d.id_persona and d.dip=%s and i.control=m.id_materia 
		and i.id_estudiante = %s ) row;""")
        self._cur.execute(query, (gestio,cip,ru,))
        return self._cur.fetchall()

    def query_get_students(self,gestion):
        query = ("""select row_to_json(row) 
                from (select distinct i.id_estudiante,d.dip, (d.paterno ||' '||d.materno)as lastname, d.nombres as firstname, d.correo, list(m.sigla||' - '||tp.letra||' II - 2022') materias
                from inscritos i, paralelos p, materias m, tiposparalelos tp, estudiantes e , dpersonales d
                where i.id_inscripcion=%s
                and i.id_inscripcion=p.id_inscripcion
                and i.id_paralelo=p.id_paralelo
                and p.id_materia=m.id_materia
                and p.paralelo=tp.paralelo
                and i.id_estudiante=e.id_estudiante
                and e.id_persona=d.id_persona
                group by i.id_estudiante, d.dip, d.paterno, d.materno, d.nombres, d.correo, d.celular
                order by  d.nombres) as row """ )
       
        self._cur.execute(query, (gestion,))
        return self._cur.fetchall()
   



    def query_get_student_by_ci(self,gestion,ci):
        query = ("""select row_to_json(row) 
                from (select distinct i.id_estudiante,d.dip, (d.paterno ||' '||d.materno)as lastname, d.nombres as firstname, d.correo, list(m.sigla||'-'||tp.letra||'-I-2022') materias
                from inscritos i, paralelos p, materias m, tiposparalelos tp, estudiantes e , dpersonales d
                where i.id_inscripcion=%s
                and i.id_inscripcion=p.id_inscripcion
                and i.id_paralelo=p.id_paralelo
                and p.id_materia=m.id_materia
                and p.paralelo=tp.paralelo
                and i.id_estudiante=e.id_estudiante
                and e.id_persona=d.id_persona
                and d.dip=%s
                group by i.id_estudiante, d.dip, d.paterno, d.materno, d.nombres, d.correo, d.celular
                order by  d.nombres) as row """ )

        self._cur.execute(query, (gestion,ci,))
        return self._cur.fetchall()