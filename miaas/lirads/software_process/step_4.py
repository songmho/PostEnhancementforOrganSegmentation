"""
Date: 2021. 04. 27.
Programmer: MH
Description: Code for evaluating image features for lesion's images
"""
import os

from miaas.lirads.util.tumor_type_classifier import LesionImagingFeatureClassifier
import numpy as np
import cv2
from miaas.lirads.constant import ImageType


class ImageFeatureEvaluator:
    def __init__(self):
        self.setCT_slices = {}
        self.setCT_seg = {}
        self.setCT_tumor_seg = {}
        self.feature_classifier = LesionImagingFeatureClassifier()
        self.feature_classifier.load_model()
        self.features = {}
        self.list_phases = []

        self.setCT_sl_groups = {}
        self.MARGIN = 15
        self.tumor_groups = {}
        self.th_sl_num = 3
        self.LEN_FEATURES = 9

    def initialize(self, std_name):
        self.features = {}
        self.list_phases = []

        self.setCT_sl_groups = {}
        self.MARGIN = 15
        self.tumor_groups = {}
        self.th_sl_num = 3
        self.LEN_FEATURES = 9
        self.setCT_slices = {}
        self.setCT_seg = {}
        self.setCT_tumor_seg = {}
        self.std_name = std_name

    def generate_slice_group(self, med_type, setMed_img):
        """
        TO generate slices groups considering different series
        :param med_type:
        :param setCT_B:
        :param setCT_B_Seg:
        :param setCT_C_Seg:
        :return:
        """
        if med_type == ImageType.NORMAL:
            pass
        elif med_type == ImageType.DCM:
            self.__parse_sl_location(setMed_img)
        elif med_type == ImageType.NII:
            self.__enhance_spine_bone_parts_mi(setMed_img)
            self.__make_group_by_spine_bone_location()

        for k, v in self.setCT_sl_groups.items():
            print(k, ": ", v)

    def make_lesion_group(self, setCT_tumor_seg):
        """
        To make groups of lesions considering multiple CT slices
        :return:
        """
        self.setCT_tumor_grps = {}
        for srs_name, srs in setCT_tumor_seg.items():
            self.setCT_tumor_grps[srs_name] = {}
            for sl_id, sl in srs.items():
                if np.count_nonzero(sl) == 0:
                    continue
                cur_sub_segs = self.__get_sub_seg_data(sl)
                for cur_msk in cur_sub_segs:
                    is_contained = False
                    for j in self.setCT_tumor_grps[srs_name].keys():
                        cur_id = int(sl_id)
                        list_del = []
                        list_del_id = []
                        for k in range(len(self.setCT_tumor_grps[srs_name][j])-1, -1, -1):
                            prv_id = int(self.setCT_tumor_grps[srs_name][j][k][0])
                            if cur_id -prv_id == 1:
                                if len(list_del_id) == 0:
                                    if self.__check_overlapped(self.setCT_tumor_grps[srs_name][j][k][1], cur_msk):
                                        self.setCT_tumor_grps[srs_name][j].append([sl_id, sl])
                                    is_contained = True
                                else:
                                    if self.__check_overlapped(self.setCT_tumor_grps[srs_name][j][k][1], cur_msk):
                                        for del_id in list_del_id:
                                            del self.setCT_tumor_grps[srs_name][j][del_id]
                                        list_del.append(cur_msk)
                                        self.setCT_tumor_grps[srs_name][j][k].append([sl_id, self.__combine_masks(list_del)])
                                        is_contained = True
                                    else:
                                        is_contained = False
                                break
                            elif cur_id-prv_id ==0:
                                list_del_id.append(k)
                                list_del.append(self.setCT_tumor_grps[srs_name][j][k][1])
                            else:
                                break
                    if not is_contained:
                        self.setCT_tumor_grps[srs_name][len(self.setCT_tumor_grps[srs_name])] = [[sl_id, sl]]
        #
        # for k, v in self.setCT_tumor_grps.items():
        #     print(k, ": ", v)

    def __find_sl_group_id(self, cur_srs, cur_sl):
        for grp_id, data in self.setCT_sl_groups.items():
            if int(self.setCT_sl_groups[grp_id][cur_srs]) == int(cur_sl):
                return grp_id

    def correct_segmented_lesion_location(self, acq_date):
        """
        To share segmented lesion location and modify the location of segmented tumor
        :param setCT_Slices:
        :param setCT_tumor_seg:
        :return:
        """
        # TODO: CONSIDER SL GROUPS
        info_tumors = {}    # {PHASE: {num_tumors: #, sl_start_end:[( , ), ...] }, ... }
        self.tumor_groups = {}
            # {tumorID: {"mask": {PHASE1: [(sl_id, sl), (sl_id, sl), ...],... }, "features": OBJECT, "type":TYPE,
            #                     "major_features":{...}, "stage":"LR-x", "ACQ_INFO": {"date:..., }}}

        for srs_name, srs in self.setCT_tumor_grps.items():
            info_tumors[srs_name] = {"num_tumors": len(list(srs.values())), "sl_start_end": [], "sl_start_end_img":[]}
            for t_id, ts in srs.items():
                start_group_id = self.__find_sl_group_id(srs_name, ts[0][0])
                end_group_id = self.__find_sl_group_id(srs_name, ts[-1][0])
                if (start_group_id, end_group_id) not in info_tumors[srs_name]["sl_start_end"]:
                    info_tumors[srs_name]["sl_start_end"].append((start_group_id, end_group_id))
                    info_tumors[srs_name]["sl_start_end_img"].append([])
                    for i in ts:
                        info_tumors[srs_name]["sl_start_end_img"][-1].append(i[1])
        new_info_tumors = {}
        for srs_name, srs in info_tumors.items():
            trg = srs["sl_start_end"]
            trg_img = srs["sl_start_end_img"]
            new_group = []
            new_group_img = []
            cur_new = trg[0]
            cur_new_img = trg_img[0]
            new_info_tumors[srs_name] = {"sl_start_end":[], "sl_start_end_img":[]}
            for i in range(1, len(list(trg))):
                if int(cur_new[1])+self.th_sl_num > int(trg[i][0])-self.th_sl_num:
                    diff = int(trg[i][0])-int(cur_new[1])
                    cur_new = (cur_new[0], trg[i][1])
                    for dddd in range(1, diff):
                        cur_new_img.append(np.array(np.zeros((512, 512)), dtype=np.uint8))
                    cur_new_img.extend(trg_img[i])
                else:
                    new_group.append(cur_new)
                    new_group_img.append(cur_new_img)
                    cur_new = trg[i]
                    cur_new_img = trg_img[i]
            if int(cur_new[1]) + self.th_sl_num > int(trg[-1][0]) - self.th_sl_num:
                diff = int(trg[-1][0])-int(cur_new[1])
                cur_new = (cur_new[0], trg[-1][1])
                for dddd in range(1, diff):
                    cur_new_img.append(np.array(np.zeros((512, 512)), dtype=np.uint8))
                cur_new_img.extend(trg_img[-1])
            else:
                new_group.append(cur_new)
                new_group_img.append(cur_new_img)
                cur_new = trg[-1]
                cur_new_img = trg_img[-1]
            new_group.append(cur_new)
            new_group_img.append(cur_new_img)
            new_info_tumors[srs_name]["sl_start_end"] = new_group
            new_info_tumors[srs_name]["sl_start_end_img"] = new_group_img

        t_groups = {}
        # for srs_name, srs in new_info_tumors.items():
        #     print(srs_name, len(srs["sl_start_end"]), srs["sl_start_end"])

        for srs_name, srs in new_info_tumors.items():
            for t_g_id in range(len(srs["sl_start_end"])):
                cur_t_g_id = len(list(t_groups.keys()))
                t_g = srs["sl_start_end"][t_g_id]
                t_groups[cur_t_g_id] = {srs_name: (t_g, srs["sl_start_end_img"][t_g_id])}
                is_trg = False
                for o_srs_name, o_srs in new_info_tumors.items():
                    if not is_trg or srs_name == o_srs_name:
                        if srs_name == o_srs_name:
                            is_trg = True
                        continue
                    for o_t_g_id in range(len(o_srs["sl_start_end"])):
                        o_t_g = o_srs["sl_start_end"][o_t_g_id]
                        if not(int(t_g[0]) > int(o_t_g[1]) or int(t_g[1]) < int(o_t_g[0])):
                            t_groups[cur_t_g_id][o_srs_name] = (o_t_g, o_srs["sl_start_end_img"][o_t_g_id])
                if len(list(t_groups[cur_t_g_id].keys())) < len(new_info_tumors.keys()):
                    del t_groups[cur_t_g_id]

        for t_id, info in t_groups.items():
            self.tumor_groups[t_id] = {"mask":{}, "ACQ_INFO":{"acq_date": acq_date}}
            for srs_id, t_g in info.items():
                self.tumor_groups[t_id]["mask"][srs_id] = []
                range_t_g = t_g[0]
                idx = 0
                for i in range(int(range_t_g[0]), int(range_t_g[1])+1):
                    self.tumor_groups[t_id]["mask"][srs_id].append((str(i).zfill(5), t_g[1][idx]))
                    idx +=1

    def evaluate_image_feature(self, setCT_c_seg):
        """
        To evaluate image features for a tumor
        :return:
        """
        self.tumor_features = {}
        for tumor_id, info in self.tumor_groups.items():
            self.tumor_groups[tumor_id]["features"] = {}
            for srs_id, list_tumors in info["mask"].items():
                list_srs = []
                for t_info in list_tumors:
                    msk = t_info[1]
                    if np.count_nonzero(msk)==0:
                        list_srs.append({"High Id": [], "Labels": [], 'ConfidenceScores': [], "WholeConf": [0.0]*self.LEN_FEATURES})
                    else:
                        sl = setCT_c_seg[srs_id][t_info[0]]["img"]
                        cur_roi = self.__make_roi(sl, msk)
                        result = self.feature_classifier.predict(cur_roi)
                        list_srs.append(self.get_image_features(result))
                self.tumor_groups[tumor_id]["features"][srs_id] = list_srs

    def evaluate_image_feature_new(self, img):
        result = self.feature_classifier.predict(img)
        return result

    def get_image_features(self, list_conf):
        result = self.feature_classifier.get_features(list_conf[0])
        return result

    def discard_insignificant_image_features(self):
        """
        To discard insignificant image features among evaluated results considering predicted image features
        Current code is based on the biggest tumor's image features.
        but it may revised to consider majority of image features or confidence scores
        :return:
        """
        path_save = r"E:\1. Lab\Daily Results\2021\2108\0817\result\step4"

        for tumor_id, info in self.tumor_groups.items():
            features = {}
            for srs_id, list_sl in info["features"].items():
                features[srs_id] = self.get_image_features([self.__extract_major_features(list_sl)])
            self.tumor_groups[tumor_id]["features"] = features

            if not os.path.isdir(os.path.join(path_save, self.std_name)):
                os.mkdir(os.path.join(path_save, self.std_name))
            f = open(os.path.join(path_save, self.std_name, "step_4.txt"), "w")
            f.write(str(tumor_id) + "  :  " + str(self.tumor_groups[tumor_id]["features"]))
            f.close()

    def __extract_major_features(self, list_features):
        """
        To extract image features of the tumor
        considering predicted image  features from each CT slice, the image features that appeared most frequently
        are selected and the results showing the highest confidence score of the selected features are gathered and
        the average value is computed and applied to the tumor's image features
        """
        dict_count = {}
        dict_result = {}
        for i in self.feature_classifier.labels:
            dict_count[i] = 0
            dict_result[i] = 0
        for fs in list_features:  # a Series
            for conf in range(len(fs["WholeConf"])):
                if fs["WholeConf"][conf] > self.feature_classifier.th_confidence:
                    dict_count[self.feature_classifier.labels[conf]] += 1

        selected_features = []
        for k, v in dict_count.items():
            if v >= int(len(dict_count.keys()) / 2):
                selected_features.append(list(dict_count.keys()).index(k))

        selected_list = []
        for f_id in range(len(list_features)):  # a Series
            fs = list_features[f_id]
            for l in selected_features:
                if fs["WholeConf"][l] > self.feature_classifier.th_confidence:
                    selected_list.append(f_id)

        selected_list = list(set(selected_list))
        for f_id in selected_list:
            for k in range(len(list_features[f_id]["WholeConf"])):
                dict_result[self.feature_classifier.labels[k]] += list_features[f_id]["WholeConf"][k]

        for k, v in dict_result.items():
            try:
                dict_result[k] = v/len(selected_list)
            except:
                dict_result[k] =0
        # for k, v in dict_result.items():
        #     dict_result[k] = round(v / len(selected_list), 3)
        return list(dict_result.values())


    def check_treatment(self):
        """
        To check the tumor's treatment information considering image features and record
        :return:
        """
        pass

    def get_current_features(self, list_data):
        return self.feature_classifier.get_features(list_data)

    def get_features(self):
        return self.features

    def get_list_phases(self):
        return self.list_phases

    def get_tumor_groups(self):
        return self.tumor_groups

    def __check_overlapped(self, m1, m2):
        num_overlapped = np.count_nonzero(np.bitwise_and(m1, m2))
        return num_overlapped > 0

    def __combine_masks(self, list_mask):
        mask_result = np.zeros(list_mask[0].shape)
        for i in list_mask:
            mask_result+= i
        return mask_result

    def __make_group_by_spine_bone_location(self):
        """
        To make groups by spine bone location
        """
        list_results = {}

        # path_save = r"E:\1. Lab\Daily Results\2021\2108\0810\result\step4\slice_group"
        #
        # if not os.path.isdir(os.path.join(path_save)):
        #     os.mkdir(path_save)
        # To find the CT series consisting of the smallest number of CT slices
        for srs_name, srs in self.setCT_d_spine_bone.items():
            list_results[srs_name] = len(list(srs.keys()))

        trg_srs_id = -1
        smaller = 1000000
        keys = list(self.setCT_d_spine_bone.keys())
        for k in range(1, len(list_results)):
            if list_results[keys[k]] != list_results[keys[k-1]]:
                if list_results[keys[k]] < list_results[keys[k-1]]:
                    if smaller <list_results[keys[k]]:
                        smaller = list_results[keys[k]]
                        trg_srs_id = keys[k]
                else:
                    if smaller < list_results[keys[k-1]]:
                        smaller = list_results[keys[k-1]]
                        trg_srs_id = keys[k-1]
        if trg_srs_id == -1:
            trg_srs_id = keys[0]

        # To select CT slices in other CT series to be a group
        trg_srs = self.setCT_d_spine_bone[trg_srs_id]
        self.setCT_sl_groups = {}

        for srs_name, srs in self.setCT_d_spine_bone.items():
            if srs_name == trg_srs_id:
                continue
            diff = len(trg_srs) - len(srs)

            list_cur_srs_groups = []
            for key, img in trg_srs.items():
                if key not in self.setCT_sl_groups.keys():
                    self.setCT_sl_groups[key] = {}
                    self.setCT_sl_groups[key][trg_srs_id] = key
                img1 = np.where(img > 0, 255, 0)
                mx_diff = list(trg_srs.keys()).index(key) + diff
                if mx_diff > len(trg_srs.keys()):
                    mx_diff = len(trg_srs.keys())

                maximum, id = -1, -1
                for k in range(list(self.setCT_d_spine_bone[srs_name].keys()).index(key), mx_diff):
                    img2 = self.setCT_d_spine_bone[srs_name][list(self.setCT_d_spine_bone[srs_name].values())[k]]
                    img2 = np.where(img2 > 0, 255, 0)
                    if maximum < np.count_nonzero(np.bitwise_and(img1, img2)):
                        maximum = np.count_nonzero(np.bitwise_and(img1, img2))
                        id = list(self.setCT_d_spine_bone[srs_name].values())[k]
                # self.groups[key][srs_name] = id
                list_cur_srs_groups.append([key, id, maximum])
            list_trg = []
            diff = int(list_cur_srs_groups[0][1])-int(list_cur_srs_groups[0][0])

            for i in range(1, len(list_cur_srs_groups)):
                if int(list_cur_srs_groups[i][1]) != int(list_cur_srs_groups[i][0])+diff:
                    list_trg.append(list_cur_srs_groups[i])
                else:
                    if len(list_trg) <= 1:
                        list_trg = []
                        list_trg.append(list_cur_srs_groups[i])
                    else:
                        list_trg.append(list_cur_srs_groups[i])
                        del list_trg[0]

                        trg_id = list_trg[-1][1]
                        del list_trg[-1]
                        for k in range(len(list_trg)):
                            list_cur_srs_groups[i-(k+1)] = [list_cur_srs_groups[i-(k+1)][0], trg_id-(k+1), 0]
            if len(list_trg) >1:
                if int(list_trg[-1][0]) +diff == int(list_trg[-1][1]):
                    for k in range(1, len(list_trg)):
                        list_cur_srs_groups[len(list_cur_srs_groups)-k] = [list_cur_srs_groups[len(list_cur_srs_groups)- k][0], int(list_cur_srs_groups[len(self.setCT_sl_groups) - k][0]) + diff, 0]
                else:
                    for k in range(len(list_trg)-1, 0, -1):
                        list_cur_srs_groups[len(list_cur_srs_groups) - k] = [list_cur_srs_groups[len(list_cur_srs_groups) - k][0], int(list_cur_srs_groups[len(self.setCT_sl_groups) - k][0]) + diff, 0]

            for i in list_cur_srs_groups:
                self.setCT_sl_groups[i[0]][srs_name] = i[1]

        # for k, v in self.setCT_sl_groups.items():
        #     print(k, ": ", v)

    def __make_roi(self, sl, msk):
        """
        To make tumor roi considering the location of mask
        """
        cur_cnt, _ = cv2.findContours(msk, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        box = None
        for k in cur_cnt:
            (x, y, w, h) = cv2.boundingRect(k)
            box = [x-self.MARGIN, y-self.MARGIN, x+w+self.MARGIN, y+h+self.MARGIN]
        cur_tumor = np.array(sl[box[1]:box[3], box[0]:box[2]], dtype=np.uint8)
        return cur_tumor

    def __enhance_spine_bone_parts_mi(self, setMed_img):
        """
        To enhance spine bone parts in slices
        """
        self.setCT_d_spine_bone = {}
        ww, wc = 400, 210
        ymin, ymax = 0, 255

        for std_name, std in setMed_img.items():
            for srs_name, srs in std.items():
                self.setCT_d_spine_bone[srs_name] = {}
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
                    self.setCT_d_spine_bone[srs_name][sl_name] = img

    def __parse_sl_location(self, setMed_img):
        """
        To parse slice information
        """
        # To select the CT series having the longest CT slices
        self.setCT_sl_groups = {}
        long_srs_name, long_srs = "", -1
        setMed_img = setMed_img[list(setMed_img.keys())[0]]
        for srs_name, srs in setMed_img.items():
            if len(srs.values()) > long_srs:
                long_srs = len(srs.values())
                long_srs_name = srs_name
        # To store sl id with slice location for each CT slice in selected series
        for sl_id, sl in setMed_img[long_srs_name].items():
            self.setCT_sl_groups[sl_id] = {long_srs_name: (sl_id, sl["info"]["slice_location"])}

        for srs_name, srs in setMed_img.items():
            if srs_name == long_srs_name:
                continue
            for sl_name, sl in srs.items():
                sl_location = sl["info"]["slice_location"]
                diff, closed_name = 10000, ""
                for k, i in self.setCT_sl_groups.items():
                    name, loc = i[long_srs_name]
                    if abs(sl_location-loc) < diff:
                        diff = abs(sl_location-loc)
                        closed_name = name
                self.setCT_sl_groups[closed_name][srs_name] = (sl_name, sl_location)

        for group_id, group in self.setCT_sl_groups.items():
            for srs, data in self.setCT_sl_groups[group_id].items():
                self.setCT_sl_groups[group_id][srs] = data[0]

        for group_id, gs in self.setCT_sl_groups.items():
            print(group_id, end=": ")
            for id, g in gs.items():
                print(g, end=", ")
            print()

    def __compare_overlapped(self, mask1, mask2):
        mask_and = cv2.bitwise_and(mask1, mask2)
        area_and = np.count_nonzero(mask_and)
        mask_or = cv2.bitwise_or(mask1, mask2)
        area_or = np.count_nonzero(mask_or)
        try:
            overlap_rate = area_and/area_or
        except:
            overlap_rate = 0.0
        return overlap_rate

    def __get_sub_seg_data(self, img):
        """
        To return each section of segmented tumors
        """
        results = []
        if img.shape[-1] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = np.array(img, dtype=np.uint8)
        cur_cnt, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for i in cur_cnt:
            new_mask = np.zeros(img.shape)
            results.append(np.array(cv2.drawContours(new_mask, [i], -1, color=255, thickness=cv2.FILLED), dtype=np.uint8))
        return results
