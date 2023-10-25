"""
Date: 2022. 09. 14.
Programmer: MH
Description: Code for detecting and enhancing organ segmentation results for 5 features
"""
import copy
import cv2
import os
import numpy as np
import nibabel as nib
# from utils.performance_measurement import ImgDataPerformanceMeasurer
from matplotlib import pyplot as plt
import matplotlib
import pandas as pd
from datetime import datetime
matplotlib.use("Qt5Agg")


class MedImageEnhancer:
    def __init__(self, is_display=False):
        self.wc, self.ww = 40, 400
        self.th_location = 0.3
        self.th_size = 0.20
        self.th_size_diff = 0.80
        self.th_shape = 0.013
        self.th_size_seq = 0.50
        self.th_shape_seq = 0.80
        self.th_hu = 1.3
        self.th_hu_scale = 0.0
        self.th_diff = 0.2
        self.th_trg_sls = 5
        self.th_grvt = 30
        self.sequences = []
        self.display = is_display

        self.th_distance = 0.5
        self.th_bbox_inclusion = 0.95
        self.th_inclusion = 0.8

        self.target = -1

        self.hu_max, self.hu_min = self.__compute_HU_scale_organ()
        self.process_statistics = {
            "Original":     {"num_slices": 0, "num_slices_having_organ": 0, "num_slices_not_having_organ": 0, "min_size":10000000, "avg_size":0, "max_size":0},
            "Sequence":     {"num_sequences": 0, "num_sequences_appeared": 0, "num_sequences_non_appeared": 0, "list_appeared_sequences":[], "list_non_appeared_sequences":[]},
            "appearance":   {"num_remedied_SLs": 0, "num_detected_violation":0, "remedy_states": {}, "size_seg":{}, "size_rmd":{},"num_slices_having_organ": 0, "num_sequences":0, "min_size":10000000, "avg_size":0, "max_size":0},
            "location":     {"num_remedied_SLs": 0, "num_detected_violation":0, "remedy_states": {}, "size_seg":{}, "size_rmd":{},"num_slices_having_organ": 0, "num_sequences":0,"min_size":10000000, "avg_size":0, "max_size":0},
            "size":         {"num_remedied_SLs": 0, "num_detected_violation":0, "remedy_states": {}, "size_seg":{}, "size_rmd":{},"num_slices_having_organ": 0, "num_sequences":0,"min_size":10000000, "avg_size":0, "max_size":0},
            "shape":        {"num_remedied_SLs": 0, "num_detected_violation":0, "remedy_states": {}, "size_seg":{}, "size_rmd":{},"num_slices_having_organ": 0, "num_sequences":0,"min_size":10000000, "avg_size":0, "max_size":0},
            "HU":           {"num_remedied_SLs": 0, "num_detected_violation":0, "remedy_states": {}, "HU_scales_seg": {}, "HU_scales_remedy": {}, "num_slices_having_organ": 0, "num_sequences":0, "size_seg":{}, "size_rmd":{}, "min_size":10000000, "avg_size":0, "max_size":0}
        }

    # Methods for Step 1. Identifying Continuity Sequence & Loading CT Series with Segmentation resutls
    def load_med_imgs(self):
        """
        To load segmentation results
        :return:
        """
        print("load_med_imgs")
        self.process_statistics = {
            "Original":     {"num_slices": 0, "num_slices_having_organ": 0, "num_slices_not_having_organ": 0, "min_size":10000000, "avg_size":0, "max_size":0},
            "Sequence":     {"num_sequences": 0, "num_sequences_appeared": 0, "num_sequences_non_appeared": 0, "list_appeared_sequences":[], "list_non_appeared_sequences":[]},
            "appearance":   {"num_remedied_SLs": 0, "num_detected_violation":0, "remedy_states": {}, "size_seg":{}, "size_rmd":{},"num_slices_having_organ": 0, "num_sequences":0, "min_size":10000000, "avg_size":0, "max_size":0},
            "location":     {"num_remedied_SLs": 0, "num_detected_violation":0, "remedy_states": {}, "size_seg":{}, "size_rmd":{},"num_slices_having_organ": 0, "num_sequences":0,"min_size":10000000, "avg_size":0, "max_size":0},
            "size":         {"num_remedied_SLs": 0, "num_detected_violation":0, "remedy_states": {}, "size_seg":{}, "size_rmd":{},"num_slices_having_organ": 0, "num_sequences":0,"min_size":10000000, "avg_size":0, "max_size":0},
            "shape":        {"num_remedied_SLs": 0, "num_detected_violation":0, "remedy_states": {}, "size_seg":{}, "size_rmd":{},"num_slices_having_organ": 0, "num_sequences":0,"min_size":10000000, "avg_size":0, "max_size":0},
            "HU":           {"num_remedied_SLs": 0, "num_detected_violation":0, "remedy_states": {}, "HU_scales_seg": {}, "HU_scales_remedy": {}, "num_slices_having_organ": 0, "num_sequences":0, "size_seg":{}, "size_rmd":{}, "min_size":10000000, "avg_size":0, "max_size":0}
        }
        # To load original medical image series (nii format)
        self.path_org_mi = os.path.join(self.path_org_mi, os.listdir(self.path_org_mi)[0])
        self.srs_org_mi = nib.load(self.path_org_mi)  # 3 dimensional array (x, y, # of Slices)
        self.srs_org_mi = self.srs_org_mi.get_fdata()  # To select only image data
        self.srs_org_mi = self.srs_org_mi[::-1, ::-1, ::-1]
        # self.srs_org_mi = self.srs_org_mi[::-1, :, :]
        self.srs_org_mi = np.transpose(self.srs_org_mi, (1, 0, 2))

        for i in range(self.srs_org_mi.shape[-1]):
            img = self.__convert_color_depth(self.srs_org_mi[:, :, i])
            cv2.imwrite(os.path.join(self.path_org_sl, str(i).zfill(5)+".png"), img)

        # TO load slice images
        list_fname = os.listdir(os.path.join(self.path_org_sl))
        for i in range(len(list_fname)):
            img = cv2.imread(os.path.join(self.path_org_sl, list_fname[i]))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.srs_org_sl.append(
                {"id": i, "img": img, "fname": list_fname[i]})  # [{"id": id, "img":img}, {"id":, "img": }, ...]

        # To load segmentation results
        list_fname = os.listdir(os.path.join(self.path_seg_result))
        sizes = 0
        min_size = 1000000
        max_size = 0

        for i in range(len(list_fname)):
            img = cv2.imread(os.path.join(self.path_seg_result, list_fname[i]))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.srs_seg_sl.append(
                {"id": i, "img": img, "fname": list_fname[i]})  # [{"id": id, "img":img}, {"id":, "img": }, ...]

            self.process_statistics["Original"]["num_slices"] += 1
            if np.count_nonzero(img) > 0:
                self.process_statistics["Original"]["num_slices_having_organ"] += 1
                sizes += np.count_nonzero(img)
                if min_size>np.count_nonzero(img):
                    min_size = np.count_nonzero(img)
                if max_size < np.count_nonzero(img):
                    max_size = np.count_nonzero(img)
            else:
                self.process_statistics["Original"]["num_slices_not_having_organ"] += 1
        self.process_statistics["Original"]["avg_size"] = round(sizes/ self.process_statistics["Original"]["num_slices_having_organ"],2)
        self.process_statistics["Original"]["min_size"] = min_size
        self.process_statistics["Original"]["max_size"] = max_size

        print("load_med_imgs Done")

    def generate_sequences(self):
        """
        To generate sequences applying segmentation results
        :return:
        """
        self.sequences = []
        cur_seq = {"type": False, "data": []}
        for i in self.srs_seg_sl:  # Loop for whole slices (Segmentation Results)
            img = i["img"]
            if len(cur_seq["data"]) == 0:  # If any data is not inserted
                cur_seq["type"] = self.__contains(img)
                cur_seq["data"].append(copy.deepcopy(i))
            else:  # If at least one seg data is inserted
                if cur_seq["type"] == self.__contains(img):  # If cur seg data is same to type of sequence
                    cur_seq["data"].append(copy.deepcopy(i))
                else:  # If cur seg data is not same to type of sequence
                    self.sequences.append(cur_seq)
                    cur_seq = {"type": self.__contains(img), "data": [copy.deepcopy(i), ]}
        if len(cur_seq["data"]) > 0:  # If current sequence is not empty
            self.sequences.append(cur_seq)

        self.process_statistics["Sequence"]["num_sequences"] = len(self.sequences)
        self.process_statistics["Sequence"]["num_sequences_appeared"] = len(self.sequences)
        self.process_statistics["Sequence"]["num_sequences_non_appeared"] = len(self.sequences)

        for seq in self.sequences:
            if seq["type"]:
                self.process_statistics["Sequence"]["num_sequences_appeared"] += 1
                list_f_names = []
                for d in seq["data"]:
                    list_f_names.append(d["fname"])
                self.process_statistics["Sequence"]["list_appeared_sequences"].append(list_f_names)
            else:
                self.process_statistics["Sequence"]["num_sequences_non_appeared"] += 1
                list_f_names = []
                for d in seq["data"]:
                    list_f_names.append(d["fname"])
                self.process_statistics["Sequence"]["list_non_appeared_sequences"].append(list_f_names)

        if self.display:
            list_data = []
            for id in range(len(self.sequences)):
                for j in range(len(self.sequences[id]["data"])):
                    cur_id = self.sequences[id]["data"][j]["id"]
                    sl = self.__get_current_sl(id, j)
                    list_data.append([{"Slice": self.srs_org_sl[cur_id]["img"],
                                     "Seg. Result": self.sequences[id]["data"][j]["img"],
                                     "Remedied": np.zeros(self.sequences[id]["data"][j]["img"].shape, np.uint8)},
                        {"Slice": {"fname": self.srs_org_sl[cur_id]["fname"].split(".")[0]},
                         "Seg. Result": {"sequence": {"id": id, "type": "Appeared" if self.sequences[id]["type"] else "Non-Appeared"},
                                         "size": format(np.count_nonzero(self.sequences[id]["data"][j]["img"]), ","),
                                         "HU Scale": self.__compute_HU_scale(sl, self.srs_seg_sl[cur_id]["img"])[0]},
                         }])
            self.visualize_sequence_generation(list_data)
            # cv2.destroyAllWindows()
        print("generate_sequences Done")

    def __contains(self, slice_seg):
        """
        To check whether the segmentation result contains the semgented organ mask or not
        :param slice_seg: Target Segmentation result
        :return: boolean, True for Contained segmented mask, False for Not contained segmetned mask
        """
        return np.count_nonzero(slice_seg)>0

    def set_img_paths(self, path_org_mi, path_org_sl, path_seg_result, path_save):
        """
        Method for setting file path
        :param path_org_mi: string, path for original medical images (series)
        :param path_org_sl: string, path for original slices (png data)
        :param path_seg_result: string, path for segmentation result
        :param path_save: string, path for saving the enhanced results
        :return:
        """
        self.path_org_mi = path_org_mi
        self.path_org_sl = path_org_sl
        self.path_seg_result = path_seg_result
        self.path_save = path_save
        self.srs_org_mi = []
        self.srs_org_sl = []
        self.srs_seg_sl = []

        self.process_statistics = {
            "Original": {"num_slices": 0, "num_slices_having_organ": 0, "num_slices_not_having_organ": 0},
            "Sequence": {"num_sequences": 0, "num_sequences_appeared": 0, "num_detected_violation":0, "num_sequences_non_appeared": 0, "list_appeared_sequences":[], "list_non_appeared_sequences":[]},
            "appearance": {"num_remedied_SLs": 0, "num_detected_violation":0, "remedy_states": {}, "size_seg":{}, "size_rmd":{}},
            "location": {"num_remedied_SLs": 0, "num_detected_violation":0, "remedy_states": {}, "location_diff_seg":{}, "location_diff_rmd":{}, },
            "size": {"num_remedied_SLs": 0, "num_detected_violation":0, "remedy_states": {}, "size_seg":{}, "size_rmd":{}},
            "shape": {"num_remedied_SLs": 0, "num_detected_violation":0, "remedy_states": {}, "shape_diff_seg":{}, "shape_diff_rmd": {}},
            "HU": {"num_remedied_SLs": 0, "num_detected_violation":0, "remedy_states": {}, "HU_scales_seg": {}, "HU_scales_remedy": {}}
        }

    # Methods for Step 2. Correcting Appearance Inconsistency
    def remedy_appearance_consistency_violation(self):
        """
        To detect appearance consistency violation and remedy them
        :return:
        """
        self.list_prv = {}
        refined_seqs = self.detect_appearance_consistency_violation()
        self.sequences = copy.deepcopy(refined_seqs)
        self.__move_empty_to_false_seq()  # To reorganize segmentation results

        # Code for Statistics
        self.process_statistics["appearance"]["num_sequences"] = len(refined_seqs)
        sizes = 0
        min_size = 1000000
        max_size = 0
        for seq in refined_seqs:
            for i in seq["data"]:
                img = i["img"]
                if np.count_nonzero(img) > 0:
                    self.process_statistics["appearance"]["num_slices_having_organ"] += 1
                    sizes += np.count_nonzero(img)
                    if min_size > np.count_nonzero(img):
                        min_size = np.count_nonzero(img)
                    if max_size < np.count_nonzero(img):
                        max_size = np.count_nonzero(img)
        self.process_statistics["appearance"]["min_size"] = min_size
        self.process_statistics["appearance"]["max_size"] = max_size
        self.process_statistics["appearance"]["avg_size"] = round(sizes / self.process_statistics["appearance"]["num_slices_having_organ"], 2)

        if self.display:
            list_data = []
            list_selected_cur_ids = []
            for id in range(len(self.sequences)):
                for j in range(len(self.sequences[id]["data"])):
                    cur_id = self.sequences[id]["data"][j]["id"]
                    sl = self.__get_current_sl(id, j)
                    if cur_id in list_selected_cur_ids:
                        continue
                    list_selected_cur_ids.append(cur_id)
                    list_data.append([{"Slice": self.srs_org_sl[cur_id]["img"],
                                     "Seg. Result": self.list_prv[cur_id],
                                     "Remedied": self.sequences[id]["data"][j]["img"]},
                        {"Slice": {"fname": self.srs_org_sl[cur_id]["fname"].split(".")[0]},
                         "Seg. Result": {"sequence": {"id": id, "type": "Appeared" if self.sequences[id]["type"] else "Non-Appeared"},
                                         "size": format(np.count_nonzero(self.list_prv[cur_id]), ","),
                                         "HU Scale": self.__compute_HU_scale(sl, self.list_prv[cur_id])[0]},
                         "Remedied": {"size": format(np.count_nonzero(self.sequences[id]["data"][j]["img"]), ","),
                                      "HU Scale": self.__compute_HU_scale(sl, self.sequences[id]["data"][j]["img"])[0],
                                      "remedy_state": self.process_statistics["appearance"]["remedy_states"][cur_id]}
                         }])


            self.display_appearance_correction_result()
            self.visualize_appearance_remedied(list_data)
            # cv2.destroyAllWindows()

    def detect_appearance_consistency_violation(self):
        """
        To detect the appearance consistency violation
        """
        refined_seqs = []  # List for Refined sequences
        cur_ref_seqs = {"type": True, "data": []}  # Current refined sequences
        # Task 1. To validate Continuity Sequence
        if len(self.sequences)>3:
            is_valid = False
        else:
            count_ap = 0
            for id in range(len(self.sequences)):
                if self.sequences[id]["type"]:
                    count_ap +=1
            if count_ap>1:
                is_valid = False
            else:
                is_valid = True

        if not is_valid:
            # Task 2. To detect Continuity Sequences Violating appearance Consistency
            for id in range(len(self.sequences)):
                for sl_id in range(len(self.sequences[id]["data"])):
                    self.process_statistics["appearance"]["remedy_states"][self.sequences[id]["data"][sl_id]["id"]] = "Not Violated"
                    self.list_prv[self.sequences[id]["data"][sl_id]["id"]] = self.sequences[id]["data"][sl_id]["img"]

                if not self.sequences[id]["type"]:
                    for d in self.sequences[id]["data"]:
                        self.process_statistics["appearance"]["remedy_states"][d["id"]] = "Not Violated"
                    if id == len(self.sequences) - 1:  # when the sequence is the last sequence
                        refined_seqs.append(cur_ref_seqs)  # To add current refined sequence to the list "refined_seqs"
                        cur_ref_seqs = self.sequences[id]  # To set the current sequence to cur_ref_seqs
                    continue
                if len(cur_ref_seqs["data"]) == 0:
                    if id == 0:  # If the true sequence is first sequence
                        cur_ref_seqs = self.sequences[0]
                    elif id==1:  # If the true sequence is second sequence
                        refined_seqs.append(self.sequences[0])  # To add first false sequence to refined list
                        cur_ref_seqs = self.sequences[1]
                    else:
                        refined_seqs.append(self.sequences[id-1])
                        cur_ref_seqs = self.sequences[id]
                    continue

                seq_ap_prv = self.sequences[id - 2]["data"]
                seq_np = self.sequences[id - 1]["data"]
                seq_ap_cur = self.sequences[id]["data"]

                sl_seg_prv_last = seq_ap_prv[-1]["img"]
                sl_seg_cur_first = seq_ap_cur[0]["img"]
                num_between = len(seq_np)

                # Comparing Inclusion relationship and Intersect Size (Location Connectivity)
                inclusion_prv = self.__check_seq_inclusion(seq_ap_prv)
                inclusion_cur = self.__check_seq_inclusion(seq_ap_cur)
                intersect_size = np.count_nonzero(np.bitwise_and(sl_seg_prv_last, sl_seg_cur_first))
                # print(intersect_size, np.min([np.count_nonzero(sl_seg_prv_last), np.count_nonzero(sl_seg_cur_first)]),
                #       (intersect_size / np.min([np.count_nonzero(sl_seg_prv_last), np.count_nonzero(sl_seg_cur_first)])))
                is_intersected = (intersect_size / np.min([np.count_nonzero(sl_seg_prv_last), np.count_nonzero(sl_seg_cur_first)]))> 0.9
                is_continued_1 = inclusion_prv and inclusion_cur and intersect_size > self.th_size and is_intersected

                # Comparing Expected Organ Size (Size Connectivity)
                exp_size_prv_last = np.count_nonzero(sl_seg_cur_first) * (
                        1 - self.__compute_transition(seq_ap_cur, 0)) ** num_between
                exp_size_cur_first = np.count_nonzero(sl_seg_prv_last) * (
                        1 + self.__compute_transition(seq_ap_prv, -1)) ** num_between
                is_diff_size_prv_last = (np.abs(np.count_nonzero(sl_seg_prv_last) - exp_size_prv_last) / np.count_nonzero(
                    sl_seg_prv_last)) < self.th_diff
                is_diff_size_cur_first = (np.abs(np.count_nonzero(sl_seg_cur_first) - exp_size_cur_first) / np.count_nonzero(
                    sl_seg_cur_first)) < self.th_diff
                if len(seq_ap_prv) == 1:
                    is_diff_size_cur_first = True
                if len(seq_ap_cur) == 1:
                    is_diff_size_prv_last = True
                if len(seq_ap_cur)>1 and len(seq_ap_prv)>1:
                    is_continued_2 = is_diff_size_prv_last and is_diff_size_cur_first
                elif len(seq_ap_prv)>1 and len(seq_ap_cur)<=1:
                    is_continued_2 = is_diff_size_prv_last
                elif len(seq_ap_cur)>1 and len(seq_ap_prv)<=1:
                    is_continued_2 = is_diff_size_cur_first
                else:
                    is_continued_2 = False

                if is_continued_1 and is_continued_2:  # Case 1.
                    # print("CASE 1")
                    self.process_statistics["appearance"]["num_detected_violation"] += len(self.sequences[id - 1])
                    cur_ref_seqs = self.revise_appearance_inconsistency(1, seq_ap_prv=cur_ref_seqs, seq_np_cur=self.sequences[id-1],seq_ap_nxt=self.sequences[id])[0]

                else:
                    # To check HU Scale
                    if self.__check_seq_HU_violation(seq_ap_prv) and self.__check_seq_HU_violation(seq_ap_cur):
                        self.process_statistics["appearance"]["num_detected_violation"] += len(cur_ref_seqs)
                        self.process_statistics["appearance"]["num_detected_violation"] += len(self.sequences[id])
                        cur_ref_seqs = self.revise_appearance_inconsistency(6, cur_ref_seqs, self.sequences[id-1], self.sequences[id])[0]   # To revise the SEQi-1 and SEQi
                        refined_seqs.append(cur_ref_seqs)  # To put gathered data to refined_seqs

                        cur_ref_seqs = {"type": True, "data": []}  # Current refined sequences
                    else:
                        do_violation = len(self.sequences[id]["data"]) > len(cur_ref_seqs["data"])
                        if do_violation:    # If the length of current sequence is longer than the length of the refined sequence
                            nxt_sl_seg = self.sequences[id]["data"][0]["img"]
                            cur_sl = self.__get_current_sl(id-1, -1)

                            is_contour, violated_area = self.__check_HU_scale_violated_pixel_location(cur_sl, nxt_sl_seg)  # To check the HU Scale area
                            try:
                                if np.count_nonzero(violated_area)/np.count_nonzero(nxt_sl_seg) > 0.7:  # If the Excluded sequence doesn't contain the organ area
                                    self.process_statistics["appearance"]["num_detected_violation"] += len(self.sequences[id])
                                    results = self.revise_appearance_inconsistency(2, seq_ap_prv=cur_ref_seqs, seq_np_cur=self.sequences[id-1], seq_ap_nxt=self.sequences[id])
                                    refined_seqs.append(results[0])
                                    cur_ref_seqs = results[1]
                                else:                        # If the Excluded sequence contains the organ area
                                    self.process_statistics["appearance"]["num_detected_violation"] += len(self.sequences[id-1])
                                    self.process_statistics["appearance"]["num_detected_violation"] += len(self.sequences[id])
                                    results = self.revise_appearance_inconsistency(3, seq_ap_prv=cur_ref_seqs, seq_np_cur=self.sequences[id-1], seq_ap_nxt=self.sequences[id])
                                    refined_seqs.append(results[0])
                                    cur_ref_seqs = results[1]
                            except:
                                refined_seqs.append(cur_ref_seqs)
                                refined_seqs.append(self.sequences[id-1])
                                cur_ref_seqs = self.sequences[id]
                        else:    # If the length of current sequence is shorter than the length of the refined sequence
                            prv_sl_seg = self.sequences[id-2]["data"][-1]["img"]
                            cur_sl = self.__get_current_sl(id-1, 0)

                            is_contour, violated_area = self.__check_HU_scale_violated_pixel_location(cur_sl, prv_sl_seg)
                            try:
                                if (np.count_nonzero(violated_area)/np.count_nonzero(prv_sl_seg) > 0.7):  # If the Excluded sequence doesn't contain the organ area
                                    self.process_statistics["appearance"]["num_detected_violation"] += len(cur_ref_seqs)
                                    results = self.revise_appearance_inconsistency(4, seq_ap_prv=cur_ref_seqs, seq_np_cur=self.sequences[id-1], seq_ap_nxt=self.sequences[id])
                                else:                       # If the Excluded sequence contains the organ area
                                    self.process_statistics["appearance"]["num_detected_violation"] += len(self.sequences[id-1])
                                    self.process_statistics["appearance"]["num_detected_violation"] += len(cur_ref_seqs)
                                    results = self.revise_appearance_inconsistency(5, seq_ap_prv=cur_ref_seqs, seq_np_cur=self.sequences[id-1], seq_ap_nxt=self.sequences[id])
                                refined_seqs.append(results[0])
                                refined_seqs.append(results[1])
                            except:
                                refined_seqs.append(cur_ref_seqs)
                                refined_seqs.append(self.sequences[id-1])
                            cur_ref_seqs = {"type": True, "data": []}  # Current refined sequences
            if len(cur_ref_seqs["data"]) > 0:  # if current refined sequences is remained not appending the refined_seqs
                refined_seqs.append(cur_ref_seqs)
                for k in cur_ref_seqs["data"]:
                    if k["id"] not in self.process_statistics["appearance"]["remedy_states"].keys():
                        self.process_statistics["appearance"]["remedy_states"][k["id"]] = "Not Violated"

        # Task 3. To detect CT Slices violating the appearance principle
        if len(refined_seqs) == 0:
            refined_seqs = self.sequences
        for id in range(len(refined_seqs)):
            if refined_seqs[id]["type"]:
                print(id, len(refined_seqs))
                seq_prv = refined_seqs[id-1]
                if id<1:
                    seq_prv = None
                seq_cur = refined_seqs[id]

                seq_nxt = refined_seqs[id+1]
                if id>len(refined_seqs)-2:
                    seq_nxt = None
                results = self.revise_appearance_inconsistency(7, seq_ap_prv=seq_prv, seq_np_cur=seq_cur, seq_ap_nxt=seq_nxt)
                if id>=1:
                    refined_seqs[id-1] = results[0]
                refined_seqs[id] = results[1]
                if id>len(refined_seqs)-2:
                    refined_seqs[id+1] = results[2]

        return refined_seqs

    def revise_appearance_inconsistency(self, case, seq_ap_prv=None, seq_np_cur=None, seq_ap_nxt=None):
        """
        To revise appearance inconsistency of sequences
        :param seq_id: int, current sequence id
        :param case:
        :return:
        """
        results = []
        if case == 1:    # Case SEQ_np_(i-1) violates appearance principle
            revised_seq = copy.deepcopy(seq_ap_prv)
            sl_seg_prv_last = seq_ap_prv["data"][-1]["img"]
            sl_seg_cur_first = seq_ap_nxt["data"][0]["img"]
            for i in range(len(seq_ap_prv["data"])):
                if seq_ap_prv["data"][i]["id"] not in self.process_statistics["appearance"]["remedy_states"].keys():
                    self.process_statistics["appearance"]["remedy_states"][seq_ap_prv["data"][i]["id"]] = "Not Violated"
            for i in range(len(seq_ap_nxt["data"])):
                if seq_ap_nxt["data"][i]["id"] not in self.process_statistics["appearance"]["remedy_states"].keys():
                    self.process_statistics["appearance"]["remedy_states"][seq_ap_nxt["data"][i]["id"]] = "Not Violated"

            # To manage false sequence
            if len(revised_seq["data"]) > 0:  # if any sequence in the cur_ref_seqs
                # To select last slice's info in previous true sequence
                last_img = self.srs_org_sl[revised_seq["data"][-1]["id"]]["img"]

                transition = self.__compute_transition(seq_ap_prv["data"], -1)
                # print("Transition", transition, revised_seq["data"][-1]["fname"])
                self.process_statistics["appearance"]["num_detected_violation"] += len(seq_np_cur["data"])
                for i in range(len(seq_np_cur["data"])):  # To repeat whole slices in false sequence
                    cur_img = self.srs_org_sl[seq_np_cur["data"][i]["id"]]["img"]
                    cur_seg = seq_np_cur["data"][i]["img"]
                    # print(">>>>>>>>", seq_np_cur["data"][i]["fname"], transition, np.count_nonzero(sl_seg_prv_last), np.count_nonzero(cur_seg), end="  ")
                    cur_seg = self.__revise_slsegs_based_on_adjacent_segmentations(sl_seg_prv_last, cur_seg, None,
                                                                                   last_img, cur_img,
                                                                                   None, transition)  # To generate segmentation result considering previous data
                    revised_seq["data"].append(
                        {"id": seq_np_cur["data"][i]["id"], "img": cur_seg, "fname": seq_np_cur["data"][i]["fname"]})  # To save the data
                    last_img = cur_img
                    sl_seg_prv_last = cur_seg

                    self.process_statistics["appearance"]["remedy_states"][seq_np_cur["data"][i]["id"]] = "Remedied"
                    self.process_statistics["appearance"]["num_remedied_SLs"] += 1

            else:  # If any sequence is not in cur_ref_seqs (no applied sequence located in previous )
                # To select first slice's info in current true sequence
                nxt_img = self.srs_org_sl[seq_ap_nxt["data"][0]["id"]]["img"]
                transition = self.__compute_transition(seq_ap_nxt["data"], 0)
                list_reverse = []
                self.process_statistics["appearance"]["num_detected_violation"] += len(seq_np_cur["data"])
                for i in range(len(seq_np_cur["data"])-1, -1,
                               -1):  # To repeat whole slices in false sequence (reverse)
                    cur_seg = seq_np_cur["data"][i]["img"]
                    cur_img = self.srs_org_sl[seq_np_cur["data"][i]["id"]]["img"]
                    cur_seg = self.__revise_slsegs_based_on_adjacent_segmentations(None, cur_seg, sl_seg_cur_first,
                                                                                   None, cur_img,
                                                                                   nxt_img, transition)  # To generate segmentation result considering next data
                    list_reverse.append({"id": seq_np_cur["data"][i]["id"],
                                         "img": cur_seg,
                                         "fname": seq_np_cur["data"][i]["fname"]})  # To gather data in buffer
                    self.process_statistics["appearance"]["remedy_states"][seq_np_cur["data"][i]["id"]] = "Remedied"
                    self.process_statistics["appearance"]["num_remedied_SLs"] += 1
                    nxt_img = cur_img
                    sl_seg_cur_first = cur_seg
                list_reverse.reverse()  # To set correct order
                for i in list_reverse:  # To save generated data to cur_ref_seqs
                    revised_seq["data"].append(i)
            for i in seq_ap_nxt["data"]:
                revised_seq["data"].append(i)
            results.append(revised_seq)
        elif case in [2, 3]:    # Case SEQ_ap_(i-2) violates the principle
            transition = self.__compute_transition(seq_ap_nxt["data"], 0)
            if case == 3:
                # compare ap_nxt and np_cur
                sl_seg_nxt = seq_ap_nxt["data"][0]["img"]
                sl_nxt = self.srs_seg_sl[seq_ap_nxt["data"][0]["id"]]["img"]
                list_removed_sl = []
                for i in range(len(seq_np_cur["data"]) - 1, 0):
                    sl_seg_cur = seq_np_cur["data"][i]["img"]
                    sl_cur = self.srs_seg_sl[seq_np_cur["data"][i]["id"]]["img"]
                    seq_np_cur["data"][i]["img"] = self.__revise_slsegs_based_on_adjacent_segmentations(None, sl_seg_cur,
                                                                                                        sl_seg_nxt, None, sl_cur,
                                                                                                        sl_nxt, transition)
                    sl_seg_cur = seq_np_cur["data"][i]["img"]
                    list_removed_sl.append(i)
                    sl_seg_nxt = sl_seg_cur
                    sl_nxt = sl_cur
                    if np.count_nonzero(sl_seg_nxt) == 0:
                        break
                for i in list_removed_sl:
                    seq_ap_nxt["data"].insert(0, seq_np_cur["data"][i])
                    seq_np_cur["data"].pop(i)
            for k in range(len(seq_ap_prv["data"])):
                seq_ap_prv["data"][k]["img"] = np.zeros(seq_ap_prv["data"][k]["img"].shape, np.uint8)
                seq_ap_prv["data"].extend(seq_np_cur["data"])
                self.process_statistics["appearance"]["remedy_states"][seq_ap_prv["data"][k]["id"]] = "Remedied"
                self.process_statistics["appearance"]["num_remedied_SLs"] += 1
            seq_ap_prv["type"] = False
            results = [seq_ap_prv, seq_ap_nxt]

        elif case in [4, 5]:    # Case SEQ_ap_i violates the principle
            transition = self.__compute_transition(seq_ap_prv["data"], -1)
            self.process_statistics["appearance"]["num_detected_violation"] += len(seq_ap_nxt["data"])
            if case == 5:
                # Compare ap_prv and np_cur
                sl_seg_prv =seq_ap_prv["data"][-1]["img"]
                sl_prv = self.srs_seg_sl[seq_ap_prv["data"][-1]["id"]]["img"]
                list_removed_sl = []
                for i in range(len(seq_np_cur["data"])-1):
                    sl_seg_cur = seq_np_cur["data"][i]["img"]
                    sl_cur = self.srs_seg_sl[seq_np_cur["data"][i]["id"]]["img"]
                    self.process_statistics["appearance"]["num_detected_violation"] += 1
                    seq_np_cur["data"][i]["img"] = self.__revise_slsegs_based_on_adjacent_segmentations(sl_seg_prv, sl_seg_cur, None, sl_prv, sl_cur, None, transition)
                    sl_seg_cur = seq_np_cur["data"][i]["img"]

                    list_removed_sl.append(i)
                    sl_seg_prv = sl_seg_cur
                    sl_prv = sl_cur
                    if np.count_nonzero(sl_seg_prv) == 0:
                        break
                for i in range(len(list_removed_sl)):
                    seq_ap_prv["data"].insert(-1, seq_np_cur["data"][0])
                    seq_np_cur["data"].pop(0)
            for k in range(len(seq_ap_nxt["data"])):
                seq_ap_nxt["data"][k]["img"] = np.zeros(seq_ap_nxt["data"][k]["img"].shape, np.uint8)
                seq_np_cur["data"].append(seq_ap_nxt["data"][k])
                self.process_statistics["appearance"]["remedy_states"][seq_ap_nxt["data"][k]["id"]] = "Remedied"
                self.process_statistics["appearance"]["num_remedied_SLs"] += 1
            results = [seq_ap_prv, seq_np_cur]

        elif case == 6:   # Case SEQ_ap_(i-2) and SEQ_ap_(i) violate the principle
            self.process_statistics["appearance"]["num_detected_violation"] += len(seq_ap_prv["data"])
            self.process_statistics["appearance"]["num_detected_violation"] += len(seq_ap_nxt["data"])
            # print(">>>>>>  case 6",)
            seq_ap_prv["type"] = False
            for k in range(len(seq_ap_prv["data"])):
                seq_ap_prv["data"][k]["img"] = np.zeros(seq_ap_prv["data"][k]["img"].shape, np.uint8)
                self.process_statistics["appearance"]["remedy_states"][seq_ap_prv["data"][k]["id"]] = "Remedied"
                self.process_statistics["appearance"]["num_remedied_SLs"] += 1
            seq_ap_prv["data"].extend(seq_np_cur["data"])
            seq_ap_prv["data"].extend(seq_ap_nxt["data"])
            for k in range(len(seq_ap_nxt["data"])):
                seq_ap_prv["data"].append(seq_ap_nxt["data"][k])
                seq_ap_prv["data"][-1]["img"] = np.zeros(seq_ap_prv["data"][-1]["img"].shape, np.uint8)
                self.process_statistics["appearance"]["remedy_states"][seq_ap_nxt["data"][k]["id"]] = "Remedied"
                self.process_statistics["appearance"]["num_remedied_SLs"] += 1
            results.append(seq_ap_prv)
        elif case == 7:
            seq_ap_cur = seq_np_cur
            seq_np_prv = seq_ap_prv
            seq_np_nxt = seq_ap_nxt
            try:
                if seq_np_prv is not None:
                    transition = self.__compute_transition(seq_ap_cur["data"], 0)
                    # compare ap_nxt and np_cur
                    sl_seg_nxt = seq_ap_cur["data"][0]["img"]
                    sl_nxt = self.srs_seg_sl[seq_ap_cur["data"][0]["id"]]["img"]
                    list_removed_sl = []
                    for i in range(len(seq_np_prv["data"]) - 1, 0):
                        sl_seg_cur = seq_np_prv["data"][i]["img"]
                        sl_cur = self.srs_seg_sl[seq_np_prv["data"][i]["id"]]["img"]
                        msk = self.__revise_slsegs_based_on_adjacent_segmentations(None, sl_seg_cur,
                                                                                   sl_seg_nxt, None, sl_cur,
                                                                                   sl_nxt, transition)
                        if np.count_nonzero(msk) < 200 or np.count_nonzero(sl_seg_nxt) <= np.count_nonzero(msk):
                            break
                        seq_np_prv["data"][i]["img"] = msk
                        sl_seg_cur = seq_np_prv["data"][i]["img"]
                        list_removed_sl.append(i)
                        sl_seg_nxt = sl_seg_cur
                        sl_nxt = sl_cur

                        self.process_statistics["appearance"]["num_detected_violation"] += 1
                    for i in list_removed_sl:
                        seq_ap_cur["data"].insert(0, seq_np_prv["data"][i])
                        seq_np_prv["data"].pop(i)

                    for k in range(len(seq_np_prv["data"])):
                        self.process_statistics["appearance"]["remedy_states"][seq_np_prv["data"][k]["id"]] = "Remedied"
                        self.process_statistics["appearance"]["num_remedied_SLs"] += 1

                if seq_np_nxt is not None:
                    transition = self.__compute_transition(seq_ap_cur["data"], -1)
                    # Compare ap_prv and np_cur
                    sl_seg_prv =seq_ap_cur["data"][-1]["img"]
                    sl_prv = self.srs_seg_sl[seq_ap_cur["data"][-1]["id"]]["img"]
                    list_removed_sl = []
                    print(seq_ap_cur["data"][-1]["id"])
                    for i in range(len(seq_np_nxt["data"])-1):
                        sl_seg_cur = seq_np_nxt["data"][i]["img"]
                        sl_cur = self.srs_seg_sl[seq_np_nxt["data"][i]["id"]]["img"]
                        msk =  self.__revise_slsegs_based_on_adjacent_segmentations(sl_seg_prv, sl_seg_cur, None, sl_prv, sl_cur, None, transition)

                        if np.count_nonzero(msk) < 200 or np.count_nonzero(sl_seg_prv) <= np.count_nonzero(msk):
                            break
                        seq_np_nxt["data"][i]["img"] = msk
                        sl_seg_cur = seq_np_nxt["data"][i]["img"]

                        list_removed_sl.append(i)
                        sl_seg_prv = sl_seg_cur
                        sl_prv = sl_cur

                        self.process_statistics["appearance"]["num_detected_violation"] += 1
                    for i in range(len(list_removed_sl)):
                        seq_ap_cur["data"].insert(-1, seq_np_nxt["data"][0])
                        seq_np_nxt["data"].pop(0)

                    for k in range(len(seq_np_nxt["data"])):
                        self.process_statistics["appearance"]["remedy_states"][seq_np_nxt["data"][k]["id"]] = "Remedied"
                        self.process_statistics["appearance"]["num_remedied_SLs"] += 1
            except:
                pass
            results = [seq_np_prv, seq_ap_cur, seq_np_nxt]
        return results

    def __check_seq_inclusion(self, seq):
        """
        To check inclusion relationship of the whole SLSeq in SEQ
        :param seq:
        :return:
        """
        is_included = True
        prv_sl_seg = seq[0]["img"]
        count = 0
        for i in range(1, len(seq)):
            cur_sl_seg = seq[i]["img"]
            if np.count_nonzero(np.bitwise_and(prv_sl_seg, cur_sl_seg)) == 0:
                count += 1
            prv_sl_seg = seq[i]["img"]
        if count / len(seq) > 0.3:
            is_included = False
        return is_included

    def __compute_transition(self, seq_, idx):
        """
        To compute transition of the size change in a SEQ
        :param seq:
        :param idx:
        :return:
        """
        seq = copy.deepcopy(seq_)
        prv = np.count_nonzero(seq[0]["img"])
        list_remove = []
        is_wrong = False
        for i in range(1, len(seq)):
            if not is_wrong:
                if np.abs((np.count_nonzero(seq[i]["img"])-prv)/np.min([np.count_nonzero(seq[i]["img"]), prv]))>1.5:
                    is_wrong = True
                    list_remove.append(i)
                    # continue
            else:
                if np.abs((np.count_nonzero(seq[i]["img"])-prv)/np.min([np.count_nonzero(seq[i]["img"]), prv]))>0.5:
                    is_wrong = False
                else:
                    list_remove.append(i)
                    # continue
            # print("  ", seq[i]["fname"], np.abs((np.count_nonzero(seq[i]["img"])-prv)/np.min([np.count_nonzero(seq[i]["img"]), prv])))
            prv = np.count_nonzero(seq[i]["img"])
        for i in reversed(list_remove):
            del seq[i]

        # print(">>>", len(seq_), len(seq))
        if idx == -1:
            idx = len(seq) - 1
        max_idx = self.__get_maximum_size_sl_id(seq)
        if max_idx == idx:  # Case 1.
            if idx == 0:
                idx = len(seq) - 1
            else:
                idx = 0
        list_diff = []

        min_size = np.inf
        min_id = -1
        maximum_size = 0
        maximum_id = -1
        transition_ = 0
        if max_idx < idx:
            max_size = np.count_nonzero(seq[max_idx]["img"])
            for i in range(max_idx+1, idx):
                cur_size = np.count_nonzero(seq[i]["img"])
                try:
                    diff = (cur_size-max_size) /cur_size
                except ZeroDivisionError:
                    diff = 0
                list_diff.append(diff)
                max_size = cur_size
                if cur_size < min_size:
                    min_size = cur_size
                    min_id = i
                if cur_size> maximum_size:
                    maximum_size = cur_size
                    maximum_id = i
            transition_ = np.sign(maximum_id-min_id)*(maximum_size-min_size) / maximum_size
        else:
            idx_size = np.count_nonzero(seq[idx]["img"])
            for i in range(idx+1, max_idx+1):
                cur_size = np.count_nonzero(seq[i]["img"])
                try:
                    diff = (cur_size-idx_size) /idx_size
                except ZeroDivisionError:
                    diff = 0
                list_diff.append(diff)
                idx_size = cur_size
                if cur_size < min_size:
                    min_size = cur_size
                if cur_size> maximum_size:
                    maximum_size = cur_size
            transition_ = np.sign(min_id-maximum_id)*(maximum_size-min_size) / maximum_size
            # max_size = np.count_nonzero(seq[max_idx]["img"])
            # cur_size = np.count_nonzero(seq[idx]["img"])
            # if max_size == 0:
            #     return 0
            # if len(seq) > 1:
            #     transition = (max_size - cur_size) / max_size
            # else:
            #     transition = (cur_size - max_size) / max_size
        list_diff = np.array(list_diff)
        list_diff = list_diff[(list_diff<1)]
        list_diff = list_diff[(list_diff>-1)]
        transition = np.average(list_diff)

        # print(len(list_diff), transition, (min_size - maximum_size) / maximum_size, maximum_size, min_size)
        if max_idx-1 == idx:
            return -0.1
        if len(list_diff) <=1:
            # print(">>>>>> ", len(list_diff), len(seq), max_idx, idx)
            return 0.0

        # print(transition, list_diff)
        return transition

    def __revise_slsegs_based_on_adjacent_segmentations(self, prv_seg, cur_seg, nxt_seg, prv_img, cur_img, nxt_img, size_diff_trend=1.0):
        """
        TO revise segmentation results considering adjacent slices
        :return:
        """
        # print(">>>>>>>>> ", size_diff_trend)
        if prv_seg is None:
            new_mask = np.zeros((512, 512))
            # Case of previous slice is None --> Apply next slice data (Re-selecting position and Erosion)

            # 1. Erode / Dilate the area depending on the size change trend
            # 2. If there is any empty area in the original SLSeg, move the area to the result of step 2
            # 3. Fill and discard area depending on HU scale

            ctrs, _ = cv2.findContours(nxt_seg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            new_mask = cv2.drawContours(new_mask, ctrs, 0, 255, -1)
            diff = np.inf
            new_msk_prv = None
            while True:
                if np.count_nonzero(nxt_seg)!= 0:
                    if size_diff_trend <0:
                        new_mask = cv2.erode(new_mask, np.ones((3, 3), np.uint8), iterations=1)
                    else:
                        new_mask = cv2.dilate(new_mask, np.ones((3, 3), np.uint8), iterations=1)
                else:
                    new_mask = cv2.dilate(new_mask, np.ones((3, 3), np.uint8), iterations=1)
                diff_cur = np.abs((np.count_nonzero(nxt_seg)-np.count_nonzero(new_mask)) /np.count_nonzero(nxt_seg))
                if np.abs(size_diff_trend) < diff_cur <diff:
                    diff= diff_cur
                else:
                    if new_msk_prv is None:
                        new_msk_prv = new_mask
                    new_mask = copy.deepcopy(new_msk_prv)
                    break
                new_msk_prv = copy.deepcopy(new_mask)
            is_located_at_contour, mask_violated = self.__check_HU_scale_violated_pixel_location(cur_img, np.array(new_mask, np.uint8))
            if np.count_nonzero(np.subtract(new_mask, mask_violated))>0:
                new_mask = np.subtract(new_mask, mask_violated)
            else:
                if np.count_nonzero(cur_seg) == 0:
                    new_mask = nxt_seg
        if nxt_seg is None:
            # Case of Next slice is None --> Apply previous slice data (Re-Selecting position and Dilation)
            ctrs, _ = cv2.findContours(prv_seg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            # new_mask = cv2.drawContours(new_mask, ctrs, 0, 255, -1)
            new_mask = copy.deepcopy(prv_seg)
            new_mask_fill = copy.deepcopy(new_mask)
            diff = np.inf
            new_msk_prv = None
            while True:
                if np.count_nonzero(prv_seg) != 0:
                    if size_diff_trend < 0:
                        new_mask = cv2.erode(new_mask, np.ones((3, 3), np.uint8), iterations=1)
                    else:
                        new_mask = cv2.dilate(new_mask, np.ones((3, 3), np.uint8), iterations=1)
                else:
                    new_mask = cv2.dilate(new_mask, np.ones((3, 3), np.uint8), iterations=1)

                diff_cur = np.abs((np.count_nonzero(prv_seg)-np.count_nonzero(new_mask)) /np.count_nonzero(prv_seg))
                if np.abs(size_diff_trend) < diff_cur < diff:
                    diff = diff_cur
                else:
                    if new_msk_prv is None:
                        new_msk_prv = copy.deepcopy(new_mask)
                    new_mask = copy.deepcopy(new_msk_prv)
                    break
                new_msk_prv = copy.deepcopy(new_mask)
            is_located_at_contour, mask_violated = self.__check_HU_scale_violated_pixel_location(cur_img, np.array(new_mask, np.uint8))
            if np.count_nonzero(np.subtract(new_mask, mask_violated))>0:
                new_mask = np.subtract(new_mask, mask_violated)
            else:
                if np.count_nonzero(cur_seg) == 0:
                    new_mask = prv_seg

        if prv_seg is not None and nxt_seg is not None:
            # Case of Previous and Next slices are None --> apply both slices data
            range_mask = np.bitwise_and(prv_seg, prv_img)
            range_mask = np.unique(range_mask)  # To select the range of  segmented area's grayscale in next slice
            range_mask = (min(range_mask), max(range_mask))

            overlapped = np.bitwise_and(prv_seg, cur_img)  # To overlap current slice and previous segmentation
            new_mask = np.where((overlapped >= range_mask[0] + 15) & (overlapped <= range_mask[1] - 15), 255, 0)
        return np.array(new_mask, dtype=np.uint8)

    def get_srs_org_sl(self):
        return self.srs_org_sl

    def get_srs_seg_sl(self):
        return self.srs_seg_sl

    ####################################################

    # Methods for Step 3. Correcting Location Inconsistency
    def remedy_location_consistency_violation(self):
        """
        To detect location consistency violation and remedy the violation
        :return:
        """
        self.list_prv = {}
        for id in range(len(self.sequences)):  # Loop for sequences
            for sl_id in range(len(self.sequences[id]["data"])):
                self.list_prv[self.sequences[id]["data"][sl_id]["id"]] = self.sequences[id]["data"][sl_id]["img"]
            if not self.sequences[id]["type"]:  # If the sequence is Excluded Sequence
                for d in self.sequences[id]["data"]:
                    self.process_statistics["location"]["remedy_states"][d["id"]] = "Not Violated"
                continue
            if len(self.sequences[id]["data"]) < len(self.srs_org_sl)*0.1:  # The length of the sequence is too short
                self.sequences[id]["type"] = False
                self.process_statistics["location"]["num_detected_violation"] += len(self.sequences[id]["data"])
                for j in range(len(self.sequences[id]["data"])):
                    self.sequences[id]["data"][j]["img"] = np.zeros(self.sequences[id]["data"][j]["img"].shape, np.uint8)
                    self.process_statistics["location"]["num_remedied_SLs"] += 1
                    self.process_statistics["location"]["remedy_states"][self.sequences[id]["data"][j]["id"]] = "Remedied"
                continue

            nxt_id = self.__get_maximum_size_sl_id(self.sequences[id]["data"])  # To set seed segmentation
            # print("  SEQUENCE # ", id,"  ", nxt_id)
            self.process_statistics["location"]["remedy_states"][
                self.sequences[id]["data"][nxt_id]["id"]] = "Not Violated"
            self.detect_enhance_location_consistency_violation(id, nxt_id=nxt_id)      # To compute the process from seed ~ 1

            prv_id = self.__get_maximum_size_sl_id(self.sequences[id]["data"])  # To set seed segmentation
            # print("  SEQUENCE # ", id,"  ", prv_id)
            self.detect_enhance_location_consistency_violation(id, prv_id=prv_id)      # To compute the process from seed ~ last

        self.__move_empty_to_false_seq()

        # Code for Statistics
        self.process_statistics["location"]["num_sequences"] = len(self.sequences)
        sizes = 0
        min_size = 1000000
        max_size = 0
        for seq in self.sequences:
            for i in seq["data"]:
                img = i["img"]
                if np.count_nonzero(img) > 0:
                    self.process_statistics["location"]["num_slices_having_organ"] += 1
                    sizes += np.count_nonzero(img)
                    if min_size > np.count_nonzero(img):
                        min_size = np.count_nonzero(img)
                    if max_size < np.count_nonzero(img):
                        max_size = np.count_nonzero(img)
        self.process_statistics["location"]["min_size"] = min_size
        self.process_statistics["location"]["max_size"] = max_size
        self.process_statistics["location"]["avg_size"] = round(sizes / self.process_statistics["location"]["num_slices_having_organ"], 2)
        if self.display:
            list_data = []
            list_selected_cur_ids = []
            for id in range(len(self.sequences)):
                for j in range(len(self.sequences[id]["data"])):
                    cur_id = self.sequences[id]["data"][j]["id"]
                    sl = self.__get_current_sl(id, j)

                    if cur_id in list_selected_cur_ids:
                        continue
                    list_selected_cur_ids.append(cur_id)
                    list_data.append([{"Slice": self.srs_org_sl[cur_id]["img"],
                                     "Seg. Result": self.list_prv[cur_id],
                                     "Remedied": self.sequences[id]["data"][j]["img"]},
                        {"Slice": {"fname": self.srs_org_sl[cur_id]["fname"].split(".")[0]},
                         "Seg. Result": {"sequence": {"id": id, "type": "Appeared" if self.sequences[id]["type"] else "Non-Appeared"},
                                         "size": format(np.count_nonzero(self.list_prv[cur_id]), ","),
                                         "HU Scale": self.__compute_HU_scale(sl, self.list_prv[cur_id])[0]},
                         "Remedied": {"size": format(np.count_nonzero(self.sequences[id]["data"][j]["img"]), ","),
                                      "HU Scale": self.__compute_HU_scale(sl, self.sequences[id]["data"][j]["img"])[0],
                                      "remedy_state": self.process_statistics["location"]["remedy_states"][cur_id]}
                         }])


            self.display_location_correction_result()
            self.visualize_location_remedied(list_data)
            # cv2.destroyAllWindows()
    def detect_enhance_location_consistency_violation(self, id, nxt_id=None, prv_id=None):
        """
        To detect and enhance the location consistency violation
        :param id: int, sequence id
        :param nxt_id: int, seed segmentation id when loop for seed~1
        :param prv_id: int, seed segmentation id when loop for seed~last
        """
        # To define the range of the loop
        if nxt_id is not None:
            # print("NXT_ID", nxt_id)
            range_loop = range(nxt_id-1, -1, -1)
            list_sl_seg_sections = self.__identify_segmented_masks(self.sequences[id]["data"][nxt_id]["img"])
            trg_id = nxt_id
        else:
            # print("PRV_ID", prv_id)
            range_loop = range(prv_id + 1, len(self.sequences[id]["data"]))
            list_sl_seg_sections = self.__identify_segmented_masks(self.sequences[id]["data"][prv_id]["img"])
            trg_id = prv_id
        slseg_trg = self.sequences[id]["data"][trg_id]["img"]
        sl_trg = self.__get_current_sl(id, trg_id)

        for sl_id in range_loop:  # loop for segmentation results
            self.process_statistics["location"]["remedy_states"][self.sequences[id]["data"][sl_id]["id"]] = "Not Violated"
            list_sl_seg_sections_cur = self.__identify_segmented_masks(self.sequences[id]["data"][sl_id]["img"])
            slseg_cur = self.sequences[id]["data"][sl_id]["img"]
            sl_cur = self.__get_current_sl(id, sl_id)
            list_not_contained_secs = list(range(len(list_sl_seg_sections)))
            is_not_violated = True
            for sec_cur in list_sl_seg_sections_cur:    # Loop for segmented masks of the current segmentation result
                is_contained = False
                idx = -1
                for sec_trg in list_sl_seg_sections:    # loop for segmented masks for the seed segmentation
                    # To check the location consistency between the segmented masks
                    idx+=1
                    inclusion_rate = np.count_nonzero(np.bitwise_and(sec_trg, sec_cur)) / np.min([np.count_nonzero(sec_trg), np.count_nonzero(sec_cur)])
                    if inclusion_rate > 0.5:
                        # Maintain the area
                        is_contained = True
                        if idx in list_not_contained_secs:
                            list_not_contained_secs.remove(idx)
                        continue
                if not is_contained:
                    slseg_cur = np.subtract(slseg_cur, sec_cur)
                    if self.process_statistics["location"]["remedy_states"][self.sequences[id]["data"][sl_id]["id"]] != "Remedied":
                        self.process_statistics["location"]["num_remedied_SLs"] += 1
                    self.process_statistics["location"]["remedy_states"][
                        self.sequences[id]["data"][sl_id]["id"]] = "Remedied"
                    if is_not_violated:
                        is_not_violated = is_contained
            if not is_not_violated:
                print(self.process_statistics["location"])
                self.process_statistics["location"]["num_detected_violation"] += 1

            # To generate the segmented sections depending on the location consistency
            if prv_id is None:
                range_trend = range(sl_id-1, -1, -1)
            else:
                range_trend = range(sl_id+1, len(self.sequences[id]["data"]))
            for sec_trg_idx in list_not_contained_secs:
                sec_trg = list_sl_seg_sections[sec_trg_idx]
                need_to_connect = False
                for k in range_trend:
                    slseg_x = self.sequences[id]["data"][k]["img"]
                    inclusion_rate_x = np.count_nonzero(np.bitwise_and(sec_trg, slseg_x)) / np.min(
                        [np.count_nonzero(sec_trg), np.count_nonzero(slseg_x)])
                    if inclusion_rate_x >self.th_inclusion and np.count_nonzero(slseg_trg) > np.count_nonzero(slseg_x):
                        need_to_connect = True
                if need_to_connect:
                    if self.process_statistics["location"]["remedy_states"][self.sequences[id]["data"][sl_id]["id"]] != "Remedied":
                        self.process_statistics["location"]["num_detected_violation"] += 1
                    new_sec = np.zeros(sec_trg.shape, np.uint8)
                    if prv_id is None:
                        new_sec = self.__revise_slsegs_based_on_adjacent_segmentations(sec_trg, new_sec, None, sl_trg, sl_cur, None, 0.8)
                    else:
                        new_sec = self.__revise_slsegs_based_on_adjacent_segmentations(None, new_sec, sec_trg, None, sl_cur, sl_trg, 0.8)

                    if self.process_statistics["location"]["remedy_states"][self.sequences[id]["data"][sl_id]["id"]] != "Remedied":
                        self.process_statistics["location"]["num_remedied_SLs"] += 1
                    self.process_statistics["location"]["remedy_states"][
                        self.sequences[id]["data"][sl_id]["id"]] = "Remedied"

                    slseg_cur = np.array(np.where(slseg_cur+new_sec>0, 255, 0), np.uint8)

            self.sequences[id]["data"][sl_id]["img"] = slseg_cur
            list_sl_seg_sections = self.__identify_segmented_masks(self.sequences[id]["data"][sl_id]["img"])
            sl_trg = sl_cur
            slseg_trg = slseg_cur

    def __get_maximum_size_sl_id(self, seq):
        """
        To get maximum size of sl and return the id of the slice
        :param seq: list, a sequence
        :return: int sl id
        """
        big_id, size = -1, -1  # Initialize
        for sl_id in range(len(seq)):  # Loop for whole slices in input sequence
            sl = seq[sl_id]
            if np.count_nonzero(
                    sl["img"]) > size:  # if segmentation result's size in current sl is bigger than prev. biggest size
                big_id = sl_id  # change
                size = np.count_nonzero(sl["img"])
        return big_id

    def __identify_segmented_masks(self, cur_sl):
        """
        To divide sections of a segmentation result
        :param cur_sl: ndarray, segmentation result
        :return:list, each section of segmentation result
        """
        list_result = []
        cur_sl = np.array(np.where(cur_sl>128, 255, 0), dtype=np.uint8)  # To convert the data type in input slice
        cur_cnt, _ = cv2.findContours(cur_sl, cv2.RETR_EXTERNAL,
                                      cv2.CHAIN_APPROX_NONE)  # To find contours in the input segmentation result
        for i in cur_cnt:  # To repeat the found contours
            new_mask = np.zeros(cur_sl.shape)
            list_result.append(np.array(cv2.drawContours(new_mask, [i], -1, color=255, thickness=cv2.FILLED),
                                        dtype=np.uint8))  # To save seg. sections
        return list_result
    ####################################################

    # Methods for Step 4. Correcting Size Inconsistency
    def remedy_size_consistency_violation(self):
        """
        To detect and remedy the shape consistency violation
        :return:
        """
        self.list_prv = {}
        for id in range(len(self.sequences)):  # Loop for sequences
            for sl_id in range(len(self.sequences[id]["data"])):
                self.process_statistics["size"]["remedy_states"][self.sequences[id]["data"][sl_id]["id"]] = "Not Violated"
                self.list_prv[self.sequences[id]["data"][sl_id]["id"]] = self.sequences[id]["data"][sl_id]["img"]
            if not self.sequences[id]["type"]:  # If the sequence contain the organ:
                for d in self.sequences[id]["data"]:
                    self.process_statistics["size"]["remedy_states"][d["id"]] = "Not Violated"
                continue
            list_groups = self.generate_groups_for_size_difference(id)
            self.detect_enhance_size_consistency_violation(list_groups, id)
        self.__move_empty_to_false_seq()

        # Code for Statistics
        self.process_statistics["size"]["num_sequences"] = len(self.sequences)
        sizes = 0
        min_size = 1000000
        max_size = 0
        for seq in self.sequences:
            for i in seq["data"]:
                img = i["img"]
                if np.count_nonzero(img) > 0:
                    self.process_statistics["size"]["num_slices_having_organ"] += 1
                    sizes += np.count_nonzero(img)
                    if min_size > np.count_nonzero(img):
                        min_size = np.count_nonzero(img)
                    if max_size < np.count_nonzero(img):
                        max_size = np.count_nonzero(img)
        self.process_statistics["size"]["min_size"] = min_size
        self.process_statistics["size"]["max_size"] = max_size
        self.process_statistics["size"]["avg_size"] = round(sizes / self.process_statistics["size"]["num_slices_having_organ"], 2)
        if self.display:
            list_data = []
            list_selected_cur_ids = []
            for id in range(len(self.sequences)):
                for j in range(len(self.sequences[id]["data"])):
                    cur_id = self.sequences[id]["data"][j]["id"]
                    sl = self.__get_current_sl(id, j)
                    if cur_id in list_selected_cur_ids:
                        continue
                    list_selected_cur_ids.append(cur_id)
                    list_data.append([{"Slice": self.srs_org_sl[cur_id]["img"],
                                     "Seg. Result": self.list_prv[cur_id],
                                     "Remedied": self.sequences[id]["data"][j]["img"]},
                        {"Slice": {"fname": self.srs_org_sl[cur_id]["fname"].split(".")[0]},
                         "Seg. Result": {"sequence": {"id": id, "type": "Appeared" if self.sequences[id]["type"] else "Non-Appeared"},
                                         "size": format(np.count_nonzero(self.list_prv[cur_id]), ","),
                                         "HU Scale": self.__compute_HU_scale(sl, self.list_prv[cur_id])[0]},
                         "Remedied": {"size": format(np.count_nonzero(self.sequences[id]["data"][j]["img"]), ","),
                                      "HU Scale": self.__compute_HU_scale(sl, self.sequences[id]["data"][j]["img"])[0],
                                      "remedy_state": self.process_statistics["size"]["remedy_states"][cur_id]}
                         }])
            self.display_size_correction_result()
            self.visualize_size_remedied(list_data)
            # cv2.destroyAllWindows()

    def generate_groups_for_size_difference(self, id):
        """
        To generate groups based on the location difference of segmentation results for adjacent CT slices
        """
        list_groups = []

        # To find size consistency violated SLSegs
        # To make groups depending on high difference of size between adjacent SLSeg
        size_sl_seg_prv = np.count_nonzero(self.sequences[id]["data"][0]["img"])
        cur_group = [self.sequences[id]["data"][0]]
        empty_sl_count = 0
        max_id = self.__get_maximum_size_sl_id(self.sequences[id]["data"])
        for sl_id in range(1, len(self.sequences[id]["data"])):     # Loop for Segmentation resutls in the Sequence
            size_sl_seg_cur = np.count_nonzero(self.sequences[id]["data"][sl_id]["img"])
            if size_sl_seg_cur == 0:
                self.sequences[id]["data"][sl_id]["img"] = np.zeros(self.sequences[id]["data"][sl_id]["img"].shape, np.uint8)
                try:
                    self.sequences[id+1]["data"].insert(empty_sl_count, self.sequences[id]["data"][sl_id])
                except:
                    pass
                empty_sl_count+=1
                continue
            if empty_sl_count>0:
                continue
            size_diff = (size_sl_seg_prv - size_sl_seg_cur) / size_sl_seg_prv
            size_sl_seg_prv = size_sl_seg_cur

            if sl_id < max_id:
                max_diff = max_id
            else:
                max_diff = len(self.sequences[id]["data"]) - max_id
            if np.abs(size_diff) > self.th_size+0.3*(np.abs(max_id-sl_id)/max_diff):
                list_groups.append(cur_group)
                cur_group = [self.sequences[id]["data"][sl_id]]
            else:
                cur_group.append(self.sequences[id]["data"][sl_id])
        if len(cur_group) > 0:
            list_groups.append(cur_group)
        return list_groups

    def detect_enhance_size_consistency_violation(self, list_groups, id):
        # try:
        # To find a group containing the most number of SLSeg
        max_id = -1
        max_size = 0
        for i in range(len(list_groups)):
            for j in range(len(list_groups[i])):
                if max_size< np.count_nonzero(list_groups[i][j]["img"]):
                    max_id = i
                    max_size = np.count_nonzero(list_groups[i][j]["img"])
        nxt_group = list_groups[max_id]
        for i in nxt_group:
            if i["id"] not in self.process_statistics["size"]["remedy_states"].keys():
                self.process_statistics["size"]["remedy_states"][i["id"]] = "Not Violated"
        size_transition = self.__compute_transition(nxt_group, 0)   # To compute the transition of the size difference from the seed to the first segmetnation result
        for i in reversed(range(max_id)):       # Loop for segmentation resutls (seed_segmentation ~ 1st segmentation)
            slseg_nxt = list_groups[i+1][0]["img"]
            slseg_cur = list_groups[i][-1]["img"]
            size_diff = (np.count_nonzero(slseg_cur) - np.count_nonzero(slseg_nxt)) / np.count_nonzero(slseg_cur)
            if np.abs(size_diff) < self.th_size+0.3:
                for k in range(len(list_groups[i])):
                    list_groups[i + 1].insert(k, list_groups[i][k])
                del list_groups[i]
                continue
            is_empty = False
            self.process_statistics["size"]["num_detected_violation"] += len(list_groups[i])
            for j in reversed(range(len(list_groups[i]))):
                slseg_cur = list_groups[i][j]["img"]
                diff = np.inf
                slseg_cur_nxt = []

                # To revise segmentation results
                while True:
                    # To resize the segmentation results based on the size transition
                    if np.sign(size_transition)>0:
                        if np.count_nonzero(slseg_cur)<np.count_nonzero(slseg_nxt):
                            slseg_cur = cv2.dilate(slseg_cur, np.ones((3, 3), np.uint8), iterations=1)
                        else:
                            slseg_cur = cv2.erode(slseg_cur, np.ones((3, 3), np.uint8), iterations=1)
                    else:
                        if np.count_nonzero(slseg_cur)<np.count_nonzero(slseg_nxt):
                            slseg_cur = cv2.erode(slseg_cur, np.ones((3, 3), np.uint8), iterations=1)
                        else:
                            slseg_cur = cv2.dilate(slseg_cur, np.ones((3, 3), np.uint8), iterations=1)

                    if np.count_nonzero(slseg_cur) == 0:
                        is_empty = True
                    if not is_empty:
                        diff_size = (np.count_nonzero(slseg_cur) - np.count_nonzero(slseg_nxt)) / np.count_nonzero(slseg_cur)

                        if np.count_nonzero(slseg_cur) > 250000 or np.count_nonzero(slseg_cur) == 0:
                            # print("ERROR 1. SIZE")
                            break
                        if np.abs(diff_size) < diff:        # if the size of the enhanced segmentation is similar to the current segmentation
                            diff = diff_size
                            slseg_cur_nxt = copy.deepcopy(slseg_cur)
                        else:                               # If the size difference is bigger than threshold.
                            slseg_cur = copy.deepcopy(slseg_cur_nxt)
                            sl_id = self.__find_cur_sl_id_for_size_violation(list_groups, i, j)
                            list_groups[i][j]["img"] = slseg_cur
                            if self.process_statistics["size"]["remedy_states"][list_groups[i][j]["id"]] != "Remedied":
                                self.process_statistics["size"]["num_remedied_SLs"] += 1
                            self.process_statistics["size"]["remedy_states"][list_groups[i][j]["id"]] = "Remedied"
                            self.sequences[id]["data"][sl_id]["img"] = copy.deepcopy(slseg_cur)
                            break
                    else:
                        slseg_cur = copy.deepcopy(slseg_cur)
                        sl_id = self.__find_cur_sl_id_for_size_violation(list_groups, i, j)
                        list_groups[i][j]["img"] = slseg_cur
                        if self.process_statistics["size"]["remedy_states"][list_groups[i][j]["id"]] != "Remedied":
                            self.process_statistics["size"]["num_remedied_SLs"] += 1
                        self.process_statistics["size"]["remedy_states"][list_groups[i][j]["id"]] = "Remedied"
                        self.sequences[id]["data"][sl_id]["img"] = copy.deepcopy(slseg_cur)
                        break
                slseg_nxt = slseg_cur
            for k in range(len(list_groups[i])):
                list_groups[i+1].insert(k, list_groups[i][k])
            del list_groups[i]

        max_id = 0
        prv_group = list_groups[max_id]
        i = 1
        while len(list_groups)>1:  # To remedy the violation from max_id to 0
            # print("CASE3",len(list_groups), len(list_groups[max_id]), max_id)
            size_transition = self.__compute_transition(prv_group, -1)

            # To check whether the current sequence complies with the size consistency
            slseg_prv = list_groups[max_id][-1]["img"]
            slseg_cur = list_groups[max_id+1][0]["img"]
            size_diff = (np.count_nonzero(slseg_prv) - np.count_nonzero(slseg_cur)) / np.count_nonzero(slseg_prv)
            # If the size difference between first seg. result in cur. group the last seg. result in prv group, skip revision
            if np.abs(size_diff) < self.th_size+0.3:
                for k in range(len(list_groups[i])):
                    list_groups[i - 1].append(list_groups[i][k])
                del list_groups[i]
                continue

            is_empty = False

            self.process_statistics["size"]["num_detected_violation"] += len(list_groups[i])
            for j in range(len(list_groups[i])):
                slseg_cur = list_groups[i][j]["img"]
                diff = np.inf
                slseg_cur_prv = []
                # To revise segmentation results
                while True:
                    if np.sign(size_transition)>0:
                        if np.count_nonzero(slseg_prv)<np.count_nonzero(slseg_cur):   # Decreasing Transition and
                            # print("REVISE Case 1")
                            slseg_cur = cv2.dilate(slseg_cur, np.ones((3, 3), np.uint8), iterations=1)
                        else:
                            # print("REVISE Case 2")
                            slseg_cur = cv2.erode(slseg_cur, np.ones((3, 3), np.uint8), iterations=1)

                    else:
                        if np.count_nonzero(slseg_prv)<np.count_nonzero(slseg_cur):
                            # print("REVISE Case 3")
                            slseg_cur = cv2.erode(slseg_cur, np.ones((3, 3), np.uint8), iterations=1)
                        else:
                            # print("REVISE Case 4")
                            slseg_cur = cv2.dilate(slseg_cur, np.ones((3, 3), np.uint8), iterations=1)

                    if np.count_nonzero(slseg_cur) == 0:
                        is_empty = True
                    if not is_empty:
                        diff_size = (np.count_nonzero(slseg_prv) - np.count_nonzero(slseg_cur)) / np.count_nonzero(
                            slseg_prv)
                        if np.count_nonzero(slseg_cur) > 250000 or np.count_nonzero(slseg_cur) == 0:
                            # print("ERROR 1. SIZE")
                            break
                        if np.abs(diff_size) < diff:
                            diff = diff_size
                            slseg_cur_prv = copy.deepcopy(slseg_cur)
                        else:
                            slseg_cur = copy.deepcopy(slseg_cur_prv)
                            sl_id = self.__find_cur_sl_id_for_size_violation(list_groups, i, j)
                            list_groups[i][j]["img"] = slseg_cur
                            if self.process_statistics["size"]["remedy_states"][list_groups[i][j]["id"]] != "Remedied":
                                self.process_statistics["size"]["num_remedied_SLs"] += 1
                            self.process_statistics["size"]["remedy_states"][list_groups[i][j]["id"]] = "Remedied"
                            self.sequences[id]["data"][sl_id]["img"] = copy.deepcopy(slseg_cur)
                            break
                    else:
                        slseg_cur = copy.deepcopy(slseg_cur_prv)
                        sl_id = self.__find_cur_sl_id_for_size_violation(list_groups, i, j)
                        list_groups[i][j]["img"] = slseg_cur
                        if self.process_statistics["size"]["remedy_states"][list_groups[i][j]["id"]] != "Remedied":
                            self.process_statistics["size"]["num_remedied_SLs"] += 1
                        self.process_statistics["size"]["remedy_states"][list_groups[i][j]["id"]] = "Remedied"
                        self.sequences[id]["data"][sl_id]["img"] = copy.deepcopy(slseg_cur)
                        break
                slseg_prv = slseg_cur
            for k in range(len(list_groups[i])):
                list_groups[i - 1].append(list_groups[i][k])
            del list_groups[i]

        ## To remove sections not showing location inconsistency.
        max_id = self.__get_maximum_size_sl_id(self.sequences[id]["data"])
        list_nxt_sections = self.__identify_segmented_masks(self.sequences[id]["data"][max_id]["img"])
        for i in reversed(range(max_id)):
            list_cur_sections = self.__identify_segmented_masks(self.sequences[id]["data"][i]["img"])
            for sec_cur in list_cur_sections:
                is_contained = False
                for sec_nxt in list_nxt_sections:
                    if np.count_nonzero(np.bitwise_and(sec_nxt, sec_cur))>0:
                        is_contained = True
                if not is_contained:
                    self.sequences[id]["data"][i]["img"] = np.subtract(self.sequences[id]["data"][i]["img"], sec_cur)
            list_nxt_sections = self.__identify_segmented_masks(self.sequences[id]["data"][i]["img"])

        list_prv_sections = self.__identify_segmented_masks(self.sequences[id]["data"][max_id]["img"])
        for i in range(max_id+1, len(self.sequences[id]["data"])):
            # print(self.sequences[id]["data"][i]["fname"], type(self.sequences[id]["data"][i]["img"]))
            if type(self.sequences[id]["data"][i]["img"]) == list:
                self.sequences[id]["data"][i]["img"] = np.zeros((512, 512), np.uint8)
            list_cur_sections = self.__identify_segmented_masks(self.sequences[id]["data"][i]["img"])
            for sec_cur in list_cur_sections:
                is_contained = False
                for sec_prv in list_prv_sections:
                    if np.count_nonzero(np.bitwise_and(sec_prv, sec_cur))>0:
                        is_contained = True
                if not is_contained:
                    self.sequences[id]["data"][i]["img"] = np.subtract(self.sequences[id]["data"][i]["img"], sec_cur)
            list_prv_sections = self.__identify_segmented_masks(self.sequences[id]["data"][i]["img"])

    ####################################################

    # Methods for Step 5. Correcting Shape Inconsistency
    def remedy_shape_consistency_violation(self):
        """
        To detect and remedy the shape consistency violation
        :return:
        """
        self.list_prv = {}
        for id in range(len(self.sequences)):  # Loop for sequences
            for sl_id in range(len(self.sequences[id]["data"])):
                self.list_prv[self.sequences[id]["data"][sl_id]["id"]] = self.sequences[id]["data"][sl_id]["img"]
            if not self.sequences[id]["type"]:  # If the sequence contain the organ
                for d in self.sequences[id]["data"]:
                    self.process_statistics["shape"]["remedy_states"][d["id"]] = "Not Violated"
                continue

            list_groups = self.generate_groups_for_shape_difference(id)   # To detect the violation in an included Sequence

            if len(list_groups)>1:
                self.sequences[id]["data"] = copy.deepcopy(self.detect_enhance_shape_consistency_violation(list_groups))
        self.__move_empty_to_false_seq()

        # Code for Statistics
        self.process_statistics["shape"]["num_sequences"] = len(self.sequences)
        sizes = 0
        min_size = 1000000
        max_size = 0
        for seq in self.sequences:
            for i in seq["data"]:
                img = i["img"]
                if np.count_nonzero(img) > 0:
                    self.process_statistics["shape"]["num_slices_having_organ"] += 1
                    sizes += np.count_nonzero(img)
                    if min_size > np.count_nonzero(img):
                        min_size = np.count_nonzero(img)
                    if max_size < np.count_nonzero(img):
                        max_size = np.count_nonzero(img)
        self.process_statistics["shape"]["min_size"] = min_size
        self.process_statistics["shape"]["max_size"] = max_size
        self.process_statistics["shape"]["avg_size"] = round(sizes / self.process_statistics["shape"]["num_slices_having_organ"], 2)
        if self.display:
            list_data = []

            list_selected_cur_ids = []
            for id in range(len(self.sequences)):
                for j in range(len(self.sequences[id]["data"])):
                    cur_id = self.sequences[id]["data"][j]["id"]
                    # if (np.count_nonzero(self.srs_seg_sl[cur_id]["img"])==0) and (np.count_nonzero(self.sequences[id]["data"][j]["img"])==0) :
                    #     continue
                    sl = self.__get_current_sl(id, j)

                    if cur_id in list_selected_cur_ids:
                        continue
                    list_selected_cur_ids.append(cur_id)
                    list_data.append([{"Slice": self.srs_org_sl[cur_id]["img"],
                                     "Seg. Result": self.list_prv[cur_id],
                                     "Remedied": self.sequences[id]["data"][j]["img"]},
                        {"Slice": {"fname": self.srs_org_sl[cur_id]["fname"].split(".")[0]},
                         "Seg. Result": {"sequence": {"id": id, "type": "Appeared" if self.sequences[id]["type"] else "Non-Appeared"},
                                         "size": format(np.count_nonzero(self.list_prv[cur_id]), ","),
                                         "HU Scale": self.__compute_HU_scale(sl, self.list_prv[cur_id])[0]},
                         "Remedied": {"size": format(np.count_nonzero(self.sequences[id]["data"][j]["img"]), ","),
                                      "HU Scale": self.__compute_HU_scale(sl, self.sequences[id]["data"][j]["img"])[0],
                                      "remedy_state": self.process_statistics["shape"]["remedy_states"][cur_id]}
                         }])

            idx = -1
            prv_seg = None
            prv_rmd = None
            for id in range(len(self.sequences)):  # Loop for sequences
                for sl_id in range(len(self.sequences[id]["data"])):  # To check empty slice
                    cur_id = self.sequences[id]["data"][sl_id]["id"]
                    idx += 1
                    if idx == 0:
                        prv_seg = self.list_prv[cur_id]
                        prv_rmd = self.sequences[id]["data"][sl_id]["img"]
                        continue
                    cur_seg = self.list_prv[cur_id]
                    cur_rmd = self.sequences[id]["data"][sl_id]["img"]
                    shape_diff_seg = self.__compute_shape_difference(prv_seg, cur_seg)
                    shape_diff_rmd = self.__compute_shape_difference(prv_rmd, cur_rmd)
                    if np.count_nonzero(prv_seg) == 0:
                        shape_diff_seg = 0
                    if np.count_nonzero(prv_rmd) == 0:
                        shape_diff_rmd = 0
                    self.process_statistics["shape"]["shape_diff_seg"][idx] = shape_diff_seg
                    self.process_statistics["shape"]["shape_diff_rmd"][idx] = shape_diff_rmd
                    prv_seg = cur_seg
                    prv_rmd = cur_rmd

            self.display_shape_correction_result()
            self.visualize_shape_remedied(list_data)
            # cv2.destroyAllWindows()

    def generate_groups_for_shape_difference(self, seq_id):
        """
        To generate groups for shape difference
        :param seq_id: int, sequence ID
        """
        list_groups = []
        sl_seg_prv = self.sequences[seq_id]["data"][0]["img"]
        sl_seg_prv_secs = self.__identify_segmented_masks(sl_seg_prv)

        cur_group = [self.sequences[seq_id]["data"][0]]

        self.process_statistics["shape"]["remedy_states"][self.sequences[seq_id]["data"][0]["id"]] = "Not Violated"
        for sl_id in range(1, len(self.sequences[seq_id]["data"])):     # Loop for segmentation results
            self.process_statistics["shape"]["remedy_states"][self.sequences[seq_id]["data"][sl_id]["id"]] = "Not Violated"
            sl_seg_cur = self.sequences[seq_id]["data"][sl_id]["img"]
            sl_seg_cur_secs = self.__identify_segmented_masks(sl_seg_cur)   # To identify segmented masks
            is_satisfy = True

            max_id = self.__get_maximum_size_sl_id(self.sequences[seq_id]["data"])
            if sl_id < max_id:
                max_diff = max_id
            else:
                max_diff = len(self.sequences[seq_id]["data"]) - max_id
            cur_th_shape = self.th_shape+0.1*(np.abs(max_id-sl_id)/max_diff)

            if len(sl_seg_cur_secs) == 1 and len(sl_seg_prv_secs) == 1:
                # Case 1. SLSegSec_cur == 1 and SLSegSec_prv == 1, compare shape difference
                diff_shape = self.__compute_shape_difference(sl_seg_prv, sl_seg_cur)
                is_satisfy = diff_shape < cur_th_shape

            elif (len(sl_seg_cur_secs) > 1 and len(sl_seg_prv_secs) == 1) or (
                    len(sl_seg_cur_secs) == 1 and len(sl_seg_prv_secs) > 1):
                # Case 2. one contains a section, the other contains multiple sections, compare inclusion
                is_satisfy = np.count_nonzero(np.bitwise_and(sl_seg_prv, sl_seg_cur)) / np.max(
                    [np.count_nonzero(sl_seg_prv), np.count_nonzero(sl_seg_cur)])
            else:
                # Case 3. Both contain multiple sections
                for sec_cur in sl_seg_cur_secs:
                    is_contained = False
                    for sec_prv in sl_seg_prv_secs:
                        if np.count_nonzero(np.bitwise_and(sec_cur, sec_prv)) > 0:
                            is_contained = True
                            diff_shape = self.__compute_shape_difference(sec_prv, sec_cur)
                            if diff_shape > cur_th_shape:
                                is_satisfy = False
                    if not is_contained:
                        self.sequences[seq_id]["data"][sl_id]["img"] = np.subtract(
                            self.sequences[seq_id]["data"][sl_id]["img"], sec_cur)
            if is_satisfy:
                # Satisfy the principle
                cur_group.append(self.sequences[seq_id]["data"][sl_id])
            else:
                # Violate the principle
                list_groups.append(cur_group)
                cur_group = [self.sequences[seq_id]["data"][sl_id]]
            sl_seg_prv = sl_seg_cur
            sl_seg_prv_secs = sl_seg_cur_secs

        if len(cur_group) > 0:
            list_groups.append(cur_group)
        return list_groups

    def detect_enhance_shape_consistency_violation(self, list_groups):
        """
        To detect and enhance the shape consistency violation
        :param list_groups: list, Target Group  violated the consistency
        """
        max_size = 0
        max_group_idx = -1
        for i in range(len(list_groups)):
            if max_size < len(list_groups[i]):
                max_size = len(list_groups[i])
                max_group_idx = i
        sl_seg_nxt = list_groups[max_group_idx][0]["img"]
        max_id = 0
        max_size = 0
        start_id = list_groups[0][0]["id"]
        for i in list_groups:
            for j in i:
                if np.count_nonzero(j["img"])>max_size:
                    max_size = np.count_nonzero(j["img"])
                    max_id = j["id"]

        for i in range(max_group_idx-1, -1, -1):    # Loop for groups (max_group_id ~ 1)
            diff_shape = self.__compute_shape_difference(list_groups[i][-1]["img"], sl_seg_nxt) # To compute the shape difference between two sequences
            cur_th_shape = self.th_shape+0.1*(np.abs(max_id-list_groups[i][-1]["id"])/(max_id-start_id))
            if diff_shape < cur_th_shape:
                for j in range(len(list_groups[i])-1, -1, -1):
                    list_groups[i + 1].insert(0, list_groups[i][j])
                    del list_groups[i][j]
                del list_groups[i]
                continue

            self.process_statistics["shape"]["num_detected_violation"] += len(list_groups[i])
            for j in range(len(list_groups[i])-1, -1, -1):  # Loop for the other groups
                sl_seg_trg = list_groups[i][j]["img"]
                cur_sl_org = self.srs_org_mi[:, :, list_groups[i][j]["id"]]
                if self.process_statistics["shape"]["remedy_states"][list_groups[i][j]["id"]] != "Remedied":
                    self.process_statistics["shape"]["num_remedied_SLs"] += 1
                self.process_statistics["shape"]["remedy_states"][list_groups[i][j]["id"]] = "Remedied"
                if np.count_nonzero(sl_seg_trg)==0:
                    list_groups[i][j]["img"] = sl_seg_trg
                    list_groups[i + 1].insert(0, list_groups[i][j])
                    del list_groups[i][j]
                    sl_seg_nxt = sl_seg_trg
                    continue
                if np.count_nonzero(sl_seg_nxt) == 0:
                    sl_seg_trg = np.zeros(sl_seg_nxt.shape, np.uint8)
                else:
                    sl_seg_trg = self.__revise_slseg_shape_violation(sl_seg_trg, sl_seg_nxt, cur_sl_org)
                list_groups[i][j]["img"] = sl_seg_trg
                list_groups[i+1].insert(0, list_groups[i][j])
                del list_groups[i][j]
                sl_seg_nxt = sl_seg_trg
            del list_groups[i]

        max_size = 0
        max_group_idx = -1
        for i in range(len(list_groups)):
            if max_size < len(list_groups[i]):
                max_size = len(list_groups[i])
                max_group_idx = i
        sl_seg_prv = list_groups[max_group_idx][-1]["img"]
        while len(list_groups)>1:   # Loop for other remaining groups
            diff_shape = self.__compute_shape_difference(sl_seg_prv, list_groups[max_group_idx+1][0]["img"])
            if diff_shape < self.th_shape:
                for j in range(len(list_groups[max_group_idx+1])):
                    list_groups[max_group_idx].append(list_groups[max_group_idx+1][j])
                del list_groups[max_group_idx+1]
                continue

            self.process_statistics["shape"]["num_detected_violation"] += len(list_groups[max_group_idx+1])
            while len(list_groups[max_group_idx+1])>0:
                sl_seg_trg = list_groups[max_group_idx+1][0]["img"]
                cur_sl_org = self.srs_org_mi[:, :, list_groups[max_group_idx+1][0]["id"]]
                if self.process_statistics["shape"]["remedy_states"][list_groups[max_group_idx+1][0]["id"]] != "Remedied":
                    self.process_statistics["shape"]["num_remedied_SLs"] += 1
                self.process_statistics["shape"]["remedy_states"][list_groups[max_group_idx+1][0]["id"]] = "Remedied"
                if np.count_nonzero(sl_seg_trg)==0:
                    list_groups[max_group_idx + 1][0]["img"] = sl_seg_trg
                    list_groups[max_group_idx].append(list_groups[max_group_idx + 1][0])
                    del list_groups[max_group_idx + 1][0]
                    sl_seg_prv = sl_seg_trg
                    continue

                if np.count_nonzero(sl_seg_prv) == 0:
                    sl_seg_trg = np.zeros(sl_seg_prv.shape, np.uint8)
                else:
                    sl_seg_trg = self.__revise_slseg_shape_violation(sl_seg_trg, sl_seg_prv, cur_sl_org)
                list_groups[max_group_idx+1][0]["img"] = sl_seg_trg
                list_groups[max_group_idx].append(list_groups[max_group_idx+1][0])
                del list_groups[max_group_idx+1][0]
                sl_seg_prv = sl_seg_trg
            del list_groups[max_group_idx+1]
        return list_groups[0]

    def __compute_shape_difference(self, msk_a, msk_b):
        return cv2.matchShapes(msk_a, msk_b, cv2.CONTOURS_MATCH_I3, 0)

    def __revise_slseg_shape_violation(self, msk_a, msk_b, sl_org):
        """
        To revise segmetnation results violating shape consistency
        """
        msk_a_org = copy.deepcopy(msk_a)
        msk_b_org = copy.deepcopy(msk_b)
        # print(np.count_nonzero(msk_a) , "\t",np.count_nonzero(msk_b))
        # To check Size of the Segmentation Result -> Resize the segmentation result
        if np.count_nonzero(msk_b_org) > np.count_nonzero(msk_a):
            diff = np.inf
            msk_b_prv = None
            while True:
                msk_b = cv2.erode(msk_b, np.ones((3, 3), np.uint8), iterations=1)
                cur_diff = np.abs((np.count_nonzero(msk_a) - np.count_nonzero(msk_b)) / np.count_nonzero(msk_a))
                if (cur_diff < diff):
                    diff = cur_diff
                else:
                    if (np.count_nonzero(msk_a) > np.count_nonzero(msk_b)):
                        msk_b = msk_b_prv
                        break
                msk_b_prv = copy.deepcopy(msk_b)
        else:
            diff = np.inf
            msk_b_prv = None
            while True:
                msk_b = cv2.dilate(msk_b, np.ones((3, 3), np.uint8), iterations=1)
                cur_diff = np.abs((np.count_nonzero(msk_b) - np.count_nonzero(msk_a)) / np.count_nonzero(msk_a))
                if diff > cur_diff:
                    diff = cur_diff
                else:
                    if (np.count_nonzero(msk_a) < np.count_nonzero(msk_b)):
                        msk_b = msk_b_prv
                        break
                msk_b_prv = msk_b

        # To find the contour locating middle of the two area
        msk_a_ivt = np.array(np.where(msk_b_org > 0, 0, 255), np.uint8)
        msk_b_ivt = np.array(np.where(msk_b > 0, 0, 255), np.uint8)

        dist_msk_a = cv2.distanceTransform(msk_b_org, cv2.DIST_L2, 3)
        dist_msk_a = cv2.normalize(dist_msk_a, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8UC1)
        dist_msk_a_ivt = cv2.distanceTransform(msk_a_ivt, cv2.DIST_L2, 5)
        dist_msk_a_ivt = cv2.normalize(dist_msk_a_ivt, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8UC1)
        dist_msk_b = cv2.distanceTransform(msk_b, cv2.DIST_L2, 3)
        dist_msk_b = cv2.normalize(dist_msk_b, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8UC1)
        dist_msk_b_ivt = cv2.distanceTransform(msk_b_ivt, cv2.DIST_L2, 5)
        dist_msk_b_ivt = cv2.normalize(dist_msk_b_ivt, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8UC1)

        dist_a = np.array(dist_msk_a, np.float) - np.array(dist_msk_a_ivt, np.float)
        dist_b = np.array(dist_msk_b, np.float) - np.array(dist_msk_b_ivt, np.float)
        result = np.array(np.where((dist_a + dist_b) > 0, 255, 0), np.uint8)

        # result = msk_b
        is_contour, violated_area = self.__check_HU_scale_violated_pixel_location(sl_org, result)
        if is_contour:
            result = np.subtract(result, violated_area)
            ctrs, _ = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            result = cv2.drawContours(result, ctrs, 0, 255, -1)
        # return result
        return msk_a

    ####################################################

    # Methods for Step 6. Correcting HU Scale Inconsistency
    def remedy_HU_scale_consistency_violation(self):
        """
        To detect and remedy HU scale consistency violation
        :return:
        """
        self.list_prv = {}
        for id in range(len(self.sequences)):   # Loop for Sequences
            if not self.sequences[id]["type"]:  # Non-Appeared Sequence
                # To check HU scale and add statistics
                for sl_id in range(len(self.sequences[id]["data"])):
                    self.process_statistics["HU"]["HU_scales_seg"][self.sequences[id]["data"][sl_id]["id"]] =\
                        self.__compute_HU_scale(self.__get_current_sl(id, sl_id), self.sequences[id]["data"][sl_id]["img"])[0]
                    self.process_statistics["HU"]["HU_scales_remedy"][self.sequences[id]["data"][sl_id]["id"]] =\
                        self.__compute_HU_scale(self.__get_current_sl(id, sl_id), self.sequences[id]["data"][sl_id]["img"])[0]
                    self.process_statistics["HU"]["remedy_states"][self.sequences[id]["data"][sl_id]["id"]] = "Not Violated"
                    self.list_prv[self.sequences[id]["data"][sl_id]["id"]] = self.sequences[id]["data"][sl_id]["img"]
                continue
            self.detect_HU_scale_consistency_violation(id)      # To detect the violation of HU scale consistency in Included Sequence

        # Code for Writing Statistics
        self.process_statistics["HU"]["num_sequences"] = len(self.sequences)
        sizes = 0
        min_size = 1000000
        max_size = 0
        for seq in self.sequences:
            for i in seq["data"]:
                img = i["img"]
                if np.count_nonzero(img) > 0:
                    self.process_statistics["HU"]["num_slices_having_organ"] += 1
                    sizes += np.count_nonzero(img)
                    if min_size > np.count_nonzero(img):
                        min_size = np.count_nonzero(img)
                    if max_size < np.count_nonzero(img):
                        max_size = np.count_nonzero(img)
        self.process_statistics["HU"]["min_size"] = min_size
        self.process_statistics["HU"]["max_size"] = max_size
        self.process_statistics["HU"]["avg_size"] = round(
            sizes / self.process_statistics["HU"]["num_slices_having_organ"], 2)
        # self.__move_empty_to_false_seq()
        if self.display:
            list_data = []

            list_selected_cur_ids = []
            # print(self.process_statistics["HU"]["remedy_states"].keys())
            for id in range(len(self.sequences)):
                for j in range(len(self.sequences[id]["data"])):
                    cur_id = self.sequences[id]["data"][j]["id"]
                    # if np.count_nonzero(self.srs_seg_sl[cur_id]["img"])==0 and np.count_nonzero(self.sequences[id]["data"][j]["img"])==0:
                    #     continue
                    sl = self.__get_current_sl(id, j)

                    if cur_id in list_selected_cur_ids:
                        continue
                    list_selected_cur_ids.append(cur_id)
                    list_data.append([{"Slice": self.srs_org_sl[cur_id]["img"],
                                     "Seg. Result": self.list_prv[cur_id],
                                     "Remedied": self.sequences[id]["data"][j]["img"]},
                        {"Slice": {"fname": self.srs_org_sl[cur_id]["fname"].split(".")[0]},
                         "Seg. Result": {"sequence": {"id": id, "type": "Appeared" if self.sequences[id]["type"] else "Non-Appeared"},
                                         "size": format(np.count_nonzero(self.list_prv[cur_id]), ","),
                                         "HU Scale": self.__compute_HU_scale(sl, self.list_prv[cur_id])[0]},
                         "Remedied": {"size": format(np.count_nonzero(self.sequences[id]["data"][j]["img"]), ","),
                                      "HU Scale": self.__compute_HU_scale(sl, self.sequences[id]["data"][j]["img"])[0],
                                      "remedy_state": self.process_statistics["HU"]["remedy_states"][cur_id]}
                         }])
            self.display_HU_scale_correction_result()
            self.visualize_HU_scale_remedied(list_data)
            # cv2.destroyAllWindows()

    def detect_HU_scale_consistency_violation(self, id):
        """
        To detect the HU Scale consistency violation
        :param id: int, Sequence ID
        """
        for sl_id in range(len(self.sequences[id]["data"])):    # Loop for Segmentation Results in Sequence
            # To get current Slice and its segmetnation result
            cur_sl_org = self.__get_current_sl(id, sl_id)
            cur_slseg = self.sequences[id]["data"][sl_id]["img"]
            list_sl_seg_masks = self.__identify_segmented_masks(cur_slseg)   # To identify segmented masks
            self.list_prv[self.sequences[id]["data"][sl_id]["id"]] = cur_slseg
            if self.sequences[id]["data"][sl_id]["id"] not in self.process_statistics["HU"]["remedy_states"].keys():     # To check the HU Scale
                self.process_statistics["HU"]["remedy_states"][
                    self.sequences[id]["data"][sl_id]["id"]] = "Not Violated"

            for cur_seged_mask in list_sl_seg_masks:     # Loop for segmented masks
                cur_hu_scale, frequency = self.__compute_HU_scale(cur_sl_org, cur_seged_mask)   # To compute HU scale
                violated_area = 0
                sect_area = np.count_nonzero(cur_seged_mask)
                for hu in frequency.keys():          # To compute violation Area
                    if hu < self.hu_min or hu > self.hu_max:
                        violated_area += frequency[hu]
                violated_rate = violated_area / sect_area

                if violated_rate > 0.0:
                    self.process_statistics["HU"]["num_detected_violation"] += 1
                if violated_rate == 0.0:  # Case 0. Not Violated. If all HU scales satisfy the range
                    if self.sequences[id]["data"][sl_id]["id"] not in self.process_statistics["HU"][
                        "remedy_states"].keys():
                        self.process_statistics["HU"]["remedy_states"][
                            self.sequences[id]["data"][sl_id]["id"]] = "Not Violated"
                        # print(">>. ", self.sequences[id]["data"][sl_id]["id"])
                    continue
                elif violated_rate > 0.3:  # Case 1
                    self.sequences[id]["data"][sl_id]["img"] = self.enhance_HU_scale_consistency_violation(id, sl_id, cur_seged_mask, 1)
                else:  # Cases 2 and 3
                    is_contour, violated_area = self.__check_HU_scale_violated_pixel_location(cur_sl_org, cur_seged_mask)
                    if is_contour:  # Case 2. If the violated pixels are located in the contour, Set False outer area
                        self.sequences[id]["data"][sl_id]["img"] = self.enhance_HU_scale_consistency_violation(id, sl_id, cur_seged_mask, 2, violated_area)
                    else:  # Case 3
                        self.sequences[id]["data"][sl_id]["img"] = self.enhance_HU_scale_consistency_violation(id, sl_id, cur_seged_mask, 3)

            # print(np.count_nonzero(self.sequences[id]["data"][sl_id]["img"]))
            self.process_statistics["HU"]["HU_scales_seg"][self.sequences[id]["data"][sl_id]["id"]] = \
            self.__compute_HU_scale(cur_sl_org, self.srs_seg_sl[self.sequences[id]["data"][sl_id]["id"]]["img"])[0]
            self.process_statistics["HU"]["HU_scales_remedy"][self.sequences[id]["data"][sl_id]["id"]] = \
            self.__compute_HU_scale(cur_sl_org, self.sequences[id]["data"][sl_id]["img"])[0]

    def enhance_HU_scale_consistency_violation(self, seq_id, sl_id, sl_seg_sec, violation_case, violated_area=None):
        """
        To revise HU Scale consistency Violation
        :param seq_id: int, Current Sequence ID
        :param sl_id: int, current Slice ID
        :param sl_seg_sec: int, current segmented mask ID
        :param violation_case: int, the case of violating the HU scale consistency
        :param violation_area:
        """
        result = np.zeros(sl_seg_sec.shape, np.uint8)
        state = "Remedied"
        if violation_case in [1, 3]:
             result = cv2.subtract(self.sequences[seq_id]["data"][sl_id]["img"], sl_seg_sec) # To discard the segmented mask in SLSeg
        elif violation_case == 2:
            if np.count_nonzero(np.bitwise_and(violated_area, self.sequences[seq_id]["data"][sl_id]["img"]))==0:
                state = "Not Violated"
            result = np.array(np.where(violated_area > 0, 0, self.sequences[seq_id]["data"][sl_id]["img"]), np.uint8)  # To discard the area of violating the HU Scale consistency

        if (self.sequences[seq_id]["data"][sl_id]["id"] not in list(self.process_statistics["HU"]["remedy_states"].keys())) or\
                (self.process_statistics["HU"]["remedy_states"][self.sequences[seq_id]["data"][sl_id]["id"]]=="Not Violated"):
            self.process_statistics["HU"]["num_remedied_SLs"] += 1
            self.process_statistics["HU"]["remedy_states"][self.sequences[seq_id]["data"][sl_id]["id"]] = state
        return result

    def __compute_HU_scale(self, sl_org, sl_seg_sec):
        """
        To compute HU Scale of the Segmented Masks
        :param sl_org: ndarray, Slice
        :param sl_seg_sec: ndarray, segmented mask
        :return: (list, dict), list for maximum and minimum HU scale values, dict for frequency of the HU Scale value
        """
        try:
            hu_values = np.where(sl_seg_sec > 0, sl_org, np.inf)        # To remain the HU Scale in Slice of the segmented mask area
            hu_values = hu_values[hu_values != np.inf]                  # To remain only valid HU scale values
            hu_scale, counts = np.unique(hu_values, return_counts=True)
            dict_frequencies = {}
            for i in range(len(hu_scale)):
                dict_frequencies[hu_scale[i]] = int(counts[i])
            return [np.min(hu_scale), np.max(hu_scale)], dict_frequencies
        except ValueError:
            return [np.inf, np.inf], {}


    ####################################################
    # Methods for Managing Images

    def visualize_sequence_generation(self, list_data):
        fig, ax = plt.subplots(1, 1)
        dsize = (665, 665)
        idx = 0
        do_visualize = True
        while do_visualize:
            imgs, data = list_data[idx][0], list_data[idx][1]
            sls_rvsd = []
            for k, v in imgs.items():
                if v is None:
                    v = np.zeros(dsize, np.uint8)
                v = cv2.cv2.resize(v, dsize=dsize, interpolation=cv2.INTER_AREA)
                v[0, :] = 255
                v[dsize[1]-1, :] = 255
                v[:, 0] = 255
                v[:, dsize[0]-1] = 255
                sls_rvsd.append(v)
            img_concat = np.hstack(sls_rvsd)
            height, width = img_concat.shape
            img = np.zeros((height+250, width), np.uint8)
            img[80:height+80, :] = img_concat
            img[height+80,:]= 255
            img[-1,:]= 255
            for i in range(len(list(imgs.keys()))):
                img[height+50:, i*dsize[0]] = 255
                img[height+50:, (i+1)*dsize[0]-1] = 255

            # Title
            cv2.putText(img, "Sequence Generation", (20, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "a: Previous Sequence, d:Next Sequence", (img.shape[1]-450, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.9, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "z: Previous Slice, x: Next Slice, c: Next Step", (img.shape[1]-510, 60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.9, 255, 1, cv2.LINE_AA)

            # Slice Title
            x_axis = {"Slice": 20, "Seg. Result": dsize[0]+20, "Remedied": dsize[0]*2+20}
            cv2.putText(img, "[Slice] ", (x_axis["Slice"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "[Segmentation Result] ", (x_axis["Seg. Result"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "[Remedied Result] ", (x_axis["Remedied"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)

            # Description
            str_hu_scale_seg = str(data["Seg. Result"]["HU Scale"][0])+" ~ "+str(data["Seg. Result"]["HU Scale"][1])+" (HU)"
            # Description for Slice
            cv2.putText(img, "Slice ID: "+data["Slice"]["fname"], (x_axis["Slice"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            # Description for Segmentation Result
            cv2.putText(img, "Sequence ID    : "+str(data["Seg. Result"]["sequence"]["id"])+" ("+data["Seg. Result"]["sequence"]["type"]+")",
                        (x_axis["Seg. Result"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ Size     : "+data["Seg. Result"]["size"]+" (Pixels)", (x_axis["Seg. Result"], dsize[0]+80+35+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ HU Scale: "+str_hu_scale_seg, (x_axis["Seg. Result"], dsize[0]+80+35+35*2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            # img = cv2.resize(img, dsize=(0,0), fx=1.5, fy=1.5)
            cv2.imwrite(r"E:\1. Lab\Daily Results\2022\2210\1001\test.png", img)
            cv2.imshow("Visualization", img)
            cv2.moveWindow("Visualization", 922, 20)
            key = cv2.waitKey()
            if key == ord('c'):
                do_visualize = False
            elif key == ord('z'):
                if idx>0:
                    idx-=1
            elif key == ord('x'):
                if idx<len(list_data)-1:
                    idx+=1
            elif key == ord("d"):
                is_appeared = np.count_nonzero(imgs["Seg. Result"])>0
                for j in range(idx+1, len(list_data)):
                    if is_appeared != (np.count_nonzero(list_data[j][0]["Seg. Result"])>0):
                        idx = j
                        break

            elif key == ord("a"):
                is_appeared = np.count_nonzero(imgs["Seg. Result"])>0
                for j in range(idx-1, -1, -1):
                    if is_appeared != (np.count_nonzero(list_data[j][0]["Seg. Result"])>0):
                        idx = j
                        break

    def save_segmentations(self, postfix=None):
        """
        To save sequence to the local
        :return:
        """
        path_save = self.path_save
        if postfix is not None:  # If the target sequence is the result of each method
            path_save = os.path.join(path_save, postfix)
            if not os.path.isdir(path_save):
                os.mkdir(path_save)

        # To load slice from sequences
        max_seq, max_id = 0, -1
        for id in range(len(self.sequences)):
            cur_seq = self.sequences[id]["data"]
            if self.sequences[id]["type"] and len(cur_seq) > max_seq:
                max_seq = len(cur_seq)
                max_id = id

        for id in range(len(self.sequences)):
            cur_seq = self.sequences[id]["data"]
            if id == max_id:
                for sl_id in range(len(cur_seq)):
                    img = cur_seq[sl_id]["img"]
                    cv2.imwrite(os.path.join(path_save, cur_seq[sl_id]["fname"]), img=img)
            else:
                for sl_id in range(len(cur_seq)):
                    img = cur_seq[sl_id]["img"]
                    cv2.imwrite(os.path.join(path_save, cur_seq[sl_id]["fname"]),
                                img=np.zeros(img.shape))

    def save_sequences(self, postfix=None):
        path_save = self.path_save
        if postfix is not None:  # If the target sequence is the result of each method
            path_save = os.path.join(path_save, postfix)
            if not os.path.isdir(path_save):
                os.mkdir(path_save)

        # To load slice from sequences
        for id in range(len(self.sequences)):
            if not os.path.isdir(os.path.join(path_save, str(id) + "-" + str(self.sequences[id]["type"])+
                                                         " ("+self.sequences[id]["data"][0]["fname"].split(".")[0]+"-"+self.sequences[id]["data"][-1]["fname"].split(".")[0]+")")):
                os.mkdir(os.path.join(path_save, str(id) + "-" + str(self.sequences[id]["type"])+
                                                         " ("+self.sequences[id]["data"][0]["fname"].split(".")[0]+"-"+self.sequences[id]["data"][-1]["fname"].split(".")[0]+")"))
            cur_seq = self.sequences[id]["data"]
            for sl_id in range(len(cur_seq)):
                img = cur_seq[sl_id]["img"]
                # cv2.imwrite(os.path.join(path_save, str(id) + "-" + str(self.sequences[id]["type"]),
                #                          str(cur_seq[sl_id]["id"]).zfill(5) + ".png"), img=img)
                cv2.imwrite(os.path.join(path_save, str(id) + "-" + str(self.sequences[id]["type"])+
                                                         " ("+self.sequences[id]["data"][0]["fname"].split(".")[0]+"-"+self.sequences[id]["data"][-1]["fname"].split(".")[0]+")",
                                         cur_seq[sl_id]["fname"]), img=img)

    def visualize_appearance_remedied(self, list_data):
        # dsize = (512, 512)
        dsize = (665, 665)
        idx = 0
        do_visualize = True
        while do_visualize:
            imgs, data = list_data[idx][0], list_data[idx][1]
            sls_rvsd = []
            for k, v in imgs.items():
                if v is None:
                    v = np.zeros(dsize, np.uint8)
                v = cv2.cv2.resize(v, dsize=dsize, interpolation=cv2.INTER_AREA)
                v[0, :] = 255
                v[dsize[1]-1, :] = 255
                v[:, 0] = 255
                v[:, dsize[0]-1] = 255
                sls_rvsd.append(v)
            img_concat = np.hstack(sls_rvsd)
            height, width = img_concat.shape
            img = np.zeros((height+250, width), np.uint8)
            img[80:height+80, :] = img_concat
            img[height+80,:]= 255
            img[-1,:]= 255
            for i in range(len(list(imgs.keys()))):
                img[height+50:, i*dsize[0]] = 255
                img[height+50:, (i+1)*dsize[0]-1] = 255

            # Title
            cv2.putText(img, "Remedy Result Visualization - Appearance Inconsistency", (20, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "a: Previous Sequence, d:Next Sequence", (img.shape[1]-450, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.9, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "z: Previous Slice, x: Next Slice, c: Next Step", (img.shape[1]-510, 60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.9, 255, 1, cv2.LINE_AA)

            # Slice Title
            x_axis = {"Slice": 20, "Seg. Result": dsize[0]+20, "Remedied": dsize[0]*2+20}
            cv2.putText(img, "[Slice] ", (x_axis["Slice"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "[Segmentation Result] ", (x_axis["Seg. Result"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "[Remedied Result] ", (x_axis["Remedied"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)

            # Description
            str_hu_scale_seg = str(data["Seg. Result"]["HU Scale"][0])+" ~ "+str(data["Seg. Result"]["HU Scale"][1])+" (HU)"
            str_hu_scale_rmd = str(data["Remedied"]["HU Scale"][0])+" ~ "+str(data["Remedied"]["HU Scale"][1])+" (HU)"
            # Description for Slice
            cv2.putText(img, "Slice ID: "+data["Slice"]["fname"], (x_axis["Slice"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            # Description for Segmentation Result
            cv2.putText(img, "Sequence ID    : "+str(data["Seg. Result"]["sequence"]["id"])+" ("+data["Seg. Result"]["sequence"]["type"]+")",
                        (x_axis["Seg. Result"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ Size     : "+data["Seg. Result"]["size"]+" (Pixels)", (x_axis["Seg. Result"], dsize[0]+80+35+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ HU Scale: "+str_hu_scale_seg, (x_axis["Seg. Result"], dsize[0]+80+35+35*2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            # Description for Remedied Result
            cv2.putText(img, "Remedy State  :".ljust(16)+data["Remedied"]["remedy_state"], (x_axis["Remedied"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ Size     :".ljust(17)+data["Remedied"]["size"]+" (Pixels)", (x_axis["Remedied"], dsize[0]+80+35+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ HU Scale:".ljust(16)+str_hu_scale_rmd, (x_axis["Remedied"], dsize[0]+80+35+35*2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)

            cv2.imshow("Visualization", img)
            cv2.moveWindow("Visualization", 922, 20)
            key = cv2.waitKey()
            if key == ord('c'):
                do_visualize = False
            elif key == ord('z'):
                if idx>0:
                    idx-=1
            elif key == ord('x'):
                if idx<len(list_data)-1:
                    idx+=1
            elif key == ord("d"):
                is_appeared = np.count_nonzero(imgs["Remedied"])>0
                for j in range(idx+1, len(list_data)):
                    if is_appeared != (np.count_nonzero(list_data[j][0]["Remedied"])>0):
                        idx = j
                        break
            elif key == ord("a"):
                is_appeared = np.count_nonzero(imgs["Remedied"])>0
                for j in range(idx-1, -1, -1):
                    if is_appeared != (np.count_nonzero(list_data[j][0]["Remedied"])>0):
                        idx = j
                        break

    def display_appearance_correction_result(self):
        for id in range(len(self.sequences)):  # Loop for sequences
            for sl_id in range(len(self.sequences[id]["data"])):  # To check empty slice
                cur_id = self.sequences[id]["data"][sl_id]["id"]
                self.process_statistics["appearance"]["size_seg"][cur_id] = np.count_nonzero(self.list_prv[cur_id])
                self.process_statistics["appearance"]["size_rmd"][cur_id] = np.count_nonzero(self.sequences[id]["data"][sl_id]["img"])

        ids = list(self.process_statistics["appearance"]["size_seg"].keys())
        list_size_segs = list(self.process_statistics["appearance"]["size_seg"].values())
        list_size_remedies = list(self.process_statistics["appearance"]["size_rmd"].values())

        plt.rc("font", size=10)
        fig, ax = plt.subplots(1, 1)
        width = 1995/ fig.dpi
        height = 915/fig.dpi
        fig.set_figwidth(width)
        fig.set_figheight(height)
        ax.plot(ids, list_size_segs, marker="s", color="r", label="Segmentation Result")
        ax.plot(ids, list_size_remedies, marker="*", color="g", label="Remedied Result")

        ax.set_xlabel("Slice ID")
        ax.set_ylabel("Segmented Organ Area (Pixels)")
        ax.legend(loc=2)
        fig.canvas.draw()
        img = np.array(fig.canvas.get_renderer()._renderer, np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        cv2.imshow("Correction Result", img)
        cv2.moveWindow("Correction Result", 922, 1000)

    def visualize_location_remedied(self, list_data):
        # dsize = (512, 512)
        dsize = (665, 665)
        idx = 0
        do_visualize = True
        while do_visualize:
            imgs, data = list_data[idx][0], list_data[idx][1]
            sls_rvsd = []
            for k, v in imgs.items():
                if v is None:
                    v = np.zeros(dsize, np.uint8)
                v = cv2.cv2.resize(v, dsize=dsize, interpolation=cv2.INTER_AREA)
                v[0, :] = 255
                v[dsize[1]-1, :] = 255
                v[:, 0] = 255
                v[:, dsize[0]-1] = 255
                sls_rvsd.append(v)
            img_concat = np.hstack(sls_rvsd)
            height, width = img_concat.shape
            img = np.zeros((height+250, width), np.uint8)
            img[80:height+80, :] = img_concat
            img[height+80,:]= 255
            img[-1,:]= 255
            for i in range(len(list(imgs.keys()))):
                img[height+50:, i*dsize[0]] = 255
                img[height+50:, (i+1)*dsize[0]-1] = 255

            # Title
            cv2.putText(img, "Remedy Result Visualization - Location Inconsistency", (20, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "a: Previous Sequence, d:Next Sequence", (img.shape[1]-450, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.9, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "z: Previous Slice, x: Next Slice, c: Next Step", (img.shape[1]-510, 60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.9, 255, 1, cv2.LINE_AA)

            # Slice Title
            x_axis = {"Slice": 20, "Seg. Result": dsize[0]+20, "Remedied": dsize[0]*2+20}
            cv2.putText(img, "[Slice] ", (x_axis["Slice"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "[Segmentation Result] ", (x_axis["Seg. Result"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "[Remedied Result] ", (x_axis["Remedied"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)

            # Description
            str_hu_scale_seg = str(data["Seg. Result"]["HU Scale"][0])+" ~ "+str(data["Seg. Result"]["HU Scale"][1])+" (HU)"
            str_hu_scale_rmd = str(data["Remedied"]["HU Scale"][0])+" ~ "+str(data["Remedied"]["HU Scale"][1])+" (HU)"
            # Description for Slice
            cv2.putText(img, "Slice ID: "+data["Slice"]["fname"], (x_axis["Slice"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            # Description for Segmentation Result
            cv2.putText(img, "Sequence ID    : "+str(data["Seg. Result"]["sequence"]["id"])+" ("+data["Seg. Result"]["sequence"]["type"]+")",
                        (x_axis["Seg. Result"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ Size     : "+data["Seg. Result"]["size"]+" (Pixels)", (x_axis["Seg. Result"], dsize[0]+80+35+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ HU Scale: "+str_hu_scale_seg, (x_axis["Seg. Result"], dsize[0]+80+35+35*2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            # Description for Remedied Result
            cv2.putText(img, "Remedy State  :".ljust(16)+data["Remedied"]["remedy_state"], (x_axis["Remedied"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ Size     :".ljust(17)+data["Remedied"]["size"]+" (Pixels)", (x_axis["Remedied"], dsize[0]+80+35+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ HU Scale:".ljust(16)+str_hu_scale_rmd, (x_axis["Remedied"], dsize[0]+80+35+35*2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)

            cv2.imshow("Visualization", img)
            cv2.moveWindow("Visualization", 922, 20)
            key = cv2.waitKey()
            if key == ord('c'):
                do_visualize = False
            elif key == ord('z'):
                if idx>0:
                    idx-=1
            elif key == ord('x'):
                if idx<len(list_data)-1:
                    idx+=1
            elif key == ord("d"):
                is_appeared = np.count_nonzero(imgs["Remedied"])>0
                for j in range(idx+1, len(list_data)):
                    if is_appeared != (np.count_nonzero(list_data[j][0]["Remedied"])>0):
                        idx = j
                        break

            elif key == ord("a"):
                is_appeared = np.count_nonzero(imgs["Remedied"])>0
                for j in range(idx-1, -1, -1):
                    if is_appeared != (np.count_nonzero(list_data[j][0]["Remedied"])>0):
                        idx = j
                        break

    def display_location_correction_result(self):
        idx = -1
        prv_cn_seg = None
        prv_cn_rmd = None
        prv_rst_seg = None
        prv_rst_rmd = None
        for id in range(len(self.sequences)):  # Loop for sequences
            for sl_id in range(len(self.sequences[id]["data"])):  # To check empty slice
                cur_id = self.sequences[id]["data"][sl_id]["id"]
                idx += 1
                if prv_rst_seg is None and prv_rst_rmd is None:
                    prv_rst_seg = self.list_prv[cur_id]
                    prv_rst_rmd = self.sequences[id]['data'][sl_id]["img"]
                    continue
                rate_seg = self.__compute_inclusion_rate(prv_rst_seg, self.list_prv[cur_id])
                rate_rmd = self.__compute_inclusion_rate(prv_rst_seg, self.sequences[id]['data'][sl_id]["img"])
                self.process_statistics["location"]["location_diff_seg"][idx] = rate_seg
                self.process_statistics["location"]["location_diff_rmd"][idx] = rate_rmd
                prv_rst_seg = self.list_prv[cur_id]
                prv_rst_rmd = self.sequences[id]['data'][sl_id]["img"]
                # if prv_cn_seg == None:
                #     prv_cn_seg, _ = self.__find_center_and_bounding_box(self.list_prv[cur_id])
                #     prv_cn_rmd, _ = self.__find_center_and_bounding_box(self.sequences[id]["data"][sl_id]["img"])
                #     continue
                # cn_seg, _ = self.__find_center_and_bounding_box(self.list_prv[cur_id]["img"])
                # cn_rmd, _ = self.__find_center_and_bounding_box(self.sequences[id]["data"][sl_id]["img"])
                # diff_seg = np.sqrt((cn_seg[1]-prv_cn_seg[1])**2+(cn_seg[0]-prv_cn_seg[0])**2)
                # if prv_cn_seg == (0,0): diff_seg = 0
                # diff_rmd = np.sqrt((cn_rmd[1]-prv_cn_rmd[1])**2+(cn_rmd[0]-prv_cn_rmd[0])**2)
                # if prv_cn_rmd == (0,0): diff_rmd = 0
                # self.process_statistics["location"]["location_diff_seg"][idx] = diff_seg
                # self.process_statistics["location"]["location_diff_rmd"][idx] = diff_rmd
                # prv_cn_seg = cn_seg
                # prv_cn_rmd = cn_rmd

        ids = list(self.process_statistics["location"]["location_diff_seg"].keys())
        list_loc_diff_segs = list(self.process_statistics["location"]["location_diff_seg"].values())
        list_loc_diff_remedys = list(self.process_statistics["location"]["location_diff_rmd"].values())

        plt.rc("font", size=10)
        fig, ax = plt.subplots(1, 1)
        width = 1995/ fig.dpi
        height = 915/fig.dpi
        fig.set_figwidth(width)
        fig.set_figheight(height)
        plt.plot(ids, list_loc_diff_segs, marker="s", color="r", label="Segmentation Result")
        plt.plot(ids, list_loc_diff_remedys, marker="*", color="g", label="Remedied Result")

        ax.set_xlabel("Slice ID")
        # ax.set_ylabel("Difference of Location Between Adjacent Slice (Pixels)")
        ax.set_ylabel("Location Similarity Rate Between Adjacent Slices (%)")
        ax.legend(loc=2)
        # fig.tight_layout()
        fig.canvas.draw()
        img = np.array(fig.canvas.get_renderer()._renderer, np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        cv2.imshow("Correction Result", img)
        cv2.moveWindow("Correction Result", 922, 1000)

    def display_post_enhancement_results(self):
        """
        To display the post-enhancement result
        :return:
        """
        category = list(self.process_statistics.keys())[2:]
        num_remedied = [self.process_statistics[x]["num_remedied_SLs"] for x in category]
        category.append("Whole Methods")
        num_whole = 0
        for id in range(len(self.sequences)):  # Loop for sequences
            for sl_id in range(len(self.sequences[id]["data"])):  # To check empty slice
                if np.count_nonzero(np.subtract(self.srs_seg_sl[self.sequences[id]["data"][sl_id]["id"]]["img"], self.sequences[id]["data"][sl_id]["img"]))>0:
                    num_whole += 1
        num_remedied.append(num_whole)

        plt.rc("font", size=10)
        fig, ax = plt.subplots(1, 1, figsize=(10, 7))

        xtick_label_position = list(range(len(category)))
        plt.xticks(xtick_label_position, category)

        rects = ax.bar(xtick_label_position, num_remedied, color="green")
        for i in range(len(rects)):
            rect = rects[i]
            height = rect.get_height()
            ax.annotate("{}".format(height), xy=(rect.get_x()+rect.get_width()/2, num_remedied[i]), xytext=(0, 3),
                        textcoords="offset points", ha="center", va="bottom",)

        cv2.destroyAllWindows()
        ax.set_xlabel("Applied Methods")
        ax.set_ylabel("# of Remedied Slices")
        ax.set_title("# of Remedied Slices from Methods")
        fig.canvas.draw()
        img = np.array(fig.canvas.get_renderer()._renderer, np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        cv2.imshow("Post-Enhancement Result", img)
        cv2.moveWindow("Post-Enhancement Result", 922, 300)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def visualize_size_remedied(self, list_data):
        # dsize = (512, 512)
        dsize = (665, 665)
        idx = 0
        do_visualize = True
        while do_visualize:
            imgs, data = list_data[idx][0], list_data[idx][1]
            sls_rvsd = []
            for k, v in imgs.items():
                if v is None:
                    v = np.zeros(dsize, np.uint8)
                v = cv2.cv2.resize(v, dsize=dsize, interpolation=cv2.INTER_AREA)
                v[0, :] = 255
                v[dsize[1]-1, :] = 255
                v[:, 0] = 255
                v[:, dsize[0]-1] = 255
                sls_rvsd.append(v)
            img_concat = np.hstack(sls_rvsd)
            height, width = img_concat.shape
            img = np.zeros((height+250, width), np.uint8)
            img[80:height+80, :] = img_concat
            img[height+80,:]= 255
            img[-1,:]= 255
            for i in range(len(list(imgs.keys()))):
                img[height+50:, i*dsize[0]] = 255
                img[height+50:, (i+1)*dsize[0]-1] = 255

            # Title
            cv2.putText(img, "Remedy Result Visualization - Size Inconsistency", (20, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "a: Previous Sequence, d:Next Sequence", (img.shape[1]-450, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.9, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "z: Previous Slice, x: Next Slice, c: Next Step", (img.shape[1]-510, 60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.9, 255, 1, cv2.LINE_AA)

            # Slice Title
            x_axis = {"Slice": 20, "Seg. Result": dsize[0]+20, "Remedied": dsize[0]*2+20}
            cv2.putText(img, "[Slice] ", (x_axis["Slice"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "[Segmentation Result] ", (x_axis["Seg. Result"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "[Remedied Result] ", (x_axis["Remedied"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)

            # Description
            str_hu_scale_seg = str(data["Seg. Result"]["HU Scale"][0])+" ~ "+str(data["Seg. Result"]["HU Scale"][1])+" (HU)"
            str_hu_scale_rmd = str(data["Remedied"]["HU Scale"][0])+" ~ "+str(data["Remedied"]["HU Scale"][1])+" (HU)"
            # Description for Slice
            cv2.putText(img, "Slice ID: "+data["Slice"]["fname"], (x_axis["Slice"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            # Description for Segmentation Result
            cv2.putText(img, "Sequence ID    : "+str(data["Seg. Result"]["sequence"]["id"])+" ("+data["Seg. Result"]["sequence"]["type"]+")",
                        (x_axis["Seg. Result"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ Size     : "+data["Seg. Result"]["size"]+" (Pixels)", (x_axis["Seg. Result"], dsize[0]+80+35+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ HU Scale: "+str_hu_scale_seg, (x_axis["Seg. Result"], dsize[0]+80+35+35*2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            # Description for Remedied Result
            cv2.putText(img, "Remedy State  :".ljust(16)+data["Remedied"]["remedy_state"], (x_axis["Remedied"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ Size     :".ljust(17)+data["Remedied"]["size"]+" (Pixels)", (x_axis["Remedied"], dsize[0]+80+35+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ HU Scale:".ljust(16)+str_hu_scale_rmd, (x_axis["Remedied"], dsize[0]+80+35+35*2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)

            cv2.imshow("Visualization", img)
            cv2.moveWindow("Visualization", 922, 20)
            key = cv2.waitKey()
            if key == ord('c'):
                do_visualize = False
            elif key == ord('z'):
                if idx>0:
                    idx-=1
            elif key == ord('x'):
                if idx<len(list_data)-1:
                    idx+=1
            elif key == ord("d"):
                is_appeared = np.count_nonzero(imgs["Remedied"])>0
                for j in range(idx+1, len(list_data)):
                    if is_appeared != (np.count_nonzero(list_data[j][0]["Remedied"])>0):
                        idx = j
                        break

            elif key == ord("a"):
                is_appeared = np.count_nonzero(imgs["Remedied"])>0
                for j in range(idx-1, -1, -1):
                    if is_appeared != (np.count_nonzero(list_data[j][0]["Remedied"])>0):
                        idx = j
                        break

    def display_size_correction_result(self):
        for id in range(len(self.sequences)):  # Loop for sequences
            for sl_id in range(len(self.sequences[id]["data"])):  # To check empty slice
                cur_id = self.sequences[id]["data"][sl_id]["id"]
                self.process_statistics["size"]["size_seg"][cur_id] = np.count_nonzero(self.list_prv[cur_id])
                self.process_statistics["size"]["size_rmd"][cur_id] = np.count_nonzero(self.sequences[id]["data"][sl_id]["img"])

        ids = list(self.process_statistics["size"]["size_seg"].keys())
        list_size_segs = list(self.process_statistics["size"]["size_seg"].values())
        list_size_remedys = list(self.process_statistics["size"]["size_rmd"].values())

        plt.rc("font", size=10)
        fig, ax = plt.subplots(1, 1)
        width = 1995/ fig.dpi
        height = 915/fig.dpi
        fig.set_figwidth(width)
        fig.set_figheight(height)
        plt.plot(ids, list_size_segs, marker="s", color="r", label="Segmentation Result")
        plt.plot(ids, list_size_remedys, marker="*", color="g", label="Remedied Result")

        ax.set_xlabel("Slice ID")
        ax.set_ylabel("Segmented Organ Area (Pixels)")
        ax.legend(loc=2)
        fig.canvas.draw()
        img = np.array(fig.canvas.get_renderer()._renderer, np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        cv2.imshow("Correction Result", img)
        cv2.moveWindow("Correction Result", 922, 1000)

    def visualize_shape_remedied(self, list_data):
        # dsize = (512, 512)
        dsize = (665, 665)
        idx = 0
        do_visualize = True
        while do_visualize:
            imgs, data = list_data[idx][0], list_data[idx][1]
            sls_rvsd = []
            for k, v in imgs.items():
                if v is None:
                    v = np.zeros(dsize, np.uint8)
                v = cv2.cv2.resize(v, dsize=dsize, interpolation=cv2.INTER_AREA)
                v[0, :] = 255
                v[dsize[1]-1, :] = 255
                v[:, 0] = 255
                v[:, dsize[0]-1] = 255
                sls_rvsd.append(v)
            img_concat = np.hstack(sls_rvsd)
            height, width = img_concat.shape
            img = np.zeros((height+250, width), np.uint8)
            img[80:height+80, :] = img_concat
            img[height+80,:]= 255
            img[-1,:]= 255
            for i in range(len(list(imgs.keys()))):
                img[height+50:, i*dsize[0]] = 255
                img[height+50:, (i+1)*dsize[0]-1] = 255

            # Title
            cv2.putText(img, "Remedy Result Visualization - Shape Inconsistency", (20, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "a: Previous Sequence, d:Next Sequence", (img.shape[1]-450, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.9, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "z: Previous Slice, x: Next Slice, c: Next Step", (img.shape[1]-510, 60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.9, 255, 1, cv2.LINE_AA)

            # Slice Title
            x_axis = {"Slice": 20, "Seg. Result": dsize[0]+20, "Remedied": dsize[0]*2+20}
            cv2.putText(img, "[Slice] ", (x_axis["Slice"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "[Segmentation Result] ", (x_axis["Seg. Result"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "[Remedied Result] ", (x_axis["Remedied"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)

            # Description
            str_hu_scale_seg = str(data["Seg. Result"]["HU Scale"][0])+" ~ "+str(data["Seg. Result"]["HU Scale"][1])+" (HU)"
            str_hu_scale_rmd = str(data["Remedied"]["HU Scale"][0])+" ~ "+str(data["Remedied"]["HU Scale"][1])+" (HU)"
            # Description for Slice
            cv2.putText(img, "Slice ID: "+data["Slice"]["fname"], (x_axis["Slice"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            # Description for Segmentation Result
            cv2.putText(img, "Sequence ID    : "+str(data["Seg. Result"]["sequence"]["id"])+" ("+data["Seg. Result"]["sequence"]["type"]+")",
                        (x_axis["Seg. Result"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ Size     : "+data["Seg. Result"]["size"]+" (Pixels)", (x_axis["Seg. Result"], dsize[0]+80+35+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ HU Scale: "+str_hu_scale_seg, (x_axis["Seg. Result"], dsize[0]+80+35+35*2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            # Description for Remedied Result
            cv2.putText(img, "Remedy State  :".ljust(16)+data["Remedied"]["remedy_state"], (x_axis["Remedied"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ Size     :".ljust(17)+data["Remedied"]["size"]+" (Pixels)", (x_axis["Remedied"], dsize[0]+80+35+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ HU Scale:".ljust(16)+str_hu_scale_rmd, (x_axis["Remedied"], dsize[0]+80+35+35*2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)

            cv2.imshow("Visualization", img)
            cv2.moveWindow("Visualization", 922, 20)
            key = cv2.waitKey()
            if key == ord('c'):
                do_visualize = False
            elif key == ord('z'):
                if idx>0:
                    idx-=1
            elif key == ord('x'):
                if idx<len(list_data)-1:
                    idx+=1
            elif key == ord("d"):
                is_appeared = np.count_nonzero(imgs["Remedied"])>0
                for j in range(idx+1, len(list_data)):
                    if is_appeared != (np.count_nonzero(list_data[j][0]["Remedied"])>0):
                        idx = j
                        break

            elif key == ord("a"):
                is_appeared = np.count_nonzero(imgs["Remedied"])>0
                for j in range(idx-1, -1, -1):
                    if is_appeared != (np.count_nonzero(list_data[j][0]["Remedied"])>0):
                        idx = j
                        break

    def display_shape_correction_result(self):
        ids = list(self.process_statistics["shape"]["shape_diff_seg"].keys())
        list_loc_diff_segs = list(self.process_statistics["shape"]["shape_diff_seg"].values())
        list_loc_diff_remedys = list(self.process_statistics["shape"]["shape_diff_rmd"].values())

        plt.rc("font", size=10)
        fig, ax = plt.subplots(1, 1)
        width = 1995/ fig.dpi
        height = 915/fig.dpi
        fig.set_figwidth(width)
        fig.set_figheight(height)
        plt.plot(ids, list_loc_diff_segs, marker="s", color="r", label="Segmentation Result")
        plt.plot(ids, list_loc_diff_remedys, marker="*", color="g", label="Remedied Result")

        ax.set_xlabel("Slice ID")
        ax.set_ylabel("Shape Difference Rate")
        ax.set_ylim([0, 0.3])
        ax.legend(loc=2)
        fig.canvas.draw()
        img = np.array(fig.canvas.get_renderer()._renderer, np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        cv2.imshow("Correction Result", img)
        cv2.moveWindow("Correction Result", 922, 1000)

    def visualize_HU_scale_remedied(self, list_data):
        # dsize = (512, 512)
        dsize = (665, 665)
        idx = 0
        do_visualize = True
        while do_visualize:
            imgs, data = list_data[idx][0], list_data[idx][1]
            sls_rvsd = []
            for k, v in imgs.items():
                if v is None:
                    v = np.zeros(dsize, np.uint8)
                v = cv2.cv2.resize(v, dsize=dsize, interpolation=cv2.INTER_AREA)
                v[0, :] = 255
                v[dsize[1]-1, :] = 255
                v[:, 0] = 255
                v[:, dsize[0]-1] = 255
                sls_rvsd.append(v)
            img_concat = np.hstack(sls_rvsd)
            height, width = img_concat.shape
            img = np.zeros((height+250, width), np.uint8)
            img[80:height+80, :] = img_concat
            img[height+80,:]= 255
            img[-1,:]= 255
            for i in range(len(list(imgs.keys()))):
                img[height+50:, i*dsize[0]] = 255
                img[height+50:, (i+1)*dsize[0]-1] = 255

            # Title
            cv2.putText(img, "Remedy Result Visualization - HU Scale Inconsistency", (20, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "a: Previous Sequence, d:Next Sequence", (img.shape[1]-450, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.9, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "z: Previous Slice, x: Next Slice, c: Next Step", (img.shape[1]-510, 60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.9, 255, 1, cv2.LINE_AA)

            # Slice Title
            x_axis = {"Slice": 20, "Seg. Result": dsize[0]+20, "Remedied": dsize[0]*2+20}
            cv2.putText(img, "[Slice] ", (x_axis["Slice"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "[Segmentation Result] ", (x_axis["Seg. Result"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)
            cv2.putText(img, "[Remedied Result] ", (x_axis["Remedied"], 80+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.7, 255, 2, cv2.LINE_AA)

            # Description
            str_hu_scale_seg = str(data["Seg. Result"]["HU Scale"][0])+" ~ "+str(data["Seg. Result"]["HU Scale"][1])+" (HU)"
            str_hu_scale_rmd = str(data["Remedied"]["HU Scale"][0])+" ~ "+str(data["Remedied"]["HU Scale"][1])+" (HU)"
            # Description for Slice
            cv2.putText(img, "Slice ID: "+data["Slice"]["fname"], (x_axis["Slice"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            # Description for Segmentation Result
            cv2.putText(img, "Sequence ID    : "+str(data["Seg. Result"]["sequence"]["id"])+" ("+data["Seg. Result"]["sequence"]["type"]+")",
                        (x_axis["Seg. Result"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ Size     : "+data["Seg. Result"]["size"]+" (Pixels)", (x_axis["Seg. Result"], dsize[0]+80+35+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ HU Scale: "+str_hu_scale_seg, (x_axis["Seg. Result"], dsize[0]+80+35+35*2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            # Description for Remedied Result
            cv2.putText(img, "Remedy State  :".ljust(16)+data["Remedied"]["remedy_state"], (x_axis["Remedied"], dsize[0]+80+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ Size     :".ljust(17)+data["Remedied"]["size"]+" (Pixels)", (x_axis["Remedied"], dsize[0]+80+35+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)
            cv2.putText(img, "Organ HU Scale:".ljust(16)+str_hu_scale_rmd, (x_axis["Remedied"], dsize[0]+80+35+35*2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.3, 255, 1, cv2.LINE_AA)

            cv2.imshow("Visualization", img)
            cv2.moveWindow("Visualization", 922, 20)
            key = cv2.waitKey()
            if key == ord('c'):
                do_visualize = False
            elif key == ord('z'):
                if idx>0:
                    idx-=1
            elif key == ord('x'):
                if idx<len(list_data)-1:
                    idx+=1
            elif key == ord("d"):
                is_appeared = np.count_nonzero(imgs["Remedied"])>0
                for j in range(idx+1, len(list_data)):
                    if is_appeared != (np.count_nonzero(list_data[j][0]["Remedied"])>0):
                        idx = j
                        break
            elif key == ord("a"):
                is_appeared = np.count_nonzero(imgs["Remedied"])>0
                for j in range(idx-1, -1, -1):
                    if is_appeared != (np.count_nonzero(list_data[j][0]["Remedied"])>0):
                        idx = j
                        break

    def display_HU_scale_correction_result(self):
        ids = list(self.process_statistics["HU"]["HU_scales_seg"].keys())
        list_hu_max_segs = []
        list_hu_min_segs = []
        list_hu_max_rmds = []
        list_hu_min_rmds = []
        for i in list(self.process_statistics["HU"]["HU_scales_seg"].values()):
            if i[0] is np.inf:
                i[0] = -1025
            if i[1] is np.inf:
                i[1] = -1025
            list_hu_max_segs.append(i[1])
            list_hu_min_segs.append(i[0])
        for i in list(self.process_statistics["HU"]["HU_scales_remedy"].values()):
            if i[0] is np.inf:
                i[0] = -1025
            if i[1] is np.inf:
                i[1] = -1025
            list_hu_max_rmds.append(i[1])
            list_hu_min_rmds.append(i[0])
        plt.rc("font", size=10)
        fig, ax = plt.subplots(1, 1)
        width = 1995/ fig.dpi
        height = 915/fig.dpi
        fig.set_figwidth(width)
        fig.set_figheight(height)
        plt.plot(ids, list_hu_max_segs, "rs-", label="Maximum HU Scale (Seg. Result)")
        plt.plot(ids, list_hu_max_rmds, "g*-", label="Maximum HU Scale (Remedied)")
        plt.plot(ids, list_hu_min_segs, "rs:", label="Minimum HU Scale (Seg. Result)")
        plt.plot(ids, list_hu_min_rmds, "g*:", label="Minimum HU Scale (Remedied)")

        ax.set_xlabel("Slice ID")
        ax.set_ylabel("HU Scale")
        ax.set_ylim([-1100, 4000])
        ax.legend(loc=2)
        fig.canvas.draw()
        img = np.array(fig.canvas.get_renderer()._renderer, np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        cv2.imshow("Correction Result", img)
        cv2.moveWindow("Correction Result", 922, 1000)

    def set_current_mi_imgs(self, p):
        root_path = r".\miaas\imgs"
        self.path_org = os.path.join(root_path)

    def get_sequences(self):
        return self.sequences

    def set_img_path(self, type, cur_path):
        if type == "srs":
            self.path_org_mi = cur_path
            self.path_org_sl = cur_path.replace("srs", "srs_png")
            os.mkdir(self.path_org_sl)
        elif type == "seg_result":
            self.path_seg_result = cur_path
        elif type == "label":
            self.path_label = cur_path
        self.srs_org_mi = []
        self.srs_org_sl = []
        self.srs_seg_sl = []

    def get_summary(self):
        return self.process_statistics

    ####################################################

    # Private Methods
    def __convert_color_depth(self, sl):
        img = 1 * sl + 0
        ymin = 0
        ymax = 255
        idx_high = img >= self.wc + self.ww / 2
        idx_low = img <= self.wc - self.ww / 2
        img = np.where(idx_high, ymax, img)
        img = np.where(idx_low, ymin, img)
        img = np.where(~idx_high & ~idx_low, ((img - self.wc) / self.ww + 0.5) * (ymax - ymin) + ymin, img)
        img = np.reshape(img, (512, 512, 1))
        return img
    def __check_seq_HU_violation(self, seq):
        do_violate = False
        count = 0
        for cur_slseg in seq:
            sl = self.srs_org_mi[:, :, cur_slseg["id"]]
            sl_seg = cur_slseg["img"]
            _, frq = self.__compute_HU_scale(sl, sl_seg)
            violated_area= 0
            for hu in frq.keys():
                if hu < self.hu_min or hu > self.hu_max:
                    violated_area += frq[hu]
            if np.count_nonzero(sl_seg) > 0 and violated_area / np.count_nonzero(sl_seg) > 0.3:
                count += 1
        # print("<<", count / len(seq), len(seq), count / len(seq)>0.5)
        if count / len(seq) > 0.6:
            do_violate = True
        return do_violate

    def __find_cur_sl_id_for_size_violation(self, list_groups, i, j):
        sl_id = 0
        for k in range(i):
            sl_id += len(list_groups[k])
        sl_id += j
        return sl_id

    def __compute_HU_scale_organ(self):
        hu_min = self.wc - self.ww / 2
        hu_max = self.wc + self.ww / 2
        if hu_min < 0:
            hu_min = hu_min * (1 + self.th_hu_scale)
        else:
            hu_min = hu_min * (1 - self.th_hu_scale)
        if hu_max < 0:
            hu_max = hu_max * (1 - self.th_hu_scale)
        else:
            hu_max = hu_max * (1 + self.th_hu_scale)
        return hu_max, hu_min

    def __check_inclusion_between_sec_and_cn(self, sec, cn):
        return sec[cn[1], cn[0]] > 0

    def __compute_inclusion_rate(self, seg_prv, seg_cur):
        if np.count_nonzero(seg_prv) == 0 or np.count_nonzero(seg_cur) == 0:
            inclusion_rate = 0.0
        else:
            inclusion_rate = round(np.count_nonzero(np.bitwise_and(seg_prv, seg_cur))/np.min([np.count_nonzero(seg_prv),np.count_nonzero(seg_cur)])*100, 2)
        return inclusion_rate

    def __check_bbox_inclusion(self, bbox_cur, bbox_nxt):
        if bbox_cur[2] < bbox_nxt[0] or bbox_nxt[2] < bbox_cur[0] or bbox_cur[1] > bbox_nxt[3] or bbox_cur[3] < \
                bbox_nxt[1]:
            return False
        x_left = max(bbox_cur[0], bbox_nxt[0])
        y_top = max(bbox_cur[1], bbox_nxt[1])
        x_right = min(bbox_cur[2], bbox_nxt[2])
        y_bottom = min(bbox_cur[3], bbox_nxt[3])
        if x_right < x_left or y_bottom < y_top:
            return False
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        cur_area = (bbox_cur[2] - bbox_cur[0]) * (bbox_cur[3] - bbox_cur[1])
        nxt_area = (bbox_nxt[2] - bbox_nxt[0]) * (bbox_nxt[3] - bbox_nxt[1])
        inclusion_rate = intersection_area / float(np.min([cur_area, nxt_area]))
        # print("INCLUSION RATE: ", inclusion_rate)
        if inclusion_rate > self.th_bbox_inclusion:
            return True
        else:
            return False

    def __find_center_and_bounding_box(self, msk):
        # To find center coordinate
        try:
            m = cv2.moments(msk)
            cx = int(m["m10"] / m["m00"])
            cy = int(m["m01"] / m["m00"])
            # To find coordinates of bounding box
            x, y, w, h = cv2.boundingRect(msk)
            return (cx, cy), (x, y, x + w, y + h)
        except:
            return (0, 0), (0, 0, 0, 0)

    def __check_HU_scale_violated_pixel_location(self, sl_org, sl_seg_sec):
        hu_values = np.where(sl_seg_sec > 0, sl_org, np.inf)
        mask = np.array(np.where((self.hu_max < hu_values) & (hu_values < np.inf) | (hu_values < self.hu_min), 255, 0), np.uint8)
        sl_seg_sec_dist = cv2.distanceTransform(sl_seg_sec, cv2.DIST_L2, 3)
        sl_seg_sec_dist = cv2.normalize(sl_seg_sec_dist, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8UC1)
        max_dist = np.max(sl_seg_sec_dist)
        dists = np.where(mask > 0, sl_seg_sec_dist, 0)
        dists = dists[dists != 0]
        if all(dists) < max_dist * 0.1:
            is_located_at_contour = True
        else:
            is_located_at_contour = True
        return is_located_at_contour, mask

    def __move_empty_to_false_seq(self):
        """
        To move segmentation results not containing anything located in true sequence to false sequence
        :return:
        """
        # Case of Empty slice in the middle
        for i in reversed(range(len(self.sequences))):
            if self.sequences[i]["data"] is None:
                del self.sequences[i]
        for id in range(len(self.sequences)):
            for sl_id in range(len(self.sequences[id]["data"])):
                if np.count_nonzero(self.sequences[id]["data"][sl_id]["img"])< 10:
                    self.sequences[id]["data"][sl_id]["img"] = np.zeros(self.sequences[id]["data"][sl_id]["img"].shape, np.uint8)

        count_appeared_seq = True
        idx_longest = -1
        length_seq = 0
        for i in range(len(self.sequences)):
            if self.sequences[i]["type"]:
                count_appeared_seq += 1
                if length_seq < len(self.sequences[i]["data"]):
                    idx_longest = i
                    length_seq = len(self.sequences[i]["data"])
        for i in range(len(self.sequences)):
            if self.sequences[i]["type"] and i != idx_longest:
                for sl_id in range(len(self.sequences[i]["data"])):
                    self.sequences[i]["data"][sl_id]["img"] = np.zeros((512, 512), dtype=np.uint8)

        refined_sequence = []
        for seq_id in range(len(self.sequences)):
            if len(refined_sequence) == 0:
                refined_sequence.append(self.sequences[seq_id])
            else:
                if not self.sequences[seq_id]["type"]:  # If current sequence is false
                    if not refined_sequence[-1]["type"]:
                        refined_sequence[-1]["data"].extend(self.sequences[seq_id]["data"])
                    else:
                        refined_sequence.append(self.sequences[seq_id])
                else:  # If current sequence is true
                    for sl_id in range(len(self.sequences[seq_id]["data"])):  # To check empty slice
                        if np.count_nonzero(self.sequences[seq_id]["data"][sl_id]["img"]) > 0:  # If not empty
                            if not refined_sequence[-1]["type"]:  # If the last seq is for false sequence
                                refined_sequence.append({"type": True, "data": []})
                            refined_sequence[-1]["data"].append(self.sequences[seq_id]["data"][sl_id])
                        else:  # If empty
                            if refined_sequence[-1]["type"]:  # If the last seq is for true sequence
                                refined_sequence.append({"type": False, "data": []})
                            refined_sequence[-1]["data"].append(self.sequences[seq_id]["data"][sl_id])

        self.sequences = copy.deepcopy(refined_sequence)
        # Case of Empty slice in the first and last
        seq_size = len(self.sequences)
        need_to_add_first = False
        data = []
        removed_seq_id = []
        for seq_id in range(seq_size):
            cur_seq = self.sequences[seq_id]
            if cur_seq["type"]:  # If the sequence contain segmentation results
                while True:
                    # To check the length of current sequence
                    if len(self.sequences[seq_id]["data"]) == 0:
                        removed_seq_id.append(seq_id)
                        break
                    if np.count_nonzero(cur_seq["data"][0]["img"]) == 0:
                        # To move to previous false sequence
                        if seq_id == 0:
                            # To generate new sequence
                            need_to_add_first = True
                            data.append(self.sequences[seq_id]["data"][0])
                        else:
                            self.sequences[seq_id - 1]["data"].append(self.sequences[seq_id]["data"][0])
                        del self.sequences[seq_id]["data"][0]
                    else:
                        break
                while True:
                    if len(self.sequences[seq_id]["data"]) == 0:
                        removed_seq_id.append(seq_id)
                        break
                    if np.count_nonzero(cur_seq["data"][-1]["img"]) == 0:
                        # To check the length of current sequence
                        if seq_id + 1 == seq_size:
                            # To generate new sequence
                            if len(self.sequences) == seq_size:
                                self.sequences.append({"type": False, "data": []})
                            self.sequences[seq_id + 1]["data"].append(self.sequences[seq_id]["data"][-1])
                        else:
                            self.sequences[seq_id + 1]["data"].append(self.sequences[seq_id]["data"][-1])
                        del self.sequences[seq_id]["data"][-1]
                    else:
                        break
        removed_seq_id.reverse()
        try:
            for i in removed_seq_id:
                if i + 1 != len(self.sequences) and i != 0:
                    # To combine adjacent sequence after the sequence is removed.
                    for j in self.sequences[i + 1]["data"]:
                        self.sequences[i - 1]["data"].append(j)
                    del self.sequences[i + 1]
                    del self.sequences[i]
                else:
                    del self.sequences[i]
        except IndexError:
           pass
        if need_to_add_first:
            self.sequences.insert(0, {"type": False, "data": data})


    def __get_current_sl(self, seq_id, sl_id):
        # idx = 0
        # for i in range(seq_id):
        #     idx += len(self.sequences[i]["data"])
        # idx += sl_id
        idx = self.sequences[seq_id]["data"][sl_id]["id"]
        cur_sl = self.srs_org_mi[:, :, idx]
        return cur_sl



if __name__ == '__main__':
    display = False
    path_save = r"D:\Daily Result\2304\0406\Enhanced Result of LITS Dataset"
    if not os.path.isdir(path_save):
        os.mkdir(path_save)
    path_org_sl = r"D:\Dataset\Liver TUmor Dataset (Medical Decathlon)\images_Training"
    path_org_mi = r"D:\Dataset\Liver TUmor Dataset (Medical Decathlon)\imagesTr"
    path_seg_results = r"E:\1. Lab\Daily Results\2022\2209\0913\Segmentation Results"
    print(path_save)
    for k in os.listdir(path_seg_results):
        if not os.path.isdir(os.path.join(path_seg_results, k)):
            continue
        if not os.path.isdir(os.path.join(path_save, k)):
            os.mkdir(os.path.join(path_save, k))
        print("[",k,"]")
        for i in os.listdir(os.path.join(path_seg_results, k)):
            if k == "Tool B. 3D Slicer" and i == "liver_10":
                continue
            print("<<",i,">>")
            if not os.path.isdir(os.path.join(path_save, k, i)):
                os.mkdir(os.path.join(path_save, k, i))
            else:
                continue
            path_cur_save = os.path.join(path_save, k, i)
            path_cur_org_sl = os.path.join(path_org_sl, i)
            path_cur_org_mi = os.path.join(path_org_mi, i+".nii")
            if not os.path.isfile(path_cur_org_mi):
                path_cur_org_mi =os.path.join(path_org_mi, i+".nii.gz")
            path_cur_test_case = os.path.join(path_seg_results, k, i)
            # To set the paths of the target folders
            pe = MedImageEnhancer(display)
            pe.set_img_paths(path_cur_org_mi, path_cur_org_sl, path_cur_test_case, path_cur_save)

            # To load images from Local
            pe.load_med_imgs()

            # Step 1. Generate sequences
            print("  Step 1. Generate sequences")
            pe.generate_sequences()
            pe.save_sequences("0.sequences")  # To save enhanced results by each sequence

            # Step 2. Remedy appearance consistency violation
            print("  Step 2. Remedy appearance consistency violation")
            pe.remedy_appearance_consistency_violation()
            pe.save_sequences("1.appearance")  # To save enhanced results by each sequence

            # Step 3. Remedy location consistency violation
            print("  Step 3. Remedy location consistency violation")
            pe.remedy_location_consistency_violation()
            pe.save_sequences("2.location")

            # Step 4. Remedy Size Consistency Violation
            print("  Step 4. Remedy Size Consistency Violation")
            pe.remedy_size_consistency_violation()
            pe.save_sequences("3.size_violation")

            # Step 5. Remedy Shape consistency violation
            print("  Step 5. Remedy Shape consistency violation")
            pe.remedy_shape_consistency_violation()
            pe.save_sequences("4.shape violation")

            # Step 6. Remedy HU Scale consistency Violation
            print("  Step 6. Remedy HU Scale consistency Violation")
            pe.remedy_HU_scale_consistency_violation()
            pe.save_sequences("5. HU Scale Violation")

            pe.save_segmentations("result")



    display = False
    path_test_case = r"E:\1. Lab\Daily Results\2022\2209\0913\Segmentation Results"
    # path_test_case = r"E:\1. Lab\Daily Results\2022\2209\0913\test"
    path_save = r"E:\1. Lab\Daily Results\2022\2210\1004\Enhanced Result of LITS Dataset"
    print(path_save)
    if not os.path.isdir(path_save):
        os.mkdir(path_save)

    # path_org = r"E:\1. Lab\Daily Results\2022\2209\0913\Step 3. Remedy Location Violation"
    # path_test_case = os.path.join(path_org, "Test Data")
    # path_save = os.path.join(path_org, "Result")


    p_label = r"D:\Dataset\Liver TUmor Dataset (Medical Decathlon)\labels\liver"

    path_org_sl = r"D:\Dataset\Liver TUmor Dataset (Medical Decathlon)\images_Training"  # Path of Original Slices (###/###_SLNUM.png)
    path_org_mi = r"D:\Dataset\Liver TUmor Dataset (Medical Decathlon)\imagesTr"  # Path of Original Medical Image (liver_#.nii)
    path_org_label = r"D:\Dataset\Liver TUmor Dataset (Medical Decathlon)\labels\liver"  # Path to save results
    for j in os.listdir(path_test_case):
        # if int(j) not in [8, 17]:
        # if int(j) not in  [ 22]:
        #     continue
        if j in os.listdir(path_save):
            continue
        print("["+j+"]")
        # if ("Case 7." not in j):
        #     continue
        pe = MedImageEnhancer(display)
        # i = j.split(",")[-1]
        i = j.split("-")[-1]
        # i = j
        path_cur_test_case = os.path.join(path_test_case, j)
        path_cur_save = os.path.join(path_save, j)
        path_cur_org_sl = os.path.join(path_org_sl, i)
        path_cur_org_label = os.path.join(path_org_label, i)
        path_cur_org_mi = os.path.join(path_org_mi, "liver_" + str(int(i)) + ".nii")
        if not os.path.isdir(path_cur_save):
            os.mkdir(path_cur_save)

        # To set the paths of the target folders
        pe.set_img_paths(path_cur_org_mi, path_cur_org_sl, path_cur_test_case, path_cur_save)

        # To load images from Local
        pe.load_med_imgs()

        # Step 1. Generate sequences
        print("  Step 1. Generate sequences")
        pe.generate_sequences()
        pe.save_sequences("0.sequences")  # To save enhanced results by each sequence

        # Step 2. Remedy appearance consistency violation
        print("  Step 2. Remedy appearance consistency violation")
        pe.remedy_appearance_consistency_violation()
        pe.save_sequences("1.appearance")  # To save enhanced results by each sequence

        # Step 3. Remedy location consistency violation
        print("  Step 3. Remedy location consistency violation")
        pe.remedy_location_consistency_violation()
        pe.save_sequences("2.location")

        # Step 4. Remedy Size Consistency Violation
        print("  Step 4. Remedy Size Consistency Violation")
        pe.remedy_size_consistency_violation()
        pe.save_sequences("3.size_violation")

        # Step 5. Remedy Shape consistency violation
        print("  Step 5. Remedy Shape consistency violation")
        pe.remedy_shape_consistency_violation()
        pe.save_sequences("4.shape violation")

        # Step 6. Remedy HU Scale consistency Violation
        print("  Step 6. Remedy HU Scale consistency Violation")
        pe.remedy_HU_scale_consistency_violation()
        pe.save_sequences("5. HU Scale Violation")

        pe.save_segmentations("result")

        # pe.display_post_enhancement_results()


    # Performance Evaluation
    # performance_measurer = ImgDataPerformanceMeasurer()
    # now = datetime.now()
    # p_excel_save = os.path.join(path_save, "result_"+now.strftime("%Y-%m-%d %H-%M-%S")+".xlsx")
    #
    # writer_test = pd.ExcelWriter(os.path.join(p_excel_save), engine='xlsxwriter')
    # summary = {"ID": [], "avgDSC_Seg":[], "avgDSC_enh":[]}
    # for i in os.listdir(path_save):
    #     if not os.path.isdir(os.path.join(path_save, i)):
    #         continue
    #     p_label_cur = os.path.join(p_label, i)
    #     p_seg_cur = os.path.join(path_test_case, i)
    #     p_enh_cur = os.path.join(path_save, i, "result")
    #     data={"fileName":[], "areaLabel":[], "areaSeg":[], "areaEnhanced":[], "DSCSeg":[], "DSCEnh":[]}
    #
    #     labels = []
    #     segs = []
    #     enhs = []
    #     print(i,"  ", len(os.listdir(p_enh_cur)))
    #     for j in os.listdir(p_label_cur):
    #         cur_label = cv2.imread(os.path.join(p_label_cur, j), cv2.IMREAD_GRAYSCALE)
    #         cur_seg = cv2.imread(os.path.join(p_seg_cur, j), cv2.IMREAD_GRAYSCALE)
    #         cur_enh = cv2.imread(os.path.join(p_enh_cur, j), cv2.IMREAD_GRAYSCALE)
    #         data["fileName"].append(j)
    #         data["areaLabel"].append(np.count_nonzero(cur_label))
    #         data["areaSeg"].append(np.count_nonzero(cur_seg))
    #         data["areaEnhanced"].append(np.count_nonzero(cur_enh))
    #         data["DSCSeg"].append(performance_measurer.compute_dsc(cur_label, cur_seg))
    #         data["DSCEnh"].append(performance_measurer.compute_dsc(cur_label, cur_enh))
    #         labels.append(cur_label)
    #         segs.append(cur_seg)
    #         enhs.append(cur_enh)
    #     data_pd = pd.DataFrame.from_dict(data)
    #     data_pd.to_excel(writer_test, sheet_name=str(i))
    #     summary["ID"].append(i)
    #     summary["avgDSC_Seg"].append(performance_measurer.compute_avg_dsc(labels, segs))
    #     summary["avgDSC_enh"].append(performance_measurer.compute_avg_dsc(labels, enhs))
    # summary_pd = pd.DataFrame.from_dict(summary)
    # summary_pd.to_excel(writer_test, sheet_name=str("Summary"))
    # writer_test.save()
