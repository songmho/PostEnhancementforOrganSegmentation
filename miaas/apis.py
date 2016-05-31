import json
import logging
import time
from pprint import pprint

from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

import constants, cloud_db, email_auth
from image_manager import ImageManager, ImageRetriever

MSG_DB_FAILED = "Failed to handle DB requests."
MSG_NO_USER_LOGGEDIN = "No user logged in."
MSG_NOT_MATCHED_USER = "Logged in user is not match with request user"
MSG_NOT_MATCHED_IMAGE = "Access with wrong path"
MSG_ALREADY_LOGGEDIN = "Already logged in."
MSG_SIGNUP_FAILED = "Sign up failed."
MSG_NEED_AUTH = "Your account is not authenticated yet. Please check your email."
MSG_INVALID_IDPW = "Invalid ID and/or PW."
MSG_INVALID_PARAMS = "Invalid parameters."
MSG_NODATA = "No data."
MSG_NO_FILE = "No file uploaded."
MSG_NO_EMAIL = "No email entered."
MSG_NO_USER_FOUND = "No user found."
MSG_UNKNOWN_ERROR = "Unknown error."
MSG_PROFILE_FAILED = "Profile update failed."
MSG_PROFILE_NO_CHANGED = "No changed profiles."
MSG_ACCOUNT_FAILED = "Account update failed."
MSG_INSERT_ERROR = "To insert data failed."
MSG_UPDATE_ERROR = "To update data failed."
MSG_DELETE_ERROR = "To delete data failed."
MSG_NO_CHANGE = "There is no change."
MSG_NO_MEDICAL_IMAGE = "There is not the requested medical image."
MSG_SESSION_ERROR = "Updating interpretation session is failed."

logging.basicConfig(
    format="[%(name)s][%(asctime)s] %(message)s",
    handlers=[logging.StreamHandler()],
    level=logging.INFO
)
logger = logging.getLogger(__name__)


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
                    if session['status'] == 0:
                        new_flag = 1
                intpr_session['new'] = new_flag
            elif user_type == 'physician':
                intpr_session['sessions'] = db.retrieve_physician_session(data['user_id'])
                new_flag = 0
                for session in intpr_session['sessions']:
                    if session['status'] == 0:
                        new_flag = 1
                intpr_session['new'] = new_flag
            request.session['intpr_session'] = intpr_session
            return JsonResponse(constants.CODE_SUCCESS)
        except TypeError:
            return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_INVALID_PARAMS}))
        except Exception:
            return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_DB_FAILED}))

    elif request.method == 'PUT':
        data = json.loads(request.body)
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
                    for session in intpr_session['sessions']:
                        if session['status'] == 0:
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
                    for session in intpr_session['sessions']:
                        if session['status'] == 0:
                            new_flag = 1

                    intpr_session['sessions'] = sessions
                    intpr_session['new'] = new_flag
                    request.session['intpr_session'] = intpr_session
                    return JsonResponse(constants.CODE_SUCCESS)
                else:
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UPDATE_ERROR}))
        except TypeError:
            return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_INVALID_PARAMS}))
        except Exception:
            return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_DB_FAILED}))

    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_UNKNOWN_ERROR}))


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
            ### login(signin) ###
            if len(request.body) == 0:
                raise Exception(MSG_NODATA)
            data = json.loads(request.body)

            if not data.get('user_id') or not data.get('password'):
                raise Exception(MSG_INVALID_PARAMS)
            if request.session.get('user'):
                raise Exception(MSG_ALREADY_LOGGEDIN)
            user_id = data['user_id']
            password = data['password']

            authenticated = db.check_authentication(user_id)
            if authenticated is None:
                raise Exception(MSG_UNKNOWN_ERROR)
            elif authenticated is False:
                return JsonResponse(constants.CODE_NEED_AUTH)

            user = {}
            intpr_session = {}
            user_type = db.retrieve_user_type(user_id, password)
            if user_type is None:
                raise Exception(MSG_INVALID_IDPW)
            elif user_type == 'patient':
                user = db.retrieve_patient(user_id, password)
                intpr_session['sessions'] = db.retrieve_patient_session(data['user_id'])
            elif user_type == 'physician':
                user = db.retrieve_physician(user_id, password)
                intpr_session['sessions'] = db.retrieve_physician_session(data['user_id'])
            else:
                raise Exception(MSG_INVALID_IDPW)
            if not user.get('user_id'):
                raise Exception(MSG_INVALID_IDPW)

            # intpr session check
            new_flag = 0
            for session in intpr_session['sessions']:
                if session['status'] == 0:
                    new_flag = 1
            intpr_session['new'] = new_flag

            # set sessions
            request.session['user'] = user
            # pprint(intpr_session)
            request.session['intpr_session'] = intpr_session
            # request.session['medical_image'] = {}
            # request.session.create('medical_image')
            logger.info('user %s logged in.' % user['user_id'])

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
                return JsonResponse(dict(constants.CODE_SUCCESS, **{'emailUsed': db.check_email(user_type, email)}))

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
                    return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': MSG_INSERT_ERROR}))

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
