"""
Date: 2021. 04. 27.
Programmer: MH
Description: Code for computing Li-RADS Features
"""
import os

from miaas.lirads.constant import ImagingFeatures, TumorType
import numpy as np
import cv2
import copy
import math
import datetime

from miaas.lirads.software_process.step_1 import MedicalImageLoader
from miaas.lirads.software_process.step_2 import LiverRegionSegmentater
from miaas.lirads.software_process.step_3 import LesionSegmentor
from miaas.lirads.software_process.step_4 import ImageFeatureEvaluator


class LIRADSFeatureComputer:
    def __init__(self):
        self.num_major_features = 0
        self.aphe_type = ""
        self.lesion_size = 0
        self.has_capsule = False
        self.has_washout = False
        self.has_threshold_growth = False
        self.mi_type = "CT"
        self.setCT_tumor_info = {}

        self.setCT_a = {}
        self.list_lirad_features = {}
        self.voxel = 0.0

    def set_mi_type(self, mi_type):
        self.mi_type = mi_type

    def initialize(self, std_name):
        self.num_major_features = 0
        self.aphe_type = ""
        self.lesion_size = 0
        self.has_capsule = False
        self.has_washout = False
        self.has_threshold_growth = False
        self.setCT_tumor_info = {}

        self.setCT_a = {}
        self.list_lirad_features = {}
        self.voxel = 0.0
        self.std_name = std_name

    def set_tumor_groups(self, tg):
        self.tumor_groups = tg

    def set_setCT_a(self, sa):
        self.setCT_a = sa

    def set_prv_data(self, path_p):
        if path_p==r"" or path_p == None:
            self.setCT_a_prv = {}
            self.prv_tumor_groups = {}
        else:
            self.path_prv_data = path_p
            # Do something for loading previous tumor data or segmenting tumor data

            # After Step 1~4, prv tumor group applied.
            prv_step1 = MedicalImageLoader()
            prv_step2 = LiverRegionSegmentater()
            prv_step3 = LesionSegmentor()
            prv_step4 = ImageFeatureEvaluator()

            # Step 1. Load Medical Image
            prv_step1.set_path(self.path_prv_data)
            prv_step1.check_mi_type()
            prv_step1.load_medical_img()
            prv_step1.convert_color_depth()
            prv_setCT_a = prv_step1.get_setCT_a()
            self.setCT_a_prv = prv_step1.get_setMed_img()

            # Step 2. Segment Liver Region
            prv_step2.set_setCT_b(prv_setCT_a)
            prv_step2.segment_liver_regions()

            setCT_b = prv_step2.get_setCT_b()
            setCT_b_seg = prv_step2.get_setCT_b_seg()

            # Step 3. Segment Lesions
            prv_step3.load_model(self.mi_type)
            prv_step3.segment_lesion(prv_setCT_a, setCT_b_seg)
            prv_setCT_c_tumor = prv_step3.get_setCT_C_tumor()
            prv_setCT_c_seg = prv_step3.get_setCT_c_seg()

            # Step 4. Evaluate Image Features
            prv_step4.generate_slice_group(prv_step1.med_img_format, self.setCT_a_prv)
            prv_step4.make_lesion_group(prv_setCT_c_tumor)
            prv_step4.correct_segmented_lesion_location(prv_step1.acquisition_date)
            prv_step4.evaluate_image_feature(prv_setCT_c_seg)
            prv_step4.discard_insignificant_image_features()
            self.prv_tumor_groups = prv_step4.get_tumor_groups()

    def set_tumor_features(self, tumor_features):
        self.setCT_tumor_info = tumor_features

    def set_tumor_type(self, list_tumor_type):
        self.list_tumor_type = list_tumor_type

    def set_tumor_info(self, setCT_tumor_info):
        self.setCT_tumor_info = setCT_tumor_info

    def get_tumor_type(self):
        """
        To check current tumor type
        :return:
        """
        tumor_types = {}    # {TUMOR_ID: type, TUMOR_ID:type, ...}
        for t_id, info in self.tumor_groups.items():
            tumor_types[t_id] = info["type"]["id"]
        return tumor_types

    def get_APHE_type(self):
        """
        To get APHE type among RimAPHE, NoAPHE, NonrimAPHE
        :return:
        """
        aphe_types = {}
        for t_id, info in self.tumor_groups.items():

            if info["features"]["ARTERIAL"]["WholeConf"][6] >= info["features"]["ARTERIAL"]["WholeConf"][4]:
                aphe_types[t_id] = "Nonrim"
            else:
                aphe_types[t_id] = "No"
            """
            if "NoAPHE" in info["features"]["ARTERIAL"]["Labels"]:
                aphe_types[t_id] = "No"
            elif "NonrimAPHE" in info["features"]["ARTERIAL"]["Labels"]:
                aphe_types[t_id] = "Nonrim"
            else:
                aphe_types[t_id] = "rim"
            """
        return aphe_types

    def compute_lesion_size(self, voxel):
        """
        To compute lesion's size
        :param i: int, index of selected tumor type
        :return:
        """
        self.voxel = voxel
        lesion_sizes = {}
        for t_id, info in self.tumor_groups.items():
            lesion_size = {"length": -1, "mass": -1}
            for srs_id, list_sl in info["mask"].items():
                for (sl_id, sl) in list_sl:
                    cur = self.__compute_lesion_size(sl, voxel)
                    if cur["length"] > lesion_size["length"]:
                        lesion_size = cur
            lesion_sizes[t_id] = lesion_size
        return lesion_sizes

    def check_capsule(self):
        """
        To check capsule among the current lesion's imaging feature
        :return:
        """
        capsules = {}
        for t_id, info in self.tumor_groups.items():
            capsules[t_id] = False
            for srs_id in info["features"].keys():
                if "Capsule" in info["features"][srs_id]["Labels"]:
                    capsules[t_id] = True
                    break
        return capsules

    def check_washout(self):
        """
        To check washout among the current lesion's imaging feature
        :param i: int, index of selected tumor type
        :return:
        """
        washouts = {}
        for t_id, info in self.tumor_groups.items():
            washouts[t_id] = False
            for srs_id in info["features"].keys():
                if "Washout" in info["features"][srs_id]["Labels"]:
                    washouts[t_id] = True
                    break
        return washouts

    def compute_threshold_growth(self):
        """
        To compute threshold growth (to use previous information)
        :param prv_info:
        :return:
        """

        th_growths = {}
        if self.prv_tumor_groups == {}:
            for t_id, info in self.tumor_groups.items():
                th_growths[t_id] = False
        else:
            """
            Firstly, Check diff of acquired date
                IF (acq_cur-acq_prv) <= 6 months, Continue 
                ELSE, Whole tumors' threshold growth is FALSE

            Secondly, each tumor from cur and prv is grouped. Some prv tumors may not be grouped.
                IF prv=>X but cur=>O ==> TH_GROWTH is TRUE

            Thirdly, Check diff of mass.
                IF (mass_cur-mass_prv)/mass_prv >= 0.5, TRUE
                ELSE, FALSE
            """
            # To check date different
            cur_date_str = self.tumor_groups[list(self.tumor_groups.keys())[0]]["ACQ_INFO"]["acq_date"]
            prv_date_str = self.prv_tumor_groups[list(self.prv_tumor_groups.keys())[0]]["ACQ_INFO"]["acq_date"]

            cur_date = datetime.datetime.strptime(cur_date_str, "%Y%m%d")
            prv_date = datetime.datetime.strptime(prv_date_str, "%Y%m%d")
            if (cur_date-prv_date).days > 6*30:  # If the acquired date is over 6 months
                for t_id, info in self.tumor_groups.items():
                    th_growths[t_id] = False
            else:

                for t_id, info in self.tumor_groups.items():
                    th_growths[t_id] = True

                # To check sl Similarity

                self.seCT_cur_spine_bone = self.__enhance_spine_bone_parts_mi(self.setCT_a)
                self.seCT_cur_spine_bone_prv = self.__enhance_spine_bone_parts_mi(self.setCT_a_prv)

                cur_art_phase = self.seCT_cur_spine_bone["ARTERIAL"]
                prv_art_phase = self.seCT_cur_spine_bone_prv["ARTERIAL"]
                list_similar_sl_ids = self.__compute_sl_similarity_group(cur_art_phase, prv_art_phase)

                set_tumor_ids = []  # [(cur_tumor_id, prv_tumor_id), ...]
                for t_id, info in self.tumor_groups.items():
                    # Same Phase, Same Sequence, Same Plane
                    # To need to compare spine bone parts
                    # When comparing location, the CT series acquired at Arterial phase is applied.
                    is_added = False
                    for t_id_p, info_p in self.prv_tumor_groups.items():
                        # To check position of tumor
                        list_cur = list(info["mask"].values()["ARTERIAL"])     # list for cur tumor
                        list_prv = list(info_p["mask"].values()["ARTERIAL"])   # list for prv tumor

                        start_id, end_id = self.__compute_start_end_ids(list_cur, list_similar_sl_ids, True)
                        start_id_prv, end_id_prv = self.__compute_start_end_ids(list_prv, list_similar_sl_ids, False)
                        if not (start_id >= end_id_prv or end_id <= start_id_prv):
                            set_tumor_ids.append((t_id, t_id_p))
                            is_added = True
                            break
                    if not is_added:
                       set_tumor_ids.append((t_id, None))

                for p in set_tumor_ids:
                    cur_tumor_id = p[0]
                    prv_tumor_id = p[1]
                    if prv_tumor_id is not None:
                        cur_lesion_size = {"length": -1, "mass": -1}
                        for srs_id, list_sl in self.tumor_groups[cur_tumor_id]["mask"].items():
                            for (sl_id, sl) in list_sl:
                                cur = self.__compute_lesion_size(sl, self.voxel)
                                if cur["length"] > cur_lesion_size["length"]:
                                    cur_lesion_size = cur
                        prv_lesion_size = {"length": -1, "mass": -1}
                        for srs_id, list_sl in self.tumor_groups[prv_tumor_id]["mask"].items():
                            for (sl_id, sl) in list_sl:
                                cur = self.__compute_lesion_size(sl, self.voxel)
                                if cur["length"] > prv_lesion_size["length"]:
                                    prv_lesion_size = cur
                        if (cur_lesion_size["mass"]-prv_lesion_size["mass"])/prv_lesion_size["mass"] >0.5:
                            th_growths[cur_tumor_id] = True
                        else:th_growths[cur_tumor_id] = False
                    else:
                        th_growths[cur_tumor_id] = True
        return th_growths

    def detect_vein_location(self, setCT_a):
        """
        To detect vein location in slice
        :return:
        """
        setCT_a = setCT_a[list(setCT_a.keys())[0]]
        self.setCT_seg_vein={}
        for srs_name, srs in setCT_a.items():
            self.setCT_seg_vein[srs_name] = {}
            for sl_id, sl in srs.items():
                ## TODO: Apply vein segmentation model
                self.setCT_seg_vein[srs_name][sl_id] = np.array(np.zeros((512, 512)), dtype=np.uint8) # NEED TO FIX

    def compute_tumor_in_vein(self):
        """
        To detect vein location in slice
        :return:
        """
        tivs = {}
        for t_id, info in self.tumor_groups.items():
            tivs[t_id] = False
            for srs_id, list_sl in info["mask"].items():
                for (sl_id, sl) in list_sl:
                    if np.count_nonzero(np.bitwise_and(self.setCT_seg_vein[srs_id][sl_id], sl))>0:
                        tivs[t_id] = True
                        break
        return tivs

    def generate_major_feature_list(self, tumor_types, aphe_types, lesion_sizes, capsules, washouts, th_growths, tivs):
        """
        To generate list for major features of each tumor
        :return:
        """
        # path_save = r"E:\1. Lab\Daily Results\2021\2108\0820\result\step6"
        self.list_major_features = {}
        for t_id in self.tumor_groups.keys():
            num_mf = 0
            if capsules[t_id]:
                num_mf += 1
            if washouts[t_id]:
                num_mf += 1
            if th_growths[t_id]:
                num_mf += 1
            self.tumor_groups[t_id]["major_features"] = {"Tumor_Type": tumor_types[t_id], "APHE_Type": aphe_types[t_id],
                                             "Lesion_Size": lesion_sizes[t_id], "Capsule": capsules[t_id],
                                             "Washout": washouts[t_id], "Threshold_Growth": th_growths[t_id],
                                             "Num_Major_Features": num_mf, "tiv": tivs[t_id]}


            # if not os.path.isdir(os.path.join(path_save, self.std_name)):
            #     os.mkdir(os.path.join(path_save, self.std_name))
            # f = open(os.path.join(path_save, self.std_name, "step_6.txt"), "w")
            # f.write(str(t_id)+"  :  "+str(self.tumor_groups[t_id]["major_features"]))
            # f.close()

    def get_tumor_groups(self):
        return self.tumor_groups

    def get_LIRADS_feature(self):
        return self.list_major_features

    def __compute_start_end_ids(self, list_cur_tumor, list_similar_sl_ids, is_current):
        start = list_cur_tumor[0][0]
        end = list_cur_tumor[-1][1]

        if is_current: k=0
        else: k=1

        start_ct_g_id, end_ct_g_id = -1, -1
        for i in range(len(list_similar_sl_ids)):
            if start == list_similar_sl_ids[i][k]:
                start_ct_g_id = i
            if end == list_similar_sl_ids[i][k]:
                end_ct_g_id = i

        return (start_ct_g_id, end_ct_g_id)


    def __compute_lesion_size(self, obs, voxel):
        """
        To compute lesion's
        :return: float, the lesion's size in the slice
        """
        obs = obs.astype(np.uint8)
        # obs*=255
        contours = self.__find_contours(copy.deepcopy(obs))
        longest = 0
        long_points = {"point1": (), "point2": ()}  #
        mass = 0
        for cnt in contours:
            # To add size measurement Code
            approx = cv2.approxPolyDP(cnt,
                                      0.009 * cv2.arcLength(cnt, True), True)
            for x in range(len(approx)):
                a = approx[x][0]

                for y in range(len(approx)):
                    if x == y:
                        continue
                    else:
                        if x == 0:
                            if y == x or (y == len(approx) - 1) or (y == x + 1):
                                continue
                        elif x == len(approx) - 1:
                            if y == x or (y == x - 1) or (y == 0):
                                continue
                        else:
                            if y == x or (y == x - 1) or (y == x + 1):
                                continue
                    b = approx[y][0]

                    is_intersect = False
                    for z in range(1, len(approx)):
                        if (z - 1 == x or z == x) or (z - 1 == y or z == y):
                            continue
                        prev = self.__doIntersect(a, b, approx[z - 1][0], approx[z][0])
                        if prev:
                            is_intersect = prev
                    if is_intersect:
                        continue
                    length = math.sqrt(float((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2))
                    if longest < length:
                        longest = length
                        long_points['point1'] = tuple(a)
                        long_points['point2'] = tuple(b)
                        mass = cv2.contourArea(cnt)
        return {'length': round(longest * voxel, 3), 'mass': mass}

    def __find_contours(self, img):
        """
        To find contours about tumors in input image
        :param img: ndarray, the masked image of the target lesion
        :return: list, list of contours
        """
        _, threshold = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)
        return contours

    def __doIntersect(self, p1, q1, p2, q2):
        # Find the 4 orientations required for
        # the general and special cases
        o1 = self.__orientation(p1, q1, p2)
        o2 = self.__orientation(p1, q1, q2)
        o3 = self.__orientation(p2, q2, p1)
        o4 = self.__orientation(p2, q2, q1)

        # General case
        if ((o1 != o2) and (o3 != o4)):
            return True

        # Special Cases
        # p1 , q1 and p2 are colinear and p2 lies on segment p1q1
        if ((o1 == 0) and self.__check_is_on_segment(p1, p2, q1)):
            return True

        # p1 , q1 and q2 are colinear and q2 lies on segment p1q1
        if ((o2 == 0) and self.__check_is_on_segment(p1, q2, q1)):
            return True

        # p2 , q2 and p1 are colinear and p1 lies on segment p2q2
        if ((o3 == 0) and self.__check_is_on_segment(p2, p1, q2)):
            return True

        # p2 , q2 and q1 are colinear and q1 lies on segment p2q2
        if ((o4 == 0) and self.__check_is_on_segment(p2, q1, q2)):
            return True

        # If none of the cases
        return False

    def __orientation(self, p, q, r):
        # to find the orientation of an ordered triplet (p,q,r)
        # function returns the following values:
        # 0 : Colinear points
        # 1 : Clockwise points
        # 2 : Counterclockwise

        # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/
        # for details of below formula.

        val = (float(q[1] - p[1]) * (r[0] - q[0])) - (float(q[0] - p[0]) * (r[1] - q[1]))
        if (val > 0):
            # Clockwise orientation
            return 1
        elif (val < 0):
            # Counterclockwise orientation
            return 2
        else:
            # Colinear orientation
            return 0

    def __check_is_on_segment(self, p, q, r):
        if ((q[0] <= max(p[0], r[0])) and (q[0] >= min(p[0], r[0])) and
                (q[1] <= max(p[1], r[1])) and (q[1] >= min(p[1], r[1]))):
            return True
        return False

    def __enhance_spine_bone_parts_mi(self, setMed_img):
        """
        To enhance spine bone parts in slices
        """
        setCT_spine_bone = {}
        ww, wc = 400, 210
        ymin, ymax = 0, 255

        for std_name, std in setMed_img.items():
            for srs_name, srs in std.items():
                setCT_spine_bone[srs_name] = {}
                for sl_name, sl in srs.items():
                    img = sl["image"]
                    img = np.reshape(img, (512, 512, 1))
                    idx_high = img >= wc + ww / 2
                    idx_low = img <= wc - ww / 2
                    img = np.where(idx_high, ymax, img)
                    img = np.where(idx_low, ymin, img)
                    img = np.where(~(idx_high | idx_low), ((img - wc) / ww + 0.5) * (ymax - ymin) + ymin, img)
                    img = np.where(img > 50, img, 0)
                    img = np.array(img, dtype=np.uint8)
                    setCT_spine_bone[srs_name][sl_name] = img
        return setCT_spine_bone

    def __compute_sl_similarity_group(self, setCT_a, setCT_a_prv):
        # To use spine bone location
        result = []

        diff = len(setCT_a.values()) - len(setCT_a_prv.values())
        list_groups = []
        for id, img_cur in setCT_a.items():
            img_cur = np.where(img_cur>0, 255, 0)

            mx_diff = list(setCT_a.keys()).index(id)+diff
            if mx_diff> len(list(setCT_a.keys())):
                mx_diff = len(list(setCT_a.keys()))
            maximum, cur_id = -1, -1
            for k in range(list(setCT_a_prv.keys()).index(id), mx_diff):
                img_prv = setCT_a_prv[list(setCT_a_prv.values())[k]]
                img_prv = np.where(img_prv>0, 255, 0)
                if maximum < np.count_nonzero(np.bitwise_and(img_prv, img_cur)):
                    maximum = np.count_nonzero(np.bitwise_and(img_prv, img_cur))
                    cur_id = list(setCT_a_prv.values())[k]
            list_groups.append([id, cur_id, maximum])

        diff = int(list_groups[0][1]) - int(list_groups[0][0])
        list_trg = []
        for i in range(1, len(list_groups)):
            if int(list_groups[i][1]) != int(list_groups[i][0])+diff:
                list_trg.append(list_groups[i])
            else:
                if len(list_trg) <=1:
                    list_trg = []
                    list_trg.append(list_groups[i])
                else:
                    list_trg.append(list_groups[i])
                    del list_trg[0]

                    trg_id = list_trg[-1][1]
                    del list_trg[-1]
                    for k in range(len(list_trg)):
                        list_groups[i-(k+1)] = [list_groups[i-(k+1)][0], trg_id-(k+1), 0]
        if len(list_trg)>1:
            if int(list_trg[-1][0])+diff == int(list_trg[-1][1]):
                for k in range(1, len(list_trg)):
                    list_groups[len(list_groups)-k] = [list_groups[len(list_groups)-k][0], int(list_groups[len(list_groups)-k][0])+diff, 0]
            else:
                for k in range(len(list_trg)-1, 0, -1):
                    list_groups[len(list_groups)-k] = [list_groups[len(list_groups)-k][0], int(list_groups[len(list_groups)-k][0])+diff, 0]

        for i in list_groups:
            result.append((i[0],i[1]))
        return result