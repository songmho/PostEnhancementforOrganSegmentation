import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from . import constants, model, cloud_db

MSG_DB_FAILED = "Failed to handle DB requests."
MSG_NO_USER_LOGGEDIN = "No user logged in."
MSG_NOT_MATCHED_USER = "logged in user is not match with request user"
MSG_ALREADY_LOGGEDIN = "Already logged in."
MSG_SIGNUP_FAILED = "Sign up failed."
MSG_INVALID_IDPW = "Invalid ID and/or PW."
MSG_INVALID_PARAMS = "Invalid parameters."
MSG_NODATA = "No data."
MSG_NO_EMAIL = "No email entered."
MSG_NO_USER_FOUND = "No user found."
MSG_UNKNOWN_ERROR = "Unknown error."
MSG_PROFILE_FAILED = "Profile update failed."
MSG_ACCOUNT_FAILED = "Account update failed."
MSG_NO_CHANGE = "There is no change."
MSG_NO_MEDICAL_IMAGE = "There is not the requested medical image."

logging.basicConfig(
    format="[%(name)s][%(asctime)s] %(message)s",
    handlers=[logging.StreamHandler()],
    level=logging.INFO
)
logger = logging.getLogger(__name__)


@csrf_exempt
def handle_session_mgt(request):
    """
    Handle login and logout requests.
    :param request:
    :return:
    """
    db = cloud_db.DbManager()
    try:
        if request.method == 'POST':
            ### login ###
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            data = json.loads(request.body.decode("utf-8"))

            if not data.get('user_id') or not data.get('password'):
                raise Exception(MSG_INVALID_PARAMS)
            if request.session.get('user'):
                raise Exception(MSG_ALREADY_LOGGEDIN)
            user_id = data['user_id']
            password = data['password']

            user = {}
            user_type = db.retrieve_user(user_id, password)
            if user_type is None:
                raise Exception(MSG_INVALID_IDPW)
            elif user_type == 'patient':
                user = db.retrieve_patient(user_id, password)
            elif user_type == 'physician':
                user = db.retrieve_physician(user_id, password)
            else:
                raise Exception(MSG_INVALID_IDPW)
            if not user.get('user_id'):
                raise Exception(MSG_INVALID_IDPW)
            request.session['user'] = user

            return JsonResponse(constants.CODE_SUCCESS)

        elif request.method == 'DELETE':
            ### Logout ###
            if request.session.get('user'):
                # del request.session['user']
                request.session.clear()
                return JsonResponse(constants.CODE_SUCCESS)
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
        if(request.method) == 'GET':
            # logger.info(request.GET)
            user_id = request.GET.get('user_id')
            if not user_id:
                raise Exception(MSG_INVALID_PARAMS)
            action = request.GET.get('action')
            if not action:
                raise Exception(MSG_INVALID_PARAMS)

            if action == 'getPatient':
                user = db.retrieve_patient(user_id)
                return JsonResponse(dict(constants.CODE_SUCCESS, **{'user': user}))
            elif action == 'getPhysician':
                user = db.retrieve_physician(user_id)
                return JsonResponse(dict(constants.CODE_SUCCESS, **{'user': user}))
            elif action == 'checkId':
                #retrieve user_id ...
                return JsonResponse(dict(constants.CODE_SUCCESS, **{'existedId': db.find_user(user_id)}))
            else:
                return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_INVALID_PARAMS}))

        if(request.method) == 'POST':
            # signup (register)
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            data = json.loads(request.body.decode("utf-8"))

            if not data.get('action') or not data.get('user'):
                raise Exception(MSG_INVALID_PARAMS)
            action = data['action']
            user = data['user']
            user_type = user['user_type']

            if action == 'signup':
                if user_type == 'patient':
                    if db.add_patient(user):
                        request.session['user'] = user
                        return JsonResponse(constants.CODE_SUCCESS)
                    else:
                        logger.info('signup patient fail')
                        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_SIGNUP_FAILED}))
                elif user_type == 'physician':
                    if db.add_physician(user):
                        request.session['user'] = user
                        return JsonResponse(constants.CODE_SUCCESS)
                    else:
                        logger.info('signup physician fail')
                        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_SIGNUP_FAILED}))
                else:
                    raise Exception(MSG_INVALID_PARAMS)
            elif action == 'update':
                if not request.session.get('user'):
                    raise Exception(MSG_NO_USER_LOGGEDIN)
                if request.session['user']['user_id'] != user['user_id']:
                    raise Exception(MSG_NOT_MATCHED_USER)

                if user_type == 'patient':
                    logger.info(user)
                    if db.update_patient(user):
                        # request.session['user'].update(user)
                        request.session['user'] = update_session(request.session['user'], user)
                        return JsonResponse(constants.CODE_SUCCESS)
                    else:
                        logger.info('update patient fail')
                        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_NO_CHANGE}))
                elif user_type == 'physician':
                    if db.update_physician(user):
                        # request.session['user'].update(user)
                        request.session['user'] = update_session(request.session['user'], user)
                        return JsonResponse(constants.CODE_SUCCESS)
                    else:
                        logger.info('update patient fail')
                        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_NO_CHANGE}))
                else:
                    raise Exception(MSG_INVALID_PARAMS)
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

        if(request.method) == 'GET':
            # retrieve patient profile
            logger.info(request.GET)
            user_id = request.GET.get('user_id')
            if not user_id:
                raise Exception(MSG_INVALID_PARAMS)

            if request.session['user']['user_id'] != user_id:
                raise Exception(MSG_NOT_MATCHED_USER)

            patient_profile = db.retrieve_patient_profile(user_id)
            return JsonResponse(dict(constants.CODE_SUCCESS, **{'profiles': patient_profile}))

        elif (request.method) == 'POST':
            # update patient profile
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            data = json.loads(request.body.decode("utf-8"))
            if not data.get('user_id') or not data.get('profiles') or not data.get('timestamp'):
                raise Exception(MSG_INVALID_PARAMS)
            user_id = data['user_id']
            timestamp = data['timestamp']

            if request.session['user']['user_id'] != user_id:
                raise Exception(MSG_NOT_MATCHED_USER)

            # for key, value in data['profiles'].items():
            # logger.info(data)
            for prof in data['profiles']:
                # logger.info(prof)
                key = prof['type']
                value = prof['value']
                if not db.add_patient_profile(user_id, key, value, timestamp):
                    raise Exception(MSG_PROFILE_FAILED)
                logger.info('userid=%s key=%s value=%s' % (user_id, key, value))
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

        if(request.method) == 'GET':
            # retrieve physician profile
            logger.info(request.GET)
            user_id = request.GET.get('user_id')
            if not user_id:
                raise Exception(MSG_INVALID_PARAMS)
            if request.session['user']['user_id'] != user_id:
                raise Exception(MSG_NOT_MATCHED_USER)

            physician_profile = db.retrieve_physician_profile(user_id)
            return JsonResponse(dict(constants.CODE_SUCCESS, **{'profiles': physician_profile}))

        elif (request.method) == 'POST':
            # update physician profile
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            data = json.loads(request.body.decode("utf-8"))
            if not data.get('user_id') or not data.get('profiles'):
                raise Exception(MSG_INVALID_PARAMS)
            user_id = data['user_id']
            if request.session['user']['user_id'] != user_id:
                raise Exception(MSG_NOT_MATCHED_USER)

            is_updated = False
            for prof in data['profiles']:
                key = prof['type']
                value = prof['value']
                prof_updated = db.add_physician_profile(user_id, key, value)
                if prof_updated:
                    is_updated = True
            if is_updated:
                return JsonResponse(constants.CODE_SUCCESS)
            else:
                logger.info('update phsycian profile fail')
                return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_NO_CHANGE}))
            return JsonResponse(constants.CODE_SUCCESS)

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))

