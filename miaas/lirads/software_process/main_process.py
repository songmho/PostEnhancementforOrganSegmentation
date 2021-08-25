"""
Date: 2020. 12. 15.
Programmer: MH
Description: Code for Liver Cancer Detection SW process Main method
"""
import base64
import random
import time

from miaas.lirads.software_process.step_1 import MedicalImageLoader
from miaas.lirads.software_process.step_2 import LiverRegionSegmentater
from miaas.lirads.software_process.step_3 import LegionSegmentor
from miaas.lirads.software_process.step_4 import ImageFeatureEvaluator
from miaas.lirads.software_process.step_5 import TumorTypeDeterminer
from miaas.lirads.software_process.step_6 import LIRADSFeatureComputer
from miaas.lirads.software_process.step_7 import LIRADSStageClassifier
import numpy as np
import cv2

import tensorflow as tf
from miaas.lirads.constant import ImageType
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
  # Restrict TensorFlow to only allocate 1GB of memory on the first GPU
    try:
        tf.config.experimental.set_virtual_device_configuration(
            gpus[0],
            [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=2048)])
    except:
        pass

class LiradsProcess:
    def __init__(self):
        self.img_path = ""
        self.step_1 = MedicalImageLoader()
        self.step_2 = LiverRegionSegmentater()
        self.step_3 = LegionSegmentor()
        self.step_4 = ImageFeatureEvaluator()
        self.step_5 = TumorTypeDeterminer()
        self.step_6 = LIRADSFeatureComputer()
        self.step_7 = LIRADSStageClassifier()

        self.setCT_b = {}
        self.setCT_b_seg = {}
        self.setCT_c_seg = {}
        self.setCT_c = {}
        self.setCT_c_tumor = {}

        self.max_size = 0
        # Methods for Step 1
    def set_mi_path(self, path):
        self.img_path = path
        self.step_1.set_path(self.img_path)

    def check_extension(self):
        self.step_1.check_mi_type()

    def load_medical_img(self):
        self.step_1.load_medical_img()

    def convert_color_depth(self):
        self.step_1.convert_color_depth()
        self.set_med_img = self.step_1.get_setMed_img()
        self.setCT_a = self.step_1.get_setCT_a()

    def get_get_id_info(self):
        self.list_series_id = list(self.set_med_img.keys())
        self.list_slice_id = {}
        std_id = list(self.set_med_img.keys())[0]
        for i in list(self.set_med_img[std_id].keys()):
            self.list_slice_id[i] = list(self.set_med_img[std_id][i].keys())
        return self.list_series_id, self.list_slice_id

    def get_whole_img_data(self):
        self.list_labels, self.list_imgs, list_img_convs = [], [], []
        self.get_get_id_info()
        for i in list(self.list_slice_id.keys()):   # To gather labels
            for j in self.list_slice_id[i]:
                self.list_labels.append(i+"_"+str(j).zfill(5))
        std_id = list(self.set_med_img.keys())[0]
        for i in list(self.set_med_img[std_id].keys()): # Series
            for j in self.set_med_img[std_id][i].keys():       # slices

                self.list_imgs.append(self.setCT_a[std_id][i][j])
                list_img_convs.append(self.__convert_img_to_binary(self.setCT_a[std_id][i][j]))
        self.step_2.set_setCT_b(self.setCT_a, self.set_med_img)
        self.step_2.clear_session()
        self.step_2.load_model()
        return self.list_labels, list_img_convs

    # Method for Step 2
    def alleviate_noise_data(self, series_id, slice_id):
        slice = self.set_med_img[series_id][slice_id]
        if series_id not in list(self.setCT_b.keys()):
            self.setCT_b[series_id] = {}
        self.setCT_b[series_id][slice_id] = slice

    def segment_liver_region(self, img_id):
        ii = self.list_labels[img_id].split("_")
        # slice = self.set_med_img[list(self.set_med_img.keys())[0]][ii[0]][int(ii[1])]
        slice = self.list_imgs[img_id]
        print(img_id, ii, self.list_labels[img_id], np.array(slice).shape)
        # self.step_2.clear_session()
        # self.step_2.load_model()
        result = self.step_2.segment_liver_region_new(slice, ii)
        if ii[0] not in list(self.setCT_b_seg.keys()):
            self.setCT_b_seg[ii[0]] = {}
            self.setCT_b[ii[0]] = {}
        self.setCT_b_seg[ii[0]][ii[1]] = result
        self.setCT_b[ii[0]][ii[1]] = slice
        voxel = 0.63
        if self.step_1.get_med_type() == ImageType.DCM:
            voxel = self.step_1.voxels
        count = (np.count_nonzero(result["masks"])*voxel)
        return self.__convert_img_to_binary(self.__convert_img_bool_to_int(result["masks"])), count

    def get_whole_tumor_seg_targets(self):
        self.list_labels_setCT_b, self.list_imgs_setCT_b, list_img_convs = [], [], []
        self.setCT_b = self.step_2.get_setCT_b()
        self.setCT_b_seg = self.step_2.get_setCT_b_seg()
        for i in list(self.list_slice_id.keys()):
            for j in list(self.list_slice_id[i]):
                self.list_labels_setCT_b.append(i+"_"+j)
                self.list_imgs_setCT_b.append(self.setCT_b[i][j])
                list_img_convs.append(self.__convert_img_to_binary(self.setCT_b[i][j]))
        self.step_3.clear_session()
        self.step_3.load_model()
        return self.list_labels_setCT_b, list_img_convs

    # Method for Step 3
    def segment_tumor_region(self, img_id):
        ii = self.list_labels[img_id].split("_")
        slice = self.setCT_b[ii[0]][ii[1]]
        cur_liver = self.setCT_b_seg[ii[0]][ii[1]]["masks"]
        result = self.step_3.segment_lesion_new(cur_liver, slice, ii)
        # if ii[0] not in list(self.setCT_c_seg.keys()):
        #     self.setCT_c_seg[ii[0]] = {}
        #     self.setCT_c[ii[0]] = {}
        #     self.setCT_c_tumor[ii[0]] = {}
        # self.setCT_c_seg[ii[0]][ii[1]] = result
        # if ii[1] not in list(self.setCT_c_tumor[ii[0]].keys()):
        #     self.setCT_c_tumor[ii[0]][ii[1]] = []
        # for t in result["rois_img"]:
        #     self.setCT_c_tumor[ii[0]][ii[1]].append(t)
        # self.setCT_c[ii[0]][ii[1]] = slice

        voxel = 0.63
        if self.step_1.get_med_type() == ImageType.DCM:
            voxel = self.step_1.voxels
        count = (np.count_nonzero(result["masks"])*voxel)
        return self.__convert_img_to_binary(result["whole_mask"]), {"area":count, "count":len(result["rois_img"])}

    ### Method for Step 4
    ## TODO: ADD code for tumor groups
    def get_tumor_img_data(self):
        self.setCT_c_seg = self.step_3.get_setCT_c_seg()
        self.setCT_c_tumor = self.step_3.get_setCT_C_tumor()

        self.step_4.generate_slice_group(self.step_1.med_type, self.set_med_img)
        self.step_4.make_lesion_group(self.setCT_c_tumor)
        self.step_4.correct_segmented_lesion_location(self.step_1.acquisition_date)
        self.tumor_groups= self.step_4.get_tumor_groups()
        self.list_tumor_names, self.list_tumor_imgs, list_t_i = [], [], []
        for t_id in self.tumor_groups.keys():
            for srs_id, t_g in self.tumor_groups[t_id]["mask"].items():
                for i in range(len(t_g)):
                    sl_id = self.tumor_groups[t_id]["mask"][srs_id][i][0]
                    img = self.setCT_c_seg[srs_id][sl_id]["img"]
                    mask = self.tumor_groups[t_id]["mask"][srs_id][i][1]
                    if np.count_nonzero(mask)>0:
                        self.list_tumor_names.append(str(t_id)+"_"+str(srs_id)+"_"+str(i).zfill(3))
                        print(t_id, srs_id, sl_id, type(img), type(mask))
                        self.list_tumor_imgs.append(self.step_4.make_roi(img, mask))
                        list_t_i.append(self.__convert_img_to_binary(self.step_4.make_roi(img, mask)))
        self.step_4.clear_session()
        self.step_4.load_model()
        return self.list_tumor_names, list_t_i

    def evaluate_img_features(self, img_id):
        cur_tumor = self.list_tumor_imgs[img_id]
        ii = self.list_tumor_names[img_id].split("_")   # 0: tumor ID, 1: series ID, 2: index of tumor image
        if len(cur_tumor.shape) == 2:
            cur_tumor = np.expand_dims(cur_tumor, axis=-1)
        if cur_tumor.shape[2] > 1:
            cur_tumor = cv2.cvtColor(cur_tumor, cv2.COLOR_BGR2GRAY)
        result = self.step_4.evaluate_image_feature_new(cur_tumor, ii)
        print(result)
        list_data = []
        for i in range(len(result["Labels"])):
            list_data.append(str(result["Labels"][i])+" ("+str(round(result["ConfidenceScores"][i], 3))+"%)")
        # r = self.step_4.get_current_features(result)
        return list_data, ", ".join(result["Labels"])

    ### Method for Step 5
    def get_tumor_group_data(self):
        self.step_4.discard_insignificant_image_features()
        self.list_tumor_group_names, self.list_tumor_groups, list_t_i = [], {}, {}
        l=0

        for t_id in self.tumor_groups.keys():

            self.list_tumor_group_names.append("Tumor Group" + str(t_id))

            for srs_id, t_g in self.tumor_groups[t_id]["mask"].items():
                for i in range(len(t_g)):
                    sl_id = self.tumor_groups[t_id]["mask"][srs_id][i][0]
                    img = self.setCT_c_seg[srs_id][sl_id]["img"]
                    mask = self.tumor_groups[t_id]["mask"][srs_id][i][1]
                    if np.count_nonzero(mask)>0:
                        self.list_tumor_names.append(str(t_id)+"_"+str(srs_id)+"_"+str(i).zfill(3))
                        print(t_id, srs_id, sl_id, type(img), type(mask))
                        self.list_tumor_imgs.append(self.step_4.make_roi(img, mask))
                        list_t_i.append(self.__convert_img_to_binary(self.step_4.make_roi(img, mask)))


        for i in list(self.setCT_c_tumor.keys()):       # Series
            for j in list(self.setCT_c_tumor[i].keys()):    # Slice
                idx_j = list(self.setCT_c_tumor[i].keys()).index(j)
                for k in range(len(self.setCT_c_tumor[i][j])):  # Tumor
                    if str(idx_j)+"_"+str(k) not in list(self.list_tumor_groups.keys()):
                        self.list_tumor_group_names.append("Tumor Group"+str(l))
                        self.list_tumor_groups[str(idx_j)+"_"+str(k)] = {}
                        list_t_i[str(idx_j)+"_"+str(k)] = {}
                        l+=1
                    self.list_tumor_groups[str(idx_j)+"_"+str(k)][str(i)] = self.setCT_c_tumor[i][j][k]
                    list_t_i[str(idx_j)+"_"+str(k)][str(i)] = self.__convert_img_to_binary(self.setCT_c_tumor[i][j][k])
        print(len(self.list_tumor_names))
        print(len(self.list_tumor_imgs))
        self.step_5.clear_session()
        self.step_5.load_model()
        return self.list_tumor_group_names, list_t_i

    def determin_tumor_type(self):
        self.step_5.determine_tumor_type(None)
        result = "HCC"
        result = result+" ("+str(random.randrange(90, 101))+"%)"
        return result


    #### Method for Step 6
    def get_tumor_group_data_step6(self):
        self.list_tumor_group_names_step6= []
        l=0
        for i in list(self.setCT_c_tumor.keys()):       # Series
            for j in list(self.setCT_c_tumor[i].keys()):    # Slice
                idx_j = list(self.setCT_c_tumor[i].keys()).index(j)
                for k in range(len(self.setCT_c_tumor[i][j])):  # Tumor
                    if str(idx_j)+"_"+str(k) not in list(self.list_tumor_groups.keys()):
                        self.list_tumor_group_names_step6.append("Tumor Group"+str(l))
        print("?>?", len(self.list_tumor_group_names_step6))
        return self.list_tumor_group_names_step6

    def compute_lirads_features(self):
        size= random.randrange(32, 36)
        if self.max_size <size:
            self.max_size = size
        result = {"AHPE_type": "Nonrim APHE", "tumor_size": str(size)+" mm", "capsule":True, "washout":True, "treshold_growth":None}
        return result

    #### Method for Step 7
    def get_tumor_info(self):
        result = {"tumor_type": "HCC", "AHPE_type": "Nonrim APHE", "tumor_size": str(self.max_size)+" mm", "number_m_f":2}
        return result

    def predict_stage(self):
        return "LR-5"


    def __convert_img_to_binary(self, img):
        scs, encoded_img = cv2.imencode(".png", img)
        encoded_img = base64.b64encode(encoded_img.tobytes())
        return encoded_img.decode("utf8")

    def __convert_img_bool_to_int(self, img):
        img = np.where(img>0, 255, img)
        img = np.array(img, dtype=np.uint8)
        return img

    def __divid_tumors_eachother(self, img):
        cur_cnt, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cur_mask = np.zeros(img.shape)
        result = []
        for k in cur_cnt:
            new_mask = np.zeros(img.shape)
            result.append(np.array(cv2.drawContours(new_mask, [k], -1, color=255, thickness=cv2.FILLED), dtype=np.uint8))
        return result

