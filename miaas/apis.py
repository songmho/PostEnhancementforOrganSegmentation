import base64
import copy
import glob
import io
import json
import logging
import math
import os
import time
from pprint import pprint

import cv2
import numpy as np
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.cache import cache

import constants
from image_manager import ImageManager, ImageRetriever
from miaas.users import User, Staff, Physician, Patient
from miaas.images import Image
from miaas.diagnosis import Diagnosis
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


def register_profile_image(request):
    if request.method == "POST":

        data = json.loads(request.POST.get("data"))
        id = data['id']
        path = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\Test\\mias\\media\\profile_image\\"+str(id)
        print(id)
        try:
            if not os.path.isdir(path):
                os.mkdir(path)
                print(1)
            else:
                for i in os.listdir(path):
                    os.remove(path+"\\"+i)
                print(2)

            print(3, enumerate(request.FILES.getlist("files")))
            for c, x in enumerate(request.FILES.getlist("files")):
                print(4)
                print(c, x)
                def process(f):
                    with open(path+"\\"+str(f), "wb+") as destination:
                        print(f)
                        for chunk in f.chunks():
                            destination.write(chunk)
                process(x)
            return JsonResponse({"state": True})
        except:
            return JsonResponse({"state": False})

def retrieve_image_info(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            print(data)
            i_id = data["i_id"]
            i = Image()
            result = i.retrieve_images(img_id=i_id)
            print(result)
            print(os.listdir(result[0]['img_path']))
            result[0]["images"] = os.listdir(result[0]['img_path'])
            return JsonResponse({"state": True, "data": result})
        except:
            return JsonResponse({"state": False})
    else:
        return JsonResponse({"state": False})


def send_profile(request):
    if request.method == "POST":

        try:
            data = json.loads(request.body.decode('utf-8'))
            id = data['id']
            path = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\Test\\mias\\media\\profile_image\\"+str(id)
            file_name = os.listdir(path)[0]
            print(len(os.listdir(path)))
            if len(os.listdir(path)) > 0:
                    with open(path+"\\"+file_name, 'rb') as f:
                        profile_data = base64.b64encode(f.read())
                        print("Profile", id, file_name)
                        return HttpResponse(profile_data, content_type="image/png")
            else:
                return HttpResponse(None, content_type="image/png")
        except:
            return HttpResponse(None, content_type="image/png")
    else:
        return HttpResponse(None, content_type="image/png")


def remove_profile(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        id = data['id']
        path = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\Test\\mias\\media\\profile_image\\"+str(id)
        try:
            if not os.path.isdir(path):
                return JsonResponse({"state": True})
            else:
                try:
                    for i in os.listdir(path):
                        os.remove(path+"\\"+i)
                        print(path+"\\"+i)
                    return JsonResponse({"state": True})
                except:
                    return JsonResponse({"state": False})
        except:
            return JsonResponse({"state": False})


def upload_images(request):
    if request.method == "POST":
        keys = list(request.FILES.keys())
        print(keys)
        try:
            try:
                data = json.loads(request.POST.get("data"))
                print(data)
            except:
                print("the data is none.")
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
            medical_record_number = data["medical_record_number"]
            print("files: ", request.FILES.getlist("images"))
            t_folder = 'E:\\1. Lab\\Projects\\Medical Image Analytics System\\mias_with_lirads\\mias\\medical_image\\'+str(medical_record_number)
            if not os.path.isdir(t_folder):
                os.mkdir(t_folder)
            t_folder_cur = os.path.join(t_folder, medical_record_number+"_"+str(acq_date).replace("/", ""))
            if not os.path.isdir(t_folder_cur):
                os.mkdir(t_folder)
            try:
                for k in keys:
                    k_folder = t_folder_cur+"\\"+k.split("_")[1]
                    if not os.path.isdir(k_folder):
                        os.mkdir(k_folder)
                    for c, x in enumerate(request.FILES.getlist(k)):
                        print(x)
                        def process(f):
                            with open(k_folder+'/' + str(f).zfill(5), 'wb+') as destination:
                                for chunk in f.chunks():

                                    destination.write(chunk)
                        process(x)
                i = Image()
                result = i.register_images(uploader_id, img_type, t_folder_cur, acq_date, first_name, last_name,
                                           birthday, gender, examination_source, interpretation, description, medical_record_number)
                return JsonResponse({"state": result})
            except Exception as e:
                print(e)
                return JsonResponse({"state": False})
        except Exception as e:
            print(e)
            return JsonResponse({"state": False})
    else:
        print("else")
        return JsonResponse({"state": False})


def get_max_img_count(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        img_id = data['img_id']
        try:
            i = Image()
            result = i.retrieve_images(img_id=img_id)
            img_path = result[0]['img_path']
            file_list = os.listdir(img_path)
            result = {}
            extension = ""
            for i in file_list:
                p = img_path+"\\"+i
                f_list = os.listdir(p)
                result[i] = len(f_list)
                extension = f_list[0].split(".")[-1]
            return JsonResponse({"state": True, "data": {"length": result, "extension": extension}})
        except:
            return JsonResponse({"state": False, "data": 0})


def send_images(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        img_id = data['img_id']
        img_loc = data['img_loc']
        cur_phase = data["cur_phase"]
        try:
            i = Image()
            result = i.retrieve_images(img_id=img_id)
            img_path = result[0]['img_path']+cur_phase+"\\"
            file_list = os.listdir(img_path)
            extension = file_list[img_loc].split(".")[-1]
            print(img_path+file_list[img_loc])
            if extension == "dcm":
                with open(img_path+file_list[img_loc], 'rb') as f:

                    file_data = f.read()
                    # file_data = base64.b64encode(f.read())
                return HttpResponse(file_data, content_type="application/dicom")
            else:

                with open(img_path+file_list[img_loc], 'rb') as f:

                    file_data = base64.b64encode(f.read())
                return HttpResponse(file_data, content_type="image/png")
        except:
            return JsonResponse({"state": False})
    else:
        return JsonResponse({"state": False})


def send_dicom(request, img_id, phase, img_loc):
    if request.method == "GET":
        img_loc = int(img_loc)
        print(img_id, phase, img_loc)
        i = Image()
        result = i.retrieve_images(img_id=img_id)
        img_path = result[0]['img_path']+phase+"\\"
        file_list = os.listdir(img_path)
        extension = file_list[img_loc].split(".")[-1]
        if extension == "dcm":
            with open(img_path+file_list[img_loc], 'rb') as f:

                file_data = f.read()
            return HttpResponse(file_data, content_type="application/dicom")
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
def encode_medical_img(request):
    if request.method == "POST":
        # TODO: To save medical images and segmentation results
        # To save medical image

        # To save segmentation results


        # To enhance the medical images


        return JsonResponse({"state": True, "data":{"num_slice": 86, "hu_start": -160, "hu_end": 240}})
    else:
        return JsonResponse({"state":False})


@csrf_exempt
def load_img_list_step2(request):
    if request.method == "POST":
        list_titles = []
        list_imgs = []
        list_segs = []
        # To load slice
        path_sl = r"D:\Dataset\Liver TUmor Dataset (Medical Decathlon)\images_Training\066"
        path_seg = r"E:\1. Lab\Daily Results\2022\2205\0501\066\0. origin_seg"
        for i in os.listdir(path_sl):
            list_titles.append("SL"+str(int(i.split("_")[1].replace(".png", ""))).zfill(3))
            list_imgs.append(convert_img_to_bytes(cv2.imread(os.path.join(path_sl, i), cv2.IMREAD_GRAYSCALE)))
        for i in os.listdir(path_seg):
            list_segs.append(convert_img_to_bytes(cv2.imread(os.path.join(path_seg, i), cv2.IMREAD_GRAYSCALE)))

        return JsonResponse({"state": True, "data":{"ids":list_titles, "sls":list_imgs, "segs": list_segs}})
    else:
        return JsonResponse({"state":False})

@csrf_exempt
def identify_continuity_sequence(request):
    if request.method == "POST":
        list_titles = []
        list_imgs = []
        list_segs = {}
        # To load slice
        path_sqs = r"E:\1. Lab\Daily Results\2022\2204\0425\Enhancement Results,1118a\066\0.sequences"
        num_true = 1
        num_false = 1
        time.sleep(2)
        cur = -1
        for i in os.listdir(path_sqs):
            if cur == -1:
                cur = i
            for j in os.listdir(os.path.join(path_sqs, i)):
                list_imgs.append(convert_img_to_bytes(cv2.imread(os.path.join(path_sqs, i, j), cv2.IMREAD_GRAYSCALE)))
                if np.count_nonzero(cv2.imread(os.path.join(path_sqs, i, j)))>0:
                    list_segs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_True_"+str(int(int(i)/2+1))
                else:
                    list_segs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_False_"+str(int(math.floor(int(i)/2)+1))
        return JsonResponse({"state": True, "data":{"seqs": list_segs, "imgs":list_imgs, "num_seq": len(os.listdir(os.path.join(path_sqs)))}})
    else:
        return JsonResponse({"state":False})

@csrf_exempt
def load_img_list_step3(request):
    if request.method == "POST":
        list_titles = []
        list_imgs = []
        list_segs = []
        list_seqs = {}
        # To load slice
        path_sl = r"D:\Dataset\Liver TUmor Dataset (Medical Decathlon)\images_Training\066"
        path_seg = r"E:\1. Lab\Daily Results\2022\2205\0501\066\0. origin_seg"
        path_sqs = r"E:\1. Lab\Daily Results\2022\2204\0425\Enhancement Results,1118a\066\0.sequences"
        for i in os.listdir(path_sl):
            list_titles.append("SL"+str(int(i.split("_")[1].replace(".png", ""))).zfill(3))
            list_imgs.append(convert_img_to_bytes(cv2.imread(os.path.join(path_sl, i), cv2.IMREAD_GRAYSCALE)))
        for i in os.listdir(path_seg):
            list_segs.append(convert_img_to_bytes(cv2.imread(os.path.join(path_seg, i), cv2.IMREAD_GRAYSCALE)))
        cur = -1
        for i in os.listdir(path_sqs):
            if cur == -1:
                cur = i
            for j in os.listdir(os.path.join(path_sqs, i)):
                list_imgs.append(convert_img_to_bytes(cv2.imread(os.path.join(path_sqs, i, j), cv2.IMREAD_GRAYSCALE)))
                if np.count_nonzero(cv2.imread(os.path.join(path_sqs, i, j)))>0:
                    list_seqs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_True_"+str(int(int(i)/2+1))
                else:
                    list_seqs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_False_"+str(int(math.floor(int(i)/2)+1))
        # To load

        return JsonResponse({"state": True, "data":{"ids":list_titles, "sls":list_imgs, "segs": list_segs, "seqs": list_seqs}})
    else:
        return JsonResponse({"state":False})

@csrf_exempt
def detect_appearance_violation(request):
    if request.method == "POST":
        list_diffs = []
        # To load slice
        path_bef = r"E:\1. Lab\Daily Results\2022\2204\0425\Enhancement Results,1118a\066\0.sequences"
        path_aft = r"E:\1. Lab\Daily Results\2022\2205\0501\066\1.appearance"
        list_bef = []
        list_aft = []
        list_names = []
        time.sleep(2)
        for i in os.listdir(path_bef):
            for j in os.listdir(os.path.join(path_bef, i)):
                list_bef.append(cv2.imread(os.path.join(path_bef, i, j), cv2.IMREAD_GRAYSCALE))
                list_names.append("SL"+str(int(j.replace(".png", ""))+1).zfill(3))
        for i in os.listdir(path_aft):
            for j in os.listdir(os.path.join(path_aft, i)):
                list_aft.append(cv2.imread(os.path.join(path_aft, i, j), cv2.IMREAD_GRAYSCALE))

        for i in range(len(list_names)):
            if np.count_nonzero(cv2.subtract(list_bef[i], list_aft[i])) >0:
                list_diffs.append(list_names[i])
        return JsonResponse({"state": True, "data":{"diffs": list_diffs}})
    else:
        return JsonResponse({"state":False})

@csrf_exempt
def remedy_appearance_violation(request):
    if request.method == "POST":
        list_titles = []
        list_imgs = []
        list_segs = {}
        # To load slice
        path_sqs = r"E:\1. Lab\Daily Results\2022\2205\0501\066\1.appearance"
        time.sleep(2)
        cur = -1
        for i in os.listdir(path_sqs):
            if cur == -1:
                cur = i
            for j in os.listdir(os.path.join(path_sqs, i)):
                list_imgs.append(convert_img_to_bytes(cv2.imread(os.path.join(path_sqs, i, j), cv2.IMREAD_GRAYSCALE)))
                if np.count_nonzero(cv2.imread(os.path.join(path_sqs, i, j)))>0:
                    list_segs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_True_"+str(int(int(i)/2+1))
                else:
                    list_segs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_False_"+str(int(math.floor(int(i)/2)+1))
        return JsonResponse({"state": True, "data":{"imgs": list_imgs, "seqs": list_segs}})
    else:
        return JsonResponse({"state":False})

@csrf_exempt
def load_img_list_step4(request):
    if request.method == "POST":
        list_titles = []
        list_imgs = []
        list_segs = []
        list_seqs = {}
        # To load slice
        path_sl = r"D:\Dataset\Liver TUmor Dataset (Medical Decathlon)\images_Training\066"
        path_sqs = r"E:\1. Lab\Daily Results\2022\2205\0501\066\1.appearance"
        for i in os.listdir(path_sl):
            list_titles.append("SL"+str(int(i.split("_")[1].replace(".png", ""))).zfill(3))
        cur = -1
        for i in os.listdir(path_sqs):
            if cur == -1:
                cur = i
            for j in os.listdir(os.path.join(path_sqs, i)):
                list_imgs.append(convert_img_to_bytes(cv2.imread(os.path.join(path_sqs, i, j), cv2.IMREAD_GRAYSCALE)))
                if np.count_nonzero(cv2.imread(os.path.join(path_sqs, i, j)))>0:
                    list_seqs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_True_"+str(int(int(i)/2+1))
                else:
                    list_seqs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_False_"+str(int(math.floor(int(i)/2)+1))
        # To load

        return JsonResponse({"state": True, "data":{"ids":list_titles, "sls":list_imgs,  "seqs": list_seqs}})
    else:
        return JsonResponse({"state":False})

@csrf_exempt
def detect_location_violation(request):
    if request.method == "POST":
        list_diffs = []
        # To load slice
        path_bef = r"E:\1. Lab\Daily Results\2022\2204\0425\Enhancement Results,1118a\066\1.appearance"
        path_aft = r"E:\1. Lab\Daily Results\2022\2205\0501\066\2.location"
        list_bef = []
        list_aft = []
        list_names = []
        time.sleep(2)
        for i in os.listdir(path_bef):
            for j in os.listdir(os.path.join(path_bef, i)):
                list_bef.append(cv2.imread(os.path.join(path_bef, i, j), cv2.IMREAD_GRAYSCALE))
                list_names.append("SL"+str(int(j.replace(".png", ""))+1).zfill(3))
        for i in os.listdir(path_aft):
            for j in os.listdir(os.path.join(path_aft, i)):
                list_aft.append(cv2.imread(os.path.join(path_aft, i, j), cv2.IMREAD_GRAYSCALE))

        for i in range(len(list_names)):
            if np.count_nonzero(cv2.subtract(list_bef[i], list_aft[i])) >0:
                list_diffs.append(list_names[i])
        return JsonResponse({"state": True, "data":{"diffs": list_diffs}})
    else:
        return JsonResponse({"state":False})

@csrf_exempt
def remedy_location_violation(request):
    if request.method == "POST":
        list_titles = []
        list_imgs = []
        list_segs = {}
        # To load slice
        path_sqs = r"E:\1. Lab\Daily Results\2022\2205\0501\066\2.location"
        time.sleep(2)
        cur = -1
        for i in os.listdir(path_sqs):
            if cur == -1:
                cur = i
            for j in os.listdir(os.path.join(path_sqs, i)):
                list_imgs.append(convert_img_to_bytes(cv2.imread(os.path.join(path_sqs, i, j), cv2.IMREAD_GRAYSCALE)))
                if np.count_nonzero(cv2.imread(os.path.join(path_sqs, i, j)))>0:
                    list_segs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_True_"+str(int(int(i)/2+1))
                else:
                    list_segs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_False_"+str(int(math.floor(int(i)/2)+1))
        return JsonResponse({"state": True, "data":{"imgs": list_imgs, "seqs": list_segs}})
    else:
        return JsonResponse({"state":False})

@csrf_exempt
def load_img_list_step5(request):
    if request.method == "POST":
        list_titles = []
        list_imgs = []
        list_segs = []
        list_seqs = {}
        # To load slice
        path_sl = r"D:\Dataset\Liver TUmor Dataset (Medical Decathlon)\images_Training\066"
        path_sqs = r"E:\1. Lab\Daily Results\2022\2205\0501\066\2.location"
        for i in os.listdir(path_sl):
            list_titles.append("SL"+str(int(i.split("_")[1].replace(".png", ""))).zfill(3))
        cur = -1
        for i in os.listdir(path_sqs):
            if cur == -1:
                cur = i
            for j in os.listdir(os.path.join(path_sqs, i)):
                list_imgs.append(convert_img_to_bytes(cv2.imread(os.path.join(path_sqs, i, j), cv2.IMREAD_GRAYSCALE)))
                if np.count_nonzero(cv2.imread(os.path.join(path_sqs, i, j)))>0:
                    list_seqs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_True_"+str(int(int(i)/2+1))
                else:
                    list_seqs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_False_"+str(int(math.floor(int(i)/2)+1))
        # To load

        return JsonResponse({"state": True, "data":{"ids":list_titles, "sls":list_imgs,  "seqs": list_seqs}})
    else:
        return JsonResponse({"state":False})


@csrf_exempt
def detect_size_violation(request):
    if request.method == "POST":
        list_diffs = []
        # To load slice
        path_bef = r"E:\1. Lab\Daily Results\2022\2204\0425\Enhancement Results,1118a\066\2.location"
        path_aft = r"E:\1. Lab\Daily Results\2022\2205\0501\066\3.size"
        list_bef = []
        list_aft = []
        list_names = []
        time.sleep(2)
        for i in os.listdir(path_bef):
            for j in os.listdir(os.path.join(path_bef, i)):
                list_bef.append(cv2.imread(os.path.join(path_bef, i, j), cv2.IMREAD_GRAYSCALE))
                list_names.append("SL"+str(int(j.replace(".png", ""))+1).zfill(3))
        for i in os.listdir(path_aft):
            for j in os.listdir(os.path.join(path_aft, i)):
                list_aft.append(cv2.imread(os.path.join(path_aft, i, j), cv2.IMREAD_GRAYSCALE))

        for i in range(len(list_names)):
            if np.count_nonzero(cv2.subtract(list_bef[i], list_aft[i])) > 0:
                list_diffs.append(list_names[i])
        return JsonResponse({"state": True, "data": {"diffs": list_diffs}})
    else:
        return JsonResponse({"state": False})


@csrf_exempt
def remedy_size_violation(request):
    if request.method == "POST":
        list_titles = []
        list_imgs = []
        list_segs = {}
        # To load slice
        path_sqs = r"E:\1. Lab\Daily Results\2022\2205\0501\066\3.size"
        time.sleep(2)
        cur = -1
        for i in os.listdir(path_sqs):
            if cur == -1:
                cur = i
            for j in os.listdir(os.path.join(path_sqs, i)):
                list_imgs.append(convert_img_to_bytes(cv2.imread(os.path.join(path_sqs, i, j), cv2.IMREAD_GRAYSCALE)))
                if np.count_nonzero(cv2.imread(os.path.join(path_sqs, i, j)))>0:
                    list_segs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_True_"+str(int(int(i)/2+1))
                else:
                    list_segs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_False_"+str(int(math.floor(int(i)/2)+1))
        return JsonResponse({"state": True, "data":{"imgs": list_imgs, "seqs": list_segs}})
    else:
        return JsonResponse({"state":False})


@csrf_exempt
def load_img_list_step6(request):
    if request.method == "POST":
        list_titles = []
        list_imgs = []
        list_segs = []
        list_seqs = {}
        # To load slice
        path_sl = r"D:\Dataset\Liver TUmor Dataset (Medical Decathlon)\images_Training\066"
        path_sqs = r"E:\1. Lab\Daily Results\2022\2205\0501\066\3.size"
        for i in os.listdir(path_sl):
            list_titles.append("SL"+str(int(i.split("_")[1].replace(".png", ""))).zfill(3))
        cur = -1
        for i in os.listdir(path_sqs):
            if cur == -1:
                cur = i
            for j in os.listdir(os.path.join(path_sqs, i)):
                list_imgs.append(convert_img_to_bytes(cv2.imread(os.path.join(path_sqs, i, j), cv2.IMREAD_GRAYSCALE)))
                if np.count_nonzero(cv2.imread(os.path.join(path_sqs, i, j)))>0:
                    list_seqs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_True_"+str(int(int(i)/2+1))
                else:
                    list_seqs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_False_"+str(int(math.floor(int(i)/2)+1))
        # To load

        return JsonResponse({"state": True, "data":{"ids":list_titles, "sls":list_imgs,  "seqs": list_seqs}})
    else:
        return JsonResponse({"state":False})


@csrf_exempt
def detect_shape_violation(request):
    if request.method == "POST":
        list_diffs = []
        # To load slice
        path_bef = r"E:\1. Lab\Daily Results\2022\2204\0425\Enhancement Results,1118a\066\3.size"
        path_aft = r"E:\1. Lab\Daily Results\2022\2205\0501\066\4.shape"
        list_bef = []
        list_aft = []
        list_names = []
        time.sleep(2)
        for i in os.listdir(path_bef):
            for j in os.listdir(os.path.join(path_bef, i)):
                list_bef.append(cv2.imread(os.path.join(path_bef, i, j), cv2.IMREAD_GRAYSCALE))
                list_names.append("SL"+str(int(j.replace(".png", ""))+1).zfill(3))
        for i in os.listdir(path_aft):
            for j in os.listdir(os.path.join(path_aft, i)):
                list_aft.append(cv2.imread(os.path.join(path_aft, i, j), cv2.IMREAD_GRAYSCALE))

        for i in range(len(list_names)):
            if np.count_nonzero(cv2.subtract(list_bef[i], list_aft[i])) > 0:
                list_diffs.append(list_names[i])
        return JsonResponse({"state": True, "data": {"diffs": list_diffs}})
    else:
        return JsonResponse({"state": False})


@csrf_exempt
def remedy_shape_violation(request):
    if request.method == "POST":
        list_titles = []
        list_imgs = []
        list_segs = {}
        # To load slice
        path_sqs = r"E:\1. Lab\Daily Results\2022\2205\0501\066\4.shape"
        time.sleep(2)
        cur = -1
        for i in os.listdir(path_sqs):
            if cur == -1:
                cur = i
            for j in os.listdir(os.path.join(path_sqs, i)):
                list_imgs.append(convert_img_to_bytes(cv2.imread(os.path.join(path_sqs, i, j), cv2.IMREAD_GRAYSCALE)))
                if np.count_nonzero(cv2.imread(os.path.join(path_sqs, i, j)))>0:
                    list_segs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_True_"+str(int(int(i)/2+1))
                else:
                    list_segs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_False_"+str(int(math.floor(int(i)/2)+1))
        return JsonResponse({"state": True, "data":{"imgs": list_imgs, "seqs": list_segs}})
    else:
        return JsonResponse({"state":False})


@csrf_exempt
def load_img_list_step7(request):
    if request.method == "POST":
        list_titles = []
        list_imgs = []
        list_segs = []
        list_seqs = {}
        # To load slice
        path_sl = r"D:\Dataset\Liver TUmor Dataset (Medical Decathlon)\images_Training\066"
        path_sqs = r"E:\1. Lab\Daily Results\2022\2205\0501\066\4.shape"
        for i in os.listdir(path_sl):
            list_titles.append("SL"+str(int(i.split("_")[1].replace(".png", ""))).zfill(3))
        cur = -1
        for i in os.listdir(path_sqs):
            if cur == -1:
                cur = i
            for j in os.listdir(os.path.join(path_sqs, i)):
                list_imgs.append(convert_img_to_bytes(cv2.imread(os.path.join(path_sqs, i, j), cv2.IMREAD_GRAYSCALE)))
                if np.count_nonzero(cv2.imread(os.path.join(path_sqs, i, j)))>0:
                    list_seqs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_True_"+str(int(int(i)/2+1))
                else:
                    list_seqs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_False_"+str(int(math.floor(int(i)/2)+1))
        # To load

        return JsonResponse({"state": True, "data":{"ids":list_titles, "sls":list_imgs,  "seqs": list_seqs}})
    else:
        return JsonResponse({"state":False})


@csrf_exempt
def detect_hu_violation(request):
    if request.method == "POST":
        list_diffs = []
        # To load slice
        path_bef = r"E:\1. Lab\Daily Results\2022\2204\0425\Enhancement Results,1118a\066\4.shape"
        path_aft = r"E:\1. Lab\Daily Results\2022\2205\0501\066\5.result"
        list_bef = []
        list_aft = []
        list_names = []
        time.sleep(2)
        for i in os.listdir(path_bef):
            for j in os.listdir(os.path.join(path_bef, i)):
                list_bef.append(cv2.imread(os.path.join(path_bef, i, j), cv2.IMREAD_GRAYSCALE))
                list_names.append("SL"+str(int(j.replace(".png", ""))+1).zfill(3))
        for i in os.listdir(path_aft):
            for j in os.listdir(os.path.join(path_aft, i)):
                list_aft.append(cv2.imread(os.path.join(path_aft, i, j), cv2.IMREAD_GRAYSCALE))

        for i in range(len(list_names)):
            if np.count_nonzero(cv2.subtract(list_bef[i], list_aft[i])) > 0:
                list_diffs.append(list_names[i])
        return JsonResponse({"state": True, "data": {"diffs": list_diffs}})
    else:
        return JsonResponse({"state": False})


@csrf_exempt
def remedy_hu_violation(request):
    if request.method == "POST":
        list_titles = []
        list_imgs = []
        list_segs = {}
        # To load slice
        path_sqs = r"E:\1. Lab\Daily Results\2022\2205\0501\066\5.result"
        time.sleep(2)
        cur = -1
        for i in os.listdir(path_sqs):
            if cur == -1:
                cur = i
            for j in os.listdir(os.path.join(path_sqs, i)):
                list_imgs.append(convert_img_to_bytes(cv2.imread(os.path.join(path_sqs, i, j), cv2.IMREAD_GRAYSCALE)))
                if np.count_nonzero(cv2.imread(os.path.join(path_sqs, i, j)))>0:
                    list_segs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_True_"+str(int(int(i)/2+1))
                else:
                    list_segs["SL"+str(int(j.replace(".png", ""))).zfill(3)] = "Seq_False_"+str(int(math.floor(int(i)/2)+1))
        return JsonResponse({"state": True, "data":{"imgs": list_imgs, "seqs": list_segs}})
    else:
        return JsonResponse({"state":False})






@csrf_exempt
def sign_out(request):
    # try:
    sess = Session()
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        ids = data['identification_number']
        result = sess.expire_session(ids)
        if result:
            print("logged out")
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
            request.session['user'] = results[0]
            cur_users = request.session.get('user')
            try:
                results[0]['birthday'] = results[0]['birthday'].strftime('%Y-%m-%d')
            except:
                results[0]['birthday'] = ""
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
def add_role(request):
    if request.method == "POST":
        # try:
            data = json.loads(request.body.decode('utf-8'))
            id = data['id']
            role = data['role']
            role_data = data["role_data"]
            u = User()
            cur_role = u.retrieve_user(identification_number=id)[0]["role"]
            print(cur_role)
            roles = cur_role.split(" ")
            if role in roles:
                return JsonResponse({'state': False})
            else:
                result = u.modify_user(identification_number=id, role=cur_role+" "+role)
                print("upadted ___>>>", result)
                if result:
                    if role == "Physician":
                        physician = Physician()
                        result = physician.add_physician(id, role_data)
                        return JsonResponse({'state': result})
                    elif role == "Patient":
                        patient = Patient()
                        result = patient.add_patient(id, role_data)
                        return JsonResponse({'state': result})
                    elif role == "Staff":
                        staff = Staff()
                        result = staff.add_staff(id, role_data)
                        return JsonResponse({'state': result})
                    else:
                        return JsonResponse({'state': False})
                else:
                    return JsonResponse({'state': False})
        # except:
        #     return JsonResponse({'state': False})
    else:
        return JsonResponse({'state': False})

@csrf_exempt
def modify_role(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            id = data['id']
            role = data['role']
            u = User()
            cur_role = u.retrieve_user(identification_number=id)[0]["role"]
            roles = cur_role.split(" ")
            if role in roles:
                return JsonResponse({'state': False})
            else:
                result = u.modify_user(identification_number=id, role=cur_role+" "+role)
                if result:
                    if role == "Physician":
                        physician = Physician()
                        result = physician.add_physician(id)
                        return JsonResponse({'state': result})
                    elif role == "Patient":
                        patient = Patient()
                        result = patient.add_patient(id)
                        return JsonResponse({'state': result})
                    elif role == "Staff":
                        staff = Staff()
                        result = staff.add_staff(id)
                        return JsonResponse({'state': result})
                    else:
                        return JsonResponse({'state': False})
                else:
                    return JsonResponse({'state': False})
        except:
            return JsonResponse({'state': False})
    else:
        return JsonResponse({'state': False})

@csrf_exempt
def remove_role(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            id = data['id']
            role = data['role']
            u = User()
            cur_role = u.retrieve_user(identification_number=id)[0]["role"]
            roles = cur_role.split(" ")
            if role in roles:
                return JsonResponse({'state': False})
            else:
                result = u.modify_user(identification_number=id, role=cur_role+" "+role)
                if result:
                    if role == "Physician":
                        physician = Physician()
                        result = physician.delete_physician(id)
                        return JsonResponse({'state': result})
                    elif role == "Patient":
                        patient = Patient()
                        result = patient.delete_patient(id)
                        return JsonResponse({'state': result})
                    elif role == "Staff":
                        staff = Staff()
                        result = staff.delete_staff(id)
                        return JsonResponse({'state': result})
                    else:
                        return JsonResponse({'state': False})
                else:
                    return JsonResponse({'state': False})
        except:
            return JsonResponse({'state': False})
    else:
        return JsonResponse({'state': False})

@csrf_exempt
def change_role_order(request):
    if request.method == "POST":
        # try:
        data = json.loads(request.body.decode('utf-8'))
        id = data['id']
        role = data['role']
        u = User()
        cur_role = u.retrieve_user(identification_number=id)[0]["role"]
        roles = cur_role.split(" ")
        roles.remove(role)
        roles.insert(0, role)
        u.modify_user(identification_number=id, role=" ".join(roles))
        return JsonResponse({"state": True})
        # except:
        #     return JsonResponse({"state": False})
    else:
        return JsonResponse({"state": False})


@csrf_exempt
def retrieve_role(request):
    if request.method == "POST":
        # try:
            data = json.loads(request.body.decode('utf-8'))
            id = data['id']
            role = data['role']
            if role == "Physician":
                physician = Physician()
                result = physician.retrieve_physician(identification_number=id)[0]
                return JsonResponse({'state': True, "data": result})
            elif role == "Patient":
                patient = Patient()
                result = patient.retrieve_patient(identification_number=id)[0]
                return JsonResponse({'state': True, "data": result})
            elif role == "Staff":
                staff = Staff()
                result = staff.retrieve_staff(identification_number=id)[0]
                return JsonResponse({'state': True, "data": result})
            else:
                return JsonResponse({'state': False})
        # except:
        #     return JsonResponse({'state': False})
    else:
        return JsonResponse({'state': False})

@csrf_exempt
def sign_up(request):
    if request.method == "POST":
        # try:
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        print(data['role'])
        data['role'] = " ".join(data['role'])
        print("role", data['role'])
        role_data = data['role_data']
        u = User()
        akg = ActivationKeyGenerator()
        a_k = akg.get_key()
        result = u.register_user(first_name=data['first_name'], last_name=data['last_name'], email=data["email"],
                        phone_number=data["phone_number"], pwd=data["pwd"], role=data['role'], active=0,
                                 activation_code=a_k, gender=data['gender'], birthday=data['birthday'])
        print("sign_up", result)
        if result:
            if "Physician" in data['role']:
                u = Physician()
                result = u.register_physician(first_name=data['first_name'], last_name=data['last_name'], email=data["email"],
                                phone_number=data["phone_number"], pwd=data["pwd"], role=data['role'], active=0, role_data=role_data)
            if "Patient" in data['role']:
                u = Patient()
                result = u.register_patient(first_name=data['first_name'], last_name=data['last_name'], email=data["email"],
                                phone_number=data["phone_number"], pwd=data["pwd"], role=data['role'], active=0, role_data=role_data)
            if "Staff" in data['role']:
                s = Staff()
                result = s.register_staff(first_name=data['first_name'], last_name=data['last_name'], email=data["email"],
                                phone_number=data["phone_number"], pwd=data["pwd"], role=data['role'], active=0, role_data=role_data)
            if result:
                # snder = MailSender()

                u_id = u.retrieve_user(first_name=data['first_name'], last_name=data['last_name'], email=data["email"],
                                       phone_number=data["phone_number"], pwd=data["pwd"], role=data['role'])[0][
                    'identification_number']
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
                return JsonResponse({'state': True, "data": "We sent an email to your email. You can change your"
                                                            " password following the email. Please check your email."})
            else:
                return JsonResponse({'state': False, "data": "Check your information again. Your email is already signed up."})

        else:
            return JsonResponse({'state': False, "data": "Check your information again. Your email is already signed up."})
            # if "Physician" in data['role']:
            #     u = Physician()
            #     result = u.register_physician(email=data["email"])
            # if "Patient" in data['role']:
            #     u = Patient()
            #     result = u.register_patient(first_name=data['first_name'], last_name=data['last_name'], email=data["email"],
            #                     phone_number=data["phone_number"], pwd=data["pwd"], role=data['role'], active=0)
            # if "Staff" in data['role']:
            #     s = Staff()
            #     result = s.register_staff(first_name=data['first_name'], last_name=data['last_name'], email=data["email"],
            #                     phone_number=data["phone_number"], pwd=data["pwd"], role=data['role'], active=0)
            #
            # if result:
            #     return JsonResponse({'state': True, "data": "Because your account was already made, only current role is added."})
            # else:
            #     return JsonResponse(
            #         {'state': False, "data": "Check your input information. It's already recorded."})
        # except:
        #     return JsonResponse({'state': False, "data": "Check your information again."})


@csrf_exempt
def change_pwd(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        target_pwd = data['target_pwd']
        id = data["id"]
        u = User()
        result = u.modify_user(identification_number=id, pwd=target_pwd)
        if result:
            return JsonResponse({'state': True})
        else:
            return JsonResponse({'state': False})
    else:
        return JsonResponse({'state': False})


@csrf_exempt
def get_current_user_info(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        id = data["id"]
        try:
            user = User()
            cur_user = user.retrieve_user(identification_number=id)
            if cur_user:
                return JsonResponse({"state": True, "data": cur_user[0]})
            else:
                return JsonResponse({"state": True})
        except:
            return JsonResponse({"state": True})
    else:
        return JsonResponse({'state': False})


@csrf_exempt
def modify_general_info(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        id = data['id']
        first_name = data["first_name"]
        last_name = data["last_name"]
        gender = data["gender"]
        birthday = data["birthday"]
        phone = data["phone"]

        u = User()
        result = u.modify_user(identification_number=id, first_name=first_name, last_name=last_name,
                               gender=gender, birthday=birthday, phone_number=phone)
        print(result)
        result = u.retrieve_user(identification_number=id)
        try:
            result[0]['birthday'] = result[0]['birthday'].strftime('%Y-%m-%d')
        except:
            result[0]['birthday'] = ""
        if result:
            return JsonResponse({'state': True, "data": result})
        else:
            return JsonResponse({'state': False})
    else:
        return JsonResponse({'state': False})


@csrf_exempt
def withdraw(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        id = data['id']
        s = Session()
        result = s.expire_session(id)
        print("Session: ", result )
        if result:
            phy = Physician()
            res_phy = phy.delete_physician(id)

            print("Phy: ", res_phy)
            pat = Patient()
            res_pat = pat.delete_patient(id)
            print("Pat: ", res_pat)

            s = Staff()
            res_s = s.delete_staff(id)
            print("Staff: ", res_s)
            u = User()
            res_u = u.delete_user(id)
            print("Staff: ", res_u)
            if res_u:
                return JsonResponse({'state': True})
            else:
                return JsonResponse({'state': False})
        else:
            return JsonResponse({'state': False})

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
def update_session(old_user, updated_user):
    for key, value in updated_user.items():
        if key in old_user:
            old_user[key] = value
    return old_user

@csrf_exempt
def initialize_diagnosis_env(request):
    if request.method == "POST":
        container.mias_container.lirads_process.initialize_env()
        return JsonResponse({'state': True})
    else:
        return JsonResponse({'state': False})

@csrf_exempt
def post_process_liver(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        step = data["step"]
        srs = data["cur_phase_id"]
        list_img, list_console = container.mias_container.lirads_process.post_process_liver(srs, step)
        print("Number of Imagess: ", len(list_img))
        return JsonResponse({"state": True, "img": list_img, "console": list_console})
    else:
        return JsonResponse({"state": False})

@csrf_exempt
def set_img_type(request):
    if request.method == "POST":
        print(request.POST.get("data"))
        data = json.loads(request.POST.get("data"))
        img_type = data["type"]
        container.mias_container.lirads_process.set_mi_type(img_type)
        return JsonResponse({"state":True})
    else:
        return JsonResponse({"state":False})

@csrf_exempt
def step1_save_imgs(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))

        target = data["img"]
        pat_name = data["pat_name"]
        type = data["type"]
        files = request.FILES.getlist("files")

        root_path = r"E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\medical_image"
        cur_path = ""

        if not os.path.isdir(os.path.join(root_path, pat_name)):
            os.mkdir(os.path.join(root_path, pat_name))
            cur_path = os.path.join(root_path, pat_name, "0")
        else:
            cur_path = os.path.join(root_path, pat_name, str(len(os.path.join(root_path, pat_name))))
        if type == "srs":
            cur_path = os.path.join(cur_path, "srs")
        elif type == "seg_result":
            cur_path = os.path.join(cur_path, "seg_result")

        format = None
        for c, x in enumerate(files):
            def process(f):
                with open(cur_path + '/' + str(f).zfill(5), 'wb+') as destination:
                    print(destination.name)
                    format = destination.name.split(".")[-1]
                    for chunk in f.chunks():
                        destination.write(chunk)
                return format
            format = process(x)
        print(format)
        type = container.mias_container.lirads_process.get_mi_type()
        return JsonResponse({'state': True, "data":{"format":format, "type":type}})
    else:
        return JsonResponse({'state': False})


@csrf_exempt
def step1_load_prv_img_data_from_local(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        pat_name = data["pat_name"]
        pat_birth = data["pat_birth"]
        mrn = data["mrn"]
        container.mias_container.lirads_process.set_mrn(mrn)
        container.mias_container.lirads_process.set_patient_name(pat_name)
        container.mias_container.lirads_process.set_birthday(pat_birth)
        container.mias_container.lirads_process.set_mi_path(data["img_path"])
        return JsonResponse({'state': True})
    else:
        return JsonResponse({'state': False})


@csrf_exempt
def step1_check_extension(request):
    if request.method == "POST":
        container.mias_container.lirads_process.check_extension()
        return JsonResponse({'state': True})
    else:
        return JsonResponse({'state': False})


@csrf_exempt
def step1_load_medical_img(request):
    if request.method == "POST":
        container.mias_container.lirads_process.load_medical_img()
        return JsonResponse({'state': True})
    else:
        return JsonResponse({'state': False})


@csrf_exempt
def step1_convert_color_depth(request):
    if request.method == "POST":
        container.mias_container.lirads_process.convert_color_depth()
        return JsonResponse({'state': True})
    else:
        return JsonResponse({'state': False})


@csrf_exempt
def load_file_list(request):
    if request.method == "POST":
        list_data, list_imgs, phase_info = container.mias_container.lirads_process.get_whole_img_data()
        return JsonResponse({"state": True, "data": list_data, "imgs": list_imgs, "phase_info": phase_info})
    else:
        return JsonResponse({"state": False})

@csrf_exempt
def load_tumor_list(request):
    if request.method == "POST":
        list_data, list_imgs = container.mias_container.lirads_process.get_tumor_img_data()
        # list_data, list_imgs = [],[]
        return JsonResponse({"state": True, "data": list_data, "imgs": list_imgs})
    else:
        return JsonResponse({"state": False})

@csrf_exempt
def load_tumor_group_list(request):
    if request.method == "POST":
        list_data, list_imgs = [], []
        return JsonResponse({"state": True, "data": list_data, "imgs": list_imgs})
    else:
        return JsonResponse({"state":False})

@csrf_exempt
def segment_liver(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        img_id = data["target_img"]
        list_img, list_console = container.mias_container.lirads_process.segment_liver_region(img_id)
        return JsonResponse({"state": False, "img":list_img, "console":list_console})
    else:
        return JsonResponse({"state": False})


@csrf_exempt
def load_setCT_a(request):
    if request.method == "POST":
        list_data, list_imgs = container.mias_container.lirads_process.get_whole_tumor_seg_targets()
        return JsonResponse({"state": True, "data": list_data, "imgs": list_imgs})
    else:
        return JsonResponse({"state": False})


@csrf_exempt
def segment_tumor(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        img_id = data["target_img"]
        list_img, list_console = container.mias_container.lirads_process.segment_tumor_region(img_id)
        return JsonResponse({"state":False, "img":list_img, "console":list_console})
    else:
        return JsonResponse({"state":False})
    
@csrf_exempt
def evaluate_img_feature(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        img_id = data["target_img"]
        list_img, list_console = container.mias_container.lirads_process.evaluate_img_features(img_id)
        return JsonResponse({"state":False, "img":list_img, "console":list_console})
    else:
        return JsonResponse({"state":False})

@csrf_exempt
def get_tumor_group_data(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        list_data, list_imgs = container.mias_container.lirads_process.get_tumor_group_data()
        return JsonResponse({"state": True, "data": list_data, "imgs": list_imgs})
    else:
        return JsonResponse({"state": False})

@csrf_exempt
def determin_tumor_type(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        list_data = container.mias_container.lirads_process.determin_tumor_type(data["tumor_id"])
        return JsonResponse({"state": True, "data": list_data})
    else:
        return JsonResponse({"state": False})


@csrf_exempt
def compute_lirads_feature(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        list_data = container.mias_container.lirads_process.compute_lirads_features(data["tumor_id"])
        return JsonResponse({"state": True, "data": list_data})
    else:
        return JsonResponse({"state": False})


@csrf_exempt
def load_tumor_group_list_step6(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        list_data = container.mias_container.lirads_process.get_tumor_group_data_step6()
        print("Step 6: ", len(list_data))
        return JsonResponse({"state": True, "data": list_data})
    else:
        return JsonResponse({"state": False})

@csrf_exempt
def load_tumor_lirads_feature_info(request):
    if request.method == "POST":
        list_data = []

        return JsonResponse({"state": True, "data": list_data})
    else:
        return JsonResponse({"state": False})

@csrf_exempt
def get_tumor_info(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        stage = container.mias_container.lirads_process.get_tumor_info()
        return JsonResponse({"state": True, "data": stage})
    else:
        return JsonResponse({"state": False})


@csrf_exempt
def predict_stage(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        stage = container.mias_container.lirads_process.predict_stage(data["tumor_id"])
        return JsonResponse({"state": True, "stage": stage})
    else:
        return JsonResponse({"state": False})


@csrf_exempt
def register_diagnosis(request):
    if request.method == "POST":
        ds = Diagnosis()
        data = json.loads(request.POST.get("data"))

        pat_name = container.mias_container.lirads_process.get_patient_name()
        mrn = container.mias_container.lirads_process.get_mrn()
        birthday = container.mias_container.lirads_process.get_birthday()
        img_id = container.mias_container.lirads_process.get_img_path()

        ds.register_diagnosis(pat_name, mrn, birthday, img_id,
                              data["tumor_types"], data["aphe_types"], data["tumor_sizes"], data["num_mfs"], data["stages"])
        return JsonResponse({"state": True})
    else:
        return JsonResponse({"state": False})


@csrf_exempt
def retrieve_diagnosis(request):
    if request.method == "POST":
        ds = Diagnosis()
        data = json.loads(request.POST.get("data"))
        list_diagnosis = ds.retrieve_diagnosis(data["diagnosis_id"])
        return JsonResponse({"state": True, "data": list_diagnosis})
    else:
        return JsonResponse({"state": False})






## Functions called by APIs
def convert_img_to_bytes(img):
    scs, encoded_img = cv2.imencode(".png", img)
    encoded_img = base64.b64encode(encoded_img.tobytes())
    return encoded_img.decode('utf8')


def convert_bytes_to_img(b):
    bb = base64.b64decode(str(b))
    bytes_io = io.BytesIO(bb)
    img_a = Image.open(bytes_io)
    img = np.array(img_a, dtype=np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img