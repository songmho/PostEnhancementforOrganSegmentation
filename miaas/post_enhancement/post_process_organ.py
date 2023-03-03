"""
Date: 2021. 11. 15.
Programmer: MH
Description: Code for detecting and enhancing organ segmentation results for 5 features
"""
import copy
import random
import cv2
import os
import numpy as np
import nibabel as nib
from miaas.utils.slice_similarity_measurer import SimilarityMeasurer
from miaas.utils.performance_measurement import ImgDataPerformanceMeasurer


class MedImageEnhancer:
    def __init__(self, display_result=False):
        self.seg_similarity_measurer = SimilarityMeasurer()
        self.seg_similarity_measurer.prepare_model()
        self.path_cmp_organ_imgs = r"E:\2. Project\Python\HighPerformedOrganSegmentation\targets\liver\dataset 1"
        self.wc, self.ww = 40, 400
        self.th_location = 0.3
        self.th_size = 0.75
        self.th_size_diff = 0.80
        self.th_shape = 0.95
        self.th_size_seq = 0.50
        self.th_shape_seq = 0.80
        self.th_hu = 1.3
        self.th_diff = 0.2
        self.th_trg_sls = 5
        self.th_grvt = 30
        self.img_visualizer = ImageVisualizer()
        self.display_result = display_result
        self.sequences = []
        self.num_slices = 0
    def get_hu_scale(self):
        return self.wc-self.ww/2, self.wc+self.ww/2

    def get_num_slices(self):
        return self.num_slices

    # METHOD 1. Method for Refining Appearance Violation
    def refine_appearance_violation(self, display=False):
        """
        To detect and refine appearance violation between sequences
        :return:
        """
        refined_seqs = []   # List for Refined sequences
        cur_ref_seqs = {"type": True, "data": []}   # Current refined sequences
        if display:
            sequences_before = copy.deepcopy(self.sequences)   # list of sequences for displaying data before enhancement

        for id in range(len(self.sequences)):   # Loop for Sequences
            # print(">> ", id)
            if self.sequences[id]["type"]:      # If the organ is in the segmentation results
                if id > 1:   # Normal Case
                    # To load required slices and their segmentation results
                    # Data in previous true sequence's last slice
                    lst_seg = self.sequences[id-2]["data"][-1]["img"]
                    lst_max_id = self.__get_maximum_size_sl_id(self.sequences[id-2]["data"])
                    lst_max_seg = self.sequences[id-2]["data"][lst_max_id]["img"]
                    diff_lst_rate = (np.count_nonzero(lst_seg) - np.count_nonzero(lst_max_seg)) / np.count_nonzero(lst_max_seg)

                    # Data in current true sequence's first slice
                    fir_seg = self.sequences[id]["data"][0]["img"]
                    nxt_max_id = self.__get_maximum_size_sl_id(self.sequences[id]["data"])
                    nxt_max_seg = self.sequences[id]["data"][nxt_max_id]["img"]
                    diff_nxt_rate = (np.count_nonzero(fir_seg) - np.count_nonzero(nxt_max_seg)) / np.count_nonzero(nxt_max_seg)

                    num_between = len(self.sequences[id-1]["data"])     # Number of slices in the false sequence
                    fir_seg_size = np.count_nonzero(fir_seg)
                    lst_seg_size = np.count_nonzero(lst_seg)

                    prd_fir_seg_size = lst_seg_size * (
                            1 + diff_lst_rate) ** num_between  # predicted organ size in the first slice
                    prd_lst_seg_size = fir_seg_size * (
                            1 + diff_nxt_rate) ** num_between  # predicted organ size in the last slice
                    # Criterion 1. Consider the number of slices whose seg. results don't contain organ.
                    # Criterion 2. Size difference comparing predicted size and real size in first and last slices' organ
                    # print("    ", diff_nxt_rate, "    ", diff_lst_rate, "    ", round((fir_seg_size - prd_fir_seg_size)/prd_fir_seg_size,4), "    ", round((lst_seg_size - prd_lst_seg_size)/prd_lst_seg_size,4), "    ", prd_fir_seg_size,"    ", prd_lst_seg_size )
                    is_continued = False
                    if (num_between < int(len(self.srs_seg_sl)*0.05)) and np.abs(prd_fir_seg_size - fir_seg_size)/fir_seg_size < self.th_diff and np.abs(prd_lst_seg_size - lst_seg_size)/lst_seg_size < self.th_diff:
                        is_continued = True
                    # Inclusion Relationship
                    elif np.any(np.bitwise_and(fir_seg, lst_seg) > 0) and num_between < int(0.05*len(self.srs_seg_sl)):
                        is_continued = True

                    if is_continued:        # If they need to connect --> proceed with generating segmentation results for false sequence
                        # To manage false sequence
                        if len(cur_ref_seqs["data"]) > 0:    # if any sequence in the cur_ref_seqs
                            # To select last slice's info in previous true sequence
                            last_img = self.srs_org_sl[cur_ref_seqs["data"][-1]["id"]]["img"]
                            last_seg = cur_ref_seqs["data"][-1]["img"]
                            for i in range(len(self.sequences[id-1]["data"])):  # To repeat whole slices in false sequence
                                cur_seg = self.sequences[id-1]["data"][i]["img"]
                                cur_img = self.srs_org_sl[self.sequences[id-1]["data"][i]["id"]]["img"]
                                last_seg = self.__revise_sl(last_seg, cur_seg,None, last_img, cur_img, None)   # To generate segmentation result considering previous data
                                cur_ref_seqs["data"].append({"id":self.sequences[id-1]["data"][i]["id"], "img":last_seg})   # To save the data
                                last_img = cur_img
                        else:       # If any sequence is not in cur_ref_seqs (no applied sequence located in previous )
                            # To select first slice's info in current true sequence
                            nxt_img = self.srs_org_sl[self.sequences[id]["data"][0]["id"]]["img"]
                            nxt_seg = self.sequences[id]["data"][0]["img"]
                            list_reverse = []
                            for i in range(len(self.sequences[id-1]["data"]), 0, -1):    # To repeat whole slices in false sequence (reverse)
                                cur_seg = self.sequences[id-1]["data"][i]["img"]
                                cur_img = self.srs_org_sl[self.sequences[id-1]["data"][i]["id"]]["img"]
                                nxt_seg = self.__revise_sl(None, cur_seg, nxt_seg, None, cur_img, nxt_img)  # To generate segmentation result considering next data
                                list_reverse.append({"id": self.sequences[id-1]["data"][i]["id"], "img": nxt_seg})    # To gather data in buffer
                                nxt_img = cur_img
                            list_reverse.reverse()  # To set correct order
                            for i in list_reverse:  # To save generated data to cur_ref_seqs
                                cur_ref_seqs["data"].append(i)
                        for i in self.sequences[id]["data"]:    # To add current true sequence's data to cur_ref_seqs
                            cur_ref_seqs["data"].append(i)
                    else:                   # If don't need to connect
                        refined_seqs.append(cur_ref_seqs)   # To put gathered data to refined_seqs
                        refined_seqs.append(self.sequences[id-1])
                        cur_ref_seqs = self.sequences[id]

                else:   # Case for the first and second sequences
                    if id == 0: # If the true sequence is first sequence
                        cur_ref_seqs = self.sequences[0]
                    else: # If the true sequence is second sequence
                        refined_seqs.append(self.sequences[0])  # To add first false sequence to refined list
                        cur_ref_seqs = self.sequences[1]
            else:   # If the sequence is false sequence
                if id == len(self.sequences)-1: # when the sequence is the last sequence
                    refined_seqs.append(cur_ref_seqs)   # To add current refined sequence to the list "refined_seqs"
                    cur_ref_seqs = self.sequences[id]   # To set the current sequence to cur_ref_seqs
        if len(cur_ref_seqs["data"]) > 0:   # if current refined sequences is remained not appending the refined_seqs
            refined_seqs.append(cur_ref_seqs)
        self.sequences = copy.deepcopy(refined_seqs)
        self.__move_empty_to_false_seq()    # To reorganize segmentation results
        if display: # If display is true, display the method's result
            displayer = ImageVisualizer()
            displayer.set_sequences(sequences_before, self.sequences)  # To set the sequences before and after enhancing
            displayer.visualize()   # To visualize enhancement results

        if self.display_result:
            self.img_visualizer.set_imgs_appear(self.sequences) # To set current sequence for appearance results

    def __compute_avg_grvt(self, list_grvt):
        avg_x, avg_y = 0, 0
        for x, y in list_grvt:
            avg_x += x
            avg_y += y
        return avg_x/len(list_grvt), avg_y/len(list_grvt)


    # METHOD 2. Method for Refining Location Violation
    def refine_location_violation(self, display=False):
        """
        Method for detecting and refining location violation in each sequence
        :return:
        """
        if display:
            sequences_before = copy.deepcopy(self.sequences)   # list of sequences for displaying data before enhancement
        # To detect and refine the violation of segmentation result in slice
        for id in range(len(self.sequences)): # Loop for sequences
            if self.sequences[id]["type"]:  # If the sequence contain the organ
                cur_seq = self.sequences[id]["data"]

                big_id = self.__get_maximum_size_sl_id(cur_seq)
                # slice and seg. result for next slice
                nxt_seg = cur_seq[big_id]["img"]
                nxt_img = self.srs_org_sl[big_id]["img"]
                list_grvt = [self.compute_gravity(nxt_seg)]
                for sl_id in range(big_id-1, -1, -1):    # Loop for slices containing segmented organs  From biggest to 0 (Decreasing Size)
                    # slice and seg. result for previous slice
                    if sl_id > 0:
                        prv_seg = self.sequences[id]["data"][sl_id-1]["img"]
                        prv_img = self.srs_org_sl[cur_seq[sl_id-1]["id"]]["img"]
                    else:
                        prv_img = None
                        prv_seg = None

                    # slice and seg. result for current slice
                    cur_seg = self.sequences[id]["data"][sl_id]["img"]
                    cur_img = self.srs_org_sl[cur_seq[sl_id]["id"]]["img"]

                    # To compute inclusion relationship and overlapped rate
                    is_contain_prv, is_contain_nxt = self.__compute_inclusion(prv_seg, cur_seg, nxt_seg)
                    if nxt_seg is not None:
                        overlapped_rate_nxt = self.__compute_overlapped_rate(nxt_seg, cur_seg)
                    # # Case 1. (prv false & nxt true) or (th_location > prv overlapped and th_location < nxt overlapped) --> revise considering prv
                    # if (prv_seg is not None) and ((not is_contain_prv and is_contain_nxt) or overlapped_rate_prv < self.th_location):
                    #     self.sequences[id]["data"][sl_id]["img"] = self.__revise_sl(prv_seg, cur_seg, None, prv_img, cur_img, None)
                    cur_grv = self.compute_gravity(cur_seg)
                    avg_x, avg_y = self.__compute_avg_grvt(list_grvt)

                    # Case 2. (prv true & nxt false) or (th_location < prv overlapped and th_location > nxt overlapped) --> revise considering next
                    if (nxt_seg is not None) and ((not is_contain_nxt or self.th_location > overlapped_rate_nxt) \
                            or not (avg_x-self.th_grvt < cur_grv[0] < avg_x+self.th_grvt and avg_y-self.th_grvt < cur_grv[1] < avg_y+self.th_grvt)):
                        self.sequences[id]["data"][sl_id]["img"] = self.__revise_sl(None, cur_seg, nxt_seg, None, cur_img, nxt_img)

                    if len(list_grvt) >= self.th_trg_sls:
                        del list_grvt[0]
                    list_grvt.append(cur_grv)

                    # # Case 3. both false --> revising considering both
                    # elif (prv_seg is not None and nxt_seg is not None) and (not (is_contain_prv or is_contain_nxt) or \
                    #         (self.th_location < overlapped_rate_prv and self.th_location < overlapped_rate_nxt)):
                    #     self.sequences[id]["data"][sl_id]["img"] = self.__revise_sl(prv_seg, cur_seg, nxt_seg, prv_img, cur_img, nxt_img)
                    nxt_seg = self.sequences[id]["data"][sl_id]["img"]
                    nxt_img = cur_img

                # slice and seg. result for next slice
                prv_seg = cur_seq[big_id]["img"]
                prv_img = self.srs_org_sl[big_id]["img"]
                for sl_id in range(big_id, len(cur_seq)):  # Loop for slices containing segmented organs  From biggest to 0 (Decreasing Size)
                    # slice and seg. result for previous slice
                    if sl_id+1 < len(cur_seq):
                        nxt_seg = self.sequences[id]["data"][sl_id+1]["img"]
                        nxt_img = self.srs_org_sl[sl_id+1]["img"]
                    else:
                        prv_img = None
                        prv_seg = None

                    # slice and seg. result for current slice
                    cur_seg = self.sequences[id]["data"][sl_id]["img"]
                    cur_img = self.srs_org_sl[cur_seq[sl_id]["id"]]["img"]

                    # To compute inclusion relationship and overlapped rate
                    is_contain_prv, is_contain_nxt = self.__compute_inclusion(prv_seg, cur_seg, nxt_seg)
                    if prv_seg is not None:
                        overlapped_rate_prv = self.__compute_overlapped_rate(prv_seg, cur_seg)
                    # if nxt_seg is not None:
                    #     overlapped_rate_nxt = self.__compute_overlapped_rate(nxt_seg, cur_seg)
                    cur_grv = self.compute_gravity(cur_seg)
                    avg_x, avg_y = self.__compute_avg_grvt(list_grvt)
                    # Case 0. no mid-point
                    if cur_grv == (-1, -1):
                        self.sequences[id]["data"][sl_id]["img"] = self.__revise_sl(prv_seg, cur_seg, nxt_seg, prv_img, cur_img, nxt_img)
                    # Case 1. (prv false & nxt true) or (th_location > prv overlapped and th_location < nxt overlapped) --> revise considering prv
                    if (prv_seg is not None) and ((not is_contain_prv or overlapped_rate_prv < self.th_location)\
                            or not (avg_x-self.th_grvt < cur_grv[0] < avg_x+self.th_grvt and avg_y-self.th_grvt < cur_grv[1] < avg_y+self.th_grvt)):
                        self.sequences[id]["data"][sl_id]["img"] = self.__revise_sl(prv_seg, cur_seg, None, prv_img,
                                                                                    cur_img, None)
                    if len(list_grvt) >= self.th_trg_sls:
                        del list_grvt[0]
                    list_grvt.append(cur_grv)

                    # # Case 2. (prv true & nxt false) or (th_location < prv overlapped and th_location > nxt overlapped) --> revise considering next
                    # elif (nxt_seg is not None) and (
                    #         (is_contain_prv and not is_contain_nxt) or self.th_location > overlapped_rate_nxt):
                    #     self.sequences[id]["data"][sl_id]["img"] = self.__revise_sl(None, cur_seg, nxt_seg, None,
                    #                                                                 cur_img, nxt_img)
                    #
                    # # Case 3. both false --> revising considering both
                    # elif (prv_seg is not None and nxt_seg is not None) and (
                    #         not (is_contain_prv or is_contain_nxt) or \
                    #         (self.th_location < overlapped_rate_prv and self.th_location < overlapped_rate_nxt)):
                    #     self.sequences[id]["data"][sl_id]["img"] = self.__revise_sl(prv_seg, cur_seg, nxt_seg,
                    #                                                                 prv_img, cur_img, nxt_img)
                    prv_seg = self.sequences[id]["data"][sl_id]["img"]
                    prv_img = cur_img

        self.__move_empty_to_false_seq()  # To reorganize segmentation results
        if display: # If display is true, display the method's result
            displayer = ImageVisualizer()
            displayer.set_sequences(sequences_before, self.sequences)  # To set the sequences before and after enhancing
            displayer.visualize()   # To visualize enhancement results

        if self.display_result:
            self.img_visualizer.set_imgs_location(self.sequences) # To set current sequence for location results

    # METHOD 3. Method for Refining Organ Size Violation
    def refine_size_violation(self, display=False):
        """
        To detect and refine size violation in slices on the each sequence
        :return:
        """
        if display:
            sequences_before = copy.deepcopy(self.sequences)   # list of sequences for displaying data before enhancement
        # To detect and refine size violation from the slice containing the biggest seg. organ to the first and the last slices
        for id in range(len(self.sequences)): # Loop for sequences
            if self.sequences[id]["type"]:  # If the sequence contain the organ
                cur_seq = self.sequences[id]["data"]

                # To check violation from the biggest slice
                big_id = self.__get_maximum_size_sl_id(cur_seq)
                seg_big = self.sequences[id]["data"][big_id]["img"]
                size_seg_big = np.count_nonzero(seg_big)

                for i in range(big_id-1, -1, -1):    # From biggest to 0 (Decreasing Size)
                    # Size of segmentation results
                    size_seg_org = np.count_nonzero(self.sequences[id]["data"][i]["img"])
                    size_seg_nxt = np.count_nonzero(self.sequences[id]["data"][i+1]["img"])
                    size_seg_overlapped = np.count_nonzero(np.bitwise_and(self.sequences[id]["data"][i]["img"], self.sequences[id]["data"][i+1]["img"]))
                    # difference
                    if size_seg_nxt > 0:
                        diff_cur_nxt = (size_seg_nxt - size_seg_overlapped) / size_seg_nxt
                    else:
                        diff_cur_nxt = -1
                    # slice and seg. result for current slice
                    cur_img = self.srs_org_sl[self.sequences[id]["data"][i]["id"]]["img"]
                    cur_seg = self.sequences[id]["data"][i]["img"]

                    # slice and seg. result for next slice
                    nxt_img = self.srs_org_sl[self.sequences[id]["data"][i+1]["id"]]["img"]
                    nxt_seg = self.sequences[id]["data"][i+1]["img"]
                    if i == big_id-1:
                        diff_enhanced = -1  # Decreased
                    else:
                        diff_enhanced = np.sign((size_seg_nxt-size_seg_big)/size_seg_big)   # negative is correct
                    diff_current = np.sign((size_seg_org-size_seg_big)/size_seg_big)   # negative is correct
                    flow_diff = diff_enhanced*diff_current
                    if i > big_id - self.th_trg_sls-1:   # not enough to generate slide
                        trg_end_id = big_id
                        trg_start_id = i+1
                        if trg_start_id == trg_end_id:  # Case of big_id -1
                            diff_rate_slide = self.th_size_diff
                            trg_area = np.count_nonzero(self.srs_org_sl[self.sequences[id]["data"][trg_end_id]["id"]]["img"])
                        else:
                            size_trg_end = np.count_nonzero(self.srs_org_sl[self.sequences[id]["data"][trg_end_id]["id"]]["img"])
                            size_trg_start = np.count_nonzero(self.srs_org_sl[self.sequences[id]["data"][trg_start_id]["id"]]["img"])
                            diff_rate_slide = (size_trg_start - size_trg_end)/ size_trg_end
                            trg_area = np.count_nonzero(self.srs_org_sl[self.sequences[id]["data"][trg_end_id]["id"]]["img"])
                    else:
                        trg_end_id = i+self.th_trg_sls
                        trg_start_id = i+1
                        size_trg_end = np.count_nonzero(self.srs_org_sl[self.sequences[id]["data"][trg_end_id]["id"]]["img"])
                        size_trg_start = np.count_nonzero(self.srs_org_sl[self.sequences[id]["data"][trg_start_id]["id"]]["img"])
                        trg_area = np.count_nonzero(self.srs_org_sl[self.sequences[id]["data"][trg_end_id]["id"]]["img"])
                        diff_rate_slide = (size_trg_start - size_trg_end)/ size_trg_end
                    area_prd = trg_area*(1+diff_rate_slide)

                    size_diff = (area_prd - np.count_nonzero(cur_seg))/area_prd

                    """
                    CRITERIA 1. the size difference is not same  
                    CRITERIA 2. Same difference & high difference than threshold
                    """
                    require_refine = False

                    if not flow_diff:   # If the sequence's flow is not correct
                        require_refine = True
                    else:
                        if size_diff < self.th_size_diff-0.35*((big_id-i)/big_id):
                            require_refine = True
                    if not require_refine:
                        if self.__compute_overlapped_rate(cur_seg, nxt_seg) < 0.35:  # Location also is checked
                            require_refine = True
                        else:
                            require_refine = False
                    # if np.sign(diff_cur_nxt) != 1:    # prv-> cur, cur->nxt must be increased (applying threshold)
                    #     require_refine = True
                    # # elif np.abs(diff_cur_nxt) < self.th_size_diff-0.3*((big_id-i)/big_id):
                    # elif self.__compute_overlapped_rate(cur_seg, nxt_seg) < self.th_size_diff-0.25*((big_id-i)/big_id):
                    # # elif self.__compute_overlapped_rate(cur_seg, nxt_seg) < 0.75:
                    #     require_refine = True
                    if require_refine:  # If the case of requiring refinement
                        self.sequences[id]["data"][i]["img"] = self.__revise_sl(None, cur_seg, nxt_seg, None, cur_img, nxt_img)

                # To check violation from the biggest slice
                big_id = self.__get_maximum_size_sl_id(cur_seq)
                seg_big = self.sequences[id]["data"][big_id]["img"]
                size_seg_big = np.count_nonzero(seg_big)
                for i in range(big_id+1, len(cur_seq)):   # From biggest to 0 (Decreasing Size )
                    # To compute size
                    size_seg_org = np.count_nonzero(self.sequences[id]["data"][i]["img"])
                    size_seg_prv = np.count_nonzero(self.sequences[id]["data"][i-1]["img"])
                    size_seg_overlapped = np.count_nonzero(np.bitwise_and(self.sequences[id]["data"][i]["img"], self.sequences[id]["data"][i-1]["img"]))

                    # To compute difference of segmentation results from  different sl
                    if size_seg_prv > 0:
                        diff_prv_cur = (size_seg_prv - size_seg_org) / size_seg_prv
                        diff_rate = (size_seg_prv-size_seg_overlapped)/ size_seg_prv
                    else:
                        diff_prv_cur = -1
                        diff_rate = 0
                    # To load previous slice information
                    prv_seg = self.sequences[id]["data"][i-1]["img"]   # Segmentation result
                    prv_img = self.srs_org_sl[cur_seq[i-1]["id"]]["img"]    # Slice

                    # To load current slice information
                    cur_img = self.srs_org_sl[cur_seq[i-1]["id"]]["img"]
                    cur_seg = self.sequences[id]["data"][i]["img"]

                    if i == big_id+1:
                        diff_enhanced = -1
                    else:
                        diff_enhanced = np.sign((size_seg_prv-size_seg_big)/size_seg_big)
                    diff_current = np.sign((size_seg_prv-size_seg_big)/size_seg_big)
                    flow_diff = diff_enhanced*diff_current

                    if i < big_id + self.th_trg_sls:   # not enough to generate slide
                        trg_end_id = big_id
                        trg_start_id = i-1
                        if trg_start_id == trg_end_id:  # Case of big_id -1
                            diff_rate_slide = self.th_size_diff
                            trg_area = np.count_nonzero(self.srs_org_sl[self.sequences[id]["data"][trg_end_id]["id"]]["img"])
                        else:
                            size_trg_end = np.count_nonzero(self.srs_org_sl[self.sequences[id]["data"][trg_end_id]["id"]]["img"])
                            size_trg_start = np.count_nonzero(self.srs_org_sl[self.sequences[id]["data"][trg_start_id]["id"]]["img"])
                            diff_rate_slide = (size_trg_start - size_trg_end) / size_trg_end
                            trg_area = np.count_nonzero(self.srs_org_sl[self.sequences[id]["data"][trg_end_id]["id"]]["img"])
                    else:
                        trg_end_id = i-self.th_trg_sls
                        trg_start_id = i-1
                        size_trg_end = np.count_nonzero(self.srs_org_sl[self.sequences[id]["data"][trg_end_id]["id"]]["img"])
                        size_trg_start = np.count_nonzero(self.srs_org_sl[self.sequences[id]["data"][trg_start_id]["id"]]["img"])
                        trg_area = np.count_nonzero(self.srs_org_sl[self.sequences[id]["data"][trg_end_id]["id"]]["img"])
                        diff_rate_slide = (size_trg_start - size_trg_end)/ size_trg_end
                    area_prd = trg_area*(1+diff_rate_slide)

                    size_diff = (area_prd - np.count_nonzero(cur_seg))/area_prd
                    """
                    CRITERIA 1. the size difference is not same  
                    CRITERIA 2. Same difference & high difference than threshold
                    """
                    require_refine = False

                    if not flow_diff:   # If the sequence's flow is not correct
                        require_refine = True
                    else:
                        if size_diff < self.th_size_diff-0.25*((len(cur_seq)-i)/len(cur_seq)):
                            require_refine = True
                    if not require_refine:
                        if self.__compute_overlapped_rate(cur_seg, prv_seg) < 0.3:  # Location also is checked
                            require_refine = True
                        else:
                            require_refine = False

                    # require_refine = False
                    # if self.__compute_overlapped_rate(cur_seg, prv_seg) < 0.3:
                    #     require_refine = True
                    # if np.sign(diff_prv_cur) != 1:    # prv-> cur, cur->nxt must be increased (sign is 1). but the case is different sign
                    #     require_refine = True
                    # # elif np.abs(diff_prv_cur) < self.th_size_diff-0.3*((i-big_id)/(len(cur_seq)-big_id)):
                    # elif np.abs( self.__compute_overlapped_rate(cur_seg, prv_seg)) < self.th_size_diff-0.25*((i-big_id)/(len(cur_seq)-big_id)):
                    # # elif np.abs( self.__compute_overlapped_rate(cur_seg, prv_seg)) < 0.75:
                    #     require_refine = True

                    if require_refine:  # If the case of requiring refinement
                        self.sequences[id]["data"][i]["img"] = self.__revise_sl(prv_seg, cur_seg, None, prv_img, cur_img,None)   # To refine the segmentation result

        self.__move_empty_to_false_seq()  # To reorganize segmentation results
        if display: # If display is true, display the method's result
            displayer = ImageVisualizer()
            displayer.set_sequences(sequences_before, self.sequences)  # To set the sequences before and after enhancing
            displayer.visualize()   # To visualize enhancement results

        if self.display_result:
            self.img_visualizer.set_imgs_size(self.sequences) # To set current sequence for size results

    # METHOD 4. Method for Refining Organ Shape Violation
    def refine_shape_violation(self, display=False):
        """
        To detect and refine shape violation in slices on the each sequence
        :return:
        """
        if display:
            sequences_before = copy.deepcopy(self.sequences)   # list of sequences for displaying data before enhancement
        # To remove sequence considering the shape of organ in label data
        list_cmp = self.__select_compared_seg_organ_data()  # To load reference masks for the organ (Applied training set)
        list_remove_seqs = []
        for id in range(len(self.sequences)):   # Loop for sequence
            if len(self.sequences[id]["data"]) < int(len(self.srs_org_sl)*0.1): # If the number of slices is lower than 10% of the whole slices
                list_remove_seqs.append(id)
                continue
            if self.sequences[id]["type"]:      # If current sequence is true
                cur_seq = self.sequences[id]["data"]
                max_id = self.__get_maximum_size_sl_id(cur_seq)     # To select the biggest organ in sequence
                trg_img = cur_seq[max_id]["img"]
                list_dist = []
                list_diff = []
                for cmp in list_cmp:    # To compute similarity and size difference for whole ref. masks
                    similar, diff = self.__compute_similarity_difference(cmp, trg_img)    # to compute similarity and size difference
                    list_diff.append(diff)
                    list_dist.append(similar)

                if np.average(list_dist) < self.th_shape_seq and np.average(list_diff) < self.th_size_seq:  # if the averages are higher or lower than threshold
                    list_remove_seqs.append(id)     # To save the sequence id for clearing
        # To clear selected sequence
        for i in list_remove_seqs:
            self.sequences[i] = self.__clear_sequence(self.sequences[i])    # To generate false sequence

        # To detect and refine violated slice in each sequence
        for id in range(len(self.sequences)):    # Loop for sequences
            if self.sequences[id]["type"]:  # If the sequence contain the organ
                cur_seq = self.sequences[id]["data"]
                big_id = self.__get_maximum_size_sl_id(cur_seq)
                list_similarity = []
                for sl_id in range(big_id-1, -1, -1):    # From biggest to 0 (Decreasing Size)
                    # To load current slice information
                    cur_seg =  self.sequences[id]["data"][sl_id]["img"]
                    cur_img = self.srs_org_sl[cur_seq[sl_id]["id"]]["img"]

                    # To load next slice information
                    if sl_id < len(cur_seq)-1:
                        nxt_seg = self.sequences[id]["data"][sl_id+1]["img"]
                        nxt_img = self.srs_org_sl[cur_seq[sl_id+1]["id"]]["img"]
                    else:
                        nxt_seg = None
                        nxt_img = None

                    if nxt_seg is not None: # Excepting last sequence
                        cur_seg_cvt = cv2.cvtColor(cur_seg, cv2.COLOR_GRAY2BGR)
                        nxt_seg_cvt = cv2.cvtColor(nxt_seg, cv2.COLOR_GRAY2BGR)
                        diff_cur_nxt = self.seg_similarity_measurer.compute_distance(cur_seg_cvt, nxt_seg_cvt)  # To compute similarity
                        rate_similar_cur_nxt = 1/(1+diff_cur_nxt)
                    else:
                        rate_similar_cur_nxt = 0.0

                    # # TODO Need to add to check Size difference
                    if nxt_seg is not None and (rate_similar_cur_nxt < self.th_shape or (len(list_similarity)>5 and np.average(list_similarity)-0.3 > rate_similar_cur_nxt)):  # low similarity for only next slice
                        self.sequences[id]["data"][sl_id]["img"] = self.__revise_sl(None, cur_seg, nxt_seg, None, cur_img, nxt_img)

                    if len(list_similarity) > 5:
                        del list_similarity[0]
                    list_similarity.append(rate_similar_cur_nxt)

                for sl_id in range(big_id + 1, len(cur_seq)):  # From biggest to 0 (Decreasing Size)
                    if sl_id > 0:  # from second sequence
                        # To load previous slice information
                        prv_seg = self.sequences[id]["data"][sl_id - 1]["img"]
                        prv_img = self.srs_org_sl[cur_seq[sl_id - 1]["id"]]["img"]
                    else:
                        prv_seg = None
                        prv_img = None

                    # To load current slice information
                    cur_seg = self.sequences[id]["data"][sl_id]["img"]
                    cur_img = self.srs_org_sl[cur_seq[sl_id]["id"]]["img"]

                    if prv_seg is not None: # excepting first sequence
                        prv_seg_cvt = cv2.cvtColor(prv_seg, cv2.COLOR_GRAY2BGR)
                        cur_seg_cvt = cv2.cvtColor(cur_seg, cv2.COLOR_GRAY2BGR)
                        diff_prv_cur = self.seg_similarity_measurer.compute_distance(prv_seg_cvt, cur_seg_cvt)  # To compute similarity
                        rate_similar_prv_cur = 1/(1+diff_prv_cur)
                    else:
                        rate_similar_prv_cur = 0.0
                    # TODO Need to add to check Size difference
                    if prv_seg is not None and (rate_similar_prv_cur < self.th_shape or (len(list_similarity)>5 and np.average(list_similarity)-0.3 > rate_similar_prv_cur)): # low similarity for only previous slice
                        self.sequences[id]["data"][sl_id]["img"] = self.__revise_sl(prv_seg, cur_seg, None, prv_img, cur_img, None)
                    if len(list_similarity) > 5:
                        del list_similarity[0]
                    list_similarity.append(rate_similar_prv_cur)

        self.__move_empty_to_false_seq()  # To reorganize segmentation results
        if display: # If display is true, display the method's result
            displayer = ImageVisualizer()
            displayer.set_sequences(sequences_before, self.sequences)  # To set the sequences before and after enhancing
            displayer.visualize()   # To visualize enhancement results

        if self.display_result:
            self.img_visualizer.set_imgs_shape(self.sequences) # To set current sequence for shape results

    # METHOD 5. Method for Refining HU Scale Violation
    def refine_HU_scale_violation(self, display=False):
        """
        To detect and refine shape violation in slices on the each sequence
        :return:
        """

        if display:
            sequences_before = copy.deepcopy(self.sequences)   # list of sequences for displaying data before enhancement
        # To remove the sequence containing different HU scales
        maxs, mins = [], []
        list_remove_seqs = []
        for id in range(len(self.sequences)):   # Loop for sequence
            if self.sequences[id]["type"]:  # If the sequence contain the organ
                # To compute the sequence's HU scale
                for sl_id in range(len(self.sequences[id]["data"])):
                    cur_sl_org = self.srs_org_mi[:, :, sl_id]   # Original Slice
                    cur_seg = self.sequences[id]["data"][sl_id]["img"]
                    img2 = self.__extract_seg_area_with_slice(cur_sl_org, cur_seg)  # To extract segmentation result from original slice
                    if len(img2)>0:  # To extract minimum and maximum values
                        maxs.append(np.max(img2))
                        mins.append(np.min(img2))
            if (np.average(maxs) < (self.wc-self.ww/2) or (self.wc+self.ww/2) < np.average(mins)):  # To check the seg's HU scale is correct
                # TODO [for Improving] :  Not only range but also Frequency of Values
                list_remove_seqs.append(id) # If not correct, it will be removed
            maxs, mins = [], []
        for i in list_remove_seqs:  # To clear whole target sequence to remove
            self.sequences[i] = self.__clear_sequence(self.sequences[i])
        count = 0
        for id in range(len(self.sequences)):
            if self.sequences[id]["type"]:
                count+= 1

        # To remove the sections of segmentation results
        for id in range(len(self.sequences)):    # Loop for sequences
            if self.sequences[id]["type"]:  # If the sequence contain the organ
                cur_seq = self.sequences[id]["data"]
                for sl_id in range(len(cur_seq)):  # Loop for slices containing segmented organs
                    cur_sections = self.__divide_sections(cur_seq[sl_id]["img"])    # To divide sections
                    cur_sl_org = self.srs_org_mi[:, :, sl_id]
                    list_remove = []
                    for cur_sct_id in range(len(cur_sections)): # Loop for sections of current slice's seg.result.
                        img2 = self.__extract_seg_area_with_slice(cur_sl_org, cur_sections[cur_sct_id]) # To select overlapped area with segmented section
                        if (np.max(img2) < (self.wc - self.ww / 2) * self.th_hu or (self.wc + self.ww / 2) * self.th_hu < np.min(img2)):
                            # If the HU scale is different to the organ
                            list_remove.append(cur_sct_id)
                    list_remove.reverse()
                    for i in list_remove:   # To remove sections showing different HU scale in the slice
                        del cur_sections[i]
                    # To combine sections for applying the mask of the slice
                    mask = np.zeros((512, 512))
                    for c in cur_sections:  # Loop for Remained Sections
                        mask += c           # To combine them
                    mask[mask >= 255] = 255
                    mask[mask < 255] = 0
                    self.sequences[id]["data"][sl_id]["img"] = mask  # To change data to refined slice

        self.__move_empty_to_false_seq()  # To reorganize segmentation results
        if display: # If display is true, display the method's result
            displayer = ImageVisualizer()
            displayer.set_sequences(sequences_before, self.sequences)  # To set the sequences before and after enhancing
            displayer.visualize()   # To visualize enhancement results

        if self.display_result:
            self.img_visualizer.set_imgs_hu(self.sequences) # To set current sequence for HU scale results

    def compute_gravity(self, msk):
        """
        Method for computing the center of gravity
        :param msk: ndarray, mask
        :return: center of gravity
        """

        cnts,_ = cv2.findContours(msk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        max_cnt = []
        max_area = 0
        for cnt in cnts:
            area = cv2.contourArea(cnt)
            if max_area < area:
                max_area = area
                max_cnt = cnt
        try:
            M = cv2.moments(max_cnt)
            cx = int(M['m10']/M["m00"])
            cy = int(M['m01']/M["m00"])
        except:
            return (-1, -1)
        return (cx, cy)

    def set_file_path(self, path_org_mi, path_org_sl, path_seg_result, path_save):
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

    def load_med_imgs(self):
        """
        To load segmentation results
        :return:
        """
        # To load original medical image series (nii format)
        self.srs_org_mi = nib.load(self.path_org_mi)            # 3dimensional array (x, y, # of Slices)
        self.srs_org_mi = self.srs_org_mi.get_fdata()            #  To select only image data

        # TO load slice images
        # TODO: To change to the code for encoding medical image data
        list_fname = os.listdir(os.path.join(self.path_org_sl))
        for i in range(len(list_fname)):
            img = cv2.imread(os.path.join(self.path_org_sl, list_fname[i]))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.srs_org_sl.append({"id": i, "img": img})       # [{"id": id, "img":img}, {"id":, "img": }, ...]
        self.img_visualizer.set_imgs_org(self.srs_org_sl)

        # To load segmentation results
        list_fname = os.listdir(os.path.join(self.path_seg_result))
        for i in range(len(list_fname)):
            img = cv2.imread(os.path.join(self.path_seg_result, list_fname[i]))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.srs_seg_sl.append({"id": i, "img": img})       # [{"id": id, "img":img}, {"id":, "img": }, ...]
            self.num_slices += 1

        list_fname = os.listdir(os.path.join(self.path_org_label))
        labels = []
        for i in range(len(list_fname)):
            img = cv2.imread(os.path.join(self.path_org_label, list_fname[i]))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            labels.append({"id": i, "img": img})       # [{"id": id, "img":img}, {"id":, "img": }, ...]
        self.img_visualizer.set_imgs_label(labels)

    def generate_sequences(self):
        """
        To generate sequences applying segmentation results
        :return:
        """
        self.sequences = []
        cur_seq = {"type": False, "data": []}
        for i in self.srs_seg_sl:   # Loop for whole slices (Segmentation Results)
            id = i["id"]
            img = i["img"]
            if len(cur_seq["data"]) == 0:   # If any data is not inserted
                cur_seq["type"] = (np.count_nonzero(img) > 0)
                cur_seq["data"].append(i)
            else:                           # If at least one seg data is inserted
                if cur_seq["type"] == (np.count_nonzero(img) > 0):  # If cur seg data is same to type of sequence
                    cur_seq["data"].append(i)
                else:                                               # If cur seg data is not same to type of sequence
                    self.sequences.append(cur_seq)
                    cur_seq = {"type": (np.count_nonzero(img) > 0), "data": [i, ]}

        if len(cur_seq["data"]) > 0:    # If current sequence is not empty
            self.sequences.append(cur_seq)

        if self.display_result:
            self.img_visualizer.set_imgs_seg(self.sequences) # To set current sequence for original sequence

    def save_segmentations(self, postfix=None):
        """
        To save sequence to the local
        :return:
        """
        path_save = self.path_save
        if postfix is not None: # If the target sequence is the result of each method
            path_save =os.path.join(path_save, postfix)
            if not os.path.isdir(path_save):
                os.mkdir(path_save)

        # To load slice from sequences
        max_seq, max_id = 0, -1
        for id in range(len(self.sequences)):
            cur_seq = self.sequences[id]["data"]
            if self.sequences[id]["type"] and len(cur_seq)> max_seq:
                max_seq = len(cur_seq)
                max_id = id

        for id in range(len(self.sequences)):
            cur_seq = self.sequences[id]["data"]
            if id == max_id:
                for sl_id in range(len(cur_seq)):
                    img = cur_seq[sl_id]["img"]
                    cv2.imwrite(os.path.join(path_save, str(cur_seq[sl_id]["id"]).zfill(5) + ".png"), img=img)
            else:
                for sl_id in range(len(cur_seq)):
                    img = cur_seq[sl_id]["img"]
                    cv2.imwrite(os.path.join(path_save, str(cur_seq[sl_id]["id"]).zfill(5) + ".png"), img=np.zeros(img.shape))

        if self.display_result:
            self.img_visualizer.set_imgs_result(self.sequences)
            self.img_visualizer.visualize_total_results()

    def save_sequences(self, postfix=None):
        path_save = self.path_save
        if postfix is not None: # If the target sequence is the result of each method
            path_save =os.path.join(path_save, postfix)
            if not os.path.isdir(path_save):
                os.mkdir(path_save)

        # To load slice from sequences
        for id in range(len(self.sequences)):
            if not os.path.isdir(os.path.join(path_save, str(id))):
                os.mkdir(os.path.join(path_save, str(id)))
            cur_seq = self.sequences[id]["data"]
            for sl_id in range(len(cur_seq)):
                img = cur_seq[sl_id]["img"]
                cv2.imwrite(os.path.join(path_save, str(id), str(cur_seq[sl_id]["id"]).zfill(5)+".png"), img=img)

    def __revise_sl(self, prv_seg, cur_seg, nxt_seg, prv_img, cur_img, nxt_img):
        """
        TO revise segmentation results considering adjacent slices
        :return:
        """
        new_mask = np.zeros((512, 512))
        print(type(prv_seg), type(cur_seg), type(nxt_seg), type(prv_img), type(cur_img), type(nxt_img))
        if prv_seg is None:
            # Case of previous slice is None --> Apply next slice data (Re-selecting position and Erosion)
            range_mask = np.bitwise_and(nxt_seg, nxt_img)
            range_mask = np.unique(range_mask)  # To select the range of  segmented area's grayscale in next slice
            range_mask = np.delete(range_mask, 0)
            print(">>> CASE 1 MIN MAX: ", range_mask)
            if len(range_mask)>0:
                range_mask = (min(range_mask), max(range_mask))

                overlapped = np.bitwise_and(nxt_seg, cur_img)    # To overlap current slice and previous segmentation
                new_mask = np.where((overlapped >= range_mask[0]) & (overlapped <= range_mask[1]), 255, 0)
            else:
                new_mask = nxt_seg
            # TODO [for Improving]: add Erosion code
        elif nxt_seg is None:
            # Case of Next slice is None --> Apply previous slice data (Re-Selecting position and Dilation)
            range_mask = np.bitwise_and(prv_seg, prv_img)
            range_mask = np.unique(range_mask)  # To select the range of  segmented area's grayscale in next slice
            range_mask = np.delete(range_mask, 0)
            print(">>> CASE 2 MIN MAX: ", range_mask)
            if len(range_mask)>0:
                range_mask = (min(range_mask), max(range_mask))

                overlapped = np.bitwise_and(prv_seg, cur_img)    # To overlap current slice and previous segmentation
                new_mask = np.where((overlapped >= range_mask[0]) & (overlapped <= range_mask[1]), 255, 0)
            else:
                new_mask = prv_seg
            # TODO [for Improving]: add Dilation code

        if prv_seg is not None and nxt_seg is not None:
            # Case of Previous and Next slices are None --> apply both slices data
            range_mask = np.bitwise_and(prv_seg, prv_img)
            range_mask = np.unique(range_mask)  # To select the range of  segmented area's grayscale in next slice
            range_mask = np.delete(range_mask, 0)
            print(">>> MIN MAX: ", range_mask)
            range_mask = (min(range_mask), max(range_mask))

            overlapped = np.bitwise_and(prv_seg, cur_img)    # To overlap current slice and previous segmentation
            new_mask = np.where((overlapped >= range_mask[0]) & (overlapped <= range_mask[1]), 255, 0)
        return np.array(new_mask, dtype=np.uint8)

    def __move_empty_to_false_seq(self):
        """
        To move segmentation results not containing anything located in true sequence to false sequence
        :return:
        """
        # Case of Empty slice in the middle
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
                else:                                   # If current sequence is true
                    for sl_id in range(len(self.sequences[seq_id]["data"])):    # To check empty slice
                        if np.count_nonzero(self.sequences[seq_id]["data"][sl_id]["img"])>0:    # If not empty
                                if not refined_sequence[-1]["type"]:    # If the last seq is for false sequence
                                    refined_sequence.append({"type": True, "data": []})
                                refined_sequence[-1]["data"].append(self.sequences[seq_id]["data"][sl_id])
                        else:       # If empty
                            if refined_sequence[-1]["type"]:    # If the last seq is for true sequence
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
            if cur_seq["type"]: # If the sequence contain segmentation results
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
                            self.sequences[seq_id-1]["data"].append(self.sequences[seq_id]["data"][0])
                        del self.sequences[seq_id]["data"][0]
                    else:
                        break
                while True:
                    if len(self.sequences[seq_id]["data"]) == 0:
                        removed_seq_id.append(seq_id)
                        break
                    if np.count_nonzero(cur_seq["data"][-1]["img"]) == 0:
                        # To check the length of current sequence
                        if seq_id+1 == seq_size:
                            # To generate new sequence
                            if len(self.sequences) == seq_size:
                                self.sequences.append({"type": False, "data": []})
                            self.sequences[seq_id+1]["data"].append(self.sequences[seq_id]["data"][-1])
                        else:
                            self.sequences[seq_id+1]["data"].append(self.sequences[seq_id]["data"][-1])
                        del self.sequences[seq_id]["data"][-1]
                    else:
                        break
        removed_seq_id.reverse()

        for i in removed_seq_id:
            if i+1 != len(self.sequences) and i!=0:
                # To combine adjacent sequence after the sequence is removed.
                for j in self.sequences[i+1]["data"]:
                    self.sequences[i-1]["data"].append(j)
                del self.sequences[i+1]
                del self.sequences[i]
            else:
                del self.sequences[i]

        if need_to_add_first:
            self.sequences.insert(0, {"type": False, "data": data})

    def __compute_similarity_difference(self, trg_mask, cur_mask):
        """
        To compute similarity of segmented results
        :param trg_mask: ndarray, masked organ from label data
        :param cur_mask: ndarray, segmentation result of slice
        :return:
        """
        trg_mask = cv2.cvtColor(trg_mask, cv2.COLOR_GRAY2BGR)
        cur_mask = cv2.cvtColor(cur_mask, cv2.COLOR_GRAY2BGR)
        distance = self.seg_similarity_measurer.compute_distance(trg_mask, cur_mask)    # To apply similarity computation model
        diff = np.inf
        if np.count_nonzero(trg_mask) != 0:
            diff = np.count_nonzero(cur_mask)/np.count_nonzero(trg_mask)    # To compute difference
        return distance, diff

    def __select_compared_seg_organ_data(self):
        list_f_name = os.listdir(self.path_cmp_organ_imgs)
        random.shuffle(list_f_name)
        list_result = []
        for i in list_f_name:   #  images
            cur_img = cv2.imread(os.path.join(self.path_cmp_organ_imgs, i)) # To load image
            cur_img = cv2.cvtColor(cur_img, cv2.COLOR_BGR2GRAY)
            list_result.append(cur_img) # To gather images
        return list_result

    def __clear_sequence(self, seq):
        """
        To modify input true sequence to false sequence
        :param seq:
        :return:
        """
        seq["type"] = False # To set type to false because the sequence is set to false
        for i in range(len(seq["data"])):   # To repeat slices
            seq["data"][i]["img"] = np.zeros((512, 512))    # To make empty seg. result
        return seq

    def __extract_seg_area_with_slice(self, sl, cur_seg):
        """
        To extract segmentation area with slice in medical image
        :param sl: np, slice in medical image
        :param cur_seg: np, segmentation result
        :return:
        """
        cur_seg = np.where(cur_seg>0, 1, np.inf)    # To convert 255 to 1 (for multiplication)
        img = np.multiply(sl, cur_seg)              # To multiply mask and original slice info
        result = img[(img > -np.inf) & (img < np.inf)]  # To select values among valid value range

        # # To consider frequency
        # unique_values = list(set(result))
        # th_num = int(len(unique_values)*0.05)
        # unique_values = unique_values[th_num:len(unique_values)-th_num]
        # frq = {x:result.count(x) for x in result}
        #
        return result

    def __divide_sections(self, cur_sl):
        """
        To divide sections of a segmentation result
        :param cur_sl: ndarray, segmentation result
        :return:list, each section of segmentation result
        """
        list_result = []
        cur_sl = np.array(cur_sl, dtype=np.uint8)   # To convert the data type in input slice
        cur_cnt, _ = cv2.findContours(cur_sl, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)   # To find contours in the input segmentation result
        for i in cur_cnt:   # To repeat the found contours
            new_mask = np.zeros(cur_sl.shape)
            list_result.append(np.array(cv2.drawContours(new_mask, [i], -1, color=255, thickness=cv2.FILLED), dtype=np.uint8))  # To save seg. sections
        return list_result

    def __get_maximum_size_sl_id(self, seq):
        """
        To get maximum size of sl and return the id of the slice
        :param seq: list, a sequence
        :return: int sl id
        """
        big_id, size = -1, -1   # Initialize
        for sl_id in range(len(seq)):   # Loop for whole slices in input sequence
            sl = seq[sl_id]
            if np.count_nonzero(sl["img"]) > size:  # if segmentation result's size in current sl is bigger than prev. biggest size
                big_id = sl_id                      # change
                size = np.count_nonzero(sl["img"])
        return big_id

    def __compute_inclusion(self, prv_sl, cur_sl, nxt_sl):
        """
        To compute inclusion relationship between input images
        :param prv_sl: ndarray, previous slice's segmentation result
        :param cur_sl: ndarray, current slice's segmentation result
        :param nxt_sl: ndarray, next slice's segmentation result
        :return: set, (bool, bool), whether included or not comparing previous and next
        """
        # To change None values to empty images
        if prv_sl is None:      # if previous slice is None
            prv_sl = np.zeros((512, 512))
        if nxt_sl is None:      # if next slice is None
            nxt_sl = np.zeros((512, 512))
        # To convert numerical values to boolean
        prv_sl_bool = np.where(prv_sl > 0, True, False)
        cur_sl_bool = np.where(cur_sl > 0, True, False)
        nxt_sl_bool = np.where(nxt_sl > 0, True, False)

        is_include_prv = np.any(np.bitwise_and(cur_sl_bool, nxt_sl_bool) == True)   # True for any pixel is overlapped between current and next
        is_include_nxt = np.any(np.bitwise_and(cur_sl_bool, prv_sl_bool) == True)   # True for any pixel is overlapped between current and previous
        return is_include_prv, is_include_nxt

    def __compute_overlapped_rate(self, sl_src, sl_trg):
        """
        To compute overlapped area's rate
        :param sl_trg: segmented organ for target slice
        :param sl_src: segmented organ for source slice
        :return: float
        """
        num_area_src = np.count_nonzero(sl_src)         # Number of pixels in source slice
        num_area_trg = np.count_nonzero(sl_trg)         # Number of pixels in source slice
        num_area_overlap = np.count_nonzero(np.bitwise_and(sl_trg, sl_src)) # Number of pixels in overlapped area
        if num_area_trg!=0:
            return num_area_overlap / num_area_trg
        else:
            return 0


class ImageVisualizer:
    """
    Class for Segmentation Display Results
    """
    def __init__(self):
        self.imgs_before = []
        self.imgs_after = []

        self.imgs_orgs = []
        self.imgs_labels = []
        self.imgs_segs = []
        self.imgs_appear = []
        self.imgs_location = []
        self.imgs_size = []
        self.imgs_shape = []
        self.imgs_hu = []
        self.imgs_results = []
        self.performance = ImgDataPerformanceMeasurer()

    def set_sequences(self, img_before, img_after):
        """
        To set image data to visualize
        :param img_before: list, images before enhancing
        :param img_after:  list, images after enhancing
        :return: None
        """
        self.imgs_before = []
        self.imgs_after = []
        for i_before in img_before:    # extracting images in before enhancing
            for j_before in i_before["data"]:
                self.imgs_before.append(j_before["img"])

        for i_after in img_after:    # extracting images in after enhancing
            for j_after in i_after["data"]:
                self.imgs_after.append(j_after["img"])

    def set_imgs_label(self, img_org):
        """
        To set list for original slices
        :param img_appear:
        :return:
        """
        for i in img_org:    # extracting imgs
            self.imgs_labels.append(i["img"])

    def set_imgs_org(self, img_org):
        """
        To set list for original slices
        :param img_appear:
        :return:
        """
        for i in img_org:    # extracting imgs
            self.imgs_orgs.append(i["img"])

    def set_imgs_seg(self, img_org):
        """
        To set list for original slices
        :param img_appear:
        :return:
        """
        for i in img_org:    # extracting imgs
            for j in i["data"]:
                self.imgs_segs.append(j["img"])

    def set_imgs_appear(self, img_appear):
        """
        To set list for enhanced slices considering appearance
        :param img_appear:
        :return:
        """
        for i in img_appear:    # extracting images in before enhancing
            for j in i["data"]:
                self.imgs_appear.append(j["img"])

    def set_imgs_location(self, img_location):
        """
        To set list for enhanced slices considering appearance
        :param img_appear:
        :return:
        """
        for i in img_location:    # extracting images in before enhancing
            for j in i["data"]:
                self.imgs_location.append(j["img"])

    def set_imgs_size(self, img_size):
        """
        To set list for enhanced slices considering appearance
        :param img_appear:
        :return:
        """
        for i in img_size:    # extracting images in before enhancing
            for j in i["data"]:
                self.imgs_size.append(j["img"])

    def set_imgs_shape(self, img_shape):
        """
        To set list for enhanced slices considering appearance
        :param img_appear:
        :return:
        """
        for i in img_shape:    # extracting images in before enhancing
            for j in i["data"]:
                self.imgs_shape.append(j["img"])

    def set_imgs_hu(self, img_hu):
        """
        To set list for enhanced slices considering appearance
        :param img_appear:
        :return:
        """
        for i in img_hu:    # extracting images in before enhancing
            for j in i["data"]:
                self.imgs_hu.append(j["img"])

    def set_imgs_result(self, img_hu):
        """
        To set list for enhanced slices considering appearance
        :param img_appear:
        :return:
        """
        for i in img_hu:    # extracting images in before enhancing
            for j in i["data"]:
                self.imgs_results.append(j["img"])

    def visualize(self):
        """
        To visualize images
        :return:
        """
        for i in range(len(self.imgs_before)):  # To repeat whole slice data
            img_before = self.imgs_before[i]
            img_after = self.imgs_after[i]
            img_concat_horizontal = np.hstack((img_before, img_after))  # To concatenate segmentation results in before and after
            cv2.putText(img_concat_horizontal, "Original SL ID:"+str(i), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(img_concat_horizontal, "Enhanced SL ID:"+str(i), (532, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow("Display", img_concat_horizontal)
            cv2.waitKey(100)

    def visualize_total_results(self):
        """
        To visualize total results from each method
        :return:
        """
        dsize = (400, 400)
        for i in range(len(self.imgs_size)):    # To repeat the whole slice data
            img_org = cv2.resize(self.imgs_orgs[i], dsize=dsize, interpolation=cv2.INTER_AREA)
            # img_org = np.zeros((400, 400))
            img_label = cv2.resize(self.imgs_labels[i], dsize=dsize, interpolation=cv2.INTER_AREA)
            img_seg = cv2.resize(self.imgs_segs[i], dsize=dsize, interpolation=cv2.INTER_AREA)
            img_result = cv2.resize(self.imgs_results[i], dsize=dsize, interpolation=cv2.INTER_AREA)
            img_appearance = cv2.resize(self.imgs_appear[i], dsize=dsize, interpolation=cv2.INTER_AREA)
            img_location = cv2.resize(self.imgs_location[i], dsize=dsize, interpolation=cv2.INTER_AREA)
            img_size = cv2.resize(self.imgs_size[i], dsize=dsize, interpolation=cv2.INTER_AREA)
            img_shape = cv2.resize(self.imgs_shape[i], dsize=dsize, interpolation=cv2.INTER_AREA)
            img_hu = cv2.resize(self.imgs_hu[i], dsize=dsize, interpolation=cv2.INTER_AREA)

            img_concat_horz_1 = np.hstack((img_org.astype(np.float64)/255.0, img_label, img_seg, img_result, np.zeros(dsize)))  # Slice, Label, Seg. Result, Enhance Result, EMPTY
            img_concat_horz_2 = np.hstack((img_appearance, img_location, img_size, img_shape, img_hu))  # Appearance, location, size, shape, hu
            result = np.vstack((img_concat_horz_1, img_concat_horz_2))
            # result = (result*255).astype(np.uint8)
            cv2.putText(result, "[Slice] SL ID:"+str(i), (20, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(result, "[Label]", (420, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(result, "[Seg. Result]", (820, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(result, "[Enh. Result]", (1220, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_AA)
            dsc_seg = round(self.performance.compute_dsc(img_label, img_seg.astype(np.uint8)),3)
            dsc_enh = round(self.performance.compute_dsc(img_label, img_result.astype(np.uint8)),3)
            if dsc_seg == -1:
                dsc_seg = "Empty"
            if dsc_enh == -1:
                dsc_enh = "Empty"
            cv2.putText(result, "[Performance]", (1620, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(result, "  DSC of Seg.: "+str(dsc_seg), (1620, 60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(result, "  DSC of enh.: "+str(dsc_enh), (1620, 90), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_AA)

            cv2.putText(result, "[Appearance]", (20, 430), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(result, "[Location]", (420, 430), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(result, "[Size]", (820, 430), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(result, "[Shape]", (1220, 430), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(result, "[HU Scale]", (1620, 430), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_AA)

            cv2.line(result, (400, 0), (400, 800), (255, 255, 255), 1)
            cv2.line(result, (800, 0), (800, 800), (255, 255, 255), 1)
            cv2.line(result, (1200, 0), (1200, 800), (255, 255, 255), 1)
            cv2.line(result, (1600, 0), (1600, 800), (255, 255, 255), 1)
            cv2.line(result, (0, 400), (2000, 400), (255, 255, 255), 1)
            cv2.imshow("Result", result)
            if i==0 or np.count_nonzero(img_label)>0:
                cv2.waitKey()
            else:
                cv2.waitKey(100)

    def visualize_series_comparison(self):
        """
        To visualize enhanced results and segmentation results for a series
        :return:
        """


if __name__ == '__main__':
    display = False
    path_seg_result = r"F:\Daily Results\2021\2107\0723\HAWK-1 Dataset 1\Dataset 1"  # Path of Segmentation Results
    path_org_sl = r"D:\Dataset\Liver TUmor Dataset (Medical Decathlon)\images_Training"  # Path of Original Slices (###/###_SLNUM.png)
    path_org_mi = r"D:\Dataset\Liver TUmor Dataset (Medical Decathlon)\imagesTr"  # Path of Original Medical Image (liver_#.nii)
    path_save = r"F:\Daily Results\2021\2111\1123\result"  # Path to save results
    path_org_label = r"D:\Dataset\Liver TUmor Dataset (Medical Decathlon)\labels\liver"  # Path to save results
    pe = MedImageEnhancer(display_result=display)
    trg_srs_id = 1  # Target Series ID (LITS Based. 0~130)
    # for trg_srs_id in [22, 40, 49, 55, 57, 65, 83, 87, 104, 108, 114, 115]:
    # for trg_srs_id in [0, 2, 8, 10, 21, 22, 31, 34, 39, 40 ,42, 46, 49, 51]:
    for trg_srs_id in range(131):
        if trg_srs_id !=4:
            continue
    # for trg_srs_id in range(131):
        # Step 1. Initialize Locations for CT series and their segmentation results
        print("\n\nCurrent Series ID: ", trg_srs_id)
        cur_path_seg_result = os.path.join(path_seg_result, str(trg_srs_id).zfill(3))
        cur_path_org_sl = os.path.join(path_org_sl, str(trg_srs_id).zfill(3))
        cur_path_org_mi = os.path.join(path_org_mi, "liver_"+str(trg_srs_id)+".nii")
        cur_path_save = os.path.join(path_save, str(trg_srs_id).zfill(3))
        cur_path_org_label = os.path.join(path_org_label, str(trg_srs_id).zfill(3))
        if not os.path.isdir(cur_path_save):
            os.mkdir(cur_path_save)
        # else:
        #     continue
        pe.set_file_path(cur_path_org_mi, cur_path_org_sl, cur_path_seg_result, cur_path_save, cur_path_org_label)  # To set path

        # Step 2. Load CT series and  segmentation results from local
        pe.load_med_imgs()

        # Step 3. Generate sequences
        pe.generate_sequences()

        pe.save_sequences("0.sequences")

        # Step 4. Refine appearance violation
        print("=== Appearance Violation ===")
        pe.refine_appearance_violation(display)
        pe.save_sequences("1.appearance")
        # pe.save_segmentations("1.appearance")
        # # Step 5. Refine Location Violation
        print("=== Location Violation ===")
        pe.refine_location_violation(display)
        pe.save_sequences("2.location")
        # # pe.save_segmentations("2.location")

        # Step 6. Refine Size Violation
        print("=== Size Violation ===")
        pe.refine_size_violation(display)
        pe.save_sequences("3.size")
        # pe.save_segmentations("3.size")

        # Step 7. Refine Shape Violation
        print("=== Shape Violation ===")
        pe.refine_shape_violation(display)
        pe.save_sequences("4.shape")
        # pe.save_segmentations("4.shape")

        # Step 8. Refine HU Scale Violation
        print("=== HU Scale Violation ===")
        pe.refine_HU_scale_violation(display)

        # Step 9. Save refined results to the local
        pe.save_segmentations("5.result")
