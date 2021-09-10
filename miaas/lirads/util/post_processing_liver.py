"""
Date: 2021. 08. 18.
Programmer: MH
Description: Code for post-processing of Liver Organ
"""
import random

import cv2
import os
import numpy as np
from miaas.lirads.util.slice_similarity_measurer import SimilarityMeasurer

class PostProcessLiver:
    def __init__(self):
        self.mask_similarity_measurer = SimilarityMeasurer()
        self.path_cmp_organ_imgs = r"E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\models\liver"
        self.th_location = 0.32
        self.th_size = 0.5
        self.th_shape = 0.010
        self.th_exp_changed = 1.5
        self.th_hu = 1.3
        self.th_similarity = 0.02
        self.th_size_diff = 0.33
        self.th_overlapped = 0.7
        self.wc, self.ww = 40, 400

    def initialize(self, masks, slices, imgs):
        self.list_seqs = []
        self.list_seq_ids = []
        self.list_seqs_t_f = []

        self.list_masks = []
        self.list_imgs = []
        self.srs = []

        self.masks = masks
        self.slices = slices

        self.list_sls, self.list_sl_ids = [], []
        for k, v in self.masks.items():
            self.list_sls.append(v["masks"])
            self.list_sl_ids.append(k)
        for k, v in self.slices.items():
            self.srs.append(v["image"])
        self.srs = np.array(self.srs)
        self.imgs = imgs

    def initialize_model(self):
        self.mask_similarity_measurer.clear_session()
        self.mask_similarity_measurer.prepare_model()

    def split_t_f_sequence(self):
        """
        Step 1
        To split true and false sequences from input mask data
        :return:
        """
        print("          POST-Step 1. Split true and false sequences from input mask data")
        # To consider A/N VVP
        cur_seq = []
        cur_tag = True
        for id in range(len(self.list_sls)):
            is_contain = len(np.unique(self.list_sls[id]))>1
            if cur_tag != is_contain:  # If changed appearance
                if len(cur_seq)>0:
                    self.list_seqs_t_f.append([cur_tag, cur_seq])    # To save current sequence
                cur_tag = is_contain                                # To reset values
                cur_seq = []
            cur_seq.append([self.list_sl_ids[id], self.list_sls[id]])
        if len(cur_seq) > 0:
            self.list_seqs_t_f.append([cur_tag, cur_seq])

    def check_continuity_false(self):
        """
        Step 2
        To check continuity false and true sequences and revise sequences
        :return:
        """
        print("          POST-Step 2. Check continuity false and true sequences and revise them")
        # Step 2-1. Check continuity of true sequence
        # To consider Size VVP, Location VVP
        print("            POST-Step 2-1. Check whether segmented organ contains many air sections")
        for id in range(len(self.list_seqs_t_f)):
            # print("\n\n"+str(id))
            if self.list_seqs_t_f[id][0]:  # If true sequence,
                # To check the segmented result focuses on organs
                is_first = True
                list_del_ids = []
                for j in range(len(self.list_seqs_t_f[id][1])):
                    img = self.__load_img(self.list_seqs_t_f[id][1][j][0])
                    mask = self.list_seqs_t_f[id][1][j][1]
                    overlapped = np.bitwise_and(img, mask)
                    if np.count_nonzero(overlapped) / np.count_nonzero(mask) < 0.05:  # if the empty area > 95%
                        self.list_seqs_t_f[id][1][j][1] = np.array(np.zeros(self.list_seqs_t_f[id][1][j][1].shape),
                                                                   dtype=np.uint8)
                        if is_first:
                            if id - 1 >= 0:
                                cur_id = int(self.list_seqs_t_f[id][1][j][0])
                                prv_last_id = int(self.list_seqs_t_f[id-1][-1][0][0])
                                if abs(cur_id-prv_last_id) == 1:
                                    self.list_seqs_t_f[id-1][1].append(self.list_seqs_t_f[id][1][j])
                            list_del_ids.append(j)
                        else:
                            if id + 1 < len(self.list_seqs_t_f[id][1]):
                                cur_id = int(self.list_seqs_t_f[id][1][j][0])
                                next_fir_id = int(self.list_seqs_t_f[id+1][1][0][0])
                                if abs(cur_id-next_fir_id) == 1:
                                    self.list_seqs_t_f[id+1][1].insert(0, self.list_seqs_t_f[id][1][j])
                            list_del_ids.append(j)
                    else:
                        is_first = False
                # If the removed slices are too much
                if len(list_del_ids) / len(self.list_seqs_t_f[id][1]) > 0.7:
                    list_del_ids = list(range(len(self.list_seqs_t_f[id][1])))

                list_del_ids.reverse()
                for j in list_del_ids:
                    del self.list_seqs_t_f[id][1][j]

        list_remove_ids = []
        for id in range(len(self.list_seqs_t_f)):
            if len(self.list_seqs_t_f[id][1]) == 0:
                list_remove_ids.append(id)
        list_remove_ids.reverse()
        for id in list_remove_ids:
            del self.list_seqs_t_f[id]

        # Step 2-2. Combine TF Sequences
        # When combining TFSequences, the adjacent true TFSequences are applied to criteria.
        # The location VVP and Size change rate are considered.
        # If two TFSequences can be combined, the false sequences are considered.
        # If it can't,
        print("            POST-Step 2-2. Combine TF Sequences")
        new_seq = []
        for id in range(len(self.list_seqs_t_f)):
            if self.list_seqs_t_f[id][0]:
                if id <= 1:  # If First true sequence
                    if id == 1:  # If The first TF sequence is False sequence
                        # To add false data
                        trg_mask = self.list_seqs_t_f[id][1][0][1]
                        trg_img = self.__load_img(self.list_seqs_t_f[id][1][0][0])
                        overlapped_trg = np.bitwise_and(trg_mask, trg_img)
                        list_new = []
                        list_del = []
                        for i in range(len(self.list_seqs_t_f[id - 1][1]) - 1, -1, -1):
                            cur_mask = self.list_seqs_t_f[id - 1][1][i][1]
                            cur_img = self.__load_img(self.list_seqs_t_f[id - 1][1][i][0])
                            overlapped_cur = np.bitwise_and(cur_mask, cur_img)
                            # To consider Shape's change
                            mask_new = self.__revise_mask(None, cur_img, trg_img, None, cur_mask, trg_mask, None,
                                                          overlapped_cur, overlapped_trg)
                            if self.__check_shape_vvp(trg_mask, mask_new):  # To check Shape VVP
                                self.list_seqs_t_f[id - 1][1][i][1] = mask_new
                                cur_mask = mask_new
                                self.list_seqs_t_f[id][1].insert(0, self.list_seqs_t_f[id - 1][1][i])
                                list_del.append(i)
                                list_new.append(self.list_seqs_t_f[id - 1][1][i])
                            else:
                                break
                            trg_mask = cur_mask
                            trg_img = cur_img
                            overlapped_trg = np.bitwise_and(cur_mask, cur_img)
                        for i in list_del:
                            del self.list_seqs_t_f[id - 1][1][i]
                    new_seq.extend(self.list_seqs_t_f[id][1])
                else:  # If the TF sequences consist of multiple true sequences
                    last_id_seq_i_2 = int(self.list_seqs_t_f[id-2][1][-1][0])
                    fir_id_seq_i_1 =  int(self.list_seqs_t_f[id-1][1][0][0])
                    last_id_seq_i_1 = int(self.list_seqs_t_f[id-1][1][-1][0])
                    fir_id_seq_i =    int(self.list_seqs_t_f[id][1][0][0])
                    # print(last_id_seq_i_2, fir_id_seq_i_1, last_id_seq_i_1, fir_id_seq_i)
                    if (abs(last_id_seq_i_2 - fir_id_seq_i_1)>1) or (abs(last_id_seq_i_2 - fir_id_seq_i_1)==1 and abs(last_id_seq_i_1 - fir_id_seq_i)>1):
                        new_seq.extend(self.list_seqs_t_f[id][1])
                        self.list_seqs.append(new_seq)
                        new_seq = []
                        continue
                    else:
                        prv_size = np.count_nonzero(self.list_seqs_t_f[id - 2][1][-1][1])
                        cur_size = np.count_nonzero(self.list_seqs_t_f[id][1][0][1])
                        num_sl_between = len(self.list_seqs_t_f[id - 1][1])
                        cur_case = -1  # Variable for Cases of managing sequences. 0: Separate id-2 and id. 1: Combine id-2 and id
                        if num_sl_between > len(self.list_seqs_t_f[id - 2][1][0]) / 2 and num_sl_between > len(
                                self.list_seqs_t_f[id][1][0]):  # The length of FSeq[id-1] is longer than half of TSeqs.
                            cur_case = 0
                        else:
                            # Check location VVP
                            is_cor_loc_vvp = self.__check_location_vvp(self.list_seqs_t_f[id - 2][1][-1][1],
                                                                       self.list_seqs_t_f[id][1][0][1])
                            if not is_cor_loc_vvp:  # If not show correct location VVP
                                cur_case = 0
                            else:  # Showing location VVP
                                avg_change_rate_prv = self.__compute_change_rate(self.list_seqs_t_f[id - 2][1],
                                                                                 len(self.list_seqs_t_f[id - 2][1]) - 1)
                                avg_change_rate_cur = self.__compute_change_rate(self.list_seqs_t_f[id][1], 0)

                                exp_cur_size = prv_size * (1 + avg_change_rate_prv) ** (num_sl_between - 1)
                                exp_prv_size = cur_size * (1 - avg_change_rate_cur) ** (num_sl_between - 1)

                                if len(self.list_seqs_t_f[id][1]) == 1 and len(
                                        self.list_seqs_t_f[id - 2]) > 1:  # If the length of ith tf sequence is 1
                                    try:
                                        diff_rate = (prv_size - cur_size) / prv_size
                                        if (diff_rate < 0 and avg_change_rate_prv < 0) or (
                                                diff_rate >= 0 and avg_change_rate_prv >= 0):
                                            exp_prv_size = prv_size
                                        else:
                                            exp_prv_size = 1
                                    except:
                                        exp_prv_size = 1
                                elif len(self.list_seqs_t_f[id - 2]) == 1 and len(
                                        self.list_seqs_t_f[id][1]) > 1:  # If the length of i-2th tf sequence is 1
                                    try:
                                        diff_rate = (cur_size - prv_size) / cur_size
                                        if (diff_rate < 0 and avg_change_rate_cur < 0) or (
                                                diff_rate >= 0 and avg_change_rate_cur >= 0):
                                            exp_cur_size = cur_size
                                        else:
                                            exp_cur_size = 1
                                    except:
                                        exp_cur_size = 1
                                elif len(self.list_seqs_t_f[id - 2]) == 1 and len(self.list_seqs_t_f[id][1]) == 1:
                                    # Only Size check
                                    if prv_size >= cur_size:
                                        bigger = prv_size
                                        smaller = cur_size
                                    else:
                                        bigger = cur_size
                                        smaller = prv_size
                                    if bigger / smaller > 1.5:
                                        exp_cur_size = 1
                                        exp_prv_size = 1
                                    else:
                                        exp_cur_size = cur_size
                                        exp_prv_size = prv_size
                                if self.th_exp_changed < np.abs(
                                        prv_size - exp_prv_size) / exp_prv_size or self.th_exp_changed < np.abs(
                                        cur_size - exp_cur_size) / exp_cur_size:
                                    cur_case = 0
                                else:
                                    cur_case = 1
                        if cur_case == 0:  # Separate TFSeq[id-2] and TFSeq[id]
                            # To add TFSeq[id-1] to current new_seq
                            trg_mask = self.list_seqs_t_f[id - 2][1][-1][1]
                            trg_img = self.__load_img(self.list_seqs_t_f[id - 2][1][-1][0])
                            overlapped_trg = np.bitwise_and(trg_mask, trg_img)
                            list_new = []
                            list_del = []
                            for i in range(len(self.list_seqs_t_f[id - 1][1])):
                                cur_mask = self.list_seqs_t_f[id - 1][1][i][1]
                                cur_img = self.__load_img(self.list_seqs_t_f[id - 1][1][i][0])
                                overlapped_cur = np.bitwise_and(cur_mask, cur_img)
                                # To consider Shape's change
                                mask_new = self.__revise_mask(trg_img, cur_img, None, trg_mask, cur_mask, None,
                                                              overlapped_trg, overlapped_cur, None)
                                if self.__check_shape_vvp(trg_mask, mask_new):  # To check Shape VVP
                                    self.list_seqs_t_f[id - 1][1][i][1] = mask_new
                                    cur_mask = mask_new
                                    self.list_seqs_t_f[id - 2][1].append(self.list_seqs_t_f[id - 1][1][i])
                                    list_del.append(i)
                                    list_new.append(self.list_seqs_t_f[id - 1][1][i])
                                else:
                                    break
                                trg_mask = cur_mask
                                trg_img = cur_img
                                overlapped_trg = np.bitwise_and(cur_mask, cur_img)
                            list_del.reverse()
                            for i in list_del:
                                del self.list_seqs_t_f[id - 1][1][i]
                            new_seq.extend(list_new)

                            # To add new_seq to self.list_seqs
                            self.list_seqs.append(new_seq)
                            new_seq = []

                            # To add TFSeq[id-1] and TFSeq[id] to new_seq
                            trg_mask = self.list_seqs_t_f[id][1][0][1]
                            trg_img = self.__load_img(self.list_seqs_t_f[id][1][0][0])
                            overlapped_trg = np.bitwise_and(trg_mask, trg_img)
                            list_new = []
                            list_del = []
                            for i in range(len(self.list_seqs_t_f[id - 1][1]) - 1, -1, -1):
                                cur_mask = self.list_seqs_t_f[id - 1][1][i][1]
                                cur_img = self.__load_img(self.list_seqs_t_f[id - 1][1][i][0])
                                overlapped_cur = np.bitwise_and(cur_mask, cur_img)
                                # To consider Shape's change
                                mask_new = self.__revise_mask(None, cur_img, trg_img, None, cur_mask, trg_mask, None,
                                                              overlapped_cur, overlapped_trg)
                                if self.__check_shape_vvp(trg_mask, mask_new):  # To check Shape VVP
                                    self.list_seqs_t_f[id - 1][1][i][1] = mask_new
                                    cur_mask = mask_new
                                    self.list_seqs_t_f[id][1].insert(0, self.list_seqs_t_f[id - 1][1][i])
                                    list_del.append(i)
                                    list_new.append(self.list_seqs_t_f[id - 1][1][i])
                                else:
                                    break
                                trg_mask = cur_mask
                                trg_img = cur_img
                                overlapped_trg = np.bitwise_and(cur_mask, cur_img)
                            for i in list_del:
                                del self.list_seqs_t_f[id - 1][1][i]
                            new_seq.extend(self.list_seqs_t_f[id][1])

                        else:  # cur_case == 1, Combine TFSeq[id-2] and TFSeq[id]
                            # To add TFSeq[id-1]
                            # TODO Criteria for revising False Seq
                            trg_mask = self.list_seqs_t_f[id - 2][1][-1][1]
                            trg_img = self.__load_img(self.list_seqs_t_f[id - 2][1][-1][0])
                            overlapped_trg = np.bitwise_and(trg_mask, trg_img)
                            list_new = []
                            list_del = []
                            for i in range(len(self.list_seqs_t_f[id - 1][1])):
                                cur_mask = self.list_seqs_t_f[id - 1][1][i][1]
                                cur_img = self.__load_img(self.list_seqs_t_f[id - 1][1][i][0])
                                overlapped_cur = np.bitwise_and(cur_mask, cur_img)
                                # To consider Shape's change
                                mask_new = self.__revise_mask(trg_img, cur_img, None, trg_mask, cur_mask, None,
                                                              overlapped_trg, overlapped_cur, None)
                                if self.__check_shape_vvp(trg_mask, mask_new):  # To check Shape VVP
                                    self.list_seqs_t_f[id - 1][1][i][1] = mask_new
                                    cur_mask = mask_new
                                    self.list_seqs_t_f[id - 2][1].append(self.list_seqs_t_f[id - 1][1][i])
                                    list_del.append(i)
                                    list_new.append(self.list_seqs_t_f[id - 1][1][i])
                                else:
                                    break
                                trg_mask = cur_mask
                                trg_img = cur_img
                                overlapped_trg = np.bitwise_and(cur_mask, cur_img)
                            list_del.reverse()
                            for i in list_del:
                                del self.list_seqs_t_f[id - 1][1][i]
                            new_seq.extend(list_new)

                            # To add TFSeq[id]
                            new_seq.extend(self.list_seqs_t_f[id][1])
                            cur_target = self.list_seqs_t_f[id - 2][1]
                            cur_target.extend(self.list_seqs_t_f[id][1])
                            self.list_seqs_t_f[id][1] = cur_target
        if len(new_seq) > 0:
            if not self.list_seqs_t_f[-1][0]:  # If the last is false
                # To add data containing similar segmented results in false sequence
                trg_mask = self.list_seqs_t_f[-2][1][-1][1]
                trg_img = self.__load_img(self.list_seqs_t_f[-2][1][-1][0])
                overlapped_trg = np.bitwise_and(trg_mask, trg_img)
                list_new = []
                list_del = []
                for i in range(len(self.list_seqs_t_f[-1][1])):
                    cur_mask = self.list_seqs_t_f[-1][1][i][1]
                    cur_img = self.__load_img(self.list_seqs_t_f[-1][1][i][0])
                    overlapped_cur = np.bitwise_and(cur_mask, cur_img)
                    # To consider Shape's change
                    mask_new = self.__revise_mask(trg_img, cur_img, None, trg_mask, cur_mask, None, overlapped_trg,
                                                  overlapped_cur, None)
                    if self.__check_shape_vvp(trg_mask, mask_new):  # To check Shape VVP
                        self.list_seqs_t_f[-1][1][i][1] = mask_new
                        cur_mask = mask_new
                        self.list_seqs_t_f[-2][1].append(self.list_seqs_t_f[-1][1][i])
                        list_del.append(i)
                        list_new.append(self.list_seqs_t_f[-1][1][i])
                    else:
                        break
                    trg_mask = cur_mask
                    trg_img = cur_img
                    overlapped_trg = np.bitwise_and(cur_mask, cur_img)
                list_del.reverse()
                for i in list_del:
                    del self.list_seqs_t_f[-1][1][i]
                new_seq.extend(list_new)
            self.list_seqs.append(new_seq)

    def revise_sequences(self):
        """
        Step 3
        To revise combined sequences considering Size VVP, location VVP, and Shape VVP
        :return:
        """
        list_new_seqs = []
        # Step 3-1. Check combined sequences and re-connect them considering continuity
        # If the slice id is continued, they are combined.
        print("          POST-Step 3. Revise combined sequences considering VVPs")
        print("            POST-Step 3-1. Revise Sequences considering Slice ID")
        list_new = []

        # To check empty sequence
        list_del_id = []
        for id in range(len(self.list_seqs)):
            if len(self.list_seqs[id]) == 0:
                list_del_id.append(id)
        list_del_id.reverse()
        for id in list_del_id:
            del self.list_seqs[id]

        for id in range(len(self.list_seqs)):
            if id == 0:
                list_new = self.list_seqs[id]
                continue
            prv_seq_last_id = int(
                self.list_seqs[id - 1][-1][0])  # last slice id in previous sequence
            cur_seq_fir_id = int(
                self.list_seqs[id][0][0])  # first slice id in current sequence

            # if len(np.unique(self.list_seqs[id-1][-1][1]))>1 and len(np.unique(self.list_seqs[id][0][1]))>1 and (cur_seq_fir_id - prv_seq_last_id == 1):   # if continued
            if (cur_seq_fir_id - prv_seq_last_id == 1) and \
                    (np.count_nonzero(np.bitwise_and(self.list_seqs[id-1][-1][1], self.list_seqs[id][0][1]))>0):   # if continued
                list_new.extend(self.list_seqs[id])
            else:
                list_new_seqs.append(list_new)
                list_new = self.list_seqs[id]
        if len(list_new) > 0:
            list_new_seqs.append(list_new)
        self.list_seqs = None
        self.list_seqs = list_new_seqs

        # Step 3-2. Check location VVP
        print("            POST-Step 3-2. Check location VVP and Revise sequence")
        for i in range(len(self.list_seqs)):
            big_id = self.__get_biggest_sl_id(self.list_seqs[i])
            trg_img = self.__load_img(self.list_seqs[i][big_id][0])
            trg_mask = self.list_seqs[i][big_id][1]

            for j in range(big_id - 1, -1, -1):  # big_id-1~0
                cur_img = self.__load_img(self.list_seqs[i][j][0])
                cur_mask = self.list_seqs[i][j][1]
                # print(self.list_seqs[i][j+1][0],"    ", self.list_seqs[i][j][0], end="    ")
                is_correct = self.__check_location_vvp(trg_mask, cur_mask)
                if not is_correct:
                    overlapped_cur = np.bitwise_and(cur_img, cur_mask)
                    overlapped_trg = np.bitwise_and(trg_img, trg_mask)
                    cur_mask = self.__revise_mask(None, cur_img, trg_img, None, cur_mask, trg_mask, None,
                                                  overlapped_cur, overlapped_trg)
                    self.list_seqs[i][j][1] = cur_mask
                trg_mask = self.list_seqs[i][j][1]
                trg_img = cur_img

            trg_img = self.__load_img(self.list_seqs[i][big_id][0])
            trg_mask = self.list_seqs[i][big_id][1]

            for j in range(big_id + 1, len(self.list_seqs[i])):  # big_id+1 ~ max
                cur_img = self.__load_img(self.list_seqs[i][j][0])
                cur_mask = self.list_seqs[i][j][1]
                # print(self.list_seqs[i][j-1][0],"    ", self.list_seqs[i][j][0], end="    ")
                is_correct = self.__check_location_vvp(trg_mask, cur_mask)

                if not is_correct:
                    overlapped_cur = np.bitwise_and(cur_img, cur_mask)
                    overlapped_trg = np.bitwise_and(trg_img, trg_mask)
                    cur_mask = self.__revise_mask(trg_img, cur_img, None, trg_mask, cur_mask, None, overlapped_trg,
                                                  overlapped_cur, None)
                    self.list_seqs[i][j][1] = cur_mask
                trg_mask = self.list_seqs[i][j][1]
                trg_img = cur_img

        """
        Size
        Don't consider the flow between CT slices located in only nearby

        set flow of change sequences using # CT slices from i, j (|i-j| = 1, # is set to 8 but can be changed considering remained slices)
        change_seq_i := [... , i-2, i-1, i]
        change_seq_j := [j, j+1, j+2, ...]
        checking change of each sequence. 
          if the change of whole seqs are constant, don't revise i and j
          if the change of seq_i or seq_j is highly different, revise sl in another sequences following the correct seqs


        Check cur's change rate considering sequence
        cur--> i, trg-->j
        set sub_seg_i := [i-3, i-2, i-1, i, j, j+1, j+2, j+3]
        len(sub_seg_i) = x or <x
        if (sign(j- (i-1)) == sign(j- (i))) and (sign(j- (i-1)) == sign((i-1)-(i))) # Same sequence
            maintain
        else      

        """

        # # Step 3-3. Check Size VVP.
        print("            POST-Step 3-3. Check Size VVP and Revise sequence")
        th_size_check = 9
        for i in range(len(self.list_seqs)):
            big_id = self.__get_biggest_sl_id(self.list_seqs[i])
            trg_img = self.__load_img(self.list_seqs[i][big_id][0])
            trg_mask = self.list_seqs[i][big_id][1]

            max_size = big_id
            for j in range(big_id - 1, -1, -1):  # big_id-1~0

                cur_img = self.__load_img(self.list_seqs[i][j][0])
                cur_mask = self.list_seqs[i][j][1]
                cur_mask_sections = self.__divide_mask_to_sections(cur_mask)

                if np.bitwise_and(np.count_nonzero(cur_mask), np.count_nonzero(trg_mask)) == 0:
                    overlapped_cur = np.bitwise_and(cur_img, cur_mask)
                    overlapped_trg = np.bitwise_and(trg_img, trg_mask)
                    cur_mask = self.__revise_mask(trg_img, cur_img, None, trg_mask, cur_mask, None, overlapped_trg,
                                                  overlapped_cur, None)
                    self.list_seqs[i][j][1] = cur_mask

                if len(cur_mask_sections) > 1 and np.count_nonzero(cur_mask) > np.count_nonzero(trg_mask):
                    new_cur_mask = np.zeros(shape=cur_mask.shape)
                    for c in cur_mask_sections:
                        if np.count_nonzero(np.bitwise_and(c, trg_mask)) / np.count_nonzero(c) >= 0.3:
                            new_cur_mask += c
                    cur_mask = np.array(new_cur_mask, dtype=np.uint8)
                    self.list_seqs[i][j][1] = cur_mask
                if np.count_nonzero(trg_mask) != 0 and np.count_nonzero(cur_mask)/np.count_nonzero(trg_mask) > 2.0:
                    overlapped_cur = np.bitwise_and(cur_img, cur_mask)
                    overlapped_trg = np.bitwise_and(trg_img, trg_mask)
                    cur_mask = self.__revise_mask(trg_img, cur_img, None, trg_mask, cur_mask, None, overlapped_trg,
                                                  overlapped_cur, None)
                    self.list_seqs[i][j][1] = cur_mask
                    # self.list_seqs[i][j][1] = np.zeros((512, 512))

                if max_size - th_size_check < j:
                    cur_high = j
                else:
                    cur_high = j + th_size_check
                if j - th_size_check < 0:
                    cur_low = 0
                else:
                    cur_low = j - th_size_check
                seq_i = self.list_seqs[i][cur_low:j]
                seq_i.reverse()
                seq_j = self.list_seqs[i][j:cur_high]
                change_seq_i = self.__check_seq_change(seq_i)
                change_seq_j = self.__check_seq_change(seq_j)
                cur_img = self.__load_img(self.list_seqs[i][j][0])
                cur_mask = self.list_seqs[i][j][1]

                # TODO: Add code for handling multiple sections of organ
                try:
                    if ((np.sign(change_seq_i)) != (np.sign(change_seq_j)) and 0.0 < np.abs(change_seq_j) < 0.3):
                        overlapped_cur = np.bitwise_and(cur_img, cur_mask)
                        overlapped_trg = np.bitwise_and(trg_img, trg_mask)
                        cur_mask = self.__revise_mask(None, cur_img, trg_img, None, cur_mask, trg_mask, None,
                                                      overlapped_cur, overlapped_trg)
                        # self.list_seqs[i][j][1] = cur_mask
                except:
                    pass

                trg_mask = self.list_seqs[i][j][1]
                trg_img = cur_img

            trg_img = self.__load_img(self.list_seqs[i][big_id][0])
            trg_mask = self.list_seqs[i][big_id][1]

            max_size = len(self.list_seqs[i])
            for j in range(big_id + 1, len(self.list_seqs[i])):   # big_id+1~MAX
                cur_img = self.__load_img(self.list_seqs[i][j][0])
                cur_mask = self.list_seqs[i][j][1]

                if np.bitwise_and(np.count_nonzero(cur_mask), np.count_nonzero(trg_mask)) == 0:
                    overlapped_cur = np.bitwise_and(cur_img, cur_mask)
                    overlapped_trg = np.bitwise_and(trg_img, trg_mask)
                    cur_mask = self.__revise_mask(trg_img, cur_img, None, trg_mask, cur_mask, None, overlapped_trg,
                                                  overlapped_cur, None)
                    self.list_seqs[i][j][1] = cur_mask

                cur_mask_sections = self.__divide_mask_to_sections(cur_mask)
                if len(cur_mask_sections) > 1 and np.count_nonzero(cur_mask) > np.count_nonzero(trg_mask):
                    new_cur_mask = np.zeros(shape=cur_mask.shape)
                    for c in cur_mask_sections:
                        if np.count_nonzero(np.bitwise_and(c, trg_mask)) / np.count_nonzero(c) >= 0.3:
                            new_cur_mask += c
                    cur_mask = np.array(new_cur_mask, dtype=np.uint8)
                    self.list_seqs[i][j][1] = cur_mask

                if np.count_nonzero(trg_mask) != 0 and np.count_nonzero(cur_mask)/np.count_nonzero(trg_mask) > 2.0:
                    overlapped_cur = np.bitwise_and(cur_img, cur_mask)
                    overlapped_trg = np.bitwise_and(trg_img, trg_mask)
                    cur_mask = self.__revise_mask(trg_img, cur_img, None, trg_mask, cur_mask, None, overlapped_trg,
                                                  overlapped_cur, None)
                    self.list_seqs[i][j][1] = cur_mask
                    # self.list_seqs[i][j][1] = np.zeros((512, 512))
                if max_size - th_size_check < j:
                    cur_high = j
                else:
                    cur_high = j + th_size_check
                if j - th_size_check < big_id:
                    cur_low = big_id + 1
                else:
                    cur_low = j - th_size_check
                seq_i = self.list_seqs[i][cur_low:j]
                seq_i.reverse()
                seq_j = self.list_seqs[i][j:cur_high]
                change_seq_i = self.__check_seq_change(seq_i)
                change_seq_j = self.__check_seq_change(seq_j)
                cur_img = self.__load_img(self.list_seqs[i][j][0])
                cur_mask = self.list_seqs[i][j][1]
                try:
                    if ((np.sign(change_seq_i)) != (np.sign(change_seq_j)) and 0.0 < np.abs(change_seq_j) < 0.3):
                        overlapped_cur = np.bitwise_and(cur_img, cur_mask)
                        overlapped_trg = np.bitwise_and(trg_img, trg_mask)
                        cur_mask = self.__revise_mask(trg_img, cur_img, None, trg_mask, cur_mask, None, overlapped_trg,
                                                      overlapped_cur, None)
                        # self.list_seqs[i][j][1] = cur_mask
                except:
                    pass
                trg_mask = self.list_seqs[i][j][1]
                trg_img = cur_img

        # Step 3-4. Check Shape VVP
        """
        To be able to change shape as high difference although the CT slices contain correct seg results
        To check shape VVP for only bigger size of organ parts
        """
        print("            POST-Step 3-4. Check Shape VVP and Revise sequence")
        for i in range(len(self.list_seqs)):
            big_id = self.__get_biggest_sl_id(self.list_seqs[i])
            trg_img = self.__load_img(self.list_seqs[i][big_id][0])
            trg_mask = self.list_seqs[i][big_id][1]

            for j in range(big_id - 1, -1, -1):  # big_id-1~0
                cur_img = self.__load_img(self.list_seqs[i][j][0])
                cur_mask = self.list_seqs[i][j][1]
                if np.count_nonzero(cur_mask) > 150000:
                    is_correct = self.__check_shape_vvp(trg_mask, cur_mask)
                    if not is_correct:
                        overlapped_cur = np.bitwise_and(cur_img, cur_mask)
                        overlapped_trg = np.bitwise_and(trg_img, trg_mask)
                        cur_mask = self.__revise_mask(None, cur_img, trg_img, None, cur_mask, trg_mask, None,
                                                      overlapped_cur, overlapped_trg)
                        self.list_seqs[i][j][1] = cur_mask
                trg_mask = self.list_seqs[i][j][1]
                trg_img = cur_img

            trg_img = self.__load_img(self.list_seqs[i][big_id][0])
            trg_mask = self.list_seqs[i][big_id][1]

            for j in range(big_id + 1, len(self.list_seqs[i])):  # big_id+1 ~ max
                cur_img = self.__load_img(self.list_seqs[i][big_id][0])
                cur_mask = self.list_seqs[i][j][1]
                if np.count_nonzero(cur_mask) > 150000:
                    is_correct = self.__check_shape_vvp(trg_mask, cur_mask)
                    if not is_correct:
                        overlapped_cur = np.bitwise_and(cur_img, cur_mask)
                        overlapped_trg = np.bitwise_and(trg_img, trg_mask)
                        cur_mask = self.__revise_mask(trg_img, cur_img, None, trg_mask, cur_mask, None, overlapped_trg,
                                                      overlapped_cur, None)
                        self.list_seqs[i][j][1] = cur_mask
                trg_mask = self.list_seqs[i][j][1]
                trg_img = cur_img

    def discard_sequence(self):
        """
        Step 4
        To discard sequences considering HU VPP
        :return:
        """
        print("          POST-Step 4. Discard sequences considering VVPs")
        print("            POST-Step 4-1. Discard sequences considering HU VVP")
        list_remove_seq = []
        if len(self.list_seqs)>1:
            for seq in self.list_seqs:
                maxs = []
                mins = []
                masks = []
                masks_org = []
                idxs = []

                for s in seq:
                    idxs.append(int(s[0]))
                count = 0
                for sl_id in self.list_sl_ids:
                    # To check the slice in sequence
                    if int(sl_id) in idxs:
                        masks_org.append(seq[count][1])
                        masks.append(np.where(seq[count][1] > 0, 1, np.inf))
                        count += 1
                    else:
                        cur_mk = np.array(seq[0][1].shape)
                        masks_org.append(np.zeros(seq[0][1].shape))
                        masks.append(cur_mk.fill(np.inf))
                masks = np.array(masks)
                for i in idxs:
                    img = np.multiply(self.srs[i - 1], masks[i - 1])
                    img2 = img[(img > -np.inf) & (img < np.inf)]
                    if img2.shape != (512, 512):
                        img2 = np.zeros((512, 512))
                    maxs.append(np.max(img2))
                    mins.append(np.min(img2))
                if (np.average(maxs) < (self.wc - self.ww / 2) * self.th_hu or (
                        self.wc + self.ww / 2) * self.th_hu < np.average(mins)):
                    list_remove_seq.append(self.list_seqs.index(seq))
            # print("List Removed Sequences: ", list_remove_seq)
            list_remove_seq.reverse()
            for i in list_remove_seq:
                del self.list_seqs[i]

        print("            POST-Step 4-2. Discard sequences considering Similarity of Shape")
        if len(self.list_seqs)>1:
            list_cmp = self.__select_compared_mask_data()
            avg_list_sim_dist = []
            avg_list_size_diff = []
            for seq in self.list_seqs:
                big_id = self.__get_biggest_sl_id(seq)
                list_sim_dist = []
                list_size_diff = []
                for i in list_cmp:
                    dist, size = self.__compute_similarity_distance(i, seq[big_id][1])
                    list_sim_dist.append(dist)
                    list_size_diff.append(size)
                avg_list_sim_dist.append(np.average(list_sim_dist))
                avg_list_size_diff.append(np.average(list_size_diff))
            list_remove_seq = []
            # print("avg_list_sim_dist", avg_list_sim_dist)
            # print("avg_list_size_diff", avg_list_size_diff)
            for i in range(len(avg_list_sim_dist)):
                if self.th_similarity < avg_list_sim_dist[i] and avg_list_size_diff[i] < self.th_size_diff:
                    list_remove_seq.append(i)
            # print("List Removed Sequences: ", list_remove_seq)
            list_remove_seq.reverse()
            for i in list_remove_seq:
                del self.list_seqs[i]

    def return_target_seq(self):
        size, id = 0, -1

        if len(self.list_seqs)>1:
            list_seqs_new = []
            list_seqs_new.append(self.list_seqs[0])
            for i in range(1, len(self.list_seqs)):
                if (abs(int(self.list_seqs[i][0][0])-int(self.list_seqs[i-1][-1][0])) == 1) and \
                        np.count_nonzero(np.bitwise_and(self.list_seqs[i][0][1], self.list_seqs[i-1][-1][1])) > 0:
                    cur = np.count_nonzero(self.list_seqs[i][0][1])
                    prv = np.count_nonzero(self.list_seqs[i - 1][-1][1])
                    if np.abs(cur-prv) / prv > 3.0:
                        list_seqs_new.append(self.list_seqs[i])
                    else:
                        # If adjacent sequences are connected and overlapped.
                        list_seqs_new[len(list_seqs_new)-1].extend(self.list_seqs[i])
                else:
                    list_seqs_new.append(self.list_seqs[i])
            self.list_seqs = list_seqs_new
            for i in self.list_seqs:
                cur_count = 0
                for j in i:
                    if np.count_nonzero(j[1]) > 0:
                        cur_count += 1
                if cur_count > size:
                    size = cur_count
                    id = self.list_seqs.index(i)
        else:
            id = 0

        list_seq_sl_id = []
        for i in self.list_seqs[id]:
            list_seq_sl_id.append(i[0])
        list_results = []
        for sl_id in self.list_sl_ids:
            if sl_id in list_seq_sl_id:
                list_results.append([sl_id, self.list_seqs[id][list_seq_sl_id.index(sl_id)][1]])
            else:
                list_results.append([sl_id, np.zeros(self.list_seqs[id][0][1].shape)])
        groups = []
        new_group = []
        for l in list_results:
            if np.count_nonzero(l[1])>0:
                new_group.append(l)
            else:
                if len(new_group)>0:
                    groups.append(new_group)
                    new_group = []

        idx, length = -1, 0
        for i in range(len(groups)):
            if len(groups[i]) >length:
                idx = i
                length = len(groups[i])

        for i in range(len(list_results)):
            if list_results[i] in groups[idx]:
                pass
            else:
                list_results[i] = [list_results[i][0], np.zeros(self.list_seqs[id][0][1].shape)]
        return list_results

    def __check_seq_change(self, sub_seq):
        sum_sign = 0
        for s in range(1, len(sub_seq)):
            sum_sign += np.sign(np.count_nonzero(sub_seq[s - 1][1]) - np.count_nonzero(sub_seq[s][1]))
        try:
            return sum_sign / (len(sub_seq) - 1)
        except:
            return 0.0

    def __compute_similarity_distance(self, trg_mask, cur_mask):
        trg_mask = cv2.cvtColor(trg_mask, cv2.COLOR_GRAY2BGR)
        cur_mask = cv2.cvtColor(cur_mask, cv2.COLOR_GRAY2BGR)
        distance = self.mask_similarity_measurer.compute_distance(trg_mask, cur_mask)
        diff = np.count_nonzero(cur_mask) / np.count_nonzero(trg_mask)
        return distance, diff

    def __get_biggest_sl_id(self, masks):
        biggest_size, biggest_id = 0, -1
        for i in range(len(masks)):
            if biggest_size < np.count_nonzero(masks[i][1]):
                biggest_size = np.count_nonzero(masks[i][1])
                biggest_id = i
        return biggest_id

    def __load_img(self, id):
        cur_img = self.imgs[id]
        if cur_img.shape[2] > 1:
            cur_img = cv2.cvtColor(cur_img, cv2.COLOR_BGR2GRAY)
        return cur_img

    def __select_compared_mask_data(self):
        list_f_name = os.listdir(self.path_cmp_organ_imgs)
        random.shuffle(list_f_name)
        list_result = []
        for i in list_f_name:  # images
            cur_img = cv2.imread(os.path.join(self.path_cmp_organ_imgs, i))
            cur_img = cv2.cvtColor(cur_img, cv2.COLOR_BGR2GRAY)
            list_result.append(cur_img)
        return list_result

    def __divide_mask_to_sections(self, mask):
        """
        To divide input mask to multiple masks having each section of segmented results
        :param mask: ndarray, segmented results having location of target organ
        :return: list, list of masks
        """
        results = []
        cur_cnt, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for i in cur_cnt:
            new_mask = np.zeros(mask.shape)
            results.append(
                np.array(cv2.drawContours(new_mask, [i], -1, color=255, thickness=cv2.FILLED), dtype=np.uint8))

        return results

    def __check_location_vvp(self, trg_mask, cur_mask):
        trg_sections = self.__divide_mask_to_sections(trg_mask)
        cur_sections = self.__divide_mask_to_sections(cur_mask)

        if (np.count_nonzero(trg_mask) == 0 and np.count_nonzero(cur_mask) > 0) or (
                np.count_nonzero(trg_mask) > 0 and np.count_nonzero(
                cur_mask) == 0):  # If next CT SL doesn't contain any seg results
            return False

        result = True
        for i in cur_sections:
            is_only_correct = False
            for j in trg_sections:
                area_overlapped = np.bitwise_and(i, j)
                smaller = np.count_nonzero(j)
                if smaller > np.count_nonzero(i):
                    smaller = np.count_nonzero(i)
                overlapped_rate = np.count_nonzero(area_overlapped) / smaller  # To compute iou
                # print(overlapped_rate)
                if overlapped_rate > self.th_location:  # if iou is higher than TH
                    is_only_correct = True  # having overlapped relationship
                    continue
            result = result and is_only_correct
        return result

    def __check_size_vvp(self, trg_mask, cur_mask):
        num_trg = np.count_nonzero(trg_mask)
        num_cur = np.count_nonzero(cur_mask)
        num_bigger = num_trg
        if num_trg < num_cur:
            num_bigger = num_cur
        if np.abs(num_trg - num_cur) / num_bigger < self.th_size:  # If the difference lower than TH
            return False
        else:
            return True

    def __check_shape_vvp(self, trg_mask, cur_mask):
        trg_mask = cv2.cvtColor(trg_mask, cv2.COLOR_GRAY2BGR)
        cur_mask = cv2.cvtColor(cur_mask, cv2.COLOR_GRAY2BGR)
        distance = self.mask_similarity_measurer.compute_distance(trg_mask, cur_mask)
        # print(distance)
        if distance > self.th_shape:
            return False
        else:
            return True

    def __compute_change_rate(self, masks, trg_id):
        change_rate = 0
        if len(masks) == 1:
            return change_rate
        else:
            tr_len = 8  # The number of CT slices for target, TO BE CHANGED
            if len(masks) > tr_len:
                if trg_id > len(masks) / 2:
                    crt_id = len(masks) - tr_len
                else:
                    crt_id = tr_len
            else:
                if trg_id > len(masks) / 2:
                    crt_id = int(len(masks) - len(masks) / 2)
                else:
                    crt_id = int(len(masks) / 2)

            sum_diff = 0
            if crt_id < trg_id:
                for i in range(crt_id + 1, trg_id + 1):
                    cur_size = np.count_nonzero(masks[i][1])
                    prv_size = np.count_nonzero(masks[i - 1][1])
                    try:
                        sum_diff += (prv_size - cur_size) / prv_size
                    except:
                        sum_diff += np.inf
                change_rate = sum_diff / len(range(crt_id + 1, trg_id + 1))
            else:
                for i in range(crt_id - 1, trg_id + 1, -1):
                    cur_size = np.count_nonzero(masks[i][1])
                    nxt_size = np.count_nonzero(masks[i + 1][1])
                    try:
                        sum_diff += (nxt_size - cur_size) / nxt_size
                    except:
                        sum_diff += np.inf
                change_rate = sum_diff / len(range(trg_id, crt_id + 1))
            return change_rate

    def __revise_mask(self, img_1=None, img_2=None, img_3=None, mask_1=None, mask_2=None, mask_3=None,
                      overlapped_1=None, overlapped_2=None, overlapped_3=None):

        """
        To revise cur mask considering nearby CT slices
        :param img_1:
        :param img_2:
        :param img_3:
        :param mask_1:
        :param mask_2:
        :param mask_3:
        :param overlapped_1:
        :param overlapped_2:
        :param overlapped_3:
        :return:
        """
        # list_mask_trg = []          # From mask_1 or mask_3
        # list_mask_cur = []          # From mask_2
        #
        # # To check Multi section
        # if type(img_1) == np.ndarray:
        #     cur_cnt, _ = cv2.findContours(np.array(mask_1, np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        #     for i in cur_cnt:
        #         new_mask = np.zeros(mask_1.shape)
        #         new_mask = np.array(cv2.drawContours(new_mask, [i], -1, color=255, thickness=cv2.FILLED), dtype=np.uint8)
        #         list_mask_trg.append(new_mask)
        # if type(img_2) == np.ndarray:
        #     cur_cnt, _ = cv2.findContours(np.array(mask_2, np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        #     for i in cur_cnt:
        #         new_mask = np.zeros(mask_2.shape)
        #         new_mask = np.array(cv2.drawContours(new_mask, [i], -1, color=255, thickness=cv2.FILLED), dtype=np.uint8)
        #         list_mask_cur.append(new_mask)
        # if type(img_3) == np.ndarray:
        #     cur_cnt, _ = cv2.findContours(np.array(mask_3, np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        #     for i in cur_cnt:
        #         new_mask = np.zeros(mask_3.shape)
        #         new_mask = np.array(cv2.drawContours(new_mask, [i], -1, color=255, thickness=cv2.FILLED), dtype=np.uint8)
        #         list_mask_trg.append(new_mask)
        #
        # selected_cur_masks = []
        # for trg_id in range(len(list_mask_trg)):
        #     cur_mak_trg = list_mask_trg[trg_id]
        #     for cur_id in range(len(list_mask_cur)):
        #         cur_mak_cur = list_mask_cur[cur_id]
        #         bit_and = np.bitwise_and(cur_mak_trg, cur_mak_cur)
        #         if np.count_nonzero(bit_and)/np.count_nonzero(cur_mak_cur) < self.th_overlapped:
        #             # NOT APPLY THE CURRENT MASK DATA
        #             pass
        #         else:
        #             selected_cur_masks.append(cur_mak_cur)
        #
        # mask_2 = np.zeros(shape=mask_2.shape)
        # for m in selected_cur_masks:
        #     mask_2+=np.array(m, dtype=np.uint8)

        # Case 1. No exist (1)
        if np.count_nonzero(mask_1) == 0:
            img_1 = None
            mask_1 = None
            overlapped_1 = None
        if np.count_nonzero(mask_3) == 0:
            img_3 = None
            mask_3 = None
            overlapped_3 = None
        if img_1 is None and img_3 is None:
            mask_new = np.zeros(img_2.shape)

        elif img_1 is None:
            color_range = np.unique(overlapped_3)
            if len(color_range) > 1:
                color_range = np.delete(color_range, [0], None)
            range_3 = (min(color_range), max(color_range))
            overlapped_2_for_3 = np.bitwise_and(img_2, mask_3)
            # if len(np.unique(overlapped_2_for_3))<=1:
            #     mask_new = np.zeros(img_3.shape)
            # else:
            mask_new = np.array(
                np.where((overlapped_2_for_3 >= range_3[0] + 10) & (overlapped_2_for_3 <= range_3[1] - 10), 255, 0),
                np.uint8)

        # Case 2. No Exist (3)
        elif img_3 is None:
            color_range = np.unique(overlapped_1)
            if len(color_range) > 1:
                color_range = np.delete(color_range, [0])
            range_1 = (min(color_range), max(color_range))

            overlapped_2_for_1 = np.bitwise_and(img_2, mask_1)
            color_range_new = np.unique(overlapped_2_for_1)

            if len(color_range_new) > 1:
                color_range_new = np.delete(color_range_new, [0])
            mask_new = np.array(
                np.where((overlapped_2_for_1 >= range_1[0] + 10) & (overlapped_2_for_1 <= range_1[1] - 10), 255, 0),
                np.uint8)

        # Case 3. Exist (1) and (3)
        else:
            overlapped_1_and_3 = np.bitwise_and(mask_1, mask_3)
            size_mask_1 = np.count_nonzero(mask_1)
            size_mask_3 = np.count_nonzero(mask_3)
            size_big = size_mask_1

            if len(np.unique(overlapped_1_and_3)) == 1:
                if size_mask_3 > 0:
                    color_range_3 = np.unique(overlapped_3)
                    if len(color_range_3) > 1:
                        color_range_3 = np.delete(color_range_3, [0])
                    overlapped_new = np.bitwise_and(img_2, mask_3)
                    mask_new = np.array(np.where(overlapped_new > min(color_range_3), 255, 0), np.uint8)
                else:
                    mask_new = np.zeros(img_3.shape)
            else:
                size_1 = np.count_nonzero(mask_1)
                size_3 = np.count_nonzero(mask_3)

                color_range_1 = np.unique(overlapped_1)
                if len(color_range_1) > 1:
                    color_range_1 = np.delete(color_range_1, [0])
                color_range_3 = np.unique(overlapped_3)
                if len(color_range_3) > 1:
                    color_range_3 = np.delete(color_range_3, [0])

                range_combine = [0, 0]
                if min(color_range_1) < min(color_range_3):
                    range_combine[0] = min(color_range_1)
                else:
                    range_combine[0] = min(color_range_3)
                if max(color_range_1) < max(color_range_3):
                    range_combine[1] = max(color_range_3)
                else:
                    range_combine[1] = max(color_range_1)

                if size_1 > size_3:
                    overlapped_new = np.bitwise_and(img_2, mask_1)
                else:
                    overlapped_new = np.bitwise_and(img_2, mask_3)
                mask_new = np.array(np.where(overlapped_new > range_combine[0], 255, 0), np.uint8)
                if size_1 > size_3 and np.count_nonzero(np.bitwise_and(mask_1, mask_new)) / np.count_nonzero(
                        mask_1) < 0.1:
                    mask_new = np.zeros(img_3.shape)
                if size_1 <= size_3 and np.count_nonzero(np.bitwise_and(mask_3, mask_new)) / np.count_nonzero(
                        mask_3) < 0.1:
                    mask_new = np.zeros(img_3.shape)

        mask = np.array(mask_new, np.uint8)
        cur_cnt, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        new_mask = np.zeros(mask.shape)
        list_area = []
        for i in cur_cnt:
            list_area.append(cv2.contourArea(i))
            if cv2.contourArea(i) > 100:
                new_mask += np.array(cv2.drawContours(new_mask, [i], -1, color=255, thickness=cv2.FILLED),
                                     dtype=np.uint8)
        new_mask = np.array(new_mask, dtype=np.uint8)
        if len(list_area) > 1 and max(list_area) < 10000:
            cur_cnt, _ = cv2.findContours(new_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            new_mask = np.zeros(mask.shape)
            cnt_small, small_size = [], 10000
            for i in cur_cnt:
                if cv2.contourArea(i) < small_size:
                    small_size = cv2.contourArea(i)
                    cnt_small = [i]
            new_mask = np.array(cv2.drawContours(new_mask, cnt_small, -1, color=255, thickness=cv2.FILLED),
                                dtype=np.uint8)
        return np.array(new_mask, dtype=np.uint8)
