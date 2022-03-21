"""
Date: 2022. 03. 12.
Programmer: MH
Description: Code for Segmenting Hepatic Segments and Lesion
"""
import os

from miaas.lirads.software_process.step_2 import LiverRegionSegmentater

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import os.path
import sys
import warnings

import cv2
import numpy as np

sys.path.append(r"E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads")
from miaas.lirads.util.hepatic_segmentator import HepaticSegmentsSegmentator
from step_1 import MedicalImageLoader
from step_3 import LegionSegmentor


class Step2HepaticSegmentSegmentator:
    def __init__(self):
        self.target_srs = {}
        self.target_study = {}
        self.target_study_cvt = {}
        self.hepatic_segments = {}
        self.hepatic_segments_detail = {}
        self.cur_srs_id = -1
        self.hss = HepaticSegmentsSegmentator("MRCNN")
        self.hss.load_model()
        self.list_cur_srs = []
        self.cur_std_id = ""
        self.n_slices_contain_liver = 0
        self.sl_start, self.sl_end = -1, -1
        self.path_save = r""
    def set_cur_save_path(self, p):
        self.path_save = p
    def set_target_study(self, std_org, std_cvt):
        self.target_study = std_org
        self.target_study_cvt = std_cvt
        self.cur_std_id = list(self.target_study.keys())[0]
        self.list_cur_srs = list(self.target_study[self.cur_std_id].keys())
        self.hepatic_segments[self.cur_std_id] = {}
        self.hepatic_segments_detail[self.cur_std_id] = {}
        for i in self.list_cur_srs:
            self.hepatic_segments[self.cur_std_id][i] = {}
            self.hepatic_segments_detail[self.cur_std_id][i] = {}

    def set_seged_liver_regions(self, setCT_b_seg):
        self.setCT_b_seg = setCT_b_seg

    def set_target_series(self):
        """
        To set series applied to target for segment hepatic segments
        """
        self.cur_srs_id += 1
        self.target_srs = self.target_study_cvt[self.cur_std_id][self.list_cur_srs[self.cur_srs_id]]    # To select target series
        self.hepatic_segments[self.cur_std_id][self.list_cur_srs[self.cur_srs_id]] = {}     # To generate dict for segmented results from target_srs
        self.hepatic_segments_detail[self.cur_std_id][self.list_cur_srs[self.cur_srs_id]] = {}     # To generate dict for segmented results from target_srs
        if self.cur_srs_id < len(self.list_cur_srs)-1:
            return True
        else:
            self.cur_srs_id = -1
            return False

    def segment_hepatic_segments(self):
        """
        To segment hepatic segments of liver organ using CNN model
        """
        list_keys = list(self.target_srs.keys())
        detail = self.hss.predict(list(self.target_srs.values()))
        for i in range(len(detail)):
            # To combine results segmented to same hepatic segment ID
            list_scores = []
            list_rois = []
            cur_masks = None
            for j in np.unique(detail[i]["class_ids"]): # To select Unique IDs
                list_cur_id = np.where(detail[i]["class_ids"] == j)[0]  # select a result
                mask_cur = detail[i]["masks"][:,:,list_cur_id[0]]
                list_scores.append(detail[i]["scores"][list_cur_id[0]])
                list_rois.append(detail[i]["rois"][list_cur_id[0]])
                for k in list_cur_id[1:]:   # To combine segmented results for each segment ID
                    mask_cur = np.where(detail[i]["masks"][:,:,k]== True, True, mask_cur)
                if cur_masks is None:
                    cur_masks = mask_cur
                    cur_masks = np.reshape(cur_masks, (512, 512, 1))
                else:
                    cur_masks = np.dstack((cur_masks, mask_cur))
            if cur_masks is None:
                cur_masks = np.array((512, 512, 1))
                cur_masks.fill(False)
            detail[i]["masks"] = cur_masks

            # To discard applied data
            detail[i]["rois"] = list_rois
            detail[i]["scores"] = list_scores
            detail[i]["class_ids"] = np.unique(detail[i]["class_ids"])

            msk = np.zeros((512, 512))
            for j in range(len(detail[i]["class_ids"])):
                msk = np.where(detail[i]["masks"][:, :, j] == True, int(detail[i]["class_ids"][j] * 28), msk)

            self.hepatic_segments_detail[self.cur_std_id][self.list_cur_srs[self.cur_srs_id]][list_keys[i]] = detail[i]
            self.hepatic_segments[self.cur_std_id][self.list_cur_srs[self.cur_srs_id]][list_keys[i]] = msk

            cv2.imwrite(os.path.join(self.path_save,r"hepatic_segs", self.list_cur_srs[self.cur_srs_id] + "_" +list_keys[i] + ".png"),
                        self.__add_seg_id_in_img(msk, self.target_study_cvt[self.cur_std_id][self.list_cur_srs[self.cur_srs_id]][list_keys[i]]))

        i = self.list_cur_srs[self.cur_srs_id]
        for j in list(self.setCT_b_seg[i].keys()):  # Slice
            if len(np.unique(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"] == True)))>1:
                for k in range(1, 10):
                    if k in self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]:
                        cur_idx = np.where(np.array(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"])==k)[0][0]
                        cur_msk_select = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, cur_idx]==True, 255, 0), np.uint8)
                        cv2.imwrite(os.path.join(self.path_save, r"hepatic_segs_detail",i + "_" + j + "_"+str(k)+".png"), cur_msk_select)

    def refine_hepatic_segments(self):
        """
        To refine hepatic segments following the tactics
        """
        # To find the start and edn slice ID containing the liver organ and the number of slices containing liver organ
        i = self.list_cur_srs[self.cur_srs_id]
        for j in list(self.setCT_b_seg[i].keys()):   # Slice
            cur_liver_seg = np.array(np.reshape(self.setCT_b_seg[i][j]["masks"], (512, 512)), np.uint8)
            if np.count_nonzero(cur_liver_seg)>0:
                self.n_slices_contain_liver+=1
                if self.sl_start == -1:
                    self.sl_start = int(j)
            else:
                if self.sl_start!= -1 and self.sl_end==-1:
                    self.sl_end = int(j)-1


        # Case 2. Not same Location and Shape of Liver to the results of liver segmentation
        i = self.list_cur_srs[self.cur_srs_id]
        for j in list(self.setCT_b_seg[i].keys()):   # Slice
            list_new_class_ids = []
            cur_liver_seg = np.array(np.reshape(self.setCT_b_seg[i][j]["masks"], (512, 512)), np.uint8)
            # if j =="00047":
            #     cv2.imshow("prv", cur_hep_seg)
            cur_masks = self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"]
            list_cur_classes = self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]
            msk_revised = np.zeros((512, 512))
            new_masks = None
            for idx in range(len(list_cur_classes)):
                cur_mask_img = np.array(np.where(cur_masks[:,:,idx]==True, 255, 0), np.uint8)
                overlapped_cur = np.bitwise_and(cur_liver_seg, cur_mask_img)
                if len(np.unique(overlapped_cur)) > 1:
                    list_new_class_ids.append(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"][idx])
                    if new_masks is None:
                        new_masks = np.where(overlapped_cur>0, True, False)
                        new_masks = np.reshape(new_masks, (512, 512, 1))
                    else:
                        new_masks= np.dstack((new_masks, np.where(overlapped_cur>0, True, False)))
                    msk_revised = np.array( np.where(new_masks[:, :, -1] == True, int(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"][idx] * 28), msk_revised), np.uint8)

            if new_masks is None:
                new_masks = np.zeros((512, 512, 1))
                new_masks.fill(False)
                list_new_class_ids = []
            self.hepatic_segments[self.cur_std_id][i][j] = msk_revised
            self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"] = list_new_class_ids
            self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"] = new_masks
            print(i, "    ",j,"    ", self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"].shape, len(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]))

            cv2.imwrite(os.path.join(self.path_save,r"hepatic_segs_refined2",
                                     i + "_" + j + ".png"),
                        self.__add_seg_id_in_img(msk_revised, self.target_study_cvt[self.cur_std_id][i][j]))

            if len(np.unique(msk_revised))>1:
                for k in range(1, 10):
                    if k in self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]:
                        cur_idx = np.where(np.array(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"])==k)[0][0]
                        cur_msk_select = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, cur_idx]==True, 255, 0), np.uint8)
                        cv2.imwrite(os.path.join(self.path_save, r"hepatic_segs_refined2_detail",i + "_" + j + "_"+str(k)+".png"), cur_msk_select)

        # Case 3.Comparing with the possible combination of hepatic segments considering the location of a slice
        i = self.list_cur_srs[self.cur_srs_id]
        for j in list(self.setCT_b_seg[i].keys()):   # Slice
            cur_masks = self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"]
            list_cur_classes = self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]
            new_masks = None
            new_classes = []

            list_discarded_ids, cls_change = self.__compute_discarded_segments(list_cur_classes, j)
            msk_revised = np.zeros((512, 512))
            # To compute area size of segmented liver region and segmented hepatic segments in each slice
            for idx in range(len(list_cur_classes)):
                cur_id = list_cur_classes[idx]
                if cur_id in list_discarded_ids:
                    if cur_id!=1:
                        self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"][idx] = cls_change[cur_id]
                    else:
                        pass
                msk_revised = np.array(np.where(cur_masks[:, :, idx] == True, int(cur_id * 28), msk_revised), np.uint8)
            # for idx in range(len(list_cur_classes)):
            #     cur_id = list_cur_classes[idx]
            #     if cur_id in list_discarded_ids:
            #         continue
            #     new_classes.append(cur_id)
            #     if new_masks is None:
            #         new_masks = cur_masks[:,:,idx]
            #         new_masks = np.reshape(new_masks, (512, 512, 1))
            #     else:
            #         new_masks = np.dstack((new_masks, cur_masks[:,:,idx]))
            #
            #     msk_revised = np.array(np.where(new_masks[:, :, -1] == True, int(cur_id * 28), msk_revised), np.uint8)
            #
            # if new_masks is None:
            #     new_masks = np.zeros((512, 512, 1))
            #     new_masks.fill(False)
            #
            #
            # self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"] = new_masks
            # self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"] = new_classes
            cv2.imwrite(os.path.join(self.path_save,r"hepatic_segs_refined3",
                                     i + "_" + j + ".png"),
                        self.__add_seg_id_in_img(msk_revised, self.target_study_cvt[self.cur_std_id][i][j]))

            if len(np.unique(msk_revised))>1:
                for k in range(1, 10):
                    if k in self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]:
                        cur_idx = np.where(np.array(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"])==k)[0][0]
                        cur_msk_select = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, cur_idx]==True, 255, 0), np.uint8)
                        cv2.imwrite(os.path.join(self.path_save, r"hepatic_segs_refined3_detail",i + "_" + j + "_"+str(k)+".png"), cur_msk_select)
        # TODO: To check the location of each section
        pass

        # Case 1-2. Checking Overlapped Segmented Results
        # SUBCase 1. Whole Overlapped hepatic segments are in possible combination --> Remain / Assign part of each section
        # SUBCase 2. Some Overlapped are not in possibles --> Remove the section (Already Removed)
        # SUBCase 3. Whole Overlapped not in possibles --> Remove whole sections (Already Removed)
        for j in list(self.setCT_b_seg[i].keys()):  # Slice
            list_cur_classes = self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]
            msk_revised = np.zeros((512, 512))
            for idx in range(len(list_cur_classes)):
                masks_cur = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, idx]== True, 255, 0), dtype=np.uint8)
                for idx_other in range(len(list_cur_classes)):
                    if idx >= idx_other:
                        continue
                    masks_oth = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, idx_other]== True, 255, 0), dtype=np.uint8)
                    overlapped = np.bitwise_and(masks_cur, masks_oth)
                    if len(np.unique(overlapped)) == 1: # Not overlapped
                        continue
                    else:
                        area_oth_remained = masks_oth - overlapped
                        self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, idx_other] = np.where(area_oth_remained>0, True, False)
                        # print("      overlapped ", i, "  ", j, "  ", idx, "  ", idx_other, "    ",  np.count_nonzero(overlapped)/np.count_nonzero(masks_cur))

                msk_revised = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, idx] == True, int(list_cur_classes[idx] * 28), msk_revised), np.uint8)
            cv2.imwrite(os.path.join(self.path_save,r"hepatic_segs_refined4",
                                     i + "_" + j + ".png"),
                        self.__add_seg_id_in_img(msk_revised, self.target_study_cvt[self.cur_std_id][i][j]))

            if len(np.unique(msk_revised))>1:
                for k in range(1, 10):
                    if k in self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]:
                        cur_idx = np.where(np.array(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"])==k)[0][0]
                        cur_msk_select = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, cur_idx]==True, 255, 0), np.uint8)
                        cv2.imwrite(os.path.join(self.path_save, r"hepatic_segs_refined4_detail",i + "_" + j + "_"+str(k)+".png"), cur_msk_select)

        # Case 1. Multiple Sections for A hepatic Segment
        i = self.list_cur_srs[self.cur_srs_id]
        for j in list(self.setCT_b_seg[i].keys()):  # Slice
            list_cur_classes = self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]
            msk_revised = np.zeros((512, 512))
            for idx in range(len(list_cur_classes)):
                masks = self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:,:,idx]
                masks = np.array(np.where(masks==True, 255, 0), np.uint8)
                ctns, _ = cv2.findContours(masks, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                if len(ctns)> 1:
                    area = []
                    for cnt in ctns:
                        area.append(cv2.contourArea(cnt))
                    if len(area)>0:
                        list_enough_area = np.where(np.array(area)/max(area) > 0.1)[0] # To remain the area is bigger than 30% of maximum size
                        cvt_masks = np.zeros((512, 512))
                        cvt_masks.fill(False)
                        for selected in list_enough_area:
                            select_mask = cv2.drawContours(np.zeros((512, 512)), [ctns[selected]], -1, 255, thickness=-1)
                            cvt_masks = np.array(np.where(select_mask==255, True, cvt_masks), np.uint8)
                        self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, idx] = cvt_masks

                msk_revised = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, idx] == True, int(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"][idx] * 28), msk_revised), np.uint8)
            self.hepatic_segments[self.cur_std_id][i][j] = msk_revised

            cv2.imwrite(os.path.join(self.path_save,r"hepatic_segs_refined1",
                                     i + "_" + j + ".png"),
                        self.__add_seg_id_in_img(msk_revised, self.target_study_cvt[self.cur_std_id][i][j]))

            if len(np.unique(msk_revised))>1:
                for k in range(1, 10):
                    if k in self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]:
                        cur_idx = np.where(np.array(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"])==k)[0][0]
                        cur_msk_select = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, cur_idx]==True, 255, 0), np.uint8)
                        cv2.imwrite(os.path.join(self.path_save, r"hepatic_segs_refined1_detail",i + "_" + j + "_"+str(k)+".png"), cur_msk_select)

        # Case 4. Checking Continuity of Each Hepatic Segment in adjacent Slices (Consider shape, location, size)
        # i = self.list_cur_srs[self.cur_srs_id]
        # for j in list(self.setCT_b_seg[i].keys()):  # Slice
        #     cur_liver_seg = np.array(np.reshape(self.setCT_b_seg[i][j]["masks"], (512, 512)), np.uint8)
        #     cur_masks = self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"]
        #     list_cur_classes = self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]
        #     total_area = 0
        #     for idx in range(len(list_cur_classes)):
        #         total_area += np.count_nonzero(np.where(cur_masks[:,:,idx]==True, 255, 0))
        #
        #     if np.count_nonzero(cur_liver_seg) > 20000:
        #         print("    ",i,"    ",j, "    ", np.count_nonzero(cur_liver_seg), "    ", total_area, "    ", np.abs(np.count_nonzero(cur_liver_seg)-total_area))

            # Considering the location groups

        # To remain a section for a hepatic segment class in a slice
        i = self.list_cur_srs[self.cur_srs_id]
        for j in list(self.setCT_b_seg[i].keys()):   # Slice
            list_cur_classes = self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]
            msk_revised = None

            for idx in range(len(list_cur_classes)):
                masks = self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:,:,idx]
                masks = np.array(np.where(masks==True, 255, 0), np.uint8)
                ctns, _ = cv2.findContours(masks, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                max_id, max_size = 0, 0
                cur_msk = self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:,:,idx]
                if len(ctns)> 2:
                    new_mask = np.zeros((512, 512))
                    for cnt_id in range(len(ctns)):
                        cur_area = cv2.contourArea(ctns[cnt_id])
                        if cur_area > max_size:
                            max_id = cnt_id
                            max_size = cur_area
                    select_mask = cv2.drawContours(np.zeros((512, 512)), [ctns[max_id]], -1, 255, thickness=-1)
                    cur_msk = np.array(np.where(select_mask == 255, True, False), np.uint8)
                if msk_revised is None:
                    msk_revised = cur_msk
                    msk_revised.reshape((512, 512, 1))
                else:
                    cur_msk.reshape((512, 512, 1))
                    msk_revised = np.dstack((msk_revised, cur_msk))

            if msk_revised is None:
                msk_revised = np.array((512, 512, 1))
                msk_revised.fill(False)
            self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"] = msk_revised

    def get_hepatic_segments(self):
        return self.hepatic_segments

    def __compute_discarded_segments(self, ids, sl_id):
        """
        To compute hepatic segments considering the location of slice and the possible returned segments combinations
        Possible Segments: [1, 2, 4a, 7, 8], [1, 3, 4b, 5, 6], [1, 3, 4b, 5, 6], [3, 4b, 5, 6]
        [1] Only Superior Liver Segments (Middle Hepatic Vein) : [1, 2, 4a, 7, 8]
        [2] Superior and Inferior        (Left Portal Vein)    : [1, 3, 4b, 7, 8], [1, 2, 4a, 7, 8]
        [3] Superior and Inferior        (Right Portal Vein)   : [1, 3, 4b, 7, 8], [1, 3, 4b, 5, 6]
        [4] Only Inferior Liver Segments (Splenic Vein)        : [3, 4b, 5, 6]

        Source: https://radiologyassistant.nl/abdomen/liver/segmental-anatomy
        """
        possible_combs_1 = [[1, 2, 4, 8, 9]]
        possible_combs_2 = [[1, 3, 4, 8, 9]]
        possible_combs_3 = [[1, 3, 5, 8, 9]]
        possible_combs_4 = [[1, 3, 5, 6, 7]]
        possible_combs_5 = [[3, 5, 6, 7]]
        result= []
        classes_to_change = {}  # {before:after}
        if self.sl_start<=int(sl_id) and self.sl_start+int((self.n_slices_contain_liver)*0.25)>int(sl_id):   #
            result = self.__return_not_contained_ids(possible_combs_1, ids)
            if 3 in result:
                classes_to_change[3] = 2
            if 5 in result:
                classes_to_change[5] = 4
            if 6 in result:
                classes_to_change[6] = 9
            if 7 in result:
                classes_to_change[7] = 8
        elif self.sl_start + int((self.n_slices_contain_liver) * 0.70) <= int(sl_id) and self.sl_start + int(
            (self.n_slices_contain_liver) * 1.0) >= int(sl_id):  # [4]
            result = self.__return_not_contained_ids(possible_combs_5, ids)

            if 2 in result:
                classes_to_change[2] = 3
            if 4 in result:
                classes_to_change[4] = 5
            if 8 in result:
                classes_to_change[8] = 7
            if 9 in result:
                classes_to_change[9] = 6

        # if self.sl_start<=int(sl_id) and self.sl_start+int((self.n_slices_contain_liver)*0.10)>int(sl_id):    # [1]
        #     # print(sl_id, "Case [1]", ids, self.__return_not_contained_ids(possible_combs_1, ids))
        #     result = self.__return_not_contained_ids(possible_combs_1, ids)
        #     if 3 in result:
        #         classes_to_change[3] = 2
        #     if 5 in result:
        #         classes_to_change[5] = 4
        #     if 6 in result:
        #         classes_to_change[6] = 9
        #     if 7 in result:
        #         classes_to_change[7] = 8
        #
        # elif self.sl_start+int((self.n_slices_contain_liver)*0.10)<=int(sl_id) and self.sl_start+int((self.n_slices_contain_liver)*0.25)>int(sl_id): # [2]
        #     # print(sl_id, "Case [2]", ids, self.__return_not_contained_ids(possible_combs_2, ids))
        #     result = self.__return_not_contained_ids(possible_combs_2, ids)
        #     if 3 in result:
        #         classes_to_change[3] = 2
        #     if 5 in result:
        #         classes_to_change[5] = 4
        #     if 6 in result:
        #         classes_to_change[6] = 9
        #     if 7 in result:
        #         classes_to_change[7] = 8
        #
        # elif self.sl_start+int((self.n_slices_contain_liver)*0.25)<=int(sl_id) and self.sl_start+int((self.n_slices_contain_liver)*0.35)>int(sl_id): # [3]
        #     # print(sl_id, "Case [2] or [3]", ids, self.__return_not_contained_ids(possible_combs_3, ids))
        #     result = self.__return_not_contained_ids(possible_combs_3, ids)
        #     if 2 in result:
        #         classes_to_change[2] = 3
        #     if 4 in result:
        #         classes_to_change[4] = 5
        #     if 6 in result:
        #         classes_to_change[6] = 9
        #     if 7 in result:
        #         classes_to_change[7] = 8
        #
        # elif self.sl_start+int((self.n_slices_contain_liver)*0.35)<=int(sl_id) and self.sl_start+int((self.n_slices_contain_liver)*0.65)>int(sl_id): # [4]
        #     # print(sl_id, "Case [3]", ids, self.__return_not_contained_ids(possible_combs_4, ids))
        #     result = self.__return_not_contained_ids(possible_combs_4, ids)
        #
        #     if 2 in result:
        #         classes_to_change[2] = 3
        #     if 4 in result:
        #         classes_to_change[4] = 5
        #     if 8 in result:
        #         classes_to_change[8] = 7
        #     if 9 in result:
        #         classes_to_change[9] = 6
        # elif self.sl_start+int((self.n_slices_contain_liver)*0.65)<=int(sl_id) and self.sl_start+int((self.n_slices_contain_liver)*1.0)>=int(sl_id): # [4]
        #     # print(sl_id, "Case [4]", ids, self.__return_not_contained_ids(possible_combs_5, ids))
        #     result = self.__return_not_contained_ids(possible_combs_5, ids)
        #
        #     if 2 in result:
        #         classes_to_change[2] = 3
        #     if 4 in result:
        #         classes_to_change[4] = 5
        #     if 8 in result:
        #         classes_to_change[8] = 7
        #     if 9 in result:
        #         classes_to_change[9] = 6
        else:   # [5]
            pass
            # print(sl_id, "Case [5]", ids, self.__return_not_contained_ids([[]], ids))
        return result, classes_to_change

    def __return_not_contained_ids(self, src, trg):
        """
        To return not contained hepatic ids in source list
        """
        result = []
        for t in trg:
            for s in src:
                if t not in s:
                    result.append(t)
        return result

    def __add_seg_id_in_img(self, img, org=None):
        background = np.zeros((512, 512))
        if org is None:
            result = np.zeros((512, 512, 3))
        else:
            cnts, _ = cv2.findContours(org, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            max_area_id, max_size = 0, 0
            for j in range(len(cnts)):
                if max_size < cv2.contourArea(cnts[j]):
                    max_area_id = j
                    max_size = cv2.contourArea(cnts[j])
            background = cv2.drawContours(np.zeros((512, 512)), [cnts[max_area_id]], -1, 255, thickness=-1)
            result = cv2.cvtColor(np.array(org, np.uint8), cv2.COLOR_GRAY2BGR)

        rgb = [(135, 75, 0), (0, 205, 255), (68, 106, 0), (45, 39, 193), (190, 173, 0), (176, 0, 166), (0, 104, 204), (28, 95, 62), (153, 87, 94)]
        for i in range(1, 10):
            cur_msk_ = np.array(np.where(img == i*28, 255, 0), np.uint8)
            cnts, _ = cv2.findContours(cur_msk_, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            for cnt in cnts:
                cv2.drawContours(result, [cnt], 0, rgb[i-1], 2)
            if len(cnts)>0:
                cur_seg = self.__convert_hepatic_segs([i])
                m = cv2.moments(cnts[0])
                try:
                    cx = int(m['m10']/m['m00'])
                    cy = int(m['m01']/m['m00'])
                    cx_new = cx
                    cy_new = cy
                    cx_arrow = cx
                    cy_arrow = cy
                    if i == 1:  # Seg I
                        # cy ++
                        list_trg = np.array(np.where(background[:, cx] == 0)[0])
                        list_slct_y = list_trg[np.where(list_trg > cy)[0]]
                        cy_new = list_slct_y[0]+25
                        cy_arrow = cy_new - 15
                        cx_arrow = cx_new +10
                    elif i == 2 or i == 3:  # Seg II and Seg III
                        # cy --

                        list_trg = np.array(np.where(background[:, cx] == 0)[0])
                        list_slct_y = list_trg[np.where(list_trg < cy)[0]]
                        cy_new = list_slct_y[-1]-15
                        cy_arrow = cy_new + 5
                        cx_arrow = cx_new +15
                    elif i == 4 or i == 5:  # Seg IVa and Seg IVb
                        # cy --
                        list_trg = np.array(np.where(background[:, cx] == 0)[0])
                        list_slct_y = list_trg[np.where(list_trg < cy)[0]]
                        cy_new = list_slct_y[-1]-15
                        cy_arrow = cy_new + 5
                        cx_arrow = cx_new +15
                    elif i == 6 or i == 9:  # Seg V and Seg VIII
                        # cy -- and cx--
                        list_trg = np.array(np.where(background[:cy, :cx] == 0))
                        cx_new = list_trg[1][-1]-10
                        cy_new = list_trg[0][-1]-20
                        cy_arrow = cy_new
                        cx_arrow = cx_new
                    else:                   # Seg VI and Seg VII
                        # cy++
                        list_trg = np.array(np.where(background[:, cx] == 0)[0])
                        list_slct_y = list_trg[np.where(list_trg > cy)[0]]
                        cy_new = list_slct_y[0]+25
                        cy_arrow = cy_new - 15
                        cx_arrow = cx_new +10
                    # print(i,":    ", cx,"-->", cx_new,"    ", cy,"-->", cy_new)
                    cv2.putText(result, cur_seg[0], (cx_new, cy_new), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_8)
                    result = cv2.line(result, (cx_arrow, cy_arrow), (cx, cy), rgb[i-1], 1, cv2.LINE_8)
                except:
                    pass
        return result

    def __convert_hepatic_segs(self, list_id):
        result = []
        for i in list_id:
            if i == 0:
                pass
            elif i == 1:
                result.append("I")
            elif i == 2:
                result.append("II")
            elif i == 3:
                result.append("III")
            elif i == 4:
                result.append("IVa")
            elif i == 5:
                result.append("IVb")
            elif i == 6:
                result.append("V")
            elif i == 7:
                result.append("VI")
            elif i == 8:
                result.append("VII")
            elif i == 9:
                result.append("VIII")
        return result


class LiverLesionSegmentator:
    def __init__(self):
        self.target_srs = []
        self.target_study = {}
        self.target_study_cvt = {}
        self.liver_lesions = {}
        self.cur_srs_id = -1
        self.cur_sl_id = -1
        self.list_cur_srs = []
        self.cur_std_id = ""
        self.hepatic_segment = {}
        self.lesion_segmentator = LegionSegmentor()
        self.list_cur_sl = []
        self.info_lesions = {}   # {Lesion_ID#1:
                                 #      {location: None, masks: {PhaseName:{SLICEID: mask, ...}, .. }},
                                 #      ... }

        self.path_save = r""
    def set_cur_save_path(self, p):
        self.path_save = p

    def set_hepatic_segments(self, hepatic_segment):
        """
        To receive hepatic segment data
        """
        self.hepatic_segment = hepatic_segment

    def set_seged_liver_regions(self, setCT_b_seg):
        self.setCT_b_seg = setCT_b_seg

    def set_target_study(self, std_org, std_cvt):
        """
        To receive target study (original data and converted color map data)
        """
        self.target_study = std_org
        self.target_study_cvt = std_cvt
        self.cur_std_id = list(self.target_study_cvt.keys())[0]
        self.list_cur_srs = list(self.target_study_cvt[self.cur_std_id].keys())
        self.liver_lesions[self.cur_std_id] = {}
        for i in self.list_cur_srs:
            self.liver_lesions[self.cur_std_id][i] = []

        # To load model for segmentation
        self.lesion_segmentator.initialize(self.cur_std_id)
        self.lesion_segmentator.load_model("CT")

    def set_target_series(self):
        """
        To set series applied to target for segment hepatic segments
        """
        self.cur_srs_id += 1
        self.target_srs = self.target_study_cvt[self.cur_std_id][self.list_cur_srs[self.cur_srs_id]]
        self.list_cur_sl = list(self.target_study_cvt[self.cur_std_id][self.list_cur_srs[self.cur_srs_id]].keys())
        self.liver_lesions[self.cur_std_id][self.list_cur_srs[self.cur_srs_id]] = {}
        if self.cur_srs_id < len(self.list_cur_srs)-1:
            return True
        else:
            self.cur_srs_id = -1
            return False

    def set_target_slice(self):
        """
        To set a slice to segment the liver lesion
        """
        self.cur_sl_id += 1
        self.target_sl = self.target_study_cvt[self.cur_std_id][self.list_cur_srs[self.cur_srs_id]][
            self.list_cur_sl[self.cur_sl_id]]
        cv2.imwrite(os.path.join(self.path_save,r"imgs",
                                 self.list_cur_srs[self.cur_srs_id] + "_" + self.list_cur_sl[
                                     self.cur_sl_id] + ".png"), self.target_sl)
        self.target_sl = np.reshape(self.target_sl,
                                    (512, 512, 1))  # To convert the slice's shape from (512, 512) to (512, 512, 1)
        if self.cur_sl_id < len(self.target_study_cvt[self.cur_std_id][self.list_cur_srs[self.cur_srs_id]])-1:
            return True
        else:
            self.cur_sl_id = -1
            return False

    def segment_liver_lesion(self):
        """
        To segment liver lesions in a slice
        """
        result, sl_a = self.lesion_segmentator.segment_lesion_a_slice(self.target_sl)
        self.liver_lesions[self.cur_std_id][self.list_cur_srs[self.cur_srs_id]][self.list_cur_sl[self.cur_sl_id]] = result
        cv2.imwrite(os.path.join(self.path_save,r"tumors",
                                 self.list_cur_srs[self.cur_srs_id]+"_"+self.list_cur_sl[self.cur_sl_id]+".png"), sl_a)

    def refine_liver_lesions(self):
        """
        To refine segmented liver lesions applying tactics
        """
        pass
        # Case 1. Check whether Included in Liver Organ or Not
        for i in  list(self.setCT_b_seg.keys()):
            for j in list(self.setCT_b_seg[i].keys()):   # Slice
                cur_liver_seg = np.array(self.setCT_b_seg[i][j]["masks"], np.uint8)
                cur_liver_lesions = np.array(self.liver_lesions[self.cur_std_id][i][j], np.uint8)
                cur_hep_seg_refined = np.zeros((512, 512, 1))
                overlapped_cur = np.bitwise_and(cur_liver_seg, cur_liver_lesions)
                cur_hep_seg_refined = np.array(np.where(overlapped_cur == 255, 255, cur_hep_seg_refined), dtype=np.uint8)
                self.liver_lesions[self.cur_std_id][i][j] = cur_hep_seg_refined
                cv2.imwrite(os.path.join(self.path_save,r"tumors_refined",
                                         i + "_" + j + ".png"),cur_hep_seg_refined)

        # Case 2. Lesion's Continuity of Location and Size in a Series

        # Case 3. Lesion's Location Synchronization Considering Inter-Series

    def set_lesion_location(self):
        """
        To measure the lesion location applying hepatic segments
        When the lesion's location is detected, the overlapped relationship is applied.
        After overlapped two images, the Class ID of hepatic segment overlapped section is applied.
        """

        for cur_phase_id in list(self.liver_lesions[self.cur_std_id].keys()):  # Phase
            for cur_sl_id in list(self.liver_lesions[self.cur_std_id][cur_phase_id].keys()):    # Slice
                cur_sl_lesion = self.liver_lesions[self.cur_std_id][cur_phase_id][cur_sl_id]
                cur_sl_hep_seg = self.hepatic_segment[self.cur_std_id][cur_phase_id][cur_sl_id]
                cur_sl_hep_seg = np.reshape(cur_sl_hep_seg, (512, 512, 1))
                overlapped = np.where(cur_sl_lesion==255, cur_sl_hep_seg, 0)
                overlapped_pixels = np.array(np.unique(overlapped)/28, dtype=np.uint8)
                if len(overlapped_pixels) > 1 or (len(overlapped_pixels)==1 and overlapped_pixels[0] != 0):
                    print("      >>", cur_phase_id + "_" + cur_sl_id, ": ", overlapped_pixels, self.__convert_hepatic_segs(overlapped_pixels))
                else:
                    print("      >>", cur_phase_id + "_" + cur_sl_id, ": Any Lesion Detected ")
                cur_sl_hep_seg_rgb = cv2.cvtColor(np.array(cur_sl_hep_seg, np.uint8), cv2.COLOR_GRAY2BGR)
                cur_sl_lesion_rgb = cv2.cvtColor(np.array(cur_sl_lesion, np.uint8), cv2.COLOR_GRAY2BGR)
                result = self.__add_seg_id_in_img(cur_sl_hep_seg_rgb, cur_sl_lesion_rgb,
                                                              self.target_study_cvt[self.cur_std_id][cur_phase_id][cur_sl_id])
                result = self.__add_overlapped_segs_name(cur_sl_lesion_rgb, result, ",".join([str(x) for x in self.__convert_hepatic_segs(overlapped_pixels)]))
                cv2.imwrite(os.path.join(self.path_save,r"overlapped",
                                     cur_phase_id + "_" + cur_sl_id+"_"+",".join([str(x) for x in overlapped_pixels]) + ".png"), result)

    def __convert_hepatic_segs(self, list_id):
        result = []
        for i in list_id:
            if i == 0:
                pass
            elif i== 1:
                result.append("I")
            elif i== 2:
                result.append("II")
            elif i== 3:
                result.append("III")
            elif i== 4:
                result.append("IVa")
            elif i== 5:
                result.append("IVb")
            elif i== 6:
                result.append("V")
            elif i== 7:
                result.append("VI")
            elif i== 8:
                result.append("VII")
            elif i== 9:
                result.append("VIII")
        return result

    def __add_seg_id_in_img(self, img, lesion, org=None):
        if org is None:
            result = np.zeros((512, 512, 3))
        else:
            result = cv2.cvtColor(np.array(org, np.uint8), cv2.COLOR_GRAY2BGR)
        # alpha_channel = np.ones((512, 512, 1), dtype=np.uint8)*255
        # result = np.concatenate((result, alpha_channel), axis=2)
        # lesion = np.concatenate((lesion, alpha_channel), axis=2)
        rgb = [(135, 75, 0), (0, 205, 255), (68, 106, 0), (45, 39, 193), (190, 173, 0),
               (176, 0, 166), (0, 104, 204), (28, 95, 62), (153, 87, 94)]
        img_ = cv2.cvtColor(np.array(img, np.uint8), cv2.COLOR_BGR2GRAY)
        for i in range(1, 10):
            cur_msk_ = np.array(np.where(img_ == i*28, 255, 0), np.uint8)
            cnts, _ = cv2.findContours(cur_msk_, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            for cnt in cnts:
                cv2.drawContours(result, [cnt], 0, rgb[i-1], 2)

        result = np.array(np.where(lesion == (255, 255, 255), (146, 234, 245), result), dtype=np.uint8)
        return result

    def __add_overlapped_segs_name(self, img, result, txt):
        img_ = cv2.cvtColor(np.array(img, np.uint8), cv2.COLOR_BGR2GRAY)
        cnts, _ = cv2.findContours(img_, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if len(cnts) > 0:
            m = cv2.moments(cnts[0])
            try:
                cx = int(m['m10'] / m['m00'])
                cy = int(m['m01'] / m['m00'])
                cv2.putText(result, txt, (cx, cy), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_8)
            except:
                pass
        return result



if __name__ == '__main__':
    warnings.filterwarnings(action='ignore')
    # INITIALIZATION
    # path_dcm = r"E:\1. Lab\Daily Results\2022\2203\0312\target\7083077 - Copy\00. DICOM\target"
    path = r"E:\1. Lab\Daily Results\2022\2203\0318\trg"
    p_save = r"E:\1. Lab\Daily Results\2022\2203\0319"

    for cur_srs in os.listdir(path):
        print(">>>>>>>>> ["+str(cur_srs)+"]")
        if os.path.isdir(os.path.join(p_save, cur_srs)):
            continue
        hss = Step2HepaticSegmentSegmentator()
        lls = LiverLesionSegmentator()
        mil = MedicalImageLoader()
        hss.set_cur_save_path(os.path.join(p_save, cur_srs))
        lls.set_cur_save_path(os.path.join(p_save, cur_srs))
        path_dcm = os.path.join(path,cur_srs, r"00. DICOM\target")
        if not os.path.isdir(os.path.join(p_save, cur_srs)):
            os.mkdir(os.path.join(p_save, cur_srs))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"cvt_img")):
            os.mkdir(os.path.join(p_save, cur_srs, r"cvt_img"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"step2")):
            os.mkdir(os.path.join(p_save, cur_srs, r"step2"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"hepatic_segs")):
            os.mkdir(os.path.join(p_save, cur_srs, r"hepatic_segs"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"imgs")):
            os.mkdir(os.path.join(p_save, cur_srs, r"imgs"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"overlapped")):
            os.mkdir(os.path.join(p_save, cur_srs, r"overlapped"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"tumors")):
            os.mkdir(os.path.join(p_save, cur_srs, r"tumors"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined1")):
            os.mkdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined1"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined1_detail")):
            os.mkdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined1_detail"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined2")):
            os.mkdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined2"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined2_detail")):
            os.mkdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined2_detail"))

        if not os.path.isdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined3")):
            os.mkdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined3"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined3_detail")):
            os.mkdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined3_detail"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined4")):
            os.mkdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined4"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined4_detail")):
            os.mkdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined4_detail"))

        # LOADING TARGET STUDY FROM LOCAL
        print("Step 1. Loading Target Study from Local")
        print("    Task . Set Path of Applied CT Study")
        mil.set_path(path_dcm)
        print("    Task . Check the Medical Image's Extension")
        mil.check_mi_type()
        print("    Task . Load Medical Images from Local")
        mil.load_medical_img()
        print("    Task . Convert Color Depth to Focus on Target Organ")
        mil.convert_color_depth()
        setMed_img = mil.get_setMed_img()   # Original Slices
        setCT_a = mil.get_setCT_a()         # Converted Slices

        hss.set_target_study(setMed_img, setCT_a)   # To receive loaded target study
        print("    Task . Segment Liver Regions")
        liver_region_segmentor = LiverRegionSegmentater()
        liver_region_segmentor.initialize(hss.cur_std_id)
        liver_region_segmentor.set_mi_type("CT")
        liver_region_segmentor.set_setCT_b(setCT_a, setMed_img)
        liver_region_segmentor.set_cur_save_path(os.path.join(p_save, cur_srs))
        liver_region_segmentor.segment_liver_regions()
        liver_region_segmentor.discard_insig_slices()

        setCT_b = liver_region_segmentor.get_setCT_b()
        setCT_b_seg = liver_region_segmentor.get_setCT_b_seg()

        # Code for Segmenting Hepatic Segments
        print("Step 2. Segmenting Hepatic Segments")
        is_srs_remained = True
        hss.set_seged_liver_regions(setCT_b_seg)            # To receive segmented liver regions
        while is_srs_remained:      # Loop for Loading Series
            print("    Task 1. Load a Series [Current Series: "+hss.list_cur_srs[hss.cur_srs_id+1]+"]")
            is_srs_remained = hss.set_target_series()       # T1. Load a Series
            print("    Task 2. Segment Hepatic Segments")
            hss.segment_hepatic_segments()                  # T2. Segment Hepatic Segments
            print("    Task 3. Refine Hepatic Segments")
            hss.refine_hepatic_segments()                   # T3. Refine Segmented Hepatic Segments
        hepatic_segments = hss.get_hepatic_segments()

        # # Code for Segmenting Liver Lesions
        # print("Step 3. Segmenting Liver lesions")
        # lls.set_target_study(setMed_img, setCT_a)   # To receive loaded target study
        # lls.set_hepatic_segments(hepatic_segments)  # To receive hepatic segments results
        # lls.set_seged_liver_regions(setCT_b_seg)    # To receive segmented liver regions
        # is_srs_remained = True
        # while is_srs_remained:  # Loop for Loading Series
        #     print("    Task 4. Load a Series [Current Series: "+lls.list_cur_srs[lls.cur_srs_id+1]+"]")
        #     is_srs_remained = lls.set_target_series()       # T4. Load a Series
        #     is_sl_remained = True
        #     while is_sl_remained:   # Loop for Loading slices
        #         print("    Task 5. Load Slice [Current Slice ID: "+str(lls.cur_sl_id+1)+"]")
        #         is_sl_remained = lls.set_target_slice()     # T5. Load Slice
        #         print("    Task 6. Segment Liver Lesion in Slice ")
        #         lls.segment_liver_lesion()                  # T6. Segment Liver Lesion
        # print("    Task 7. Refine Segment Lesions")
        # lls.refine_liver_lesions()                          # T7. Refine Segmented Lesions
        # print("    Task 8. Set Lesion Location")
        # lls.set_lesion_location()                           # T8. Set Lesion Location

