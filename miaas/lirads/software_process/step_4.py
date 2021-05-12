"""
Date: 2021. 04. 27.
Programmer: MH
Description: Code for evaluating image features for lesion's images
"""
from miaas.lirads.util.tumor_type_classifier import LesionImagingFeatureClassifier
import numpy as np
import cv2


class ImageFeatureEvaluator:
    def __init__(self):
        self.setCT_slices = {}
        self.setCT_seg = {}
        self.setCT_tumor_seg = {}
        self.feature_classifier = LesionImagingFeatureClassifier()
        self.feature_classifier.load_model()
        self.features = {}
        self.list_phases = []

    def generate_slice_group(self, setCT_B, setCT_B_Seg, setCT_C_Seg):
        """
        TO generate slices groups considering different series
        :param setCT_B:
        :param setCT_B_Seg:
        :param setCT_C_Seg:
        :return:
        """
        min_slices = len(list(setCT_B[list(setCT_B.keys())[0]]))
        # To consider the series minimum number of slices
        self.list_phases = list(setCT_B.keys())
        for i in list(setCT_B.keys())[1:]:
            cur_slices = len(setCT_B[i])
            if min_slices > cur_slices:
                min_slices = cur_slices
        for i in range(min_slices):
            self.setCT_slices[i] = {}
            self.setCT_seg[i] = {}
            self.setCT_tumor_seg[i] = {}
            for j in list(setCT_B.keys()):
                self.setCT_slices[i][j] = setCT_B[j][i]
                self.setCT_seg[i][j] = setCT_B_Seg[j][i]
                self.setCT_tumor_seg[i][j] = setCT_C_Seg[j][i]

        # TODO: To need to add code for comparing similarity

        return self.setCT_tumor_seg

    def correct_segmented_lesion_location(self, setCT_tumor_seg):
        """
        To share segmented lesion location and modify the location of segmented tumor
        :param setCT_Slices:
        :param setCT_tumor_seg:
        :return:
        """
        # To setCT_slices , setCT_tumor
        setCT_tumor = {}
        for sl_id in range(len(setCT_tumor_seg)):      # Slice group ID
            for series_id in list(setCT_tumor_seg[sl_id].keys()):   # Series
                cur_target_list = setCT_tumor_seg[sl_id][series_id]["masks"]
                cur_target_rois = setCT_tumor_seg[sl_id][series_id]["rois"]
                for other_series_id in list(setCT_tumor_seg[sl_id].keys()):
                    if series_id == other_series_id:
                        continue
                    other_target_list = setCT_tumor_seg[sl_id][other_series_id]["masks"]    # list of masks
                    for i in range(len(cur_target_list)):       # To compare each mask in current tumor list to masks in other lists
                        c = cur_target_list[i]
                        cr = cur_target_rois[i]
                        is_contained_c = False
                        for o_i in range(len(other_target_list)):
                            o = other_target_list[o_i]
                            result_and = cv2.bitwise_and(c, o)
                            if len(np.unique(result_and)) > 1:
                                is_contained_c = True
                                break
                        if not is_contained_c:
                            ### To add information of "c" ROI, ..............
                            setCT_tumor_seg[sl_id][other_series_id]["masks"].insert(i, c)
                            setCT_tumor_seg[sl_id][other_series_id]["rois"].insert(i, cr)   # TO be changed
            list_masks = {"masks": [], "rois": [], "img":None}             # list_masks = [list_for_phase 1, list_for_phase 2,list_for_phase 3,list_for_phase 4]
            for srs_id in list(setCT_tumor_seg[sl_id].keys()):
                list_masks["masks"].append(setCT_tumor_seg[sl_id][srs_id]["masks"])
                list_masks["rois"].append(setCT_tumor_seg[sl_id][srs_id]["rois"])
                list_masks["img"] = setCT_tumor_seg[sl_id][srs_id]["img"]
            setCT_tumor[sl_id] = list_masks
        for sg_id in list(setCT_tumor.keys()):
            for mask_id in range(len(setCT_tumor[sg_id]["masks"])):
                for srs_id in range(len(setCT_tumor[sg_id]["masks"][mask_id])):
                    k = setCT_tumor[sg_id]["masks"][mask_id][srs_id]
                    k = np.where(k>0, 255, k)
                    cv2.imwrite("E:\\2. Project\\Python\\LiverDiseaseDetection\\img\\step4\\"+str(sg_id)+"_"+str(srs_id)+"_"+str(mask_id)+".png", k)
        return setCT_tumor  # {Slice ID: [mask_list_Srs_1, mask_list_Srs_2, ...], Slice ID2: [mask_list_Srs_1, mask_list_Srs_2, ...], }

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

    def make_lesion_group(self, setCT_tumor_seg):
        """
        TODO
        To make groups of lesions considering multiple CT slices
        :return:
        """
        self.tumor_groups = {}  # {tumor Group ID:{slice Group ID: [mask_srs_1, mask_srs_2, ...]}, }
        lesion_group_id = -1
        list_tumor_segs = list(setCT_tumor_seg.keys())
        for s in range(len(list_tumor_segs)):      # Slice group ID
            sg_id = list_tumor_segs[s]
            cur_group_ids = []
            for srs_id in range(len(setCT_tumor_seg[sg_id]["masks"])):  # series
                if srs_id == 0:
                    # First phase. defining tumor group id.
                    for mask_id in range(len(setCT_tumor_seg[sg_id]["masks"][srs_id])):
                        cur_mask = setCT_tumor_seg[sg_id]["masks"][srs_id][mask_id]
                        cur_roi = setCT_tumor_seg[sg_id]["rois"][srs_id][mask_id]
                        cur_img = setCT_tumor_seg[sg_id]["img"]
                        do_need_new_group = True
                        for tg_id in list(self.tumor_groups.keys()):    # Tumor Group ID
                            last_sg_id = list(self.tumor_groups[tg_id].keys())[-1]
                            if (last_sg_id+1 == sg_id) and len(np.unique(cv2.bitwise_and(cur_mask, self.tumor_groups[tg_id][last_sg_id][-1]["masks"])))>0:
                                lesion_group_id = tg_id
                                do_need_new_group = False
                                break

                        if do_need_new_group:   # If new tumor group is required
                            try:
                                lesion_group_id = list(self.tumor_groups.keys())[-1]+1  # To add 1 to last tumor group id
                            except:
                                lesion_group_id = 0 # set zero (Initialization)


                        # To initialize new tumor group
                        if lesion_group_id not in list(self.tumor_groups.keys()):
                            self.tumor_groups[lesion_group_id] = {}
                        cur_group_ids.append(lesion_group_id)
                        if sg_id not in list(self.tumor_groups[lesion_group_id]):
                            self.tumor_groups[lesion_group_id][sg_id] = []

                        self.tumor_groups[lesion_group_id][sg_id].append({"masks": cur_mask, "rois": cur_roi, "img": cur_img})
                else:
                    # Other phases. Just add following selected group id
                    for mask_id in range(len(setCT_tumor_seg[sg_id]["masks"][srs_id])):
                        cur_mask = setCT_tumor_seg[sg_id]["masks"][srs_id][mask_id]
                        cur_roi = setCT_tumor_seg[sg_id]["rois"][srs_id][mask_id]
                        cur_img = setCT_tumor_seg[sg_id]["img"]
                        # To check overlapped
                        for g_id in cur_group_ids:
                            is_appended = False
                            for s_i in list(self.tumor_groups[g_id].keys()):
                                if len(self.tumor_groups[g_id][s_i])-1 == srs_id or len(setCT_tumor_seg[sg_id]["masks"])==len(self.tumor_groups[g_id][s_i]):
                                    continue
                                if len(np.unique(cv2.bitwise_and(self.tumor_groups[g_id][s_i][-1]["masks"], cur_mask)))>1:
                                    self.tumor_groups[g_id][s_i].append({"masks": cur_mask, "rois": cur_roi, "img": cur_img})
                                    is_appended = True
                                    break
                            if is_appended:
                                break
        return self.tumor_groups

    def check_treatment(self):
        """
        To check the tumor's treatment information considering image features and record
        :return:
        """
        pass

    def evaluate_image_feature(self, set_tumor_groups):
        """
        To evaluate image features for a tumor
        :return:
        """
        self.features = {}
        for i in list(set_tumor_groups.keys()):     # Tumor Group ID
            self.features[i] = {}
            for j in list(set_tumor_groups[i].keys()):    # Slice Group ID
                self.features[i][j] = []
                for mask in set_tumor_groups[i][j]:
                    cur_roi = self.__slice_roi(mask["img"], mask["rois"])
                    result = self.feature_classifier.predict(cur_roi)
                    self.features[i][j].append(self.feature_classifier.get_features(result[0]))
        return self.features

    def __slice_roi(self, cur_img, roi):
        return cur_img[roi[0]:roi[2], roi[1]:roi[3]]

    def discard_insignificant_image_features(self):
        """
        TODO
        To discard insignificant image features among evaluated results considering predicted image features
        :return:
        """
        pass

    def get_features(self):
        return self.features

    def get_list_phases(self):
        return self.list_phases
