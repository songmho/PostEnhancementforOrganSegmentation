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
class MainProcess:
    def __init__(self):
        self.step1 = MedicalImageLoader()
        self.step2 = LiverRegionSegmentater()
        self.step3 = LegionSegmentor()
        self.step4 = ImageFeatureEvaluator()
        self.step5 = TumorTypeDeterminer()
        self.step6 = LIRADSFeatureComputer()
        self.step7 = LIRADSStageClassifier()

    def set_path(self, path_mi, path_prv_data):
        self.path_mi = path_mi
        self.path_prv_data = path_prv_data

    def initialize(self, std_name):
        self.step1.initialize()
        self.step2.initialize(std_name)
        self.step3.initialize(std_name)
        self.step4.initialize(std_name)
        self.step5.initialize(std_name)
        self.step6.initialize(std_name)
        self.step7.initialize(std_name)

    def diagnose(self):
        # Step 1. Load Medical Image
        print("Step 1. Load Medical Image")
        self.step1.set_path(self.path_mi)
        print("    Task 1. Check Medical Image Type")
        self.step1.check_mi_type()
        print("    Task 2. Load Medical Image")
        self.step1.load_medical_img()
        print("    Task 3. Convert Color Depth")
        self.step1.convert_color_depth()
        print("Acquisition Date: ", self.step1.acquisition_date)
        setCT_a = self.step1.get_setCT_a()
        setMed_img = self.step1.get_setMed_img()

        # Step 2. Segment Liver Region
        print("\n\nStep 2. Segment Liver Region")
        self.step2.set_setCT_b(setCT_a, setMed_img)
        print("    Task 1. Segment Liver Region")
        self.step2.segment_liver_regions()
        print("    Task 2. Discard Insignificant Slices")
        self.step2.discard_insig_slices()
        # print("    Task 3. Detect Liver Hepatic Segments (Not Completed)")
        # step2.detect_liver_hepatic_segments()

        setCT_b = self.step2.get_setCT_b()
        setCT_b_seg = self.step2.get_setCT_b_seg()

        # Step 3. Segment Lesions
        print("\n\nStep 3. Segment Lesions")
        self.step3.load_model()
        print("    Task 1. Checking Presence of Lesion")
        result = self.step3.check_target_presence(setCT_a, setCT_b_seg)
        print("    Task 2. Segmenting Lesions")
        self.step3.segment_lesion(setCT_a, setCT_b_seg)
        # print("    Task 3. Detecting Hepatic Segments for Each Lesion (Not Completed)")
        # step3.detect_hepatic_segments()

        setCT_c_tumor = self.step3.get_setCT_C_tumor()
        setCT_c_seg = self.step3.get_setCT_c_seg()


        # Step 4. Evaluate Image Features
        print("\n\nStep 4. Evaluate Image Features")
        print("    Task 1. Generate CT Slice Group")
        self.step4.generate_slice_group(self.step1.med_type, setMed_img)
        print("    Task 2. Generate Lesion Group")
        self.step4.make_lesion_group(setCT_c_tumor)
        print("    Task 3. Share Location of Lesions")
        self.step4.correct_segmented_lesion_location(self.step1.acquisition_date)
        print("    Task 4. Evaluate Image Features")
        self.step4.evaluate_image_feature(setCT_c_seg)
        print("    Task 5. Discard Insignificant Image Features")
        self.step4.discard_insignificant_image_features()

        tumor_groups = self.step4.get_tumor_groups()

        # Step 5. Determine Tumor Type
        self.step5.set_tumor_groups(tumor_groups)
        print("\n\nStep 5. Determine Tumor Type")
        print("    Task 1. Sort Image Features")
        self.step5.sort_img_features()
        print("    Task 2. Predict Tumor Type")
        self.step5.predict_tumor_type()

        tumor_groups = self.step5.get_tumor_groups()

        # Step 6. Compute LI-RADS Features
        self.step6.set_tumor_groups(tumor_groups)
        print("\n\nStep 6. Compute LI-RADS Features")
        print("    Task 1. Check Tumor Type")
        t_type_list = self.step6.get_tumor_type()
        print("    Task 2. Check Type of APHE")
        list_aphe = self.step6.get_APHE_type()
        print("    Task 3. Compute Size of Lesions")
        list_size = self.step6.compute_lesion_size(self.step1.voxels)
        print("    Task 4. Check presence of Capsule and Washout")
        capsules = self.step6.check_capsule()
        washouts = self.step6.check_washout()
        print("    Task 5. Compute Threshold Growth")
        self.step6.set_prv_data(self.path_prv_data)
        self.step6.set_setCT_a(setMed_img)
        th_growths = self.step6.compute_threshold_growth()
        print("    Task 6. Classify Tumor in Vein")
        self.step6.detect_vein_location(setCT_a)
        tivs = self.step6.compute_tumor_in_vein()
        print("    Task 7. Count Number of Major Features")
        self.step6.generate_major_feature_list(t_type_list, list_aphe, list_size, capsules, washouts, th_growths, tivs)
        tumor_groups = self.step6.get_tumor_groups()

        # Step 7. Determine LR Stage
        print("\n\nStep 7. Determine LR Stage")
        self.step7.set_tumor_groups(tumor_groups)
        self.step7.load_model()
        print("    Task 1. Classify Stage")
        self.step7.classify_stage()

    def print_diagnosis_result(self):
        print("\n\n[DIAGNOSIS RESULT]")
        for i in self.step7.get_tumor_groups().keys():
            print("  <Information of Tumor #"+str(i)+">")
            print("    - Tumor Type: ", self.step7.get_tumor_groups()[i]["type"]["Tumor Type"])
            print("    - Stage: ", self.step7.get_tumor_groups()[i]["stage"])
            print("    - Major Features: ", self.step7.get_tumor_groups()[i]["major_features"])
            print("    - Image Features for Phases")
            for key, value in self.step7.get_tumor_groups()[i]["features"].items():
                print("          "+key+": "+str(value))
            print("    - # of Slices for Phases")
            for key, value in self.step7.get_tumor_groups()[i]["mask"].items():
                print("          "+key+": "+str(len(value)), "    [",value[0][0], ", ",value[-1][0],"]" )
            print()