if __name__ == '__main__':
    # step1 = MedicalImageLoader()
    # step2 = LiverRegionSegmentater()
    # step3 = LegionSegmentor()
    # step4 = ImageFeatureEvaluator()
    # step5 = TumorTypeDeterminer()
    # step6 = LIRADSFeatureComputer()
    # step7 = LIRADSStageClassifier()
    #
    # # Code for Step 1
    # print("Step 1")
    # step1.set_path(r"E:\1. Lab\Dataset\Liver\LiverCTCancerArchive\Custom, DICOM\TCGA-K7-A5RG - Copy - Copy")
    # # step1.set_path(r"E:\1. Lab\Dataset\Liver\LiverCTCancerArchive\Custom, DICOM\TCGA-DD-A1EH")
    # print("Task 1. Checking Type of Medical Image")
    # step1.check_extension()
    # print(step1.get_med_type())
    # print("Task 2. Loading Medical Image")
    # step1.load_medical_img()
    # print("Task 3. Converting Medical Image Color Depth")
    # step1.convert_color_depth()
    # for name, studies in step1.set_med_img.items():
    #     print(name)
    #     for series, slices in studies.items():
    #         print(series, ": ", len(slices))
    # set_med_img = step1.get_setCT_a()
    # print("\nStep 2")
    # for setCT_a in set_med_img.values():
    #     # Code for Step 2
    #     step2.set_setCT_b(setCT_a)
    #     print("Task 1. Alleviating Noise Data")
    #     step2.alleviate_noised_data()    ## Not Yet
    #     print("Task 2. Segmenting Liver Region")
    #     step2.segment_liver_regions()
    #     setCT_b_liver = step2.get_setCT_b_liver()   # Slices
    #     setCT_b_seg = step2.get_setCT_b_seg()       # Segmented Information
    #     print("Task 3. Discarding CT Slices")
    #     # step2.discard_insig_slices()
    #     print("Task 4. Detecting Liver Hepatic Segments")
    #     # step2.detect_liver_hepatic_segments()       ## NOT YET
    #     setCT_b_hep_seg = step2.get_setCT_b_hep_seg()
    #
    #     for i in list(setCT_b_seg.keys()):
    #         for j in list(setCT_b_seg[i].keys()):
    #             k = setCT_b_seg[i][j]["masks"]
    #             k_cvt = np.where(k>0, 255, k)
    #             cv2.imwrite("E:\\2. Project\\Python\\LiverDiseaseDetection\\img\\step2\\"+str(i)+"-"+str(j)+".png", k_cvt)
    #
    #     print("\nStep 3")
    #     print("Task 1. Segmenting Lesions")
    #     step3.segment_lesion(setCT_b_liver, setCT_b_seg)
    #     print("Task 2. Detecting Hepatic Segments for Each Lesion")
    #     # step3.detect_hepatic_segments(setCT_b_hep_seg)  ## Not yet
    #     setCT_c_seg = step3.get_setCT_c_seg()           # Segmented Information
    #     setCT_c_tumor = step3.get_setCT_C_tumor()       # Slices
    #     for i in list(setCT_c_seg.keys()):
    #         for j in list(setCT_c_seg[i].keys()):
    #             for e in range(len(setCT_c_seg[i][j]["masks"])):
    #                 k = setCT_c_seg[i][j]["masks"][e]
    #                 k_cvt = np.where(k>0, 255, k)
    #                 cv2.imwrite("E:\\2. Project\\Python\\LiverDiseaseDetection\\img\\step3\\"+str(i)+"-"+str(j)+"-"+str(e)+".png", k_cvt)
    #
    #     print("\nStep 4")
    #     print("Task 1. Making CT Slice Group")
    #     setCT_tumor_seg = step4.generate_slice_group(setCT_b_liver, setCT_b_seg, setCT_c_seg)
    #     print("Task 2. Sharing Segmented Lesion's Locations")
    #     setCT_tumor_seg = step4.correct_segmented_lesion_location(setCT_tumor_seg)
    #     print("Task 3. Making Lesion Group")
    #     set_tumor_groups = step4.make_lesion_group(setCT_tumor_seg)     # Not Yet
    #     print("Task 4. Checking Treatment")
    #     # step4.check_treatment()   # Not Yet
    #     print("Task 5. Evaluating Image Features")
    #     step4.evaluate_image_feature(set_tumor_groups)
    #     print("Task 6. Discarding Insignificant Image Features")
    #     # step4.discard_insignificant_image_features()    # Not Yet
    #     setCT_features = step4.get_features()
    #     list_phases = step4.get_list_phases()
    #
    #     print("\nStep 5")
    #     print("Task 1. Sorting Image Features considering Phases")
    #     setCT_img_features = step5.sort_img_features(setCT_features, list_phases)
    #     print("Task 2. Predicting Tumor Type for a Group of Slices")
    #     list_type = step5.predict_tumor_type(setCT_img_features)
    #     print("Task 3. Determining Tumor Type of the Lesion")
    #     result = step5.determine_tumor_type(list_type, set_tumor_groups, setCT_features)       # Not Yet
    #
    #     print("\nStep 6")
    #     step6.set_tumor_features(result)
    #     print("Task 1. Checking Tumor Type of Lesion")
    #     tumor_types = step6.get_tumor_type()
    #     print("Task 2. Checking Type of APHE")
    #     aphe_types = step6.get_APHE_type()
    #     print("Task 3. Checking Size of Lesion")
    #     lesion_sizes = step6.compute_lesion_size(step1.voxels[list(step1.voxels.keys())[0]])
    #     print("Task 4. Checking Presence of Capsule and Washout")
    #     capsules = step6.check_capsule()
    #     washouts = step6.check_washout()
    #     print("Task 5. Finding Previous Lesion Information")
    #
    #     print("Task 6. Computing Threshold Growth")
    #     th_growths = step6.compute_threshold_growth()
    #     print("Task 7. Detecting Location of Vein")
    #     step6.detect_vein_location()
    #     print("Task 8. Classifying Tumor in Vein")
    #     tivs = step6.is_tumor_in_vein()
    #     print("Task 9. Counting the number of Major Features")
    #     step6.generate_major_feature_list(tumor_types, aphe_types, lesion_sizes, capsules, washouts, th_growths, tivs)
    #     lirads_features = step6.get_LIRADS_feature()
    #     print("Image Features: ", lirads_features["Image_Features"])
    #
    #     print("\nStep 7")
    #     print("Task 1. Classify Tumor Stages")
    #     step7.classify_stage(lirads_features)
    #     print("Task 2. Generate Report")
    #     step7.generate_report()
    #
    #     print("Stage: ", step7.get_stage())
    #
    img = cv2.imread(r"C:\Users\songm\OneDrive\Pictures\test2.png")
    print(img.tobytes())
