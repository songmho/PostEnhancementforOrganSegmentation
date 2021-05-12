"""
Date: 2021. 04. 28.
Programmer: MH
Description: Code for classifying Li-RADS grade using gathered tumor information
"""
from miaas.lirads.util.tumor_stage_classifier import BenignStageClassifier, MalignantStageClassifier
from miaas.lirads.constant import Stages, TumorType, TumorSeverity


class LIRADSStageClassifier:
    def __init__(self):
        self.HCC_classifier = MalignantStageClassifier()
        self.benign_classifier = BenignStageClassifier()
        self.HCC_classifier.load_model()
        self.benign_classifier.load_model()
        self.stage = Stages.none

    def classify_stage(self, tumor_info):
        """
        To classify HCC stage based on LI-RADS Stage
        :param tumor_info:
        :return:
        """
        self.stages = {}
        for i in list(tumor_info.keys()):
            self.stages[i] = []
            if tumor_info[i]["tiv"]:
                self.stages[i].append(Stages.LR_TIV)
            if tumor_info[i]["Tumor_Type"] in TumorSeverity.Benign:        ## LR-1 or LR-2
                data =[]
                self.stages[i].append(self.benign_classifier.predict(data))
            elif tumor_info[i]["Tumor_Type"]==TumorType.HCC:               # LR-3, LR-4, or LR-5
                if tumor_info[i]["APHE_Type"] in ["No", "Nonrim"]:
                    cur_info = [tumor_info[i]["APHE_Type"], tumor_info[i]["Lesion_Size"], tumor_info[i]["Capsule"], tumor_info[i]["Washout"],
                                tumor_info[i]["Threshold_Growth"], tumor_info[i]["Num_Major_Features"]]
                    self.stages[i].append(self.HCC_classifier.predict(cur_info))
                else:
                    self.stages[i].append(Stages.LR_M)
            else:               # LR-M for other Malignant Tumor
                self.stages[i].append(Stages.LR_M)

    def generate_report(self):
        """
        To generate report for LI-RADS
        :return:
        """
        pass

    def get_stage(self):
        return self.stages