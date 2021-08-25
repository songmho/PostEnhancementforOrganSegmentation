"""
Date: 2021. 04. 26.
Programmer: MH
Description: Code for Step 3 of Liver Cancer Detection Process with ML
"""
import os

import numpy as np
import cv2
from tensorflow.python.keras.backend import clear_session

from miaas.lirads.util import tumor
import miaas.lirads.util.mrcnn.model as modellib


import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(gpus[0], True)

class LegionSegmentor:
    def __init__(self):
        self.setCT_C_Seg = {}
        self.setCT_C_tumor = {}
        self.config = tumor.TumorConfig()
        self.tumor_class_names = ['None', 'Tumor']
        self.is_contain_target = False

    def initialize(self, std_name):
        self.setCT_C_Seg = {}
        self.setCT_C_tumor = {}
        self.is_contain_target = False
        self.std_name = std_name

    def clear_session(self):
        clear_session()

    def load_model(self):
        # TUMOR_SEG_MODEL_DIR = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\mias_with_lirads\\mias\\miaas\\lirads\\models\\tumor_segment\\logs"
        # TUMOR_SEG_WEIGHT_DIR = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\mias_with_lirads\\mias\\miaas\\lirads\\models\\tumor_segment\\mask_rcnn_lesion_0100.h5"

        TUMOR_SEG_MODEL_DIR = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\mias_with_lirads\\mias\\miaas\\lirads\\models\\tumor_segment_2\\logs"
        TUMOR_SEG_WEIGHT_DIR = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\mias_with_lirads\\mias\\miaas\\lirads\\models\\tumor_segment_2\\mask_rcnn_tumor_000140.h5"
        self.tumor_detector = modellib.MaskRCNN(mode="inference", model_dir=TUMOR_SEG_MODEL_DIR, config=self.config)
        self.tumor_detector.load_weights(TUMOR_SEG_WEIGHT_DIR, by_name=True)

    def check_target_presence(self, setCT_b, setCT_b_seg):
        """
        To check tumor's existence in plain phase
        If the CT study doesn't contain plain phase, the method returns true.
        If the CT study contains plain phase, the method check the existence of tumors.
            and if the tumor is existed, the method returns true.
        """
        setCT_b = setCT_b[list(setCT_b.keys())[0]]
        if "PLAIN" in setCT_b.keys():
            is_contain = False
            for key, sl in setCT_b["PLAIN"].items():
                results = self.tumor_detector.detect([sl], verbose=0)
                masks = np.zeros(shape=sl.shape)
                for m in results[0]["masks"][0,0,:]:
                    masks += m
                msk_cur_liver = np.array(setCT_b_seg["PLAIN"][key]["masks"], dtype=np.uint8)
                masks = np.array(masks, dtype=np.uint8)
                msks_new = self.__enhance_seg_tumor_data(msk_cur_liver, masks)
                if np.count_nonzero(msks_new) > 0:
                    is_contain = True     # If tumor in liver
            return is_contain
        else:   # Not in plain phase in the CT Study
            return True

    def segment_lesion(self, setCT_b, setCT_b_seg):
        setCT_b = setCT_b[list(setCT_b.keys())[0]]

        for name in setCT_b.keys():
            self.setCT_C_Seg[name] = {}
            self.setCT_C_tumor[name] = {}

        # path_save = r"E:\1. Lab\Daily Results\2021\2108\0820\result\step3"
        for srs_name, slices in setCT_b.items():
            count = 0
            keys = []
            # if not os.path.isdir(os.path.join(path_save, self.std_name)):
            #     os.mkdir(os.path.join(path_save, self.std_name))
            # if not os.path.isdir(os.path.join(path_save, self.std_name, srs_name)):
            #     os.mkdir(os.path.join(path_save, self.std_name, srs_name))
            for key, sl in slices.items():
                results = self.tumor_detector.detect([sl], verbose=0)
                mask_result, roi_result, conf_value_result, roi_imgs_result = \
                    results[0]["masks"], results[0]["rois"], results[0]["scores"], results[0]["rois_img"]
                masks = np.array(np.zeros(shape=(512, 512, 1)), dtype=np.uint8)
                if len(results[0]["masks"][0, 0, :]) > 0:
                    for m in results[0]["masks"][0,0,:]:
                        if m.shape == (512, 512, 0):
                            m = np.expand_dims(m, axis=-1)
                        masks += m
                msk_cur_liver = np.array(setCT_b_seg[srs_name][key]["masks"], dtype=np.uint8)
                msks_new = self.__enhance_seg_tumor_data(msk_cur_liver, masks)
                masks, rois, conf_values, rois_img = [], [], [], []
                for k in range(len(mask_result[0, 0, :])):    # Tumor Mask ID
                    cur_lesion = np.array(np.expand_dims(mask_result[:, :, k], axis=-1), dtype=np.uint8)
                    msks_new = self.__enhance_seg_tumor_data(msk_cur_liver, cur_lesion)
                    if np.count_nonzero(msks_new)>0:
                        masks.append(cur_lesion)
                        rois.append(roi_result[k])
                        conf_values.append(conf_value_result[k])
                        rois_img.append(roi_imgs_result[k])
                if len(masks) > 0:
                    count += 1
                    keys.append(key)
                # cv2.imshow("img", sl)
                # cv2.imshow("mask", msks_new)
                # cv2.imwrite(os.path.join(path_save, self.std_name, srs_name, key+".png"), msks_new)
                # cv2.waitKey(5)

                self.setCT_C_Seg[srs_name][key] = {"masks": masks, 'rois': rois, "confidence_values": conf_values, "rois_img":rois_img, "img": sl}
                self.setCT_C_tumor[srs_name][key] = msks_new
            print("       >>", srs_name, len(slices), count, keys)

    def segment_lesion_new(self, cur_liver, img, ii):

        results = self.tumor_detector.detect([img], verbose=0)
        mask_result, roi_result, conf_value_result, roi_imgs_result = \
            results[0]["masks"], results[0]["rois"], results[0]["scores"], results[0]["rois_img"]
        masks = np.array(np.zeros(shape=(512, 512, 1),dtype=np.uint8))

        msks_new = self.__enhance_seg_tumor_data(cur_liver, masks)
        masks, rois, conf_values, rois_img = [], [], [], []
        whole_mask = np.zeros(shape=(512, 512, 3), dtype=np.uint8)
        for k in range(len(mask_result[0, 0, :])):  # Tumor Mask ID
            cur_lesion = np.array(np.expand_dims(mask_result[:, :, k], axis=-1), dtype=np.uint8)
            msks_new = self.__enhance_seg_tumor_data(cur_liver, cur_lesion)
            if np.count_nonzero(msks_new) > 0:
                cm = np.where(cur_lesion>0, np.array([0, 255, 255], dtype=np.uint8), np.array([0,0,0], dtype=np.uint8)) # TO add color
                whole_mask += cm
                masks.append(cur_lesion)
                rois.append(roi_result[k])
                conf_values.append(conf_value_result[k])
                rois_img.append(roi_imgs_result[k])

        if ii[0] not in list(self.setCT_C_Seg.keys()):
            self.setCT_C_Seg[ii[0]] = {}
        if ii[0] not in list(self.setCT_C_tumor.keys()):
            self.setCT_C_tumor[ii[0]] = {}
        result = {"masks": masks, "whole_mask": whole_mask, 'rois': rois, "confidence_values": conf_values,
                  "rois_img": rois_img, "img": img}
        self.setCT_C_Seg[ii[0]][ii[1]] = result
        self.setCT_C_tumor[ii[0]][ii[1]] = msks_new
        return result

    def detect_hepatic_segments(self, setCT_B_Hep_Seg):
        pass

    def get_setCT_c_seg(self):
        return self.setCT_C_Seg

    def get_setCT_C_tumor(self):
        return self.setCT_C_tumor

    def __enhance_seg_tumor_data(self, cur_organ_msk, cur_tumor_msk):
        """
        To discard tumor segmented results that are not located in target organ
        :return:
        """
        cur_cnt, _ = cv2.findContours(cur_tumor_msk, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cur_mask = np.zeros(cur_tumor_msk.shape)
        for k in cur_cnt:
            new_mask = np.zeros(cur_tumor_msk.shape)
            new_mask = np.array(cv2.drawContours(new_mask, [k], -1, color=255, thickness=cv2.FILLED), dtype=np.uint8)
            if np.count_nonzero(np.bitwise_and(cur_organ_msk, new_mask)) > 0:
                cur_mask += new_mask
        return np.array(cur_mask, dtype=np.uint8)

    def __divid_tumors_eachother(self, img):
        cur_cnt, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cur_mask = np.zeros(img.shape)
        result = [] 
        for k in cur_cnt:
            new_mask = np.zeros(img.shape)
            result.append(np.array(cv2.drawContours(new_mask, [k], -1, color=255, thickness=cv2.FILLED), dtype=np.uint8))

