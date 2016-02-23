import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from . import constants, model, cloud_db

MSG_DB_FAILED = "Failed to handle DB requests."
MSG_NO_USER_LOGGEDIN = "No user logged in."
MSG_ALREADY_LOGGEDIN = "Already logged in."
MSG_SIGNUP_FAILED = "Sign up failed."
MSG_INVALID_IDPW = "Invalid ID and/or PW."
MSG_INVALID_PARAMS = "Invalid parameters."
MSG_NODATA = "No data."
MSG_NO_EMAIL = "No email entered."
MSG_NO_USER_FOUND = "No user found."
MSG_UNKNOWN_ERROR = "Unknown error."
MSG_PROFILE_FAILED = "Profile update failed."

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
                del request.session['user']
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
                pass
            elif action == 'checkId':
                #retrieve user_id ...
                return JsonResponse(dict(constants.CODE_SUCCESS, **{'isValidId': True}))
            else:
                return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_INVALID_PARAMS}))

        if(request.method) == 'POST':
            # signup (register)
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            data = json.loads(request.body.decode("utf-8"))

            if not data.get('user'):
                raise Exception(MSG_INVALID_PARAMS)
            user = data['user']
            user_type = user['user_type']
            # logger.info("sign up with userid=%s and usertype=%s" % (data['user']['user_id'], data['user_type']))
            logger.info(user)

            if user_type == 'patient':
                if db.add_patient(user):
                    request.session['user'] = user
                    return JsonResponse(constants.CODE_SUCCESS)
                else:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_SIGNUP_FAILED}))
            elif user_type == 'physician':
                if db.add_physician(user):
                    request.session['user'] = user
                    return JsonResponse(constants.CODE_SUCCESS)
                else:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_SIGNUP_FAILED}))
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
        if(request.method) == 'GET':
            # retrieve patient profile
            logger.info(request.GET)
            user_id = request.GET.get('user_id')
            if not user_id:
                raise Exception(MSG_INVALID_PARAMS)
            patient_profile = db.retrieve_patient_profile(user_id)
            return JsonResponse(dict(constants.CODE_SUCCESS, **{'profile': patient_profile}))

        elif (request.method) == 'POST':
            # update patient profile
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            data = json.loads(request.body.decode("utf-8"))
            if not data.get('user_id') or not data.get('profiles') or not data.get('timestamp'):
                raise Exception(MSG_INVALID_PARAMS)
            user_id = data['user_id']
            timestamp = data['timestamp']
            for key, value in data['profiles'].items():
                if not db.add_patient_profile(user_id, key, value, timestamp):
                    raise Exception(MSG_PROFILE_FAILED)
                # logger.info('userid=%s key=%s value=%s' % (user_id, key, value))
            return JsonResponse(constants.CODE_SUCCESS)

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))

@csrf_exempt
def handle_physician_profile_mgt(request):
    db = cloud_db.DbManager()
    try:
        if(request.method) == 'GET':
            # retrieve physician profile
            logger.info(request.GET)
            user_id = request.GET.get('user_id')
            if not user_id:
                raise Exception(MSG_INVALID_PARAMS)
            physician_profile = db.retrieve_physician_profile(user_id)
            return JsonResponse(dict(constants.CODE_SUCCESS, **{'profile': physician_profile}))

        elif (request.method) == 'POST':
            # update physician profile
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            data = json.loads(request.body.decode("utf-8"))
            if not data.get('user_id') or not data.get('profiles'):
                raise Exception(MSG_INVALID_PARAMS)
            user_id = data['user_id']
            for key, value in data['profiles'].items():
                if not db.add_physician_profile(user_id, key, value):
                    raise Exception(MSG_PROFILE_FAILED)
                # logger.info('userid=%s key=%s value=%s' % (user_id, key, value))
            return JsonResponse(constants.CODE_SUCCESS)

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))

@csrf_exempt
def handle_medical_image_mgt(request):
    db = cloud_db.DbManager();
    try:
        if(request.method) == 'GET':
            pass

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))

@csrf_exempt
def handle_interpretation_mgt(request):
    db = cloud_db.DbManager();
    try:
        if(request.method) == 'GET':
            pass

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))

@csrf_exempt
def handle_analytics_mgt(request):
    db = cloud_db.DbManager();
    try:
        if(request.method) == 'GET':
            pass

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))

@csrf_exempt
def handle_payment_mgt(request):
    db = cloud_db.DbManager();
    try:
        if(request.method) == 'GET':
            pass

    except Exception as e:
        logger.exception(e)
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))