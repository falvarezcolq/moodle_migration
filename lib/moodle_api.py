from collections import UserList
from venv import create
from requests import get, post
import json
import random


KEY = ""
URL = ""
ENDPOINT="/admivirtual/webservice/rest/server.php"
COURSEID=885

def rest_api_parameters(in_args, prefix='', out_dict=None):
    """Transform dictionary/array structure to a flat dictionary, with key names
    defining the structure.
    Example usage:
    >>> rest_api_parameters({'courses':[{'id':1,'name': 'course1'}]})
    {'courses[0][id]':1,
     'courses[0][name]':'course1'}
    """
    if out_dict==None:
        out_dict = {}
    if not type(in_args) in (list,dict):
        out_dict[prefix] = in_args
        return out_dict
    if prefix == '':
        prefix = prefix + '{0}'
    else:
        prefix = prefix + '[{0}]'
    if type(in_args)==list:
        for idx, item in enumerate(in_args):
            rest_api_parameters(item, prefix.format(idx), out_dict)
    elif type(in_args)==dict:
        for key, item in in_args.items():
            rest_api_parameters(item, prefix.format(key), out_dict)
    return out_dict

def call(fname, **kwargs):
    """Calls moodle API function with function name fname and keyword arguments.
    Example:
    >>> call_mdl_function('core_course_update_courses',
                           courses = [{'id': 1, 'fullname': 'My favorite course'}])
    """
    parameters = rest_api_parameters(kwargs)
    parameters.update({"wstoken": KEY, 'moodlewsrestformat': 'json', "wsfunction": fname})
    # print(parameters)
    response = post(URL+ENDPOINT, parameters)
    response = response.json()
    if type(response) == dict and response.get('exception'):
        print(parameters)
        raise SystemError("Error calling Moodle API\n", response)
    return response

class CourseList():
    """Class for list of all courses in Moodle and order them by id and idnumber."""
    def __init__(self):
        # TODO fullname atribute is filtered
        # (no <span class="multilang" lang="sl">)
        courses_data = call('core_course_get_courses')
        self.courses = []
        for data in courses_data:
            self.courses.append(Course(**data))
        self.id_dict = {}
        self.idnumber_dict = {}
        for course in self.courses:
            self.id_dict[course.id] = course
            if course.idnumber:
                self.idnumber_dict[course.idnumber] = course
    def __getitem__(self, key):
        if 0<= key < len(self.courses):
            return self.courses[key]
        else:
            raise IndexError
                
    def by_id(self, id):
        "Return course with given id."
        return self.id_dict.get(id)
    
    def by_idnumber(self, idnumber):
        "Course with given idnumber"
        return self.idnumber_dict.get(idnumber)
    
    def update_courses(courses_to_update, fields):
        "Update a list of courses in one go."
        if not ('id' in fields):
            fields.append('id')
        courses = [{k: c.__dict__[k] for k in fields} for c in courses_to_update]
        return call("core_course_update_courses", 
             courses = courses)

class Course():
    
    """Class for a single course.
    Example:
    >>> Course(name="Example course", shortname="example", categoryid=1, idnumber=123)
    """
    def __init__(self, **data):
        self.__dict__.update(data)
        
    def create(self):
        "Create this course on moodle"
        res = call('core_course_create_courses', courses = [self.__dict__])
        if type(res) == list:
            self.id = res[0].get('id')
    
    def update(self):
        "Update course"
        r = call('core_course_update_courses', courses = [self.__dict__])
    
    