if __name__ == '__main__':
    lirads_process = MainProcess()
    # 7083077:  4 Phases, 2 Tumors ([Nonrim, WO], [Nonrim, WO]), [LR5, LR5]
    # 1611730:  4 Phases, 1 Tumor ([Nonrim, WO, Capsule]), LR5
    # 7064369:  4 Phases, 1 Tumor ([Nonrim, WO,]), LR5
    # 1668171:  4 Phases, 1 Tumor ([Nonrim, WO,]), LR5
    # 7048295:  4 Phases, 1 Tumor ([Nonrim, WO]), LR5

    # 8112000:  4 Phases, 1 Tumor ([Nonrim, WO, Capsule]), LR5        # NOT DETECTED
    # 7159233:  4 Phases, 1 Tumor ([Nonrim, WO]), LR5
    # 1383803:  4 Phases, 1 Tumor ([No, WO, Capsule]) LR5 (?)

    # 8523522:
    # 8082200_07312017:

    # "7006698", "1604844": NO DICOM


    # "1383803", "1611730", "1668171",  "7048295", "7064369",
    #  "7083077", "7159233", "8112000", "99. 8523522", "99. 8082200_07312017"
    for std_name in ["7083077", "7159233", "8112000", "99. 8523522", "99. 8082200_07312017"]:
        if len(std_name.split(" ")) > 1:
            print("["+std_name.split(" ")[1]+"]")
        else:
            print("["+std_name+"]")
        path_mi = r"E:\1. Lab\Daily Results\2021\2107\0728\LLU Dataset"+"\\"+str(std_name)+"\\00. DICOM\\target"              # 4 Phases, 2 Tumors ([Nonrim, WO], [Nonrim, WO])
    # path_mi = r"E:\1. Lab\Daily Results\2021\2107\0728\LLU Dataset\1611730\00. DICOM-COPY\target"              # 4 Phases, 2 Tumors ([Nonrim, WO], [Nonrim, WO])
    # std_name = "1611730"
        lirads_process.initialize(std_name)
        lirads_process.set_path(path_mi, path_prv_data=r"")
        lirads_process.diagnose()
        lirads_process.print_diagnosis_result()
        print("\n\n")
