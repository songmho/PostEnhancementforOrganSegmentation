"""
Date: 2021. 04. 27.
Programmer: MH
Description: Code for computing Li-RADS Features
"""
from miaas.lirads.constant import ImagingFeatures, TumorType
import numpy as np
import cv2
import copy
import math


class LIRADSFeatureComputer:
    def __init__(self):
        self.num_major_features = 0
        self.aphe_type = ""
        self.lesion_size = 0
        self.has_capsule = False
        self.has_washout = False
        self.has_threshold_growth = False
        self.setCT_tumor_info = {}

        self.list_lirad_features = {}

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
        tumor_types = {}
        for i in list(self.setCT_tumor_info.keys()):
            tumor_types[i] = self.setCT_tumor_info[i]["type"]
        return tumor_types

    def get_APHE_type(self):
        """
        To get APHE type among RimAPHE, NoAPHE, NonrimAPHE
        :return:
        """
        aphe_types = {}
        for i in list(self.setCT_tumor_info.keys()):
            aphe_types[i] = ""
            for j in self.setCT_tumor_info[i]["features"]:
                if j=="NoAPHE":
                    aphe_types[i] = "No"
                    break
                elif j=="NonrimAPHE":
                    aphe_types[i] = "Nonrim"
                    break
        return aphe_types

    def compute_lesion_size(self, voxel):
        """
        To compute lesion's size
        :param i: int, index of selected tumor type
        :return:
        """

        lesion_sizes = {}
        for i in list(self.setCT_tumor_info.keys()):
            cur_mask = self.setCT_tumor_info[i]["masks"]
            cur_voxel = voxel
            lesion_sizes[i] = self.__compute_lesion_size(cur_mask, cur_voxel)
        return lesion_sizes

    def check_capsule(self):
        """
        To check capsule among the current lesion's imaging feature
        :return:
        """
        capsules = {}
        for i in list(self.setCT_tumor_info.keys()):
            capsules[i] = []
            is_contain = False
            for j in self.setCT_tumor_info[i]["features"]:
                if "capsule" in j:
                    capsules[i] = True
                    is_contain = True
                    break
            if not is_contain:
                capsules[i] = False
        return capsules

    def check_washout(self):
        """
        To check washout among the current lesion's imaging feature
        :param i: int, index of selected tumor type
        :return:
        """
        washouts = {}
        for i in list(self.setCT_tumor_info.keys()):
            is_contain = False
            for j in self.setCT_tumor_info[i]["features"]:
                if "Washout" in j:
                    washouts[i] = True
                    is_contain = True
                    break
            if not is_contain:
                washouts[i] = False
        return washouts

    def compute_threshold_growth(self, prv_info=None):
        """
        To compute threshold growth (to use previous information)
        :param prv_info:
        :return:
        """
        th_growths = {}
        for i in list(self.setCT_tumor_info.keys()):
            th_growths[i] = False
        return th_growths

    def detect_vein_location(self):
        """
        To detect vein location in slice
        :return:
        """

    def is_tumor_in_vein(self):
        """
        To detect vein location in slice
        :return:
        """
        tivs = {}
        for i in list(self.setCT_tumor_info.keys()):
            tivs[i] = False
        return tivs

    def generate_major_feature_list(self, tumor_types, aphe_types, lesion_sizes, capsules, washouts, th_growths, tivs):
        """
        To generate list for major features of each tumor
        :return:
        """
        self.list_major_features = {}
        for i in list(tumor_types.keys()):
            num_mf = 0
            if capsules[i]:
                num_mf += 1
            if washouts[i]:
                num_mf += 1
            if th_growths[i]:
                num_mf += 1

            self.list_major_features[i] = {"Tumor_Type": tumor_types[i], "APHE_Type": aphe_types[i],
                                             "Lesion_Size": lesion_sizes[i], "Capsule": capsules[i],
                                             "Washout": washouts[i], "Threshold_Growth": th_growths[i],
                                             "Num_Major_Features": num_mf, "tiv": tivs[i], "Image_Features":self.list_lirad_features[i]}

    def get_LIRADS_feature(self):
        return self.list_major_features

    def __compute_lesion_size(self, obs, voxel):
        """
        To compute lesion's size
        :return: float, the lesion's size in the slice
        """
        obs = obs.astype(np.uint8)
        obs*=255
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
