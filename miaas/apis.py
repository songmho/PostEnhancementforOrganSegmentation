import base64
import copy
import json
import logging
import os
import time
from pprint import pprint

from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.cache import cache

import constants, cloud_db, email_auth
from image_manager import ImageManager, ImageRetriever
from miaas.users import User, Staff, Physician, Patient
from miaas.images import Image
from miaas.sessions import Session
from miaas.mias_smtp import MailSender
from miaas.generate_random import ActivationKeyGenerator
from miaas.forms import TestForm
from django.test import Client

from miaas import container

from miaas.apps import MedicalImageConfig
from django.http import FileResponse


MSG_DB_FAILED = "Handling DB requests are failed."
MSG_NO_USER_LOGGEDIN = "There is no loggged in  user."
MSG_NOT_MATCHED_USER = "Logged in user is not match with request user"
MSG_NOT_MATCHED_IMAGE = "You accessed wrong path"
MSG_ALREADY_LOGGEDIN = "You have already logged in."
MSG_SIGNUP_FAILED = "Signing up is failed."
MSG_NEED_AUTH = "Your account is not authenticated yet. Please check your email."
MSG_INVALID_IDPW = "ID and/or PW is/are invalid."
MSG_INVALID_PARAMS = "There are some invalid parameters."
MSG_NODATA = "There are no data."
MSG_NO_FILE = "No file is uploaded."
MSG_NO_EMAIL = "The email is not entered."
MSG_NO_USER_FOUND = "There is no user found."
MSG_UNKNOWN_ERROR = "Unknown error is occured."
MSG_PROFILE_FAILED = "Updating profile is failed."
MSG_PROFILE_NO_CHANGED = "There are no changed profiles."
MSG_ACCOUNT_FAILED = "Updating account is failed."
MSG_INSERT_ERROR = "To insert data is failed."
MSG_UPDATE_ERROR = "To update data is failed."
MSG_DELETE_ERROR = "To delete data is failed."
MSG_NO_CHANGE = "There is no change."
MSG_NO_MEDICAL_IMAGE = "It is not the requested medical image."
MSG_SESSION_ERROR = "Updating interpretation session is failed."

