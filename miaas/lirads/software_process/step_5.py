"""
Date: 2021. 04. 27.
Programmer: MH
Description: Code for step 5. Determining tumor type
"""
import os

from miaas.lirads.util.tumor_progress_diagnosis import LesionTypeClassifier
from collections import Counter
import numpy as np
from miaas.lirads.constant import LIRADSPhase


class TumorTypeDeterminer:
    def __init__(self):
        self.t_type_classifier = LesionTypeClassifier()
        self.t_type_classifier.load_model()
        self.img_features = {} # {TUMOR_ID: [[... ],[... ],.. ], TUMOR_ID: [... ]}
        self.LEN_FEATURES = 9

    def initialize(self, std_name):
        self.img_features = {}  # {TUMOR_ID: [[... ],[... ],.. ], TUMOR_ID: [... ]}
        self.std_name = std_name
    def set_tumor_groups(self, tg):
        self.tumor_groups = tg

    def sort_img_features(self):
        """
        To sort image features
        :param setCT_features:
        :return:
        """
        list_excepted_phase_id = []
        list_max_phase = LIRADSPhase.LIST_PHASE.value

        for t_id, info in self.tumor_groups.items():
            self.img_features[t_id] = []
            for srs_id, features in info["features"].items():
                for phase_name in list_max_phase:
                    if phase_name in list(features.keys()):
                        self.img_features[t_id].append(features[phase_name]["WholeConf"])
                    else:    # Not in information for the pahse
                        self.img_features[t_id].append([0.0]*self.LEN_FEATURES)

    def predict_tumor_type(self):
        """
        To predict the tumor type in a group of CT slices for a tumor's section
        :return:
        """
        path_save = r"E:\1. Lab\Daily Results\2021\2108\0817\result\step5"

        for t_id, list_features in self.img_features.items():
            result = self.t_type_classifier.predict([[list_features]])
            self.tumor_groups[t_id]["type"] = self.t_type_classifier.get_tumor_type(result)

            if not os.path.isdir(os.path.join(path_save, self.std_name)):
                os.mkdir(os.path.join(path_save, self.std_name))
            f = open(os.path.join(path_save, self.std_name, "step_5.txt"), "w")
            f.write(str(t_id)+"  :  "+str(self.tumor_groups[t_id]["type"]))
            f.close()

    def get_tumor_groups(self):
        return self.tumor_groups


    def determine_tumor_type(self, setCT_tumor_types, setCT_tumor_group, setCT_features):
        result = []
        tumor_info = {}
        setCT_tumor_types_bf = {}
        # To make setCT_tumor_types_bf consisting of list for tumor type
        for i in list(setCT_tumor_types.keys()):
            setCT_tumor_types_bf[i] = []
            for j in list(setCT_tumor_types[i].keys()):
                setCT_tumor_types_bf[i].append(setCT_tumor_types[i][j]["Tumor Type"])   # To pick only tumor type from dictionary type data

        for i in list(setCT_tumor_types.keys()):    # Tumor Group
            biggest_tumor_id = -1
            biggest_tumor_size = -1
            biggest_mask = None
            tumor_info[i] = {"type": "", "features": [], "masks": None}
            # try:
            result_exist = list(Counter(setCT_tumor_types_bf[i]).keys())[0]   # To check the most existed tumor type
            for j in list(setCT_tumor_group[i].keys()):     # Slice
                cur_mask = setCT_tumor_group[i][j][0]["masks"]  # To select mask for first CT slice TODO Need to change following data structure
                if biggest_tumor_size < np.count_nonzero(cur_mask):
                    biggest_tumor_size = np.count_nonzero(cur_mask)
                    biggest_tumor_id = j
                    biggest_mask = cur_mask
            # result.append(result_exist)
            for f in setCT_features[i][biggest_tumor_id]:
                tumor_info[i]["features"] += f["Labels"]
            tumor_info[i]["features"] = list(set(tumor_info[i]["features"]))    # To remove overlapped features
            tumor_info[i]["masks"] = biggest_mask
            if result_exist == setCT_tumor_types[i][biggest_tumor_id]["Tumor Type"]:  # TODO Need to change following data type
                result.append(result_exist)
                tumor_info[i]["type"] = result_exist
            else:
                result.append(setCT_tumor_types[i][biggest_tumor_id]["Tumor Type"])
                tumor_info[i]["type"] = setCT_tumor_types[i][biggest_tumor_id]["Tumor Type"]
            # except:
            #     result.append("")
            #     tumor_info[i]["type"] = ""
        return tumor_info