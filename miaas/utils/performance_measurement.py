"""
Date: 2021. 11. 16.
Programmer: MH
Description: Code for Measuring performance
"""
import os

import numpy as np
import cv2


class ImgDataPerformanceMeasurer:
    def __init__(self):
        pass

    def compute_dsc(self, org, trg):
        """
        To compute dice similarity coefficient
        dsc = 2*TP / ((TP+FP)+(TP+FN))
        :param org: ndarray,
        :param trg: ndarray,
        :return: dsc
        """
        num_org = np.count_nonzero(org)
        num_trg = np.count_nonzero(trg)
        num_inter = np.count_nonzero(cv2.bitwise_and(org, trg))
        if num_org+num_trg>0:
            return 2*num_inter / (num_trg+num_org)
        elif num_org==0 and num_trg==0:
            return -1


    def compute_avg_dsc(self, orgs, trgs):
        """
        To compute average DSCs
        :param orgs: list,
        :param trgs: list,
        :return:
        """
        avg_dsc = []
        for i in range(len(orgs)):
            result = self.compute_dsc(orgs[i], trgs[i])
            if result != -1:
                avg_dsc.append(result)
        return np.average(avg_dsc)

    def compute_confusion_matrix(self, orgs, trgs):
        """
        To compute confusion matrix
        :param orgs:
        :param trgs:
        :return:
        """
        self.tp, self.tn, self.fp, self.fn = 0, 0, 0, 0
        self.orgs_bool, self.trgs_bool = [], []
        for i in range(len(orgs)):
            if np.count_nonzero(orgs[i]) > 0 and np.count_nonzero(trgs[i]) > 0:
                self.tp += 1
            elif np.count_nonzero(orgs[i]) == 0 and np.count_nonzero(trgs[i]) == 0:
                self.tn += 1
            elif np.count_nonzero(orgs[i]) == 0 and np.count_nonzero(trgs[i]) > 0:
                self.fp += 1
            elif np.count_nonzero(orgs[i]) > 0 and np.count_nonzero(trgs[i]) == 0:
                self.fn += 1

        self.total = self.tp+self.tn+self.fp+self.fn

    def compute_accuracy(self):
        """
        To compute accuracy
        :return:
        """
        if self.total != 0:
            return (self.tp+self.tn)/self.total
        else:
            return 0.0

    def compute_precision(self):
        """
        To compute precision
        :return:
        """
        if self.tp+self.fp !=0:
            return self.tp / (self.tp+self.fp)
        else:
            return 0.0

    def compute_recall(self):
        """
        To compute recall
        :return:
        """
        if self.tp+self.fn !=0:
            return self.tp / (self.tp+self.fn)
        else:
            return 0.0


if __name__ == '__main__':
    path_src = r"D:\Dataset\Liver TUmor Dataset (Medical Decathlon)\labels\liver"
    path_trg = r"E:\1. Lab\Daily Results\2021\2111\1122\result2"
    # path_trg = r"E:\1. Lab\Daily Results\2021\2107\0723\HAWK-1 Dataset 1\Dataset 1"
    # for k in range(80):
    for k in os.listdir(path_trg):
        path_cur_src = os.path.join(path_src, str(k).zfill(3))
        path_cur_trg = os.path.join(path_trg, str(k).zfill(3))
        list_src = []
        if not os.path.isdir(path_cur_trg):
            continue
        for i in os.listdir(path_cur_src):
            list_src.append(cv2.imread(os.path.join(path_cur_src, i)))

        list_trg = []
        # for i in os.listdir(os.path.join(path_cur_trg)):
        #     list_trg.append(cv2.imread(os.path.join(path_cur_trg, i)))
        for i in os.listdir(os.path.join(path_cur_trg, "5.result")):
            list_trg.append(cv2.imread(os.path.join(path_cur_trg, "5.result",i)))

        idpm = ImgDataPerformanceMeasurer()
        idpm.compute_confusion_matrix(list_src, list_trg)
        avg_dsc = idpm.compute_avg_dsc(list_src, list_trg)
        accuracy = idpm.compute_accuracy()
        precision = idpm.compute_precision()
        recall = idpm.compute_recall()
        print(k, ", ", round(avg_dsc, 3), ", ", round(accuracy, 3), ", ", round(precision, 3), ", ", round(recall, 3))