logging.basicConfig(
    format="[%(name)s][%(asctime)s] %(message)s",
    handlers=[logging.StreamHandler()],
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def upload_images(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        uploader_id = data['uploader_id']
        img_type = data['img_type']
        acq_date = data['acquisition_date']
        first_name = data['fir_name']
        last_name = data['last_name']
        birthday = data['birthday']
        gender = data['gender']
        examination_source = data['examination_source']
        interpretation = data['interpretation']
        description = data['description']

        try:
            t = str(int(time.time()))
            t_folder = '../media/'+str(uploader_id)+"_"+t
            if not os.path.isdir(t_folder):
                os.mkdir(t_folder)
            for c, x in enumerate(request.FILES.getlist("files")):
                def process(f):
                    with open(t_folder+'/' + str(f), 'wb+') as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)
                process(x)

            i = Image()
            result = i.register_images(uploader_id, img_type, t_folder+'/', acq_date, first_name, last_name,
                                       birthday, gender, examination_source, interpretation, description)
            if result:
                return JsonResponse({"state": True})
            else:
                return JsonResponse({"state": False})
        except:
            return JsonResponse({"state": False})
    else:
        return JsonResponse({"state": False})

def test(request):
    if request.method == "POST":
        print(request.POST)

def get_max_img_count(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        img_id = data['img_id']
        try:
            i = Image()
            result = i.retrieve_images(img_id=img_id)
            img_path = result[0]['img_path']
            result = len(os.listdir(img_path))
            return JsonResponse({"state": True, "data": result})
        except:
            return JsonResponse({"state": False, "data": 0})



def send_images(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        # data = json.loads()
        # print(request.POST.get("data"))
        # data = request.POST.get("data")
        img_id = data['img_id']
        img_loc = data['img_loc']
        try:
            i = Image()
            result = i.retrieve_images(img_id=img_id)
            img_path = result[0]['img_path']
            # responce = HttpResponse(mimetype="application/force-download")
            file_list = os.listdir(img_path)

            with open(img_path+file_list[img_loc], 'rb') as f:

                file_data = base64.b64encode(f.read())
            # return JsonResponse({"state":True, "data": b64})
            # file_data = "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAa0lEQVQoU2NkgIKmQ37/6+w2MYK4xpnX/h9piWDgFL4E54MZhBSdna7FyEiMIpBhYBNxWQcyCWYjTjchKwK5nRGbw9EVga3+/lbvP7LvsCkCGYbiRlyKdtW2QDwD0oFPkbDUMogbCSkCGQYAka1/qtQO9d8AAAAASUVORK5CYII="
            # file_data = file_data + "="
            return HttpResponse(file_data, content_type="image/png")
        except:
            return JsonResponse({"state": False})
    else:
        return JsonResponse({"state": False})

def upload_txt(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        i = Image()
        uploader_id = data['uploader_id']
        img_path = data['img_path']
        img_type = data['img_type']
        acq_date = data['acquisition_date']
        first_name = data['fir_name']
        last_name = data['last_name']
        birthday = data['birthday']
        gender = data['gender']
        examination_source = data['examination_source']
        interpretation = data['interpretation']
        description = data['description']
        result = i.register_images(uploader_id, img_type, img_path, acq_date, first_name, last_name, birthday, gender,
                                   examination_source, interpretation, description)
        if result:
            return JsonResponse({"state": True})
        else:
            return JsonResponse({"state": False})
    else:
        return JsonResponse({"state": False})


@csrf_exempt
def sign_out(request):
    # try:
    sess = Session()
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        ids = data['identification_number']
        result = sess.expire_session(ids)
        if result:
            return JsonResponse({"state": True})
    # except:
    #     print("sign out    ", False)
    #     return JsonResponse({"state":False})
    # print("sign out    ", False)
    else:
        print("what")
    return JsonResponse({"state":False})


@csrf_exempt
def retrieve_user(request):
    if request.method == "POST":
        u = User()
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        email = data['email']
        result = u.retrieve_user(email=email)
        if (len(result) > 0):
            return JsonResponse({"state": True, "data": result})
        else:
            return JsonResponse({"state": False, "data": []})


@csrf_exempt
def retrieve_images(request):
    if request.method == "POST":
        i = Image()
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        if data["uid"] is not None:
            result = i.retrieve_images(uploader_id=data["uid"])
        else:
            result = i.retrieve_images()
        if (len(result) > 0):
            return JsonResponse({"state": True, "data": result})
        else:
            return JsonResponse({"state": False, "data": []})


@csrf_exempt
def remove_image(request):
    if request.method == "POST":
        i = Image()
        data = json.loads(request.body.decode('utf-8'))
        trg_id = data["id"]
        result = i.delete_images(img_id=trg_id)
        if result:
            return JsonResponse({"state": True, "data": []})
        else:
            return JsonResponse({"state": False, "data": []})


@csrf_exempt
def send_activate_mail(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        container.mias_container.s.send_new_pwd()
        snder = MailSender()

        result = snder.send_new_pwd(fir_name=data['first_name'], last_name=data['last_name'], email=data['email'],
                                   url="")
        if result:
            return JsonResponse({"state": True, "data": result})
        else:
            return JsonResponse({"state": False, "data": []})


@csrf_exempt
def forgot_pwd(request):
    if request.method == "POST":
        u = User()
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        email = data['email']
        result = u.retrieve_user(email=email)
        print(result)
        if len(result) > 0:
            data = result[0]
            # snder = MailSender()
            if data:
                result = container.mias_container.s.send_new_pwd(fir_name=data['first_name'], last_name=data['last_name'],
                                                  email=data['email'], u_id=data['identification_number'])
                if not result:
                    container.mias_container.reset()
                    result = container.mias_container.s.send_new_pwd(fir_name=data['first_name'],
                                                                     last_name=data['last_name'],
                                                                     email=data['email'],
                                                                     u_id=data['identification_number'])
                if result:
                    return JsonResponse({"state": True, "data": result})
                else:
                    return JsonResponse({"state": False, "data": []})
            else:
                return JsonResponse({"state": False, "data": []})
        else:
            return JsonResponse({"state": False, "data": []})

@csrf_exempt
def reset_pwd(request):
    if request.method == "POST":
        u = User()
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        id = data['id']
        email = data['email']
        pwd = data['pwd']

        result = u.retrieve_user(identification_number=id, email=email)
        if len(result) > 0:
            result = u.modify_user(identification_number=id, pwd=pwd)
            if result:
                return JsonResponse({"state": True, "data": result})
            else:
                return JsonResponse({"state": False, "data": []})
        else:
            return JsonResponse({"state": False, "data": []})

@csrf_exempt
def modify_user_info(request):
    if request.method == "POST":
        u = User()
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        email = data['email']
        result = u.retrieve_user(email=email)
        if (len(result) > 0):
            return JsonResponse({"state":True, "data":result})
        else:
            return JsonResponse({"state":False, "data":[]})


@csrf_exempt
def sign_in(request):

    sess = Session()
    # try:
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        input_id = data['id']
        input_pwd = data['pwd']

        u = User()
        print(input_id, input_pwd)
        results = u.retrieve_user(email=input_id, pwd=input_pwd)
        print(results)
        if len(results) == 0:
            return JsonResponse({"state": False, "data": ["Check ID or Password"]})
        else:
            cur_users = request.session.get('user')
            request.session['user'] = results[0]
            cur_users = request.session.get('user')
            try:
                results[0]['birthday'] = results[0]['birthday'].strftime('%Y-%m-%d')
            except:
                results[0]['birthday'] = "1990-01-01"
            print(">>>>", cur_users, results[0]['active']==1)
            if results[0]['active'] == 1:
                result = sess.generate_session(results[0]['identification_number'])
                print(result)
                if result:
                        return JsonResponse({"state": True, "data": results[0]})
                else:
                    return JsonResponse({"state": False, "data": ["Check Session"]})
            else:
                return JsonResponse({"state": False, "data": ["Activate Account"]})
    #
    # except:
    #     return JsonResponse({"state": False, "data": ["Check ID or PWD"]})


@csrf_exempt
def load_curr_user_info(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        email = data['email']
        first_name = data['first_name']
        last_name = data['last_name']
        role = data['cur_role']
        id = data['identification_number']
        result = {}
        print(role)
        if role == "Staff":
            s = Staff()
            result = s.retrieve_staff(email=email, first_name=first_name, last_name=last_name)
            print(result)
        elif role == "Trainee":
            t = Patient()
            result = t.retrieve_patient(email=email, first_name=first_name, last_name=last_name)
            print(result)
        elif role == "Evaluator":
            e = Physician()
            result = e.retrieve_physician(email=email, first_name=first_name, last_name=last_name)
            print(result)
        print(result)
        return JsonResponse(result[0])


@csrf_exempt
def generate_invitation_code(request):
    if request.method == "POST":
        icg = ActivationKeyGenerator()

        user = User()
        query = user.retrieve_user()
        list_code = []
        for q in query:
            data = q['invitation_code']
            if(data not in list_code) and data is not None:
                list_code.append(data)

        result = icg.get_key(list_code)
        return JsonResponse({"result": result})

@csrf_exempt
def invite_user(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        fir_name = data['first_name']
        last_name =data["last_name"]
        email = data['email']
        inv_code = data['invitation_code']
        roles = data['role']
        user = User()
        result = user.register_user(first_name=fir_name, last_name=last_name, identification_form="", affiliation="",
                                    email=email, phone_number="", pwd="", role=' '.join(roles), invitation_code=inv_code)
        if result:
            ms = MailSender()
            result = ms.send_mail(fir_name=fir_name, last_name= last_name, list_role=roles,
                         email=email, invite_code=inv_code)
            return JsonResponse({"result": result})
        else:
            return JsonResponse({"result": False})

@csrf_exempt
def sign_up(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        print(data['role'])
        data['role'] = " ".join(data['role'])
        print("role", data['role'])
        u = User()
        akg = ActivationKeyGenerator()
        a_k = akg.get_key()
        result = u.register_user(first_name=data['first_name'], last_name=data['last_name'], email=data["email"],
                        phone_number=data["phone_number"], pwd=data["pwd"], role=data['role'], active=0,
                                 activation_code=a_k, gender=data['gender'], birthday=data['birthday'])
        u_id = u.retrieve_user(first_name=data['first_name'], last_name=data['last_name'], email=data["email"],
                        phone_number=data["phone_number"], pwd=data["pwd"], role=data['role'])[0]['identification_number']

        if result:
            if "Physician" in data['role']:
                u = Physician()
                result = u.register_physician(first_name=data['first_name'], last_name=data['last_name'], email=data["email"],
                                phone_number=data["phone_number"], pwd=data["pwd"], role=data['role'], active=0)
            if "Patient" in data['role']:
                u = Patient()
                result = u.register_patient(first_name=data['first_name'], last_name=data['last_name'], email=data["email"],
                                phone_number=data["phone_number"], pwd=data["pwd"], role=data['role'], active=0)
            if "Staff" in data['role']:
                s = Staff()
                result = s.register_staff(first_name=data['first_name'], last_name=data['last_name'], email=data["email"],
                                phone_number=data["phone_number"], pwd=data["pwd"], role=data['role'], active=0)

        if result:
            # snder = MailSender()

            result = container.mias_container.s.send_activate_mail(fir_name=data['first_name'], last_name=data['last_name'],
                                                                   email=data['email'], u_id=u_id, key=a_k)
            if not result:
                container.mias_container.reset()
                result = container.mias_container.s.send_activate_mail(fir_name=data['first_name'],
                                                                       last_name=data['last_name'],
                                                                       email=data['email'], u_id=u_id, key=a_k)
            # result = snder.send_activate_mail(fir_name=data['first_name'], last_name=data['last_name'], email=data['email'],
            #                    u_id= u_id, key=a_k)
            print("Result of Sending Mail", result)
            return JsonResponse({'state': True})
        else:
            return JsonResponse({'state': False})


@csrf_exempt
def withdrawal(request):
    if request.method == "POST":
        result = False
        data = json.loads(request.body.decode('utf-8'))
        data = data['current_user']
        if data['role'] == "Evaluator":
            e = Physician()
            e.identification_number = data["identification_number"]
            result = e.delete_physician()
        elif data['role'] == "Staff":
            s = Staff()
            s.identification_number = data["identification_number"]
            result = s.delete_staff()
        elif data['role'] == "Trainee":
            t = Patient()
            t.identification_number = data["identification_number"]
            result = t.delete_patient()

        if result is True:
            return JsonResponse({'state': True})
        else:
            return JsonResponse({'state': False})


@csrf_exempt
def handle_intpr_session_mgt(request):
    db = cloud_db.DbManager()
    if len(request.body) == 0:
        raise Exception(MSG_NODATA)

    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            user_type = data['user_type']
            if not user_type:
                raise Exception(MSG_INVALID_PARAMS)
            intpr_session = {}
            if user_type == 'patient':
                intpr_session['sessions'] = db.retrieve_patient_session(data['user_id'])
                new_flag = 0
                for session in intpr_session['sessions']:
                    if session['type'] == 'select' or session['type'] == 'cancel':
                        continue
                    elif session['status'] == 0:
                        new_flag = 1
                intpr_session['new'] = new_flag
            elif user_type == 'physician':
                intpr_session['sessions'] = db.retrieve_physician_session(data['user_id'])
                new_flag = 0
                for session in intpr_session['sessions']:
                    if session['type'] == 'response' or session['type'] == 'write':
                        continue
                    elif session['status'] == 0:
                        new_flag = 1
                intpr_session['new'] = new_flag
            request.session['intpr_session'] = intpr_session
            # pprint (intpr_session)
            return JsonResponse(constants.CODE_SUCCESS)
        except TypeError as te:
            logger.exception(te)
            return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_INVALID_PARAMS}))
            logger.exception(e)
        except Exception as e:
            return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_DB_FAILED}))

    elif request.method == 'PUT':
        data = json.loads(request.body)
        pprint(data)
        try:
            action = data['action']
            if not action:
                raise Exception(MSG_INVALID_PARAMS)

            elif action == 'read':
                res = db.update_session(data['session_id'])
                if res:
                    intpr_session = request.session['intpr_session']
                    sessions = intpr_session['sessions']
                    for i in range(0, len(sessions)):
                        if sessions[i]['session_id'] == int(data['session_id']):
                            sessions[i]['status'] = 1
                            break

                    new_flag = 0
                    if request.session['user']['user_type'] == 'patient':
                        for session in intpr_session['sessions']:
                            if session['type'] == 'select' or session['type'] == 'cancel':
                                continue
                            elif session['status'] == 0:
                                new_flag = 1
                    elif request.session['user']['user_type'] == 'physician':
                        for session in intpr_session['sessions']:
                            if session['type'] == 'response' or session['type'] == 'write':
                                continue
                            elif session['status'] == 0:
                                new_flag = 1

                    intpr_session['sessions'] = sessions
                    intpr_session['new'] = new_flag
                    request.session['intpr_session'] = intpr_session
                    return JsonResponse(constants.CODE_SUCCESS)
                else:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UPDATE_ERROR}))
            elif action == 'delete':
                res = db.delete_session(data['session_id'])
                if res:
                    intpr_session = request.session['intpr_session']
                    sessions = intpr_session['sessions']
                    for i in range(0, len(sessions)):
                        if sessions[i]['session_id'] == int(data['session_id']):
                            sessions[i]['status'] = 2
                            break

                    new_flag = 0
                    if request.session['user']['user_type'] == 'patient':
                        for session in intpr_session['sessions']:
                            if session['type'] == 'select' or session['type'] == 'cancel':
                                continue
                            elif session['status'] == 0:
                                new_flag = 1
                    elif request.session['user']['user_type'] == 'physician':
                        for session in intpr_session['sessions']:
                            if session['type'] == 'response' or session['type'] == 'write':
                                continue
                            elif session['status'] == 0:
                                new_flag = 1

                    intpr_session['sessions'] = sessions
                    intpr_session['new'] = new_flag
                    request.session['intpr_session'] = intpr_session
                    return JsonResponse(constants.CODE_SUCCESS)
                else:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UPDATE_ERROR}))
        except TypeError as te:
            logger.exception(te)
            return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_INVALID_PARAMS}))
        except Exception as e:
            logger.exception(e)
            return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_DB_FAILED}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))