class User():
    """Class for a single user.
    
    Example:
    >>> User(name="Janez", surname="Novak", email="janez.novak@student.si", username="jnovak", password="sila varno geslo")"""
    
    def __init__(self, **data):
        
        self.__dict__.update(data)

    def __str__(self) -> str:
        return "user"
    

    def create_fake_email(self):
        # crea un correo falso
        fake = str(random.randint(10000000,100000000))
        return 'sistemas'+fake+'@umsa.bo'

    def create(self):
        "Create new user on moodle site"
        email_not_valid = ['sistemas@umsa.bo']


        valid_keys = ['username', 
                      'firstname', 
                      'lastname', 
                      'email', 
                    #   'auth',
                    #   'idnumber',
                      'password']
        values = {key: self.__dict__[key] for key in valid_keys}

        if self.email in email_not_valid:
            values['email']=self.create_fake_email()

        res = call('core_user_create_users', users = [values])
        if type(res) == list:
            # self.id  = res[0].get('id')
            self.__dict__.update(res[0])
        
        print("NUEVO: "+self.username+ ": "+self.firstname + " " +self.lastname + " " +self.email )
            
    def update(self, field=None):
        "Upte user data on moodle site"
        if field:
            values = {"id": self.id, field: self.__dict__[field]}
        else:
            values = self.__dict__
    
        r = call('core_user_update_users', users = [values])
    
    def get_by_field(self, field='username'):
        "Create new user if it does not exist, otherwise update data"
        res = call('core_user_get_users_by_field', field = field, values = [self.__dict__[field]])
        
        if (type(res) == list) and len(res) > 0:
            self.__dict__.update(res[0])
            return self
        else:
            return None

    def get_moodle_user(self, field='username'):
        "Create new user if it does not exist, otherwise update data"
        res = call('core_user_get_users_by_field', field = field, values = [self.__dict__[field]])
        if (type(res) == list) and len(res) > 0:
            self.__dict__.update(res[0])
            return self
        else:
            return None

    def get_courses_array(self):
        courses = self.materias.split(";")[1:]

        for i in range(len(courses)):
            if courses[i] == '-A-I-2022':
                courses[i] = 'INGLES-A-I-2022'
            elif courses[i] == '-B-I-2022':
                courses[i] = 'INGLES-B-I-2022'

        return courses

    def get_courses_from_moodle(self):
        params=[{"userid":self.id,"courseid":COURSEID }]
        res = call('core_user_get_course_user_profiles', userlist=params)
            
        if (type(res) == list) and len(res) > 0:
            self.__dict__.update(res[0])
            return self
        else:
            return None

    def update_courses(self,courses,mostrar=False):
        materias = self.get_courses_array()
        add_list=[]
        remove_list=[]
        message = ""
        try:
            materias_moodle = [ c['shortname'] for c in self.enrolledcourses]
        except AttributeError:
            materias_moodle=[]

        for materia_db in materias:
            if materia_db not in materias_moodle:
                add_list.append(materia_db)

        for materia_m in materias_moodle:
            if materia_m not in materias:
                remove_list.append(materia_m) 

        if len(add_list) >0 or len(remove_list)>0 or mostrar:
            message = message + "\n"+ str("******************************************************")
            message = message + "\n"+ str(self.username + ": " + self.firstname + " " + self.lastname)
            message = message + "\n"+ str(materias)
            message = message + "\n"+ str(materias_moodle) 
            message = message + "\n"+ str("------------------------------------")
            message = message + "\n"+ str(add_list)
            message = message + "\n"+ str(remove_list) 
            
            print(message) 
            self.add_courses(add_list=add_list,courses=courses)
            self.remove_courses(remove_list=remove_list,courses=courses)
        return message

    

    def add_courses(self,add_list,courses):
        roleid=5 
        "Enroll users in courses with specific role"

        if len(add_list)<=0:
            return None
        
        enrolments = []
        for course in add_list :
            try:
                enrolments.append(
                {
                 'roleid': roleid,
                 'userid': self.id, 
                 'courseid': courses[course] # return course id
                 })
            except KeyError:
                print("Add NO encontrado: " + course)
        r = call('enrol_manual_enrol_users', enrolments = enrolments)
        return r
        # pass

    def remove_courses(self,remove_list,courses):
        "Unenroll users in courses with specific role"

        if len(remove_list)<=0:
            return None
        
        enrolments = []
        for course in remove_list :
            try:
                enrolments.append(
                {
                 'userid': self.id, 
                 'courseid': courses[course] # return course id
                 })
            except KeyError:
                print("Remove NO encontrado: " + course)

        r = call('enrol_manual_unenrol_users', enrolments = enrolments)
        return r
        # pass
        
    def create_or_get_id(self):
        "Get Moodle id of the user or create one if it does not exists."
        if not self.get_by_field():
            self.create()

    def enroll(self, roleid=5):
        "Enroll users in courses with specific role"
        if len(self.courses)<=0:
            return None
        enrolments = []
        for course in self.courses:
            enrolments.append({'roleid': roleid, 'userid': self.id, 'courseid': course.id})
        r = call('enrol_manual_enrol_users', enrolments = enrolments)
        return r

    def enrolments(self, m_courses):
        "Get moodle courses, the user has to enroll"
        self.courses = []
        for idnumber in self.course_idnumbers:
            course = m_courses.by_idnumber(idnumber)
            if course:
                self.courses.append(course)
        return self.courses
                
class Cathegory():
    pass

class Enrolments():
    pass
