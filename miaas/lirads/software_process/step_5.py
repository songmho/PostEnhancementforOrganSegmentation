"""
Date: 2021. 04. 27.
Programmer: MH
Description: Code for step 5. Determining tumor type
"""
from miaas.lirads.util.tumor_progress_diagnosis import LesionTypeClassifier
from collections import Counter
import numpy as np
from miaas.lirads.constant import LIRADSPhase


class TumorTypeDeterminer:
    def __init__(self):
        self.t_type_classifier = LesionTypeClassifier()
        self.t_type_classifier.load_model()

    def sort_img_features(self, setCT_features, list_phase):
        """
        To sort image features
        :param setCT_features:
        :return:
        """
        list_excepted_phase_id = []
        list_max_phase = LIRADSPhase.LIST_PHASE.value
        for i in range(len(list_max_phase)):
            p = list_max_phase[i]
            is_not_include = True
            for p_i in list_phase:
                if p.lower() in p_i.lower():
                    is_not_include = False
            if is_not_include:
                list_excepted_phase_id.append(i)
        print(list_excepted_phase_id)
        self.img_features = {}
        for i in list(setCT_features.keys()):   # Tumor Group ID
            self.img_features[i] = {}
            for j in list(setCT_features[i].keys()): #Slice Group ID
                self.img_features[i][j] = []
                len_features = 0
                for k in range(len(setCT_features[i][j])):      # series
                    self.img_features[i][j].append(setCT_features[i][j][k]["WholeConf"])
                    len_features = len(setCT_features[i][j][k]["WholeConf"])
                for l in list_excepted_phase_id:
                    self.img_features[i][j].insert(l, [0.0]*len_features)
                print(len(self.img_features[i][j]))
        return self.img_features

    def predict_tumor_type(self, list_f):
        """
        To predict the tumor type in a group of CT slices for a tumor's section
        :return:
        """
        list_type = {}
        for i in list(list_f.keys()):
            list_type[i] = {}
            for j in list(list_f[i].keys()):
                result = self.t_type_classifier.predict([[list_f[i][j]]])     # To predict tumor type from a series of slices for a tumor
                list_type[i][j] = self.t_type_classifier.get_tumor_type(result)  # To get a tumor type
        return list_type

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