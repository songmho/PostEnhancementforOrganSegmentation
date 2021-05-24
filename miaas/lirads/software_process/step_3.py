"""
Date: 2021. 04. 26.
Programmer: MH
Description: Code for Step 3 of Liver Cancer Detection Process with ML
"""
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

    def clear_session(self):
        clear_session()

    def load_model(self):
        TUMOR_SEG_MODEL_DIR = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\mias_with_lirads\\mias\\miaas\\lirads\\models\\tumor_segment\\logs"
        TUMOR_SEG_WEIGHT_DIR = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\mias_with_lirads\\mias\\miaas\\lirads\\models\\tumor_segment\\mask_rcnn_lesion_0100.h5"
        self.tumor_detector = modellib.MaskRCNN(mode="inference", model_dir=TUMOR_SEG_MODEL_DIR, config=self.config)
        self.tumor_detector.load_weights(TUMOR_SEG_WEIGHT_DIR, by_name=True)

    def check_target_presence(self, setCT_b, setCT_b_seg):
        # for i in list(setCT_b.keys()):
        #     for j in range(len(setCT_b[i])):
        #         cur_mask = np.array(setCT_b_seg[i][j]["masks"], dtype=np.uint8)
        #         masked = np.expand_dims(cv2.bitwise_or(setCT_b[i][j], cur_mask, mask=cur_mask),-1)
        #         print(masked.shape)
        #         results = self.tumor_detector.detect([masked], verbose=0)       # To need to change
        #         if len(results[0]["masks"]) != 0:
        #             self.is_contain_target = True
        #             return
        pass

    def segment_lesion(self, setCT_b, setCT_b_seg):
        for i in list(setCT_b.keys()):  # Series ID
            self.setCT_C_Seg[i] = {}
            self.setCT_C_tumor[i]={}
            for j in list(setCT_b[i].keys()):   # Slice ID
                img = setCT_b[i][j]
                results = self.tumor_detector.detect([img], verbose=0)
                mask_result, roi_result, conf_value_result, roi_imgs_result =\
                    results[0]["masks"], results[0]["rois"], results[0]["scores"], results[0]["rois_img"]
                masks, rois, conf_values, rois_img = [], [], [], []
                for k in range(len(mask_result[0,0,:])):    # Tumor Mask ID
                    area_lesion = np.count_nonzero(mask_result[:, :, k])
                    cur_mask = np.array(np.expand_dims(mask_result[:, :, k], axis=-1), dtype=np.uint8)
                    cur_liver = np.array(setCT_b_seg[i][j]["masks"], dtype=np.uint8)

                    if len(np.unique(cur_liver))>0:  # If liver is segmented
                        mask_sum = cv2.bitwise_or(cur_mask, cur_liver)
                        area_sum = np.count_nonzero(mask_sum)
                        area_liver = np.count_nonzero(setCT_b_seg[i][j])
                        include_rate = 1-(area_sum-area_liver)/area_lesion

                        # if include_rate > 0:
                        #     masks.append(cur_mask)
                        #     rois.append(roi_result[k])
                        #     conf_values.append(conf_value_result[k])
                        #     rois_img.append(roi_imgs_result[k])

                        masks.append(cur_mask)
                        rois.append(roi_result[k])
                        conf_values.append(conf_value_result[k])
                        rois_img.append(roi_imgs_result[k])
                self.setCT_C_Seg[i][j] = {"masks": masks, 'rois': rois, "confidence_values": conf_values, "rois_img":rois_img, "img": img}
                self.setCT_C_tumor[i][j] = setCT_b[i]

    def segment_lesion_new(self, cur_liver, img):
        results = self.tumor_detector.detect([img], verbose=0)
        mask_result, roi_result, conf_value_result, roi_imgs_result = \
            results[0]["masks"], results[0]["rois"], results[0]["scores"], results[0]["rois_img"]
        masks, rois, conf_values, rois_img = [], [], [], []
        whole_mask = np.zeros((mask_result.shape[0], mask_result.shape[1], 3), dtype=np.uint8)
        for k in range(len(mask_result[0, 0, :])):  # Tumor Mask ID
            area_lesion = np.count_nonzero(mask_result[:, :, k])
            cur_mask = np.array(np.expand_dims(mask_result[:, :, k], axis=-1), dtype=np.uint8)
            # cm = np.where(cur_mask>0, 255, cur_mask)
            cm = np.where(cur_mask>0, np.array([0, 255, 255], dtype=np.uint8), np.array([0,0,0], dtype=np.uint8))
            whole_mask += cm
            if len(np.unique(cur_liver)) > 0:  # If liver is segmented
                mask_sum = cv2.bitwise_or(cur_mask, cur_liver)
                area_sum = np.count_nonzero(mask_sum)
                area_liver = np.count_nonzero(cur_liver)
                include_rate = 1 - (area_sum - area_liver) / area_lesion

                if include_rate > 0:
                    masks.append(cur_mask)
                    rois.append(roi_result[k])
                    conf_values.append(conf_value_result[k])
                    rois_img.append(roi_imgs_result[k])
        print(">>>>>. ", len(rois_img))
                # masks.append(cur_mask)
                # rois.append(roi_result[k])
                # conf_values.append(conf_value_result[k])
                # rois_img.append(roi_imgs_result[k])

        result = {"masks": masks,"whole_mask":whole_mask, 'rois': rois, "confidence_values": conf_values, "rois_img": rois_img,
                                  "img": img}
        return result
    def detect_hepatic_segments(self, setCT_B_Hep_Seg):
        pass

    def get_setCT_c_seg(self):
        return self.setCT_C_Seg

    def get_setCT_C_tumor(self):
        return self.setCT_C_tumor