@csrf_exempt
def handle_session_mgt(request):
    """
    Handle login and logout requests.
    :param request:
    :return:
    """
    # db = cloud_db.DbManager()
    try:
        if request.method == 'POST':
            ### login(signin) ###
            # if len(request.body) == 0:
            #     raise Exception(MSG_NODATA)
            data = json.loads(request.body)
            #
            # if not data.get('user_id') or not data.get('password'):
            #     raise Exception(MSG_INVALID_PARAMS)
            # if request.session.get('user'):
            #     raise Exception(MSG_ALREADY_LOGGEDIN)
            # user_id = data['user_id']
            # password = data['password']
            #
            # authenticated = db.check_authentication(user_id)
            # if authenticated is None:
            #     raise Exception(MSG_UNKNOWN_ERROR)
            # elif authenticated is False:
            #     return JsonResponse(constants.CODE_NEED_AUTH)
            #
            # user = {}
            # intpr_session = {}
            # user_type = db.retrieve_user_type(user_id, password)
            # if user_type is None:
            #     raise Exception(MSG_INVALID_IDPW)
            # elif user_type == 'patient':
            #     user = db.retrieve_patient(user_id, password)
            #     intpr_session['sessions'] = db.retrieve_patient_session(data['user_id'])
            # elif user_type == 'physician':
            #     user = db.retrieve_physician(user_id, password)
            #     intpr_session['sessions'] = db.retrieve_physician_session(data['user_id'])
            # else:
            #     raise Exception(MSG_INVALID_IDPW)
            # if not user.get('user_id'):
            #     raise Exception(MSG_INVALID_IDPW)
            #
            # # intpr session check
            # new_flag = 0
            # for session in intpr_session['sessions']:
            #     if session['status'] == 0:
            #         new_flag = 1
            # intpr_session['new'] = new_flag
            #
            # # set sessions
            # request.session['user'] = user
            # # pprint(user)
            # request.session['intpr_session'] = intpr_session
            # # request.session['medical_image'] = {}
            # # request.session.create('medical_image')
            # logger.info('user %s logged in.' % user['user_id'])
            user_id = data['user_id']
            password = data['password']
            if user_id == "patient":
                request.session['user'] = {'session_id': 1, 'patient_id': 1, 'physician_id': 1,
                                           'user_id': "user_id", 'password': "password", 'user_type': 'patient',
                                           'first_name': 'Brown', 'last_name': 'Simpson', "name": "Brown Simpson"}
            elif user_id == "physician":
                request.session['user'] = {'session_id': 1, 'patient_id': 1, 'physician_id': 1,
                                       'user_id': "user_id", 'password': "password", 'user_type': 'physician',
                                           'first_name': 'John', 'last_name': 'Johns', "user_name": "John Johns", "name": "John Johns"}
            else:
                raise Exception(MSG_INVALID_IDPW)
            return JsonResponse(constants.CODE_SUCCESS)

        elif request.method == 'DELETE':
            ### Logout ###
            if request.session.get('user'):
                # del request.session['user']
                print(request.session.get('user'))
                sess = Session()
                result = sess.expire_session(request.session.get('user')['identification_number'])
                if result:
                    request.session.clear()
                    return JsonResponse(constants.CODE_SUCCESS)
                else:
                    raise Exception(MSG_NO_USER_LOGGEDIN)
            else:
                raise Exception(MSG_NO_USER_LOGGEDIN)

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))


