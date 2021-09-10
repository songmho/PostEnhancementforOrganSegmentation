"""
Date: 2020. 12. 15.
Programmer: MH
Description: Code for segmenting liver regions
"""
import os

from tensorflow.python.keras.backend import clear_session

from miaas.lirads.software_process.livers import LiverSegmenter
import cv2
import numpy as np
from scipy import ndimage
from miaas.lirads.util.post_processing_liver import PostProcessLiver

class LiverRegionSegmentater:
    def __init__(self):
        self.ml_liver_seg = LiverSegmenter()
        self.post_processor = PostProcessLiver()
        self.setCT_b = None
        self.setCT_b_liver = {}
        self.setCT_b_seg = {}
        # self.ml_liver_seg.clear_session()
        self.ml_liver_seg.load_model()

    def initialize(self, std_name):
        self.setCT_b = None
        self.setCT_b_liver = {}
        self.setCT_b_seg = {}
        self.std_name = std_name

    def set_setCT_b(self, setCT_a, setMed_img):
        """
        To receive set_med_img data
        :param med_imgs: dict, medical images
        :return:
        """
        self.setCT_b = setCT_a[list(setCT_a.keys())[-1]]
        self.setMed_img = setMed_img[list(setMed_img.keys())[-1]]

        for name in self.setCT_b.keys():
            self.setCT_b_liver[name] = {}
            self.setCT_b_seg[name] = {}

    def get_setCT_b(self):
        return self.setCT_b

    def segment_liver_regions(self):
        """
        To segment liver regions in CT slices
        :return:
        """
        for srs_name, slices in self.setCT_b.items():
            print("       >>", srs_name, len(slices))
            i = 0
            for k, sl in slices.items():
                result = self.ml_liver_seg.segment(sl)  # To segment liver region
                # if result["roi"] != []: # To append CT slices having liver region
                self.setCT_b_liver[srs_name][i] = sl
                # if result["masks"].shape[2]> 0:
                zeros = np.zeros((result["masks"].shape[0], result["masks"].shape[1], 1), dtype=np.uint8)
                if result["masks"].shape[2] > 1:
                    for q in range(result["masks"].shape[2]):
                        cur = np.array(np.expand_dims(result["masks"][:, :, q], axis=-1), dtype=np.uint8)
                        zeros = np.add(cur, zeros)
                    result["masks"] = zeros
                elif result["masks"].shape[2] == 0:
                    result["masks"] = zeros
                result["masks"] = np.array(np.where(result["masks"] > 0, 255, 0), dtype=np.uint8)
                self.setCT_b_seg[srs_name][k] = result
                i+=1

    def clear_session(self):
        clear_session()

    def load_model(self):
        self.ml_liver_seg.load_model()

    def segment_liver_region_new(self, slice, loc):
        if loc[0] not in list(self.setCT_b_seg.keys()):
            self.setCT_b_seg[loc[0]] = {}
        result = self.ml_liver_seg.segment(slice)
        # try:
        zeros = np.zeros((result["masks"].shape[0], result["masks"].shape[1], 1), dtype=np.uint8)
        if result["masks"].shape[2] > 1:
            for k in range(result["masks"].shape[2]):
                cur = np.array(np.expand_dims(result["masks"][:, :, k], axis=-1), dtype=np.uint8)
                zeros = np.add(cur, zeros)
            result["masks"] = zeros
        elif result["masks"].shape[2] == 0:
            result["masks"] = zeros
        result["masks"] = np.array(np.where(result["masks"]>0, 255, 0), dtype=np.uint8)
        self.setCT_b_seg[loc[0]][loc[1]] = result
        print(os.path.join(r"E:\1. Lab\Daily Results\2021\2108\0827\test0",
                                 str(loc[0]) + "_" + str(loc[1]) + ".png"),
              type(self.setCT_b_seg[loc[0]][loc[1]]["masks"]), np.unique(self.setCT_b_seg[loc[0]][loc[1]]["masks"]),
              self.setCT_b_seg[loc[0]][loc[1]]["masks"].shape)
        cv2.imwrite(os.path.join(r"E:\1. Lab\Daily Results\2021\2108\0827\test0",
                                 str(loc[0]) + "_" + str(loc[1]) + ".png"), self.setCT_b_seg[loc[0]][loc[1]]["masks"])
        #     return result
        # except:
        return result

    def discard_insig_slices(self):
        """
        To discard insignificant slices
        :return:
        """

        # self.setCT_b_seg    # For mask
        # self.setMed_img     # For slice before transform
        # path_save = r"E:\1. Lab\Daily Results\2021\2108\0820\result\step2"
        for srs_name, imgs in self.setCT_b.items():   # For Image
            print("       [", srs_name,"]", )
            # if not os.path.isdir(os.path.join(path_save, self.std_name)):
            #     os.mkdir(os.path.join(path_save, self.std_name))
            # if not os.path.isdir(os.path.join(path_save, self.std_name, srs_name)):
            #     os.mkdir(os.path.join(path_save, self.std_name, srs_name))
            self.post_processor.initialize(self.setCT_b_seg[srs_name], self.setMed_img[srs_name], imgs)
            self.post_processor.split_t_f_sequence()
            self.post_processor.check_continuity_false()
            self.post_processor.revise_sequences()
            self.post_processor.discard_sequence()
            seqs = self.post_processor.return_target_seq()
            for i in range(len(self.setCT_b_seg[srs_name].values())):
                self.setCT_b_seg[srs_name][list(self.setCT_b_seg[srs_name].keys())[i]]["masks"] = seqs[i][1]
                # cv2.imwrite(os.path.join(path_save, self.std_name, srs_name, list(self.setCT_b_seg[srs_name].keys())[i] + ".png"), seqs[i][1])

    def proceed_post_step1(self, srs_id):
        srs_name = list(self.setCT_b.keys())[srs_id]
        imgs = self.setCT_b[srs_name]
        for sl_id, data in self.setCT_b_seg[srs_name].items():
            cv2.imwrite(os.path.join(r"E:\1. Lab\Daily Results\2021\2108\0827\test1", str(srs_name)+"_"+str(sl_id)+".png"), data["masks"])
        self.post_processor.initialize(self.setCT_b_seg[srs_name], self.setMed_img[srs_name], imgs)
        self.post_processor.initialize_model()
        self.post_processor.split_t_f_sequence()

    def proceed_post_step2(self):
        self.post_processor.check_continuity_false()

    def proceed_post_step3(self):
        self.post_processor.revise_sequences()

    def proceed_post_step4(self, srs_id):
        srs_name = list(self.setCT_b.keys())[srs_id]
        self.post_processor.discard_sequence()
        seqs = self.post_processor.return_target_seq()
        for i in range(len(self.setCT_b_seg[srs_name].values())):
            self.setCT_b_seg[srs_name][list(self.setCT_b_seg[srs_name].keys())[i]]["masks"] = seqs[i][1]

    def get_mask_list(self, srs_id):
        srs_name = list(self.setCT_b.keys())[srs_id]
        list_masks = []
        count = 0
        for sl_id, data in self.setCT_b_seg[srs_name].items():
            print(type(data["masks"]))
            print(data["masks"].shape)
            list_masks.append(data["masks"])
            cv2.imwrite(os.path.join(r"E:\1. Lab\Daily Results\2021\2108\0827\test", str(srs_name)+"_"+str(sl_id)+".png"), data["masks"])
        return list_masks

    def detect_liver_hepatic_segments(self):
        """
        To detect liver anatomical segments
        :return:
        """

    def get_setCT_b_liver(self):
        return self.setCT_b_liver

    def get_setCT_b_seg(self):
        return self.setCT_b_seg

    def get_setCT_b_hep_seg(self):
        return []

    def __discard_wrong_segmented_results(self):
        """
        To discard wrong segmented liver results
        :return:
        """
        # Criteria 2.
        list_liver = {}
        for srs_name, slices in self.setCT_b_seg.items():
            list_liver[srs_name] = []
            for i in range(len(slices)):
                sl = slices[i]
                mask_cur = self._combine_segments(i, sl["masks"])
                list_liver[srs_name].append(mask_cur)
        self.whole_segs = {}
        for srs_name, livers in list_liver.items():
            slice_id = 0
            self.whole_segs[srs_name] = []
            for l in livers:
                self._detect_overlapped_segments(srs_name, slice_id, l)
                slice_id += 1

        # To select the largest group
        set_liver_masks = {}
        for k, v in self.whole_segs.items():
            # print("Current Phase: ", k)
            # print("# of Groups: ", len(self.whole_segs[k]))
            os.mkdir(".\\test\\"+k)
            max_slices = 0
            set_liver_masks[k] = []
            for i in range(len(self.whole_segs[k])):
                for j in range(len(self.whole_segs[k][i])):
                    img = np.zeros((512, 512))
                    for seg in self.whole_segs[k][i][j][1]:
                        img += seg
                    img = img.astype(np.uint8)
                    img = np.where(img > 0, 255, 0)
                    self.whole_segs[k][i][j] = (self.whole_segs[k][i][j][0], img)
                if max_slices < len(self.whole_segs[k][i]):
                    set_liver_masks[k] = self.whole_segs[k][i]
                    max_slices = len(self.whole_segs[k][i])
            for i in range(len(set_liver_masks[k])):
                cv2.imwrite(".\\test\\" + k + "\\" + str(set_liver_masks[k][i][0]) + ".jpg", set_liver_masks[k][i][1])

        # Criteria 1.
        for srs_name, slices_info in set_liver_masks.items():
            # print("Current Series: ", srs_name)
            fir_small, biggest, last_small = 512*512, 0, 512*512
            for i in range(len(slices_info)):
                sl = slices_info[i][1]
                area = self._calculate_mask_area(sl)
                if biggest == 0 and fir_small > area:   # 1
                    fir_small = area
                else:
                    if fir_small < area and biggest < area < last_small: # 2
                        biggest = area
                    elif biggest > area and last_small > area:  # 3
                        last_small = area
                    elif biggest > area > last_small:   # 4
                        pass

    def _combine_segments(self, k, masks):
        """
        To combine segments for input slice
        :param masks:
        :return:
        """
        m = np.zeros((512, 512))
        for i in (range(masks.shape[2])):
            m += masks[:, :, i]
        m = np.where(m > 0, 255, 0)
        return m

    def divide_segments(self, mask):
        ret, img_binary = cv2.threshold(mask.astype(np.uint8), 127, 255, 0)
        contours, hierarchy = cv2.findContours(img_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        result = []
        for contour in contours:
            img = np.zeros((512, 512))
            for j in range(contour.shape[0]):
                img[ contour[j, :, 1], contour[j, :, 0]] = 1
            cur_con = ndimage.morphology.binary_fill_holes(img)
            result.append(cur_con)
        return result

    def _detect_overlapped_segments(self, cur_phase, slice_id, m):
        segments = self.divide_segments(m)
        num_segs = len(segments)    # Number of segments in a Slice
        seg_id = 0
        if num_segs == 0:
            return
        if len(self.whole_segs[cur_phase]) > 0:     # Segmentation Groups are already existed
            is_included = False
            for g_id in range(len(self.whole_segs[cur_phase])):
                selected_segs = []
                if slice_id - self.whole_segs[cur_phase][g_id][-1][0] >1:   # The group's last slice is not near to current slice.
                    continue
                for prv_seg in self.whole_segs[cur_phase][g_id][-1][1]:
                    for i in range(len(segments)):
                        cur_seg = segments[i]
                        overlap_rate = self._compute_overlap(prv_seg, cur_seg)
                        if overlap_rate > 0.0:
                            selected_segs.append(cur_seg)
                if len(selected_segs) > 0:
                    self.whole_segs[cur_phase][g_id].append((slice_id, selected_segs))
                    is_included = True
            if not is_included:     # Whole segments don't have inclusion relationship with previous slice.
                self.whole_segs[cur_phase].append([(slice_id, segments)])
        else:       # Any Segmentation Group is not existed
            self.whole_segs[cur_phase].append([(slice_id, segments)])

    def _calculate_mask_area(self, masks):
        """
        To compute mask area
        :param mask: ndarray, Size: n*512*512*1 (n: The Number of Segmented Liver Segments)
        :return:
        """
        m = np.where(masks > 0, 1, 0)
        return np.sum(m)

    def _compute_overlap(self, m1, m2):
        """
        To compute overlapped rate applying following formula
         ==> overlapRate = (m1 Intersection m2) / (Small one between m1 and m2)
        :param m1: ndarray, mask for criterion (Previous Mask)
        :param m2: ndarray, mask for target
        :return: double, overlap rate between 0..1
        """
        m1 = m1.astype(np.uint8)    # To change data type from boolean to numeric
        m2 = m2.astype(np.uint8)    # To change data type from boolean to numeric
        area_intersection = np.sum(np.where(m1+m2 > 1, 1, 0))
        area_small = min(np.sum(m1), np.sum(m2))
        return area_intersection/area_small