@csrf_exempt
def handle_medical_image_mgt(request):
    db = cloud_db.DbManager()
    try:
        if not request.session.get('user'):
            raise Exception(MSG_NO_USER_LOGGEDIN)

        if request.method == 'GET':
            #retrieve medical image
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
            else:
                raise Exception(MSG_INVALID_PARAMS)
        elif request.method == 'POST':
            #add medical image
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            data = json.loads(request.body.decode("utf-8"))
            if not data.get('action') or not data.get('medical_image'):
                raise Exception(MSG_INVALID_PARAMS)
            action = data['action']
            medical_image = data['medical_image']

            if request.session['user']['user_id'] != medical_image['user_id']:
                raise Exception(MSG_NOT_MATCHED_USER)

            if action == 'upload':
                if db.add_medical_image(medical_image):
                    return JsonResponse(constants.CODE_SUCCESS)
                else:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_NO_MEDICAL_IMAGE}))
            elif action == 'update':
                # update image
                pass
            else:
                raise Exception(MSG_INVALID_PARAMS)


    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))

@csrf_exempt
def handle_interpretation_mgt(request):
    db = cloud_db.DbManager()
    try:
        if not request.session.get('user'):
            raise Exception(MSG_NO_USER_LOGGEDIN)

        if(request.method) == 'GET':
            pass

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))

@csrf_exempt
def handle_analytics_mgt(request):
    db = cloud_db.DbManager()
    try:
        if not request.session.get('user'):
            raise Exception(MSG_NO_USER_LOGGEDIN)

        if(request.method) == 'GET':
            pass

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))

@csrf_exempt
def handle_payment_mgt(request):
    db = cloud_db.DbManager()
    try:
        if not request.session.get('user'):
            raise Exception(MSG_NO_USER_LOGGEDIN)

        if(request.method) == 'GET':
            pass

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))

def update_session(old_user, updated_user):
    for key, value in updated_user.items():
        if key in old_user:
            old_user[key] = value
    return old_user