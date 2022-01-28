import os
import shutil

target_std = "6218843_07202017"
path_src = os.path.join(r"E:\1. Lab\Daily Results\2022\2201\0117\Original Slices\mask - Tumor", target_std)
path_save = r"E:\1. Lab\Daily Results\2022\2201\0117\Tumor Segementation Dataset - 5\msks\origin"

for i in os.listdir(path_src):
    for j in os.listdir(os.path.join(path_src, i)):
        shutil.copy(os.path.join(path_src, i, j),os.path.join(path_save, target_std+"_"+i+"_"+j.split(".")[0]+".png"))


# import os
# import cv2
# import numpy as np
#
# p = r"E:\1. Lab\Daily Results\2022\2201\0117\data for classifying tumor image features from 5 studies\origin"
# p = r"E:\1. Lab\Daily Results\2022\2201\0117\data for classifying tumor image features from 5 studies\Increasing Size\origin"
# list_x = []
# list_y = []
# for i in os.listdir(p):
#     img = cv2.imread(os.path.join(p, i), cv2.IMREAD_GRAYSCALE)
#     list_x.append(img.shape[1])
#     list_y.append(img.shape[0])
#
# print("Average: ", np.average(list_x), np.average(list_y))
# print("Max: ", np.max(list_x), np.max(list_y))
# print("Min: ", np.min(list_x), np.min(list_y))
# print("Median: ", np.median(list_x), np.median(list_y))
# print("\n\n")
# p = r"F:\SELab\700.... PROJECTS\2022.02, Liver Cancer Diagnosis System with LI-RADS\9. Medical Image Dataset\03. Tumor Image Feature Classification\train"
# list_x = []
# list_y = []
# for i in os.listdir(p):
#     img = cv2.imread(os.path.join(p, i), cv2.IMREAD_GRAYSCALE)
#     list_x.append(img.shape[1])
#     list_y.append(img.shape[0])
#
# p = r"F:\SELab\700.... PROJECTS\2022.02, Liver Cancer Diagnosis System with LI-RADS\9. Medical Image Dataset\03. Tumor Image Feature Classification\test"
# for i in os.listdir(p):
#     img = cv2.imread(os.path.join(p, i), cv2.IMREAD_GRAYSCALE)
#     list_x.append(img.shape[1])
#     list_y.append(img.shape[0])
#
# print("Average: ", np.average(list_x), np.average(list_y))
# print("Max: ", np.max(list_x), np.max(list_y))
# print("Min: ", np.min(list_x), np.min(list_y))
# print("Median: ", np.median(list_x), np.median(list_y))