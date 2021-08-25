"""
Date: 2021. 04. 28.
Programmer: MH
Description: Code for classifying Li-RADS grade using gathered tumor information
"""
import os

from miaas.lirads.util.tumor_stage_classifier import BenignStageClassifier, MalignantStageClassifier
from miaas.lirads.constant import Stages, TumorType, TumorSeverity


class LIRADSStageClassifier:
    def __init__(self):
        self.HCC_classifier = MalignantStageClassifier()
        self.benign_classifier = BenignStageClassifier()

    def initialize(self, std_name):
        self.std_name = std_name

    def set_tumor_groups(self, tg):
        self.tumor_groups = tg

    def load_model(self):
        self.HCC_classifier.load_model()
        self.benign_classifier.load_model()

    def classify_stage(self):
        """
        To classify HCC stage based on LI-RADS Stage
        :param tumor_info:
        :return:
        """
        # path_save = r"E:\1. Lab\Daily Results\2021\2108\0820\result\step7"

        self.stages = {}
        for i, info in self.tumor_groups.items():
            self.tumor_groups[i]["stage"] = []
            tumor_info = info["major_features"]
            if tumor_info["tiv"]:
                self.tumor_groups[i]["stage"].append(Stages.LR_TIV)
            if info["type"]["Tumor Type"] in TumorSeverity.Benign:        ## LR-1 or LR-2
                data =[]
                self.tumor_groups[i]["stage"].append(self.benign_classifier.predict(data))
            elif info["type"]["Tumor Type"] == TumorType.HCC:               # LR-3, LR-4, or LR-5
                if tumor_info["APHE_Type"] in ["No", "Nonrim"]:
                    cur_info = [tumor_info["APHE_Type"], tumor_info["Lesion_Size"]["length"], tumor_info["Capsule"], tumor_info["Washout"],
                                tumor_info["Threshold_Growth"], tumor_info["Num_Major_Features"]]
                    self.tumor_groups[i]["stage"].append(self.HCC_classifier.predict(cur_info))
                else:
                    self.tumor_groups[i]["stage"].append(Stages.LR_M)
            else:               # LR-M for other Malignant Tumor
                self.tumor_groups[i]["stage"].append(Stages.LR_M)

            # if not os.path.isdir(os.path.join(path_save, self.std_name)):
            #     os.mkdir(os.path.join(path_save, self.std_name))
            #     f = open(os.path.join(path_save, self.std_name, "step_7.txt"), "w")
            #     f.write(str(i)+"  :  "+str(self.tumor_groups[i]["stage"]))
            #     f.close()

    def get_tumor_groups(self):
        return self.tumor_groups

    def generate_report(self):
        """
        To generate report for LI-RADS
        :return:
        """
        pass
