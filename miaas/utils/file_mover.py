import os
import random
import shutil
import cv2
import numpy as np

std_id = "7267285_03162017"
path_img = os.path.join(r"D:\Dataset\LLU Dataset\7267285_03162017 (MR)\01. Original Image\03. PNG\selected")
path_label = os.path.join(r"D:\Dataset\LLU Dataset\7267285_03162017 (MR)\02. Label\04. PNG\02. Tumor")
path_save = r"E:\1. Lab\Daily Results\2022\2202\0209\Dataset_MRI Segmentation\slice"
path_save_label = r"E:\1. Lab\Daily Results\2022\2202\0209\Dataset_MRI Segmentation\mask"

for i in os.listdir(path_img):
    if i not in ["ARTERIAL", "DELAY", "PLAIN", "VENOUS"]:
        continue
    path_cur_img = os.path.join(path_img, i)
    for j in os.listdir(path_cur_img):
        shutil.copy(os.path.join(path_cur_img, j), os.path.join(path_save, std_id+"_"+i+"_"+j))

for i in os.listdir(path_label):
    if i not in ["ARTERIAL", "DELAY", "PLAIN", "VENOUS"]:
        continue
    path_cur_img = os.path.join(path_label, i)
    for j in os.listdir(path_cur_img):
        shutil.copy(os.path.join(path_cur_img, j), os.path.join(path_save_label, std_id+"_"+i+"_"+j))



# list_dataset = [2, 7, 15, 30]
# p_org = r"E:\1. Lab\Daily Results\2022\2201\0129\Tumor Image Type Dataset"
# p_sav = r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification - not cropped"
# for i in list_dataset:
#     for j in ["Training Set", "Test Set"]:
#         imgs = os.listdir(os.path.join(p_org, "Dataset (Margin "+str(i)+"px)", j))
#         for k in imgs:
#             shutil.copy(os.path.join(p_sav, "Original (Margin "+str(i)+"px)", k), os.path.join(p_sav, "Dataset (Margin "+str(i)+"px)", j, k))



# k = 0
# for i in os.listdir(r"E:\1. Lab\Daily Results\2022\2201\0117\data\label\origin_liver"):
#     img = cv2.imread(os.path.join(r"E:\1. Lab\Daily Results\2022\2201\0117\data\label\origin_liver", i))
#     if (np.count_nonzero(img)>0):
#         k+=1
# print(len(os.listdir(r"E:\1. Lab\Daily Results\2022\2201\0117\data\label\origin_liver")))
# print(k)



# list_whole = os.listdir(r"E:\1. Lab\Daily Results\2022\2201\0117\data\label\origin_tumor")
# list_contain = []
# list_not_contain = []
# for i in list_whole:
#     img = cv2.imread(os.path.join(r"E:\1. Lab\Daily Results\2022\2201\0117\data\label\origin_tumor", i))
#     if (np.count_nonzero(img)>0):
#         list_contain.append(i)
#     else:
#         list_not_contain.append(i)
#
# random.shuffle(list_not_contain)
# random.shuffle(list_contain)
#
# num_true_train = int(len(list_contain)/2)
# num_true_test = int(len(list_contain)*0.8)
# list_train_true = list_contain[:num_true_train]
# list_test_true = list_contain[num_true_train:num_true_test]
# list_val_true = list_contain[num_true_test:]
# path_liver = r"E:\1. Lab\Daily Results\2022\2201\0117\data\img\liver"
# path_liver_mask = r"E:\1. Lab\Daily Results\2022\2201\0117\data\label\liver"
# path_src = r"E:\1. Lab\Daily Results\2022\2201\0117\data\img\origin"
# path_src_mask = r"E:\1. Lab\Daily Results\2022\2201\0117\data\label\origin_liver"
# for i in list_train_true:
#     shutil.copy(os.path.join(path_src, i), os.path.join(path_liver, "train", i))
#     shutil.copy(os.path.join(path_src_mask, i), os.path.join(path_liver_mask, "train", i))
# for i in list_test_true:
#     shutil.copy(os.path.join(path_src, i), os.path.join(path_liver, "test", i))
#     shutil.copy(os.path.join(path_src_mask, i), os.path.join(path_liver_mask, "test", i))
# for i in list_val_true:
#     shutil.copy(os.path.join(path_src, i), os.path.join(path_liver, "val", i))
#     shutil.copy(os.path.join(path_src_mask, i), os.path.join(path_liver_mask, "val", i))
#
#
# num_false_train = int(len(list_not_contain)/2)
# num_false_test = int(len(list_not_contain)*0.8)
# if num_false_train>num_true_train:
#     num_false_train = num_true_train
# if num_false_test>num_true_test:
#     num_false_test = num_true_test
# list_train_false = list_not_contain[:num_false_train]
# list_test_false = list_not_contain[num_false_train:num_false_test]
# list_val_false = list_not_contain[num_false_test:]
# for i in list_train_false:
#     shutil.copy(os.path.join(path_src, i), os.path.join(path_liver, "train", i))
#     shutil.copy(os.path.join(path_src_mask, i), os.path.join(path_liver_mask, "train", i))
# for i in list_test_false:
#     shutil.copy(os.path.join(path_src, i), os.path.join(path_liver, "test", i))
#     shutil.copy(os.path.join(path_src_mask, i), os.path.join(path_liver_mask, "test", i))
# for i in list_val_false:
#     shutil.copy(os.path.join(path_src, i), os.path.join(path_liver, "val", i))
#     shutil.copy(os.path.join(path_src_mask, i), os.path.join(path_liver_mask, "val", i))
#
#
# print(len(list_not_contain), len(list_contain))



# path_1 = r"D:\Dataset\LLU Dataset\6218843_07202017 (MR)\01. Original Study\img\test-resized"
# path_2 = r"D:\Dataset\LLU Dataset\6218843_07202017 (MR)\01. Original Study\img\test-resized 2"
# for i in os.listdir(path_1):
#     os.mkdir(os.path.join(path_2, i))
#     max_len = len(os.listdir(os.path.join(path_1, i)))
#     for k in range(len(os.listdir(os.path.join(path_1, i)))):
#         shutil.copy(os.path.join(path_1, i, os.listdir(os.path.join(path_1, i))[max_len-k-1]), os.path.join(path_2, i, str(k+1).zfill(5)+".png"))




# p_img = r"E:\1. Lab\Daily Results\2022\2201\0117\Tumor Segementation Dataset - 5\imgs\val"
# p_org = r"E:\1. Lab\Daily Results\2022\2201\0117\Tumor Segementation Dataset - 5\msks\origin"
# p_save = r"E:\1. Lab\Daily Results\2022\2201\0117\Tumor Segementation Dataset - 5\msks\val"
# list_img = os.listdir(p_img)
#
# for i in list_img:
#     shutil.copy(os.path.join(p_org, i), os.path.join(p_save, i))

