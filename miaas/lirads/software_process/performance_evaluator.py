"""
Date: 2021. 08. 17.
Programmer: MH
Description: Code for evaluating performance using
"""
import cv2
import numpy as np


class PerformanceEvaluator:
    def __init__(self):
        self.tp, self.tn, self.fp, self.fn = 0, 0, 0, 0
        self.org = None
        self.prd = None

    def load_data(self, org, prd, step=None):
        """
        To load original data and predicted data
        """
        self.org = org
        self.prd = prd

        if type(org[0]) == np.ndarray:  # Input Type is Image
            for i in range(len(org)):
                cur_org = org[i]
                cur_prd = prd[i]
                if np.count_nonzero(cur_prd)>0:
                    if np.count_nonzero(cur_org)>0:
                        self.tp += 1
                    else:
                        self.fn += 1
                else:
                    if np.count_nonzero(cur_org)>0:
                        self.fp += 1
                    else:
                        self.tn += 1
        else:                           # Input Type is numeric or categorical
            # table for multi-class classification
            if step == 4:
                labels = range(len(org[0]))
                table = np.zeros(shape=(len(labels), len(labels))) # row: org, col: prd
                for i in range(len(org)):
                    for j in range(len(org[i])):
                        table[labels.index(org[i, j]), labels.index(prd[i, j])] += 1

                for trg in range(len(labels)):
                    for i in range(len(table)): # org
                        for j in range(len(table)): # prd
                            if trg==i and trg==j:
                                self.tp += table[i, j]
                            if trg==i and trg!=j:
                                self.fn += table[i, j]
                            if trg!=i and trg==j:
                                self.fp += table[i, j]
                            if trg != i and trg != j:
                                self.tn += table[i, j]

            elif step == 5:
                unq_org = np.unique(org)
                table = np.zeros(shape=(len(unq_org), len(unq_org))) # row: org, col: prd
                for i in range(len(org)):
                    table[unq_org.index(org[i]), unq_org.index(prd[i])] += 1

                for trg in range(len(unq_org)):
                    for i in range(len(table)): # org
                        for j in range(len(table)): # prd
                            if trg==i and trg==j:
                                self.tp += table[i, j]
                            if trg==i and trg!=j:
                                self.fn += table[i, j]
                            if trg!=i and trg==j:
                                self.fp += table[i, j]
                            if trg != i and trg != j:
                                self.tn += table[i, j]

            elif step == 7:
                unq_org = np.unique(org)
                table = np.zeros(shape=(len(unq_org), len(unq_org))) # low: org, col: prd
                for i in range(len(org)):
                    table[unq_org.index(org[i]), unq_org.index(prd[i])] += 1

                for trg in range(len(unq_org)):
                    for i in range(len(table)): # org
                        for j in range(len(table)): # prd
                            if trg==i and trg==j:
                                self.tp += table[i, j]
                            if trg==i and trg!=j:
                                self.fn += table[i, j]
                            if trg!=i and trg==j:
                                self.fp += table[i, j]
                            if trg != i and trg != j:
                                self.tn += table[i, j]


    def compute_avg_dsc(self):
        count = 0
        total_dsc = 0
        for i in range(len(self.org)):
            dsc = self.__compute_dsc(self.org[i], self.prd[i])
            if dsc >= 0:
                count += 1
                total_dsc += dsc
        return total_dsc/count

    def compute_accuracy(self):
        try:
            return (self.tp+self.tn)/(self.tp+self.tn+self.fp+self.fn)
        except:
            return 0

    def compute_precision(self):
        try:
            return (self.tp)/(self.tp+self.fp)
        except:
            return 0

    def compute_recall(self):
        try:
            return (self.tp)/(self.tp+self.fn)
        except:
            return 0

    def compute_f1_score(self):
        precision = self.compute_precision()
        recall = self.compute_recall()
        try:
            return (2*precision*recall)/(precision+recall)
        except:
            return 0

    def compute_seg_performance(self):
        avg_dsc = self.compute_avg_dsc()
        accuracy = self.compute_accuracy()
        precision = self.compute_precision()
        recall = self.compute_recall()
        try:
            return (avg_dsc+(accuracy+precision+recall)/3)/2
        except:
            return 0

    def compute_lr_features_performance(self):
        total_correctness = 0
        corr_rate = 0
        for i in range(len(self.org)):
            cor_aphe = 0
            cor_capsule = 0
            cor_washout = 0
            cor_tiv = 0
            cor_th_growth = 0
            cor_diameter = 0
            if self.org[i]["APHE_Type"] == self.prd[i]["APHE_Type"]:
                cor_aphe += 1
            if self.org[i]["Capsule"] == self.prd[i]["Capsule"]:
                cor_capsule += 1
            if self.org[i]["Washout"] == self.prd[i]["Washout"]:
                cor_washout += 1
            if self.org[i]["tiv"] == self.prd[i]["tiv"]:
                cor_tiv += 1
            if self.org[i]["Threshold_Growth"] == self.prd[i]["Threshold_Growth"]:
                cor_th_growth += 1
            if self.org[i]["Lesion_Size"]["length"] == self.prd[i]["Lesion_Size"]["length"]:
                if self.org[i]["APHE_Type"] == "No"\
                    and np.abs(self.org[i]["Lesion_Size"]["length"] - self.org[i]["Lesion_Size"]["length"]) < 10:
                   cor_diameter += 1
                if self.org[i]["APHE_Type"] == "Nonrim"\
                    and np.abs(self.org[i]["Lesion_Size"]["length"] - self.org[i]["Lesion_Size"]["length"]) < 5:
                    cor_diameter += 1
            corr_rate = (cor_aphe+cor_capsule+cor_washout+cor_tiv+cor_th_growth+cor_diameter)/6
            total_correctness += corr_rate
        total_correctness /= len(self.org)
        return total_correctness

    def __compute_dsc(self, org, prd):
        """
        To compute dsc of an image
        """
        overlapped = np.count_nonzero(cv2.bitwise_and(org, prd))
        x = np.count_nonzero(org)
        y = np.count_nonzero(prd)
        try:
            dsc = 2*(overlapped) / (x+y)
        except ZeroDivisionError:
            dsc = -1
        return dsc

