import os

import cv2
import nibabel as nib
import numpy as np

path_org = r"E:\2. Project\Python\pytorch-3dunet\raw\data\mask"
# path_save = r'E:\1. Lab\Daily Results\2022\2203\0311\result'
path_save = r"E:\1. Lab\Daily Results\2022\2203\0311\series"

total = 0
for i in os.listdir(path_org):
    cur_save = os.path.join(path_save, i)
    if not os.path.isdir(cur_save):
        os.mkdir(cur_save)

    # if "mask" not in i:
    #     continue
    srs = nib.load(os.path.join(path_org, i))
    srs = srs.get_fdata()
    # new_srs =np.zeros((srs.shape[0], srs.shape[1], srs.shape[2], 9))
    new_srs = np.zeros((srs.shape[0], srs.shape[1], srs.shape[2], 1))
    num_contain = 0
    for j in range(srs.shape[2]):   # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
        new_data = np.array(srs[:, ::-1, srs.shape[2]-j-1]*28, np.uint8)
        if np.count_nonzero(new_data) >0:
            num_contain+=1
    total+= num_contain
    print(i.replace("mask", "").replace(".nii.gz","").zfill(2), srs.shape[2], "     ", num_contain)
        # new_data = np.rot90(new_data, -1)
        # cv2.imwrite(os.path.join(cur_save, str(j).zfill(5)+".png"), new_data)
print(total)
        # for y in range(srs.shape[1]):
        #     for x in range(srs.shape[0]):
        #         cur_px = srs[x, y, j]
        #         if cur_px>0:
        #             new_srs[x, y, j, int(cur_px)-1] = 1
    # print(i, new_srs.shape)
    # new_srs_cvt = nib.Nifti1Image(new_srs, affine=None)
    # nib.save(new_srs_cvt, os.path.join(path_save, i))
