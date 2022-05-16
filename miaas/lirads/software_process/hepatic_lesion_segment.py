"""
Date: 2022. 03. 12.
Programmer: MH
Description: Code for Segmenting Hepatic Segments and Lesion
"""
import copy
import math
import os

from miaas.lirads.software_process.step_2 import LiverRegionSegmentater

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import os.path
import sys
import warnings

import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(r"E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads")
from miaas.lirads.util.hepatic_segmentator import HepaticSegmentsSegmentator
from step_1 import MedicalImageLoader
from step_3 import LesionSegmentor

plt.rcParams["figure.autolayout"] = True

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
            revised_mask = None
            for j in np.unique(detail[i]["class_ids"]): # To select unique IDs
                list_cur_id = np.where(detail[i]["class_ids"] == j)[0]  # select a result
                mask_cur = detail[i]["masks"][:,:,list_cur_id[0]]
                list_scores.append(detail[i]["scores"][list_cur_id[0]])
                list_rois.append(detail[i]["rois"][list_cur_id[0]])
                for k in list_cur_id[1:]:   # To combine segmented results for each segment ID
                    mask_cur = np.where(detail[i]["masks"][:,:,k]== True, True, mask_cur)
                if revised_mask is None:       # If the segmented hepatic segment is the first to be saved at revised_mask
                    revised_mask = mask_cur
                    revised_mask = np.reshape(revised_mask, (512, 512, 1))
                else:
                    revised_mask = np.dstack((revised_mask, mask_cur))    # To connect the current mask to the last of revised_mask
            if revised_mask is None:    # If any hepatic segment is not segmented
                revised_mask = np.array((512, 512, 1))
                revised_mask.fill(False)
            detail[i]["masks"] = revised_mask

            # To discard applied data
            detail[i]["rois"] = list_rois
            detail[i]["scores"] = list_scores
            detail[i]["class_ids"] = np.unique(detail[i]["class_ids"])

            # To generate an image expressing each hepatic segment using grayscale color
            msk = np.zeros((512, 512))
            for j in range(len(detail[i]["class_ids"])):
                msk = np.where(detail[i]["masks"][:, :, j] == True, int(detail[i]["class_ids"][j] * 28), msk)

            self.hepatic_segments_detail[self.cur_std_id][self.list_cur_srs[self.cur_srs_id]][list_keys[i]] = detail[i]
            self.hepatic_segments[self.cur_std_id][self.list_cur_srs[self.cur_srs_id]][list_keys[i]] = msk

            # To save segmented hepatic segment with each segment's name
            cv2.imwrite(os.path.join(self.path_save,r"hepatic_segs", self.list_cur_srs[self.cur_srs_id] + "_" +list_keys[i] + ".png"),
                        self.__add_seg_id_in_img(detail[i], self.target_study_cvt[self.cur_std_id][self.list_cur_srs[self.cur_srs_id]][list_keys[i]]))

        # To save each segmented hepatic segment in each slice
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

        # TACTIC 2. Remaining Hepatic Segments in Liver Region (Problem 4 in Challenge 4) (DONE) (O)
        #  To refine segmented results considering Not same Location and Shape of Liver to the results of liver segmentation
        # print("    Step 5 - TACTIC2")
        i = self.list_cur_srs[self.cur_srs_id]
        for j in list(self.setCT_b_seg[i].keys()):   # Slice
            list_new_class_ids = []
            cur_liver_seg = np.array(np.reshape(self.setCT_b_seg[i][j]["masks"], (512, 512)), np.uint8)
            cur_masks = self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"]            # List of Segmented Hepatic Segments mask
            list_cur_classes = self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"] # List of segmented Hepatic Segments ID
            msk_revised = np.zeros((512, 512))
            new_masks = None
            if len(np.unique(cur_liver_seg)) == 0:
                msk_revised = np.zeros((512, 512, 1))
                list_new_class_ids = []
                new_masks = np.zeros((512, 512, 1))
                new_masks.fill(False)
            else:
                msk_revised = self.hepatic_segments[self.cur_std_id][i][j]
                list_new_class_ids = self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]
                new_masks = self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"]

            # for idx in range(len(list_cur_classes)):
            #     cur_mask_img = np.array(np.where(cur_masks[:,:,idx]==True, 255, 0), np.uint8)
            #     overlapped_cur = np.bitwise_and(cur_liver_seg, cur_mask_img)            # To compute inclusion relationship between two segmented results
            #     if len(np.unique(overlapped_cur)) > 1:                      # If any area is overlapped
            #         list_new_class_ids.append(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"][idx])
            #         if new_masks is None:   # Case of First hepatic segment to be saved at new_masks
            #             new_masks = np.where(overlapped_cur > 0, True, False)
            #             new_masks = np.reshape(new_masks, (512, 512, 1))
            #         else:       # To save current mask to the last of new_masks (512*512*n) (n: # of stacked masks)
            #             new_masks = np.dstack((new_masks, np.where(overlapped_cur>0, True, False)))
            #         msk_revised = np.array( np.where(new_masks[:, :, -1] == True, int(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"][idx] * 28), msk_revised), np.uint8)

            # To save refined result to local
            if new_masks is None:
                new_masks = np.zeros((512, 512, 1))
                new_masks.fill(False)
                list_new_class_ids = []
            self.hepatic_segments[self.cur_std_id][i][j] = msk_revised
            self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"] = list_new_class_ids
            self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"] = new_masks
            # print(i, "    ",j,"    ", self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"].shape, len(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]))

            cv2.imwrite(os.path.join(self.path_save,r"hepatic_segs_refined1",
                                     i + "_" + j + ".png"),
                        self.__add_seg_id_in_img(self.hepatic_segments_detail[self.cur_std_id][i][j], self.target_study_cvt[self.cur_std_id][i][j]))

            # To save each section of segmented hepatic segment considering ID of hepatic segment
            if len(np.unique(msk_revised))>1:
                for k in range(1, 10):
                    if k in self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]:
                        cur_idx = np.where(np.array(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"])==k)[0][0]
                        cur_msk_select = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, cur_idx]==True, 255, 0), np.uint8)
                        cv2.imwrite(os.path.join(self.path_save, r"hepatic_segs_refined1_detail",i + "_" + j + "_"+str(k)+".png"), cur_msk_select)

        # TACTIC 4. Checking possible combinations of hepatic segments considering slice location in a series (DONE)
        # To refine segmented results considering Comparing with the possible combination of hepatic segments considering the location of a slice  (Challenge 2)
        print("    Step 5 - TACTIC4")
        i = self.list_cur_srs[self.cur_srs_id]
        for j in list(self.setCT_b_seg[i].keys()):   # Slice
            cur_masks = self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"]
            list_cur_classes = self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]
            new_masks = None
            new_classes = []

            list_discarded_ids, cls_change = self.__compute_discarded_segments(list_cur_classes, j)
            msk_revised = np.zeros((512, 512))
            # To remain the hepatic segments that can be located in the slice
            for idx in range(len(list_cur_classes)):
                cur_id = list_cur_classes[idx]
                if cur_id in list_discarded_ids:
                    continue
                new_classes.append(cur_id)
                if new_masks is None:
                    new_masks = self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:,:,idx]
                    new_masks = np.reshape(new_masks, (512, 512, 1))
                else:
                    cur_msk = self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:,:,idx]
                    cur_msk = np.reshape(cur_msk, (512, 512, 1))
                    new_masks = np.dstack((new_masks, cur_msk))
                msk_revised = np.array(np.where(new_masks[:, :, -1] == True, int(cur_id * 28), msk_revised), np.uint8)
            cv2.imwrite(os.path.join(self.path_save, r"hepatic_segs_refined2", i + "_" + j + ".png"),
                        self.__add_seg_id_in_img(self.hepatic_segments_detail[self.cur_std_id][i][j], self.target_study_cvt[self.cur_std_id][i][j]))
            self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"] = new_masks
            self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"] = new_classes

            if len(np.unique(msk_revised))>1:
                for k in range(1, 10):
                    if k in self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]:
                        cur_idx = np.where(np.array(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"])==k)[0][0]
                        cur_msk_select = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, cur_idx]==True, 255, 0), np.uint8)
                        cv2.imwrite(os.path.join(self.path_save, r"hepatic_segs_refined2_detail",i + "_" + j + "_"+str(k)+".png"), cur_msk_select)
        # TODO: To check the location of each section
        # pass

        # TACTIC 5-1. To refine segmented results considering Checking Overlapped Segmented Results (Problem 1 in Challenge 4) (DONE)  (O)
        # Case of Overlapped Hepatic Segments
        # Case 1. Overlapped Hepatic Segments that can be reflected at the slice
        # Case 2. some hepatic segments can't be reflected at the slice
        # Case 3. Overlapped Hepatic Segments that can be reflected at the slice
        # print("    Step 5 - TACTIC5-1")
        for j in list(self.setCT_b_seg[i].keys()):  # Slice
            list_cur_classes = self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]
            msk_revised = np.zeros((512, 512))
            for idx in range(len(list_cur_classes)):

                masks_cur = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, idx] == True, 255, 0), dtype=np.uint8)
                for idx_other in range(len(list_cur_classes)):
                    if idx >= idx_other:
                        continue
                    masks_oth = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, idx_other] == True, 255, 0), dtype=np.uint8)
                    overlapped = np.bitwise_and(masks_cur, masks_oth)
                    if len(np.unique(overlapped)) == 1: # Not overlapped
                        continue
                    else:
                        area_oth_remained = masks_oth - overlapped
                        self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, idx_other] = np.where(area_oth_remained>0, True, False)
                        # print("      overlapped ", i, "  ", j, "  ", idx, "  ", idx_other, "    ",  np.count_nonzero(overlapped)/np.count_nonzero(masks_cur))

                msk_revised = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, idx] == True, int(list_cur_classes[idx] * 28), msk_revised), np.uint8)
            cv2.imwrite(os.path.join(self.path_save,r"hepatic_segs_refined3",
                                     i + "_" + j + ".png"),
                        self.__add_seg_id_in_img(self.hepatic_segments_detail[self.cur_std_id][i][j], self.target_study_cvt[self.cur_std_id][i][j]))

            if len(np.unique(msk_revised))>1:
                for k in range(1, 10):
                    if k in self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]:
                        cur_idx = np.where(np.array(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"])==k)[0][0]
                        cur_msk_select = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, cur_idx]==True, 255, 0), np.uint8)
                        cv2.imwrite(os.path.join(self.path_save, r"hepatic_segs_refined3_detail",i + "_" + j + "_"+str(k)+".png"), cur_msk_select)

        # TACTIC 5-2. To refine segmented results considering Multiple Sections for A hepatic Segment (Problem 2 in Challenge 4)  (O)
        # print("    Step 5 - TACTIC5-2")
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
                        list_enough_area = np.where(np.array(area)/max(area) > 0.3)[0] # To remain the area is bigger than 30% of maximum size
                        cvt_masks = np.zeros((512, 512))
                        cvt_masks.fill(False)
                        for selected in list_enough_area:
                            select_mask = cv2.drawContours(np.zeros((512, 512)), [ctns[selected]], -1, 255, thickness=-1)
                            cvt_masks = np.array(np.where(select_mask==255, True, cvt_masks), np.uint8)
                        self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, idx] = cvt_masks

                msk_revised = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, idx] == True, int(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"][idx] * 28), msk_revised), np.uint8)
            self.hepatic_segments[self.cur_std_id][i][j] = msk_revised

            cv2.imwrite(os.path.join(self.path_save,r"hepatic_segs_refined4",
                                     i + "_" + j + ".png"),
                        self.__add_seg_id_in_img(self.hepatic_segments_detail[self.cur_std_id][i][j], self.target_study_cvt[self.cur_std_id][i][j]))

            if len(np.unique(msk_revised))>1:
                for k in range(1, 10):
                    if k in self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]:
                        cur_idx = np.where(np.array(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"])==k)[0][0]
                        cur_msk_select = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, cur_idx]==True, 255, 0), np.uint8)
                        cv2.imwrite(os.path.join(self.path_save, r"hepatic_segs_refined4_detail",i + "_" + j + "_"+str(k)+".png"), cur_msk_select)


        # TACTIC 3. Revising shape of segmented result filling segmented iver region
        # To apply dilation in OpenCV
        # print("    Step 5 - TACTIC3")
        i = self.list_cur_srs[self.cur_srs_id]
        for j in list(self.setCT_b_seg[i].keys()):  # Slice
            cur_liver_seg = np.array(np.reshape(self.setCT_b_seg[i][j]["masks"], (512, 512)), np.uint8)
            cur_masks = self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"]
            list_cur_classes = self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]
            total_area = 0

            msk_revised = np.zeros((512, 512))
            for idx in range(len(list_cur_classes)):
                cur_seg_mask = cur_masks[:,:, idx]
                total_area += np.count_nonzero(np.where(cur_masks[:,:,idx]==True, 255, 0))
                mask_remained_area = cur_liver_seg
                # cv2.imshow("Original Lesions", np.array(np.where(cur_seg_mask==True, 255, 0), dtype=np.uint8))
                for idx_others in range(len(list_cur_classes)):
                    if idx != idx_others:
                        continue
                    mask_remained_area = mask_remained_area-cur_masks[:,:,idx_others]
                # cv2.imshow("mask_remained_area", np.array(np.where(mask_remained_area>0, 255, 0), dtype=np.uint8))
                is_repeat = True
                repeat_num = 0
                cur_seg_mask_ = np.array(np.where(cur_seg_mask==True, 255, 0), np.uint8)
                while is_repeat:
                    cur_seg_mask_ = cv2.dilate(cur_seg_mask_, np.ones((3, 3), np.uint8), iterations=2)
                    cur_seg_mask = np.bitwise_and(cur_seg_mask_, mask_remained_area)
                    if repeat_num == 3:
                        break
                    repeat_num+=1

                # cv2.imshow("cur_seg_mask", np.array(np.where(cur_seg_mask>0, 255, 0), dtype=np.uint8))
                self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:,:,idx] = cur_seg_mask
                # cv2.waitKey()
                msk_revised = np.array(
                    np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, idx] == True,
                             int(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"][idx] * 28), msk_revised),
                    np.uint8)
                self.hepatic_segments[self.cur_std_id][i][j] = msk_revised
            cv2.imwrite(os.path.join(self.path_save,r"hepatic_segs_refined5",
                                     i + "_" + j + ".png"),
                        self.__add_seg_id_in_img(self.hepatic_segments_detail[self.cur_std_id][i][j], self.target_study_cvt[self.cur_std_id][i][j]))

            if len(np.unique(msk_revised))>1:
                for k in range(1, 10):
                    if k in self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]:
                        cur_idx = np.where(np.array(self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"])==k)[0][0]
                        cur_msk_select = np.array(np.where(self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:, :, cur_idx]==True, 255, 0), np.uint8)
                        cv2.imwrite(os.path.join(self.path_save, r"hepatic_segs_refined5_detail",i + "_" + j + "_"+str(k)+".png"), cur_msk_select)

            # if np.count_nonzero(cur_liver_seg) > 20000:
            #     print("    ",i,"    ",j, "    ", np.count_nonzero(cur_liver_seg), "    ", total_area, "    ", np.abs(np.count_nonzero(cur_liver_seg)-total_area))


        # TACTIC 6.
        # # TODO:  To refine segmented results considering inter-slice relationship
        # # Case 4. Checking Continuity of Each Hepatic Segment in adjacent Slices (Consider shape, location, size)
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


        # To remain a section for a hepatic segment class in a slice
        # i = self.list_cur_srs[self.cur_srs_id]
        # for j in list(self.setCT_b_seg[i].keys()):   # Slice
        #     list_cur_classes = self.hepatic_segments_detail[self.cur_std_id][i][j]["class_ids"]
        #     msk_revised = None
        #
        #     for idx in range(len(list_cur_classes)):
        #         masks = self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:,:,idx]
        #         masks = np.array(np.where(masks==True, 255, 0), np.uint8)
        #         ctns, _ = cv2.findContours(masks, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        #         max_id, max_size = 0, 0
        #         cur_msk = self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"][:,:,idx]
        #         if len(ctns)> 2:
        #             new_mask = np.zeros((512, 512))
        #             for cnt_id in range(len(ctns)):
        #                 cur_area = cv2.contourArea(ctns[cnt_id])
        #                 if cur_area > max_size:
        #                     max_id = cnt_id
        #                     max_size = cur_area
        #             select_mask = cv2.drawContours(np.zeros((512, 512)), [ctns[max_id]], -1, 255, thickness=-1)
        #             cur_msk = np.array(np.where(select_mask == 255, True, False), np.uint8)
        #         if msk_revised is None:
        #             msk_revised = cur_msk
        #             msk_revised.reshape((512, 512, 1))
        #         else:
        #             cur_msk.reshape((512, 512, 1))
        #             msk_revised = np.dstack((msk_revised, cur_msk))
        #
        #     if msk_revised is None:
        #         msk_revised = np.array((512, 512, 1))
        #         msk_revised.fill(False)
        #     self.hepatic_segments_detail[self.cur_std_id][i][j]["masks"] = msk_revised

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
                background = cv2.drawContours(background, [cnts[j]], -1, 255, thickness=-1)
            result = cv2.cvtColor(np.array(org, np.uint8), cv2.COLOR_GRAY2BGR)
        candidate_points = []       # Points for Showing segment ID
        for y in range(0, 512, 30):
            for x in range(0, 512, 30):
                if background[y, x] == 0:
                    candidate_points.append((x, y))

        rgb = [(135, 75, 0), (0, 205, 255), (68, 106, 0), (45, 39, 193), (190, 173, 0), (176, 0, 166), (0, 104, 204), (28, 95, 62), (153, 87, 94)]
        list_msks = np.array(np.where(img["masks"]==True, 255, 0), np.uint8)
        list_class = img["class_ids"]

        for i in range(len(list_class)):
            cur_class_id = list_class[i]
            cur_class_name = self.__convert_hepatic_segs([cur_class_id])[0]
            cur_msk = list_msks[:,:,i]
            ctns, _ = cv2.findContours(cur_msk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if len(ctns)==0:
                continue
            biggest_id, biggest_area = 0, 0
            for cnt_idx in range(len(ctns)):
                cv2.drawContours(result, [ctns[cnt_idx]], 0, rgb[cur_class_id-1], 2)
                if biggest_area < cv2.contourArea(ctns[cnt_idx]):
                    biggest_id = cnt_idx
                    biggest_area = cv2.contourArea(ctns[cnt_idx])
            m = cv2.moments(ctns[biggest_id])

            try:
                t_pnt = (int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"]))
            except:
                continue
            short_dist, short_id = 1000, -1
            for cp_idx in range(len(candidate_points)):
                cp = candidate_points[cp_idx]
                dst = self.__compute_dist(t_pnt, cp)
                if short_dist > dst:
                    short_dist = dst
                    short_id = cp_idx

            # set Margin for text box location
            mx, my = 0, 0  # margin
            if t_pnt[0] <= 256 and t_pnt[1] <= 256:
                mx -= 20
                my -= 20
            elif t_pnt[0] <= 256 and t_pnt[1] > 256:
                mx -= 20
                my += 20
            elif t_pnt[0] > 256 and t_pnt[1] <= 256:
                mx += 20
                my -= 20
            elif t_pnt[0] > 256 and t_pnt[1] > 256:
                mx += 20
                my -= 20
            selected_point = (candidate_points[short_id][0] + mx, candidate_points[short_id][1] + my)

            mx_txt, my_txt = mx, my
            if selected_point[1] < t_pnt[1] - 30:
                my_txt += 5
                if selected_point[0] < t_pnt[0] + 5:
                    mx_txt += 8
                else:
                    mx_txt -= 8
            elif selected_point[1] > t_pnt[1] - 30 and selected_point[1] < t_pnt[1]:
                my_txt += 5
                if selected_point[0] < t_pnt[0] + 5:
                    mx_txt += 8
                else:
                    mx_txt -= 8
            elif selected_point[1] == t_pnt[1]:
                if selected_point[0] < t_pnt[0] + 5:
                    mx_txt += 8
                else:
                    mx_txt -= 8
            elif selected_point[1] < t_pnt[1] - 30 and selected_point[1] > t_pnt[1]:
                my_txt += 5
                if selected_point[0] < t_pnt[0] + 5:
                    mx_txt += 8
                else:
                    mx_txt -= 8
            else:
                my_txt -= 5
                if selected_point[0] < t_pnt[0] + 5:
                    mx_txt += 8
                else:
                    mx_txt -= 8

            selected_point_txt_box = (candidate_points[short_id][0] + mx_txt, candidate_points[short_id][1] + my_txt)
            cv2.putText(result, cur_class_name, selected_point, cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_8)
            result = cv2.line(result, t_pnt, selected_point_txt_box, rgb[int(cur_class_id) - 1], 1, cv2.LINE_8)
            del candidate_points[short_id]
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

    def __compute_dist(self, a, b):
        ax, ay = a[0], a[1]
        bx, by = b[0], b[1]
        dist = np.sqrt((ax - bx) ** 2 + (ay - by) ** 2)
        return dist

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
        self.lesion_segmentator = LesionSegmentor()
        self.list_cur_sl = []
        self.info_lesions = {}   # {Lesion_ID#1:
                                 #      {location: None, masks: {PhaseName:{SLICEID: mask, ...}, .. }},
                                 #      ... }

        self.path_save = r""
        self.lesion_with_hep_segs = {}

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
                overlapped_cur = np.bitwise_and(cur_liver_seg, cur_liver_lesions)   # To check inclusion relationship
                cur_hep_seg_refined = np.array(np.where(overlapped_cur == 255, 255, cur_hep_seg_refined), dtype=np.uint8)
                self.liver_lesions[self.cur_std_id][i][j] = cur_hep_seg_refined
                cv2.imwrite(os.path.join(self.path_save,r"tumors_refined",
                                         i + "_" + j + ".png"),cur_hep_seg_refined)

        # Case 2. Lesion's Continuity of Location and Size in a Series

        # Case 3. Lesion's Location Synchronization Considering Inter-Series

    def locate_lesions_on_segments(self):
        """
        To measure the lesion location applying hepatic segments
        When the lesion's location is detected, the overlapped relationship is applied.
        After overlapped two images, the Class ID of hepatic segment overlapped section is applied.
        """

        for cur_phase_id in list(self.liver_lesions[self.cur_std_id].keys()):  # Phase
            self.lesion_with_hep_segs[cur_phase_id] = {}
            for cur_sl_id in list(self.liver_lesions[self.cur_std_id][cur_phase_id].keys()):    # Slice
                cur_sl_lesion = self.liver_lesions[self.cur_std_id][cur_phase_id][cur_sl_id]
                cur_sl_hep_seg = self.hepatic_segment[self.cur_std_id][cur_phase_id][cur_sl_id]
                cur_sl_hep_seg = np.reshape(cur_sl_hep_seg, (512, 512, 1))
                overlapped = np.where(cur_sl_lesion==255, cur_sl_hep_seg, 0)    # To overlap segmented lesions and hepatic segments
                overlapped_pixels = np.array(np.unique(overlapped)/28, dtype=np.uint8)  # To extract class of overlapped hepatic segments
                if len(overlapped_pixels) > 1 or (len(overlapped_pixels)==1 and overlapped_pixels[0] != 0):
                    print("      >>", cur_phase_id + "_" + cur_sl_id, ": ", overlapped_pixels, self.__convert_hepatic_segs(overlapped_pixels))
                    cur_lesion_size = self.__compute_lesion_size(cur_sl_lesion,self.target_study[self.cur_std_id][cur_phase_id][cur_sl_id]["info"]["voxel"])
                    self.lesion_with_hep_segs[cur_phase_id][len(self.lesion_with_hep_segs[cur_phase_id].keys())] = {"sl_id": cur_sl_id,
                                                                                                                    "hep_seg_ids": list(overlapped_pixels),
                                                                                                                    "size": cur_lesion_size["mass"],
                                                                                                                    "diameter": cur_lesion_size["length"]}
                else:
                    # print("      >>", cur_phase_id + "_" + cur_sl_id, ": Any Lesion Detected ")
                    pass
                cur_sl_hep_seg_rgb = cv2.cvtColor(np.array(cur_sl_hep_seg, np.uint8), cv2.COLOR_GRAY2BGR)
                cur_sl_lesion_rgb = cv2.cvtColor(np.array(cur_sl_lesion, np.uint8), cv2.COLOR_GRAY2BGR)
                result = self.__add_seg_id_in_img(cur_sl_hep_seg_rgb, cur_sl_lesion_rgb,
                                                              self.target_study_cvt[self.cur_std_id][cur_phase_id][cur_sl_id])
                result = self.__add_overlapped_segs_name(cur_sl_lesion_rgb, result, ",".join([str(x) for x in self.__convert_hepatic_segs(overlapped_pixels)]))

                cv2.imwrite(os.path.join(self.path_save,r"overlapped",
                                     cur_phase_id + "_" + cur_sl_id+"_"+",".join([str(x) for x in overlapped_pixels]) + ".png"), result)

    def visualize(self):
        """
        To visualize statistics of the relationship between hepatic segments and lesions
        """
        dict_num_lesions_per_hepatic_segs = {}  # Dict for # of lesions per hepatic segment
        dict_hepatic_segs_per_lesions = {}      # Dict for hepatic segments per Lesions
        dict_size_n_volume_per_lesions = {}     # Dict for size and volumes per Lesions
        dict_configu_per_hepatic_segs = {}      # Dict for configuration per hepatic segments

        for cur_phase_id in list(self.lesion_with_hep_segs.keys()):     # Phase
            dict_num_lesions_per_hepatic_segs[cur_phase_id] = {"Hepatic Segment":["# of Lesions"],"1":[0], "2":[0], "3":[0], "4a":[0], "4b":[0], "5":[0], "6":[0], "7":[0], "8":[0], "Total":[0]}
            dict_hepatic_segs_per_lesions[cur_phase_id] = {"Lesion ID (Slice ID)": [], "Hepatic Segments":[]}
            dict_size_n_volume_per_lesions[cur_phase_id] = {"Lesion ID (Slice ID)": [], "Diameter (mm)":[], "Area (mm^2)":[]}
            dict_configu_per_hepatic_segs[cur_phase_id] = {"Hepatic Segment":["# of Lesions", "Total Area"],"1":[0,0], "2":[0,0], "3":[0,0], "4a":[0,0], "4b":[0,0], "5":[0,0], "6":[0,0], "7":[0,0], "8":[0,0]}

            for lesion_id in list(self.lesion_with_hep_segs[cur_phase_id].keys()):    # Lesion
                cur_sl_id = self.lesion_with_hep_segs[cur_phase_id][lesion_id]["sl_id"]
                hep_seg_ids = self.lesion_with_hep_segs[cur_phase_id][lesion_id]["hep_seg_ids"]
                size = self.lesion_with_hep_segs[cur_phase_id][lesion_id]["size"]
                diameter = self.lesion_with_hep_segs[cur_phase_id][lesion_id]["diameter"]
                for hsi in hep_seg_ids: # Hepatic Segments for a lesion (lesion_id)
                    if hsi == 0:        # To skip ID for background
                        continue

                    # To count the number lesions of on hepatic segments
                    dict_num_lesions_per_hepatic_segs[cur_phase_id][list(dict_num_lesions_per_hepatic_segs[cur_phase_id].keys())[hsi]][0]+=1
                    dict_num_lesions_per_hepatic_segs[cur_phase_id]["Total"][0]+=1

                    # To count the number lesions of on hepatic segments
                    dict_configu_per_hepatic_segs[cur_phase_id][list(dict_configu_per_hepatic_segs[cur_phase_id].keys())[hsi]][0]+=1
                    dict_configu_per_hepatic_segs[cur_phase_id][list(dict_configu_per_hepatic_segs[cur_phase_id].keys())[hsi]][1]+=size

                # To get hepatic segments for each lesion in a slice
                dict_hepatic_segs_per_lesions[cur_phase_id]["Lesion ID (Slice ID)"].append(str(lesion_id+1)+" ("+cur_sl_id+")")
                dict_hepatic_segs_per_lesions[cur_phase_id]["Hepatic Segments"].append(",".join(self.__convert_hepatic_segs(hep_seg_ids)))

                # To get physical size for each lesion in a slice
                dict_size_n_volume_per_lesions[cur_phase_id]["Lesion ID (Slice ID)"].append(str(lesion_id+1)+" ("+cur_sl_id+")")
                dict_size_n_volume_per_lesions[cur_phase_id]["Diameter (mm)"].append(diameter)
                dict_size_n_volume_per_lesions[cur_phase_id]["Area (mm^2)"].append(size)

            # To convert dictionary data to dataframe data
            pd_dict_num_lesions_per_hepatic_segs_cur =pd.DataFrame.from_dict(dict_num_lesions_per_hepatic_segs[cur_phase_id])
            pd_dict_hepatic_segs_per_lesions_cur =pd.DataFrame.from_dict(dict_hepatic_segs_per_lesions[cur_phase_id])
            pd_dict_size_n_volume_per_lesions_cur =pd.DataFrame.from_dict(dict_size_n_volume_per_lesions[cur_phase_id])

            print("\n\n\n<<"+cur_phase_id+">>")
            print("[Number of Lesions per Hepatic Segments]")
            print(pd_dict_num_lesions_per_hepatic_segs_cur.to_string(index=False))  # To print table for # of lesions per hepatic segments

            print("\n\n[Located Hepatic Segments per Lesions]")
            print(pd_dict_hepatic_segs_per_lesions_cur.to_string(index=False))      # To print table for hepatic segments per lesions

            print("\n\n[Physical Sizes per Lesions]")
            print(pd_dict_size_n_volume_per_lesions_cur.to_string(index=False))     #

            pd_dict_configu_per_hepatic_segs_cur = pd.DataFrame.from_dict(dict_configu_per_hepatic_segs[cur_phase_id])
            fig, ax = plt.subplots()
            print(pd_dict_configu_per_hepatic_segs_cur.columns[0])
            print(pd_dict_configu_per_hepatic_segs_cur.iloc[0, 1:10])
            print(pd_dict_configu_per_hepatic_segs_cur.iloc[1, 1:10])
            ax.set_xlabel("Hepatic Segments", fontsize=14)
            ax.bar(["1", "2", "3","4a","4b", "5", "6", "7", "8"], pd_dict_configu_per_hepatic_segs_cur.iloc[0, 1:10], color="seagreen")
            ax.set_ylabel("# of Lesions", color="seagreen", fontsize=14)

            ax2 = ax.twinx()
            ax2.plot(["1", "2", "3","4a","4b", "5", "6", "7", "8"], pd_dict_configu_per_hepatic_segs_cur.iloc[1, 1:10], color="orangered", marker="o")
            ax2.set_ylabel("Total Area (mm^2)", color="orangered", fontsize=14)
            plt.show()

    def compute_diameter(self, ):
        pass

    def __convert_hepatic_segs(self, list_id):
        """
        To convert hepatic segments' class id to hepatic segment name (Roman Textual Name)
        """
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
                        mass = cv2.contourArea(cnt)*voxel
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


if __name__ == '__main__':
    warnings.filterwarnings(action='ignore')
    # INITIALIZATION
    # path_dcm = r"E:\1. Lab\Daily Results\2022\2203\0312\target\7083077 - Copy\00. DICOM\target"
    path = r"E:\1. Lab\Daily Results\2022\2203\0318\trg"
    p_save = r"E:\1. Lab\Daily Results\2022\2203\0323"
    cur_srs = "7083077_10302013"
    for cur_srs in os.listdir(path):
        print("["+str(cur_srs)+"]")

        if int(cur_srs) < 18:
            continue
        # if os.path.isdir(os.path.join(p_save, cur_srs)):
        #     continue
        hss = Step2HepaticSegmentSegmentator()
        liver_region_segmentor = LiverRegionSegmentater()
        lls = LiverLesionSegmentator()
        mil = MedicalImageLoader()

        hss.set_cur_save_path(os.path.join(p_save, cur_srs))
        lls.set_cur_save_path(os.path.join(p_save, cur_srs))
        liver_region_segmentor.set_cur_save_path(os.path.join(p_save, cur_srs))
        liver_region_segmentor.initialize(hss.cur_std_id)
        liver_region_segmentor.set_mi_type("CT")

        # To make folders to save each step's result
        path_dcm = os.path.join(path, cur_srs, r"00. DICOM\target")
        if not os.path.isdir(os.path.join(p_save, cur_srs)):
            os.mkdir(os.path.join(p_save, cur_srs))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"cvt_img")):
            os.mkdir(os.path.join(p_save, cur_srs, r"cvt_img"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"step2")):
            os.mkdir(os.path.join(p_save, cur_srs, r"step2"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"step2_refined")):
            os.mkdir(os.path.join(p_save, cur_srs, r"step2_refined"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"hepatic_segs")):
            os.mkdir(os.path.join(p_save, cur_srs, r"hepatic_segs"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"imgs")):
            os.mkdir(os.path.join(p_save, cur_srs, r"imgs"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"overlapped")):
            os.mkdir(os.path.join(p_save, cur_srs, r"overlapped"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"tumors")):
            os.mkdir(os.path.join(p_save, cur_srs, r"tumors"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"tumors_refined")):
            os.mkdir(os.path.join(p_save, cur_srs, r"tumors_refined"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"hepatic_segs_detail")):
            os.mkdir(os.path.join(p_save, cur_srs, r"hepatic_segs_detail"))
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
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined5")):
            os.mkdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined5"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined5_detail")):
            os.mkdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined5_detail"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined6")):
            os.mkdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined6"))
        if not os.path.isdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined6_detail")):
            os.mkdir(os.path.join(p_save, cur_srs, r"hepatic_segs_refined6_detail"))

        # LOADING TARGET STUDY FROM LOCAL
        print("Section 1. Segmenting Liver Regions")
        # Step 1. Load a medical images from local
        print("    Step 1. Load a Medical Image")
        mil.set_path(path_dcm)              # To set path of applied CT study
        mil.check_mi_type()                 # To check the medical image's extension
        mil.load_medical_img()              # To load medical images from local
        mil.convert_color_depth()           # To convert color depth to focus on target organ
        setMed_img = mil.get_setMed_img()   # Original Slices
        setCT_a = mil.get_setCT_a()         # Converted Slices

        hss.set_target_study(setMed_img, setCT_a)   # To receive loaded target study
        # Step 2. segment liver regions on loaded slices
        print("    Step 2. Segment Liver Regions")
        liver_region_segmentor.set_setCT_b(setCT_a, setMed_img)     # set loaded medical images (converted and original)
        liver_region_segmentor.segment_liver_regions()              # To segment liver region in the whole input series

        # Step 3. refine segmented liver regions
        print("    Step 3. Refine Segmented Liver Regions")
        liver_region_segmentor.discard_insig_slices()               # To discard insignificant slices
                                                                    # To consider continuity of liver's  appearance, size, location, shape, HU value in a series
        setCT_b_seg = liver_region_segmentor.get_setCT_b_seg()      # To get refined result

        # Code for Segmenting Hepatic Segments
        print("Section 2. Segmenting Hepatic Segments")
        is_srs_remained = True
        hss.set_seged_liver_regions(setCT_b_seg)            # To receive segmented liver regions
        while is_srs_remained:      # Loop for Loading Series
            is_srs_remained = hss.set_target_series()       # To load a series
            # Step 4. segment hepatic segments in whole slices of each series
            print("    Step 4. Segment Hepatic Segments  [Current Series: "+hss.list_cur_srs[hss.cur_srs_id+1]+"]")
            hss.segment_hepatic_segments()                  # To segment hepatic segments
            # Step 5. refine segmented hepatic segments applying segmented result for a series
            print("    Step 5. Refine Segmented Hepatic Segments  [Current Series: "+hss.list_cur_srs[hss.cur_srs_id+1]+"]")
            hss.refine_hepatic_segments()                   # To refine segmented hepatic segments
        hepatic_segments = hss.get_hepatic_segments()       # To get refined result

        # # # Code for Segmenting Liver Lesions
        # print("Section 3. Segmenting Liver lesions")
        # lls.set_target_study(setMed_img, setCT_a)   # To receive loaded medical images (converted and original)
        # lls.set_hepatic_segments(hepatic_segments)  # To receive hepatic segments results
        # lls.set_seged_liver_regions(setCT_b_seg)    # To receive segmented liver regions
        # is_srs_remained = True
        # # Step 6. Segment liver lesions in whole slices
        # while is_srs_remained:  # Loop for Loading Series
        #     is_srs_remained = lls.set_target_series()       # To load a series
        #     is_sl_remained = True
        #     print("    Step 6. Segment Liver Lesion in Slice ")
        #     while is_sl_remained:   # Loop for Loading slices
        #         is_sl_remained = lls.set_target_slice()     # To load slice
        #         lls.segment_liver_lesion()                  # To segment liver lesion
        # # Step 7. Refine segment lesions
        # print("    Step 7. Refine Segment Lesions")
        # lls.refine_liver_lesions()                          # To refine segmented lesions
        # # Step 8. locate lesions on segments
        # print("    Step 8. Locate Lesions on Segments")
        # lls.locate_lesions_on_segments()                           # To set lesion location based on hepatic segments
        # # Step 9. Visualize Results
        # print("    Task 9. Visualize")
        # lls.visualize()                           # To visualize the statistics