@csrf_exempt
def handle_user_mgt(request):
    """
    Retrieve, update, or inactivate a user.
    :param request: The body of request is a JSON object of a user.
    :return:
    """
    db = cloud_db.DbManager()
    try:
        if request.method == 'GET':
            logger.info(request.GET)
            action = request.GET.get('action')
            if not action:
                raise Exception(MSG_INVALID_PARAMS)

            if action == 'checkEmail':
                user_type = request.GET.get('user_type')
                email = request.GET.get('email')
                if not user_type or not email:
                    raise Exception(MSG_INVALID_PARAMS)
                return JsonResponse(dict(constants.CODE_SUCCESS,
                                         **{'emailUsed': db.check_email(user_type, email)}))

            user_id = request.GET.get('user_id')
            if not user_id:
                raise Exception(MSG_INVALID_PARAMS)

            if action == 'getPatient':
                user = db.retrieve_patient(user_id)
                return JsonResponse(dict(constants.CODE_SUCCESS, **{'user': user}))

            elif action == 'getPhysician':
                user = db.retrieve_physician(user_id)
                return JsonResponse(dict(constants.CODE_SUCCESS, **{'user': user}))

            elif action == 'checkId':
                # retrieve user_id ...
                return JsonResponse(dict(constants.CODE_SUCCESS, **{'existedId': db.find_user(user_id)}))

            elif action == 'resendAuth':
                authenticated = db.check_authentication(user_id)
                if authenticated is None:
                    raise Exception(MSG_UNKNOWN_ERROR)
                elif authenticated is True:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': 'Already authenticated email.'}))

                user = db.retrieve_user_info(user_id)
                if not user:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': 'User not found.'}))

                auth_code = email_auth.generate_auth_code()
                if not db.update_authentication(user_id, auth_code):
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_SIGNUP_FAILED}))
                try:
                    email_auth.send_auth_mail(user, auth_code)
                except Exception as e:
                    logger.exception(e)

                return JsonResponse(constants.CODE_SUCCESS)

            else:
                return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_INVALID_PARAMS}))

        if request.method == 'POST':
            # signup (register)
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            data = json.loads(request.body)

            if not data.get('action'):
                raise Exception(MSG_INVALID_PARAMS)
            action = data['action']

            if action == 'signup':
                if not data.get('user'):
                    raise Exception(MSG_INVALID_PARAMS)
                user = data['user']
                user_type = user['user_type']

                signup_success = False
                if user_type == 'patient':
                    if db.add_patient(user):
                        signup_success = True
                elif user_type == 'physician':
                    if db.add_physician(user):
                        signup_success = True
                else:
                    raise Exception(MSG_INVALID_PARAMS)

                if not signup_success:
                    logger.info('signup fail')
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_SIGNUP_FAILED}))

                auth_code = email_auth.generate_auth_code()
                if not db.add_authentication(user['user_id'], auth_code):
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_SIGNUP_FAILED}))
                try:
                    email_auth.send_auth_mail(user, auth_code)
                except Exception as e:
                    logger.exception(e)
                    pass

                return JsonResponse(constants.CODE_SUCCESS)

            elif action == 'update':
                if not data.get('user'):
                    raise Exception(MSG_INVALID_PARAMS)
                user = data['user']
                logger.info(user)
                user_type = user['user_type']

                if not request.session.get('user'):
                    raise Exception(MSG_NO_USER_LOGGEDIN)
                if request.session['user']['user_id'] != user['user_id']:
                    raise Exception(MSG_NOT_MATCHED_USER)

                old_email = request.session['user']['email']
                new_email = user['email']
                is_email_same = (old_email == new_email)
                print('old:%s, new:%s, isSame?%s' % (old_email, new_email, is_email_same))

                if not is_email_same and db.check_email(user_type, new_email) == -1:
                    raise Exception("The email is already used.")

                email_wait_added = True
                auth_code = None
                if not is_email_same:
                    user['email'] = old_email
                    auth_code = email_auth.generate_auth_code()
                    email_wait_added = db.update_authentication(user['user_id'], auth_code,
                                                                'update_email', new_email)
                    if not email_wait_added:
                        raise Exception("Changing Email is failed.")

                try:
                    update_user_success = False
                    pprint (request.session['user'])
                    if user_type == 'patient':
                        update_user_success = db.update_patient(user)
                    elif user_type == 'physician':
                        update_user_success = db.update_physician(user)
                    else:
                        raise Exception(MSG_INVALID_PARAMS)

                    if update_user_success:
                        request.session['user'] = update_session(request.session['user'], user)
                        if email_wait_added and auth_code:
                            user['email'] = new_email
                            email_auth.send_email_change_mail(user, auth_code)
                            return JsonResponse(constants.CODE_WAIT)
                        else:
                            return JsonResponse(constants.CODE_SUCCESS)
                    else:
                        if email_wait_added and auth_code:
                            user['email'] = new_email
                            email_auth.send_email_change_mail(user, auth_code)
                            return JsonResponse(constants.CODE_WAIT)
                        else:
                            return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_NO_CHANGE}))
                except Exception as ef:
                    logger.exception(ef)
                    if auth_code is not None:
                        db.delete_authentication(user['user_id'], auth_code)

                raise Exception(MSG_UNKNOWN_ERROR)

            elif action == 'findid':
                if not data.get('email') and not data.get('user_type'):
                    raise Exception(MSG_INVALID_PARAMS)
                user_id = db.find_id(data['email'], data['user_type'])
                if user_id:
                    return JsonResponse(dict(constants.CODE_SUCCESS, **{'user_id': user_id}))
                else:
                    raise Exception(MSG_NO_USER_FOUND)

            elif action == 'findpw':
                if not data.get('email') and not data.get('user_id'):
                    raise Exception(MSG_INVALID_PARAMS)
                password = db.find_passwd(data['user_id'], data['email'])
                if password:
                    user = db.retrieve_user_info(data['user_id'])
                    if not user:
                        raise Exception(MSG_NO_USER_FOUND)

                    temp_pw = email_auth.generate_temp_password()
                    if not db.change_password(data['user_id'], temp_pw):
                        raise Exception("Finding Password failed.")

                    try:
                        del request.session['user']
                        request.session.clear()
                    except: pass

                    email_auth.send_find_pw_mail(user, temp_pw)
                    return JsonResponse(constants.CODE_SUCCESS)
                else:
                    raise Exception(MSG_NO_USER_FOUND)

            # elif action == 'resetPassword':
            #     result = db.reset_passwd(data.get('user_id'), data['password'])
            #     if result:
            #         return JsonResponse(dict(constants.CODE_SUCCESS, **{'msg': 'success'}))
            #     else:
            #         raise Exception(MSG_DB_FAILED)

            return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))


