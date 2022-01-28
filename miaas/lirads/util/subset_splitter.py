import os
import numpy as np
import cv2
import random
import shutil

p_img = r"E:\1. Lab\Daily Results\2022\2201\0117\Tumor Segementation Dataset - 5\imgs\origin"
p_msk = r"E:\1. Lab\Daily Results\2022\2201\0117\Tumor Segementation Dataset - 5\msks\origin"
p_save = r"E:\1. Lab\Daily Results\2022\2201\0117\Tumor Segementation Dataset - 5\imgs"
p_save_msk = r"E:\1. Lab\Daily Results\2022\2201\0117\Tumor Segementation Dataset - 5\msks"

list_name_contain = []
list_name_not_contain = []
list_imgs_contain = []
list_imgs_not_contain = []
list_msks_contain = []
list_msks_not_contain = []

list_trg = os.listdir(p_msk)
random.shuffle(list_trg)

for i in list_trg:
    msk = cv2.imread(os.path.join(p_img, i), cv2.IMREAD_GRAYSCALE)
    img = cv2.imread(os.path.join(p_msk, i), cv2.IMREAD_GRAYSCALE)
    if np.count_nonzero(img)>0:
        list_name_contain.append(i)
        list_imgs_contain.append(img)
        list_msks_contain.append(msk)
    else:
        list_name_not_contain.append(i)
        list_imgs_not_contain.append(img)
        list_msks_not_contain.append(msk)

for i in range(len(list_name_contain[:int(len(list_name_contain)*0.5)])):
    shutil.copy(os.path.join(p_img, list_name_contain[i]), os.path.join(p_save, "train", list_name_contain[i]))
    shutil.copy(os.path.join(p_msk, list_name_contain[i]), os.path.join(p_save_msk, "train", list_name_contain[i]))

for i in range(len(list_name_contain[int(len(list_name_contain) * 0.5):int(len(list_name_contain) * 0.8)])):
    shutil.copy(os.path.join(p_img, list_name_contain[i]), os.path.join(p_save, "test", list_name_contain[i]))
    shutil.copy(os.path.join(p_msk, list_name_contain[i]), os.path.join(p_save_msk, "test", list_name_contain[i]))

for i in range(len(list_name_contain[int(len(list_name_contain) * 0.8): ])):
    shutil.copy(os.path.join(p_img, list_name_contain[i]), os.path.join(p_save, "val", list_name_contain[i]))
    shutil.copy(os.path.join(p_msk, list_name_contain[i]), os.path.join(p_save_msk, "val", list_name_contain[i]))


# for i in range(len(list_name_not_contain[:int(len(list_name_not_contain)*0.5)])):
for i in range(len(list_name_contain[:int(len(list_name_contain) * 0.5)])):
    shutil.copy(os.path.join(p_img, list_name_not_contain[i]), os.path.join(p_save, "train", list_name_not_contain[i]))
    shutil.copy(os.path.join(p_msk, list_name_not_contain[i]), os.path.join(p_save_msk, "train", list_name_not_contain[i]))

# for i in range(len(list_name_not_contain[int(len(list_name_not_contain) * 0.5):int(len(list_name_not_contain) * 0.8)])):
for i in range(len(list_name_contain[int(len(list_name_contain) * 0.5):int(len(list_name_contain) * 0.8)])):
    shutil.copy(os.path.join(p_img, list_name_not_contain[i]), os.path.join(p_save, "test", list_name_not_contain[i]))
    shutil.copy(os.path.join(p_msk, list_name_not_contain[i]), os.path.join(p_save_msk, "test", list_name_not_contain[i]))

# for i in range(len(list_name_not_contain[int(len(list_name_not_contain) * 0.8): ])):
for i in range(len(list_name_contain[int(len(list_name_contain) * 0.8): ])):
    shutil.copy(os.path.join(p_img, list_name_not_contain[i]), os.path.join(p_save, "val", list_name_not_contain[i]))
    shutil.copy(os.path.join(p_msk, list_name_not_contain[i]), os.path.join(p_save_msk, "val", list_name_not_contain[i]))


print(len(list_name_contain), len(list_name_not_contain))