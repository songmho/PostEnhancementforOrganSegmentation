"""
Date: 2021. 08. 05.
Programmer: MH
Description: Code for LI-RADS Process
"""

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
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
  # Restrict TensorFlow to only allocate 2GB of memory on the first GPU
    try:
        tf.config.experimental.set_virtual_device_configuration(
            gpus[0],
            [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=2048)])
    except:
        pass


if __name__ == '__main__':
    path_mi = r"E:\1. Lab\Daily Results\2021\2107\0728\LLU Dataset\03. 7083077\00. DICOM\target"
    path_prv_data = r""

    step1 = MedicalImageLoader()
    step2 = LiverRegionSegmentater()
    step3 = LegionSegmentor()
    step4 = ImageFeatureEvaluator()
    step5 = TumorTypeDeterminer()
    step6 = LIRADSFeatureComputer()
    step7 = LIRADSStageClassifier()

    # Step 1. Load Medical Image
    print("Step 1. Load Medical Image")
    step1.set_path(path_mi)
    print("    Task 1. Check Medical Image Type")
    step1.check_mi_type()
    print("    Task 2. Load Medical Image")
    step1.load_medical_img()
    print("    Task 3. Convert Color Depth")
    step1.convert_color_depth()
    print("Acquisition Date: ", step1.acquisition_date)
    setCT_a = step1.get_setCT_a()
    setMed_img = step1.get_setMed_img()

    # Step 2. Segment Liver Region
    print("\n\nStep 2. Segment Liver Region")
    step2.set_setCT_b(setCT_a)
    print("    Task 1. Segment Liver Region")
    step2.segment_liver_regions()
    print("    Task 2. Discard Insignificant Slices (Not Completed)")
    # step2.discard_insig_slices()
    print("    Task 3. Detect Liver Hepatic Segments (Not Completed)")
    # step2.detect_liver_hepatic_segments()

    setCT_b = step2.get_setCT_b()
    setCT_b_seg = step2.get_setCT_b_seg()

    # Step 3. Segment Lesions
    print("\n\nStep 3. Segment Lesions")
    step3.load_model()
    print("    Task 1. Checking Presence of Lesion (Not Completed)")
    result = step3.check_target_presence(setCT_a, setCT_b_seg)
    print("    Task 2. Segmenting Lesions")
    step3.segment_lesion(setCT_a, setCT_b_seg)
    print("    Task 3. Detecting Hepatic Segments for Each Lesion (Not Completed)")
    # step3.detect_hepatic_segments()

    setCT_c_tumor = step3.get_setCT_C_tumor()
    setCT_c_seg = step3.get_setCT_c_seg()


    # Step 4. Evaluate Image Features
    print("\n\nStep 4. Evaluate Image Features")
    print("    Task 1. Generate CT Slice Group")
    step4.generate_slice_group(step1.med_type, setMed_img)
    print("    Task 2. Generate Lesion Group")
    step4.make_lesion_group(setCT_c_tumor)
    print("    Task 3. Share Location of Lesions")
    step4.correct_segmented_lesion_location(step1.acquisition_date)
    print("    Task 4. Evaluate Image Features")
    step4.evaluate_image_feature(setCT_c_seg)
    print("    Task 5. Discard Insignificant Image Features")
    step4.discard_insignificant_image_features()

    tumor_groups = step4.get_tumor_groups()
    print("    # of Tumor Groups: ", len(tumor_groups.keys()), tumor_groups.keys())

    # Step 5. Determine Tumor Type
    step5.set_tumor_groups(tumor_groups)
    print("\n\nStep 5. Determine Tumor Type")
    print("    Task 1. Sort Image Features")
    step5.sort_img_features()
    print("    Task 2. Predict Tumor Type")
    step5.predict_tumor_type()

    tumor_groups = step5.get_tumor_groups()
    print("    # of Tumor Groups: ", len(tumor_groups.keys()), tumor_groups.keys())

    # Step 6. Compute LI-RADS Features
    step6.set_tumor_groups(tumor_groups)
    print("\n\nStep 6. Compute LI-RADS Features")
    t_type_list = step6.get_tumor_type()
    print("    Task 1. Check Type of APHE")
    list_aphe = step6.get_APHE_type()
    print("    Task 2. Compute Size of Lesions")
    list_size = step6.compute_lesion_size(step1.voxels)
    print("    Task 3. Check presence of Capsule and Washout")
    capsules = step6.check_capsule()
    washouts = step6.check_washout()
    print("    Task 4. Find Previous Lesions Information in Same Location")
    step6.set_prv_data(path_prv_data)
    print("    Task 5. Compute Threshold Growth")
    step6.set_setCT_a(setMed_img)
    th_growths = step6.compute_threshold_growth()
    print("    Task 6. Classify Tumor in Vein")
    step6.detect_vein_location(setCT_a)
    tivs = step6.compute_tumor_in_vein()

    print("    Task 7. Count Number of Major Features")
    step6.generate_major_feature_list(t_type_list, list_aphe, list_size, capsules, washouts, th_growths, tivs)
    tumor_groups = step6.get_tumor_groups()
    print("    # of Tumor Groups: ", len(tumor_groups.keys()), tumor_groups.keys())

    # Step 7. Determine LR Stage
    print("\n\nStep 7. Determine LR Stage")
    step7.set_tumor_groups(tumor_groups)
    step7.load_model()
    print("    Task 1. Classify Stage")
    step7.classify_stage()
    print(step7.get_tumor_groups().keys())
    for i in step7.get_tumor_groups().keys():
        print(step7.get_tumor_groups()[i]["type"]["Tumor Type"], step7.get_tumor_groups()[i]["stage"],
          step7.get_tumor_groups()[i]["major_features"], step7.get_tumor_groups()[i]["features"], step7.get_tumor_groups()[i]["mask"].keys())
        print()