@csrf_exempt
def handle_patient_profile_mgt(request):
    db = cloud_db.DbManager()
    try:
        if not request.session.get('user'):
            raise Exception(MSG_NO_USER_LOGGEDIN)

        if (request.method) == 'GET':
            # retrieve patient profile
            logger.info(request.GET)
            user_id = request.GET.get('user_id')
            if not user_id:
                raise Exception(MSG_INVALID_PARAMS)

            if request.session['user']['user_type'] == 'patient':
                if request.session['user']['user_id'] != user_id:
                    raise Exception(MSG_NOT_MATCHED_USER)
            patient_profile = db.retrieve_patient_profile(user_id)
            # print(patient_profile)
            return JsonResponse(dict(constants.CODE_SUCCESS, **{'profiles': patient_profile}))

        elif (request.method) == 'POST':
            # update patient profile
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            # logger.info(request.body)
            # logger.info(request.body)
            data = json.loads(request.body)
            # logger.info(data)

            if not data.get('profiles'):
                raise Exception("No changed data")
            if not data.get('user_id'):
                raise Exception(MSG_INVALID_PARAMS)
            user_id = data['user_id']

            if request.session['user']['user_id'] != user_id:
                raise Exception(MSG_NOT_MATCHED_USER)

            pprint(data['profiles'])
            # if not db.add_patient_profile(user_id, timestamp, data['profiles']):
            if not db.update_patient_profile(user_id, data['profiles']):
                raise Exception(MSG_PROFILE_NO_CHANGED)

            return JsonResponse(constants.CODE_SUCCESS)

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))


