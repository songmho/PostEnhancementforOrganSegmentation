"""

"""
import os
import cv2

path = r"D:\Dataset\LLU Dataset\6218843_07202017 (MR)\01. Original Study\img"
path_save = r"E:\1. Lab\Daily Results\2021\2109\0924\img"

for i in os.listdir(path):
    cur_path = os.path.join(path, i)
    if i == "backup":
        continue
    for j in os.listdir(cur_path):
        img = cv2.imread(os.path.join(cur_path, j))
        cv2.imwrite(os.path.join(path_save, i+"_"+str(j).zfill(5)+".png"), img)


# for i in os.listdir(path):
#     cur_path = os.path.join(path, i, "T2SPIR", "Ground")
#     list_sl = os.listdir(cur_path)
#     for j in range(len(list_sl)):
#         img = cv2.imread(os.path.join(cur_path, list_sl[j]))
#         img[img>100] = 0
#         img[img>0] = 255
#         cv2.imwrite(os.path.join(path_save, i+"_"+str(j+1).zfill(5)+".png"), img)