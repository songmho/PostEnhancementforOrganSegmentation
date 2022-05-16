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
from miaas.utils.polygon_drawer import PolygonDrawer

import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
# tf.config.experimental.set_memory_growth(gpus[0], True)


class LesionSegmentor:
    def __init__(self):
        self.setCT_C_Seg = {}
        self.setCT_C_tumor = {}
        self.config = tumor.TumorConfig()
        self.tumor_class_names = ['None', 'Tumor']
        self.is_contain_target = False
        self.margin = 30
        self.poly_drawer = PolygonDrawer()

    def initialize(self, std_name):
        self.setCT_C_Seg = {}
        self.setCT_C_tumor = {}
        self.is_contain_target = False
        self.std_name = std_name

    def clear_session(self):
        clear_session()

    def load_model(self, mi_type):
        # TUMOR_SEG_MODEL_DIR = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\mias_with_lirads\\mias\\miaas\\lirads\\models\\tumor_segment\\logs"
        # TUMOR_SEG_WEIGHT_DIR = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\mias_with_lirads\\mias\\miaas\\lirads\\models\\tumor_segment\\mask_rcnn_lesion_0100.h5"

        TUMOR_SEG_MODEL_DIR = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\mias_with_lirads\\mias\\miaas\\lirads\\models\\tumor_segment_2\\logs"
        if mi_type == "CT":
            TUMOR_SEG_WEIGHT_DIR = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\mias_with_lirads\\mias\\miaas\\lirads\\models\\tumor_segment_2\\mask_rcnn_tumor_000140.h5"
        else:
            TUMOR_SEG_WEIGHT_DIR = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\mias_with_lirads\\mias\\miaas\\lirads\\models\\tumor_segment_2\\mask_rcnn_lesion_mri_02000_selected.h5"
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

    def segment(self, img):
        results = self.tumor_detector.detect([img], verbose=0)
        result = results[0]
        rois = result['rois']
        final_rois = []
        for i in range(len(rois)):
            roi = rois[i]
            final_rois.append(img[roi[0] - self.margin:roi[2] + self.margin, roi[1] - self.margin:roi[3] + self.margin])
        result['rois'] = final_rois
        try:
            result['roi'] = rois[0]
        except:
            result['roi'] = []
        return result

    def segment_lesion_a_slice(self, sl):
        results = self.tumor_detector.detect([sl], verbose=0)
        mask_result, roi_result, conf_value_result, roi_imgs_result = \
            results[0]["masks"], results[0]["rois"], results[0]["scores"], results[0]["rois_img"]
        masks = np.array(np.zeros(shape=(512, 512, 1)), dtype=np.uint8)
        # print(len(results[0]["masks"][0, 0, :]), results[0]["scores"], np.unique(results[0]["masks"][:, :, :]))

        if len(results[0]["masks"][0, 0, :]) > 0:

            for m in range(len(results[0]["masks"][0,0,:])):
                cur_img = np.array(np.where(results[0]["masks"][:,:,m]==True, 255, 0), dtype=np.uint8)
                if cur_img.shape == (512, 512):
                    cur_img = np.expand_dims(cur_img, axis=-1)
                masks += cur_img

        masks = np.array(np.where(masks >0, 255, 0), dtype=np.uint8)
        sl_a = cv2.cvtColor(sl, cv2.COLOR_GRAY2BGR)
        masks_ = cv2.cvtColor(masks, cv2.COLOR_GRAY2BGR)
        sl_a = np.array(np.where(masks_==(255, 255, 255), (0,255, 255), sl_a), np.uint8)
        return masks, sl_a

    def segment_lesion(self, setCT_b, setCT_b_seg):
        setCT_b = setCT_b[list(setCT_b.keys())[0]]

        for name in setCT_b.keys():
            self.setCT_C_Seg[name] = {}
            self.setCT_C_tumor[name] = {}

        path_save = r"E:\1. Lab\Daily Results\2022\2201\0121\result\step3"
        path_save_liver = r"E:\1. Lab\Daily Results\2022\2201\0121\result\step3_liver"
        path_save_before = r"E:\1. Lab\Daily Results\2022\2201\0121\result\step3_tumor_before"
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
                    for m in range(len(results[0]["masks"][0,0,:])):
                        cur_img = np.where(results[0]["masks"][:,:,m]==True, 255, 0)
                        if cur_img.shape == (512, 512):
                            cur_img = np.expand_dims(cur_img, axis=-1)
                        masks += cur_img
                masks = np.array(np.where(masks>0, 255, 0), dtype=np.uint8)
                msk_cur_liver = np.array(setCT_b_seg[srs_name][key]["masks"], dtype=np.uint8)
                cv2.imwrite(os.path.join(path_save_liver, str(self.std_name)+"_"+str(srs_name)+"_"+str(int(key)).zfill(5)+".png"), msk_cur_liver)
                rrrr = np.array(np.where(masks==True, 255, 0), dtype=np.uint8)
                cv2.imwrite(os.path.join(path_save_before, str(self.std_name)+"_"+str(srs_name)+"_"+str(int(key)).zfill(5)+".png"), rrrr)
                msks_new = self.__enhance_seg_tumor_data(msk_cur_liver, masks)
                masks, rois, conf_values, rois_img = [], [], [], []
                for k in range(len(mask_result[0, 0, :])):    # Tumor Mask ID
                    cur_lesion = np.array(np.where(mask_result[:,:,k] == True, 255, 0), dtype=np.uint8)
                    msks_new = self.__enhance_seg_tumor_data(msk_cur_liver, cur_lesion)
                    if np.count_nonzero(msks_new) > 0:
                        masks.append(cur_lesion)
                        rois.append(roi_result[k])
                        conf_values.append(conf_value_result[k])
                        rois_img.append(roi_imgs_result[k])
                if len(masks) > 0:
                    count += 1
                    keys.append(key)
                # cv2.imshow("img", sl)
                # cv2.imshow("mask", msks_new)
                cv2.imwrite(os.path.join(path_save, str(self.std_name)+"_"+str(srs_name)+"_"+str()+"_"+str(int(key)).zfill(5)+".png"), msks_new)
                # cv2.waitKey(5)

                self.setCT_C_Seg[srs_name][key] = {"masks": masks, 'rois': rois, "confidence_values": conf_values, "rois_img":rois_img, "img": sl}
                self.setCT_C_tumor[srs_name][key] = msks_new
            print("       >> Phase and Slices ID Containing Liver: ", srs_name," / ",keys)

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

    def revise_seged_tumors(self):
        for sr_id, sls in self.setCT_C_Seg.items():
            for sl_id, data in sls.items():
                # key = self.display_result(self.setCT_C_Seg[sr_id][sl_id])
                # if key == ord("n"):     # No, need to fix
                #     self.poly_drawer.set_img(self.setCT_C_Seg[sr_id][sl_id]["img"])
                #     self.poly_drawer.run()
                #     result = self.poly_drawer.return_seg_data()
                #     self.setCT_C_Seg[sr_id][sl_id] = result
                #     msks_new = np.zeros(result["img"].shape)
                #     for i in result["masks"]:
                #         msks_new += i
                #     self.setCT_C_tumor[sr_id][sl_id] = msks_new
                # elif key == ord("p"):     # Pass
                    pass

    def display_result(self, data):
        """
        To display segmented tumors data
        """
        # To display seg results
        # To receive input key
        cv2.imshow("Tumor Segmentation Result", data["img"])
        key = cv2.waitKey(0)

        return key

    def __enhance_seg_tumor_data(self, cur_organ_msk, cur_tumor_msk):
        """
        To discard tumor segmented results that are not located in target organ
        :return:
        """
        cur_organ_msk = np.array(cur_organ_msk, np.uint8)
        cur_tumor_msk = np.array(cur_tumor_msk, np.uint8)
        cur_cnt, _ = cv2.findContours(cur_tumor_msk, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
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


if __name__ == "__main__":
    ls = LesionSegmentor()
    ls.load_model("mri")
    path_std = r"D:\Dataset\LLU Dataset\6218843_07202017 (MR)\01. Original Study\img\test-resized"
    path_save = r"E:\1. Lab\Daily Results\2022\2201\0115\lesion\6218843_07202017 (MR)"
    if not os.path.isdir(path_save):
        os.mkdir(path_save)

    for j in os.listdir(path_std):
        path_srs = os.path.join(path_std, j)
        os.mkdir(os.path.join(path_save, j))
        for i in os.listdir(path_srs):
            result = ls.segment(cv2.imread(os.path.join(path_srs, i)))
            result["masks"] = np.array(np.where(result["masks"] > 0, 255, 0), dtype=np.uint8)
            result_mask = np.zeros((512, 512))
            if result["masks"].shape[2] > 0:
                for k in range(result["masks"].shape[2]):
                    result_mask += result["masks"][:, :, k]
            cv2.imshow("origin", cv2.imread(os.path.join(path_srs, i)))
            cv2.imshow("test", np.array(result_mask, np.uint8))
            cv2.imwrite(os.path.join(path_save, j, i), np.array(result_mask, np.uint8))
            cv2.waitKey(5)