@csrf_exempt
def handle_physician_profile_mgt(request):
    db = cloud_db.DbManager()
    try:
        if not request.session.get('user'):
            raise Exception(MSG_NO_USER_LOGGEDIN)

        if (request.method) == 'GET':
            # retrieve physician profile
            logger.info(request.GET)
            user_id = request.GET.get('user_id')
            if not user_id:
                raise Exception(MSG_INVALID_PARAMS)
            # if request.session['user']['user_id'] != user_id:
            #     raise Exception(MSG_NOT_MATCHED_USER)

            physician_profile = db.retrieve_physician_profile(user_id)
            # print(physician_profile)
            return JsonResponse(dict(constants.CODE_SUCCESS, **{'profiles': physician_profile}))

        elif (request.method) == 'POST':
            # update physician profile
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            data = json.loads(request.body)
            # logger.info(data)
            # print(data)
            if not data.get('user_id') or not data.get('profiles'):
                raise Exception(MSG_INVALID_PARAMS)
            user_id = data['user_id']
            if request.session['user']['user_id'] != user_id:
                raise Exception(MSG_NOT_MATCHED_USER)
            physician_profile = {}
            keys = []
            values = []
            for prof in data['profiles']:
                keys.append(prof['type'])
                values.append(prof['value'])
            prof_updated = db.add_physician_profile(user_id, keys, values)
            if prof_updated:
                return JsonResponse(constants.CODE_SUCCESS)
            else:
                logger.info('update phsycian profile fail')
                return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_NO_CHANGE}))

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))


@csrf_exempt
def handle_image_uploading_progress(request):
    progress_id = ''
    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']

    if progress_id:
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        data = cache.get(cache_key)
        jsondata = json.dumps(data)
        # logger.info("cache_key=%s / json data=%s" % (cache_key, jsondata))
        return HttpResponse(jsondata)
    else:
        return JsonResponse(dict(constants.CODE_FAILURE,
                                 **{'msg': 'Server Error: You must provide X-Progress-ID header or query param.'}))


@csrf_exempt
def handle_medical_image_mgt(request):
    db = cloud_db.DbManager()
    try:
        if not request.session.get('user'):
            raise Exception(MSG_NO_USER_LOGGEDIN)

        if request.method == 'GET':
            # retrieve medical images
            logger.info(request.GET)
            action = request.GET.get('action')
            if not action:
                raise Exception(MSG_INVALID_PARAMS)
            if action == 'getImage':
                image_id = request.GET.get('image_id')
                image = db.retrieve_medical_image_by_id(image_id)
                return JsonResponse(dict(constants.CODE_SUCCESS, **{'medical_image': image}))
                pass

            elif action == 'getImages':
                user_id = request.GET.get('user_id')
                if request.session['user']['user_id'] != user_id:
                    raise Exception(MSG_NOT_MATCHED_USER)

                image_list = db.retrieve_medical_image(user_id)
                return JsonResponse(dict(constants.CODE_SUCCESS, **{'image_list': image_list}))

            elif action == 'getImageDirs':
                user_id = request.GET.get('user_id')
                if request.session['user']['user_type'] == 'patient' \
                        and request.session['user']['user_id'] != user_id:
                    raise Exception(MSG_NOT_MATCHED_USER)
                image_id = request.GET.get('image_id')
                image_dir = request.GET.get('image_dir')
                # if request.session.get('archive') and request.session['archive'].get('now_image_id') and\
                #         request.session['archive']['now_image_id'] != image_id:
                #     raise Exception(MSG_NOT_MATCHED_IMAGE)

                if not image_id or not image_dir:
                    return Exception(MSG_INVALID_PARAMS)

                # logger.info('from session image page: %s' % (request.session['medical_image']))
                # image_dir = request.session['medical_image'][str(image_id)]['image_dir']
                # image_dir = request.session['curr_image']['image_dir']
                image_dirs_dict = ImageRetriever.get_image_list(image_dir)
                return JsonResponse(dict(constants.CODE_SUCCESS, **{'image_list': image_dirs_dict}))

            else:
                raise Exception(MSG_INVALID_PARAMS)

        elif request.method == 'PUT':
            # update medical image
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            data = json.loads(request.body)

            action = data['action']
            if not action:
                raise Exception(MSG_INVALID_PARAMS)
            # To update image
            elif action == 'update':
                image_info = data['image_info']
                if not image_info:
                    raise Exception(MSG_INVALID_PARAMS)
                if request.session['user']['user_id'] != image_info['user_id']:
                    raise Exception(MSG_NOT_MATCHED_USER)
                db.update_medical_image_by_id(image_info)
                return JsonResponse(dict(constants.CODE_SUCCESS))
            else:
                raise Exception(MSG_INVALID_PARAMS)

        elif request.method == 'DELETE':
            # delete medical image
            user_id = request.GET.get('user_id')
            image_id = request.GET.get('image_id')
            image_dir = request.GET.get('image_dir')
            if not user_id or not image_id or not image_dir:
                raise Exception(MSG_INVALID_PARAMS)
            if request.session['user']['user_id'] != user_id:
                raise Exception(MSG_NOT_MATCHED_USER)
            db.delete_medical_image_by_id(image_id)
            try:
                ImageManager.delete_file(image_dir)
                # ImageManager.delete_uploaded_archive_file(image_dir)
            except:
                pass
            if request.session.get('image_cnt'):
                request.session['image_cnt'] -= 1
            return JsonResponse(dict(constants.CODE_SUCCESS))

        elif request.method == 'POST':
            # add medical iamge and upload medical image
            if 'image_file' in request.FILES and 'image_info' in request.POST:
                action = request.POST['action']

                image_info = json.loads(request.POST['image_info'])
                prev_timestamp = 0
                if image_info.get('timestamp'):
                    prev_timestamp = image_info['timestamp']
                image_info['timestamp'] = int(round(time.time() * 1000))
                image_file = request.FILES['image_file']

                if request.session['user']['user_id'] != image_info['user_id']:
                    raise Exception(MSG_NOT_MATCHED_USER)
                if action != 'upload' and action != 'update':
                    raise Exception(MSG_INVALID_PARAMS)

                uploaded_path = None
                im = ImageManager(image_file, image_info)
                uploaded_path = im.upload_file()
                # logger.info(uploaded_path)
                # uploaded_path = uploaded_path.encode('UTF-8')
                # logger.info(uploaded_path)

                logger.info('image is uploaded to: %s', uploaded_path)

                if action == 'upload':
                    try:
                        image_info['image_dir'] = uploaded_path
                        db.add_medical_image(image_info)
                    except Exception as e:
                        if uploaded_path:
                            ImageManager.delete_file(uploaded_path)
                            im.delete_temp_file()
                        raise e
                    if not request.session.get('image_cnt'):
                        request.session['image_cnt'] += 1
                    return JsonResponse(dict(constants.CODE_SUCCESS))
                elif action == 'update':
                    prev_path = image_info['image_dir']
                    try:
                        image_info['image_dir'] = uploaded_path
                        db.update_medical_image_dir(image_info)
                    except Exception as e:
                        image_info['timestamp'] = prev_timestamp
                        image_info['image_dir'] = prev_path
                        # db.update_medical_image_dir(image_info)
                        ImageManager.delete_file(uploaded_path)
                        raise e
                    # remove here!
                    image_id = int(image_info['image_id'])
                    # request.session['image'][image_id] = dict()
                    # request.session['medical_image'][image_id]['timestamp'] = image_info['timestamp']
                    # request.session['medical_image'][image_id]['image_dir'] = image_info['image_dir']
                    # request.session['curr_image'] = dict()
                    # request.session['curr_image']['timestamp'] = image_info['timestamp']
                    # request.session['curr_image']['image_dir'] = image_info['image_dir']
                    # logger.info('curr_image session is updated: %s' % request.session['medical_image'][image_info['image_id']])

                    logger.info('remove old file: %s', prev_path)
                    ImageManager.delete_file(prev_path)
                    return JsonResponse(dict(constants.CODE_SUCCESS, **{'new_dir': image_info['image_dir']}))

            else:
                raise Exception(MSG_INVALID_PARAMS)

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))


