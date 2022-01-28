"""
Date: 2022. 01. 14.
Programmer: MH
Description: Code for resizing slices from MRI study to (512, 512) (same to CT slice)
"""
import cv2
import numpy as np
import os


class SliceResizer:
    def __init__(self):
        self.sl_size = (512, 512)  # Target Slice Size
        self.list_sls = []
        self.list_names = []

    def load_trg_sl(self, path):
        """
        To load target slices from local
        """
        self.list_sls = []
        self.list_names = []
        for i in os.listdir(path):
            msk = cv2.imread(os.path.join(path, i), cv2.IMREAD_GRAYSCALE)
            self.list_sls.append(msk)
            self.list_names.append(i)

    def resize(self):
        """
        To resize the slices
        """
        for i in range(len(self.list_sls)):
            new_img = np.zeros(self.sl_size)
            shape_img = self.list_sls[i].shape
            y, x = shape_img
            print(y, x)
            if x < self.sl_size[0] and y <self.sl_size[1]:
                margin_y = int((self.sl_size[0]-y)/2)
                margin_x = int((self.sl_size[1]-x)/2)
                new_img[margin_y:int(self.sl_size[0])-margin_y, margin_x:int(self.sl_size[1])-margin_x] = self.list_sls[i]
            else:
                if x > y:
                    y = int(self.sl_size[0]*y/x)
                    x = self.sl_size[1]
                    if self.list_sls[i].shape[1] > self.sl_size[1] or self.list_sls[i].shape[0] > self.sl_size[0]:
                        self.list_sls[i] = cv2.resize(self.list_sls[i], (x, y), interpolation=cv2.INTER_AREA)
                    margin_y = int((self.sl_size[0] - y) / 2)
                    margin_x = int((self.sl_size[1] - x) / 2)
                    new_img[margin_y:margin_y+y, margin_x:x] = self.list_sls[i]
                else:
                    x = int(self.sl_size[1]*x/y)
                    y = self.sl_size[1]
                    if self.list_sls[i].shape[1] > self.sl_size[1] or self.list_sls[i].shape[0] > self.sl_size[0]:
                        self.list_sls[i] = cv2.resize(self.list_sls[i], (x, y), interpolation=cv2.INTER_AREA)
                    margin_y = int((self.sl_size[0] - y) / 2)
                    margin_x = int((self.sl_size[1] - x) / 2)
                    new_img[margin_y:margin_y+y, margin_x:x] = self.list_sls[i]
            self.list_sls[i] = new_img

    def save(self, path):
        """
        To save the resized slice to the local
        """
        if not os.path.isdir(path):
            os.mkdir(path)
        for i in range(len(self.list_sls)):
            cv2.imwrite(os.path.join(path, self.list_names[i]), self.list_sls[i])


if __name__ == '__main__':
    path_cur_study = r"E:\1. Lab\Daily Results\2022\2201\0117\Resolution Increasement\mask - Tumor"
    path_cur_study_save = r"E:\1. Lab\Daily Results\2022\2201\0117\Resolution Resizer\mask - Tumor"
    sr = SliceResizer()
    for std in os.listdir(path_cur_study):
        print(std)
        for srs in os.listdir(os.path.join(path_cur_study, std)):
            print(srs)
            sr.load_trg_sl(os.path.join(path_cur_study, std, srs))
            sr.resize()
            sr.save(os.path.join(path_cur_study_save, std, srs))