@csrf_exempt
def handle_multple_image_upload(request):
    try:
        if request.FILES == None:
            raise Exception(MSG_NO_FILE)

        files = request.FILES['attachments']
        logger.info(files)
        return JsonResponse(constants.CODE_SUCCESS)

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))


@csrf_exempt
def handle_interpretation_mgt(request):
    db = cloud_db.DbManager()
    try:
        # To handle patient and physician interpretation request
        if request.method == 'PUT':
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            data = json.loads(request.body)
            action = data['action']
            if not action:
                raise Exception(MSG_INVALID_PARAMS)
            # To create a patient request
            elif action == 'patientReq':
                status = 3
                timestamp = int(round(time.time() * 1000))
                request = {
                    'image_id': data['image_id'],
                    'status': status,
                    'subject': data['subject'],
                    'message': data['message'],
                    'timestamp': timestamp,
                    'level': data['level']
                }
                if_inserted = db.add_patient_intpr_request(request)
                if if_inserted:
                    return JsonResponse(constants.CODE_SUCCESS)
                else:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_INSERT_ERROR}))
            # To create a response on a patient request
            elif action == 'physicianResp':
                timestamp = int(round(time.time() * 1000))
                status = 2
                response = {
                    'request_id': data['request_id'],
                    'physician_id': data['physician_id'],
                    'message': data['message'],
                    'timestamp': timestamp,
                    'status': status
                }
                if_inserted = db.add_physician_intpr_resp(response)
                if if_inserted:
                    value = {
                        "request_id": data['request_id'],
                        "request_subject": data['request_subject'],
                        "acceptance_message": data['message']
                    }
                    res_session = db.add_session(data['patient_id'], data['physician_id'], 'response',
                                                 json.dumps(value), timestamp)
                    if res_session:
                        return JsonResponse(constants.CODE_SUCCESS)
                    else:
                        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_SESSION_ERROR}))
                else:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_INSERT_ERROR}))

            elif action == 'tempSaveIntpr':
                intpr = {
                    'summary': data['summary'],
                    'request_id': data['request_id'],
                    'suspected_disease': data['suspected_disease'],
                    'opinion': data['opinion'],
                    'recommendation': data['recommendation']
                }
                if_inserted = db.temp_save_intpr(intpr)
                if if_inserted:
                    return JsonResponse(constants.CODE_SUCCESS)
                else:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_NO_CHANGE}))

            # To create an interpretation and update request and response
            elif action == 'finishIntpr':
                fee = 20
                timestamp = int(round(time.time() * 1000))
                request_id = data['request_id']
                intpr = {
                    'patient_id': data['patient_id'],
                    'physician_id': data['physician_id'],
                    'image_id': data['image_id'],
                    'level': data['level'],
                    'fee': fee,
                    'timestamp': timestamp,
                    'summary': data['summary'],
                    'request_id': request_id,
                    'suspected_disease': data['suspected_disease'],
                    'opinion': data['opinion'],
                    'recommendation': data['recommendation']
                }
                if_inserted = db.add_intpr(intpr)
                db.update_medical_image_intprnum(data['image_id'])
                if if_inserted:
                    status = 0
                    if_updated = db.update_req_and_resp(request_id, status, timestamp)
                    db.delete_temp_intpr(request_id)
                    if if_updated:
                        value = {
                            "request_id": data['request_id'],
                            "request_subject": data['request_subject'],
                            "summary": data['summary']
                        }
                        res_session = db.add_session(data['patient_id'], data['physician_id'], 'write',
                                                     json.dumps(value), timestamp)
                        if res_session:
                            return JsonResponse(constants.CODE_SUCCESS)
                        else:
                            return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_SESSION_ERROR}))
                    else:
                        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UPDATE_ERROR}))
                else:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_INSERT_ERROR}))
        # To handle 'GET' interpretation request
        if request.method == 'GET':
            logger.info(request.GET)
            action = request.GET.get('action')
            if not action:
                raise Exception(MSG_INVALID_PARAMS)
            # To get all interpretations of a patient
            elif action == 'getPatientIntpr':
                patient_id = request.GET.get('patient_id')
                if not request.GET.get('time_from'):
                    time_from = 0
                intpr = db.retrieve_patient_intpr(patient_id, time_from)
                return JsonResponse(dict(constants.CODE_SUCCESS, **{'intpr': intpr}))
            # To get all interpretations of a physician
            elif action == 'getPhysicianIntpr':
                physician_id = request.GET.get('physician_id')
                if not physician_id:
                    raise Exception(MSG_INVALID_PARAMS)
                if not request.GET.get('time_from'):
                    time_from = 0
                intpr = db.retrieve_physician_intpr(physician_id, time_from)
                return JsonResponse(dict(constants.CODE_SUCCESS, **{'intpr': intpr}))
            # To get all interpretations of a medical image
            elif action == 'getImageIntpr':
                image_id = request.GET.get('image_id')
                if not image_id:
                    raise Exception(MSG_INVALID_PARAMS)
                time_from = request.GET.get('time_from')
                if not time_from:
                    time_from = 0
                offset = request.GET.get('offset')
                limit = request.GET.get('limit')
                if (not offset) and (not limit):
                    offset = None
                    limit = None
                intpr = db.retrieve_image_intpr(image_id, time_from, offset, limit)
                return JsonResponse(dict(constants.CODE_SUCCESS, **{'intpr': intpr}))
            else:
                return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_INVALID_PARAMS}))
        # To handle 'POST' interpretation request
        elif request.method == 'POST':
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            data = json.loads(request.body)
            action = data['action']
            if not action:
                raise Exception(MSG_INVALID_PARAMS)
            # To update a patient request and delete patient responses
            elif action == 'patientSelReq':
                request_id = data['request_id']
                physician_id = data['physician_id']
                status = 1
                timestamp = int(round(time.time() * 1000))
                if_updated = db.update_patient_request_by_selection(request_id, physician_id, status)
                if if_updated:
                    value = {
                        "request_id": data['request_id'],
                        "request_subject": data['request_subject'],
                    }
                    res_session = db.add_session(data['patient_id'], data['physician_id'], 'select',
                                                 json.dumps(value), timestamp)
                    if res_session:
                        return JsonResponse(constants.CODE_SUCCESS)
                    else:
                        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_SESSION_ERROR}))
                else:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_INSERT_ERROR}))
            # To update subject and message of a patient request
            elif action == 'reqUpdate':
                request_id = data['request_id']
                subject = data['subject']
                message = data['message']
                timestamp = int(round(time.time() * 1000))
                if_updated = db.update_patient_request(request_id, subject, message, timestamp)
                if if_updated:
                    return JsonResponse(constants.CODE_SUCCESS)
                else:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UPDATE_ERROR}))
        # To handle 'DELETE' interpretation request
        if request.method == 'DELETE':
            logger.info(request.GET)
            action = request.GET.get('action')
            if not action:
                raise Exception(MSG_INVALID_PARAMS)
            # To delete a patient request and relevant physician responses
            elif action == 'delPatientReq':
                request_id = request.GET.get('request_id')
                if_deleted = db.delete_patient_request(request_id)
                if if_deleted:
                    return JsonResponse(constants.CODE_SUCCESS)
                else:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_DELETE_ERROR}))
    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))
    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))


@csrf_exempt
def handle_analytics_mgt(request):
    db = cloud_db.DbManager()
    try:
        # To handle patient and physician interpretation request
        if request.method == 'PUT':
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            data = json.loads(request.body)
            action = data['action']
            if not action:
                raise Exception(MSG_INVALID_PARAMS)
            elif action == 'addAnalytic':
                timestamp = int(round(time.time() * 1000))
                analytic = {
                    'image_id': data['image_id'],
                    'level': data['status'],
                    'fee': data['subject'],
                    'timestamp': timestamp,
                    'summary': data['summary'],
                    'result': data['result']
                }
                if_inserted = db.add_analytic(analytic)
                if if_inserted:
                    return JsonResponse(constants.CODE_SUCCESS)
                else:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_INSERT_ERROR}))
        if (request.method) == 'POST':
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            data = json.loads(request.body)
            action = data['action']
            if not action:
                raise Exception(MSG_INVALID_PARAMS)
            elif action == 'updateAnalytic':
                level = data['level']
                fee = data['fee']
                timestamp = int(round(time.time() * 1000))
                summary = data['summary']
                result = data['result']
                anal_id = data['anal_id']
                if_updated = db.update_analytic(level, fee, timestamp, summary, result, anal_id)
                if if_updated:
                    return JsonResponse(constants.CODE_SUCCESS)
                else:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UPDATE_ERROR}))
        if request.method == 'GET':
            logger.info(request.GET)
            action = request.GET.get('action')
            if not action:
                raise Exception(MSG_INVALID_PARAMS)
            elif action == 'getPatientIntpr':
                image_id = request.GET.get('image_id')
                analytics = db.retrieve_analytic_by_image(image_id)
                return JsonResponse(dict(constants.CODE_SUCCESS, **{'analytics': analytics}))
    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))


@csrf_exempt
def handle_archive(request):
    logger.info(request.GET)

    image_user_id = request.GET.get('image_user_id')
    image_id = request.GET.get('image_id')
    image_dir = request.GET.get('image_dir')
    image_name = ImageRetriever._get_file_name(image_dir)
    if image_user_id and image_id and image_dir:
        logger.info("Image DIR: %s" % image_dir)

        with open(image_dir, "rb") as image_file:
            response = HttpResponse(image_file, content_type='application/dicom', )
            response['Content-Disposition'] = 'attachment; filename=' + image_name
        return response
        # return HttpResponse('');
    else:

        return HttpResponseNotFound()


@csrf_exempt
def handle_payment_mgt(request):
    db = cloud_db.DbManager()
    try:
        if (request.method) == 'GET':
            pass

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))


@csrf_exempt
def update_session(old_user, updated_user):
    for key, value in updated_user.items():
        if key in old_user:
            old_user[key] = value
    return old_user


@csrf_exempt
def handle_test(request):
    logger.info(request)
    if len(request.body) == 0:
        logger.info('no data')
    else:
        logger.info('=== API Handler Test ===')
        logger.info(request.body)

        user_info = {
            'user_id': 'hanter',
            'name': 'Hanter Jung',
            'email': 'hanterkr@gmail.com'
        }
        email_auth.send_auth_mail(user_info, '9fudsiu32q984rhds98')

    return JsonResponse(constants.CODE_SUCCESS)
