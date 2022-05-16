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
        self.sl_size = (512, 512, 1)  # Target Slice Size
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

    def resize_slices(self):
        for i in range(len(self.list_sls)):
            img = self.list_sls[i]
            self.list_sls[i] = self.resize(img)

    def resize(self, img):
        """
        To resize the slices
        """
        if len(img.shape) != 3:
            img = np.expand_dims(img, -1)
        y, x, z = img.shape
        new_img = np.zeros(self.sl_size)
        if x < self.sl_size[0] and y < self.sl_size[1]:
            margin_y = int((self.sl_size[0]-y)/2)
            margin_x = int((self.sl_size[1]-x)/2)
            new_img[margin_y:int(self.sl_size[0])-margin_y, margin_x:int(self.sl_size[1])-margin_x, :] = img
        else:
            if x > y:
                y = int(self.sl_size[0]*y/x)
                x = self.sl_size[1]
                if img.shape[1] > self.sl_size[1] or img.shape[0] > self.sl_size[0]:
                    img = cv2.resize(img, (x, y), interpolation=cv2.INTER_AREA)
                    img = np.expand_dims(img, -1)
                margin_y = int((self.sl_size[0] - y) / 2)
                margin_x = int((self.sl_size[1] - x) / 2)
                new_img[margin_y:int(self.sl_size[0]) - margin_y, margin_x:int(self.sl_size[1]) - margin_x, :] = img
            else:
                x = int(self.sl_size[1]*x/y)
                y = self.sl_size[1]
                if img.shape[1] > self.sl_size[1] or img.shape[0] > self.sl_size[0]:
                    img = cv2.resize(img, (x, y), interpolation=cv2.INTER_AREA)
                    img = np.expand_dims(img, -1)
                margin_y = int((self.sl_size[0] - y) / 2)
                margin_x = int((self.sl_size[1] - x) / 2)
                new_img[margin_y:int(self.sl_size[0]) - margin_y, margin_x:int(self.sl_size[1]) - margin_x, :] = img
        return new_img

    def save(self, path):
        """
        To save the resized slice to the local
        """
        if not os.path.isdir(path):
            os.mkdir(path)
        for i in range(len(self.list_sls)):
            cv2.imwrite(os.path.join(path, self.list_names[i]), self.list_sls[i])


if __name__ == '__main__':
    path_cur_study = r"E:\1. Lab\Daily Results\2022\2202\0224\Dataset with CHAOS and LLU\source\CHAOS\mask"
    path_cur_study_save = r"E:\1. Lab\Daily Results\2022\2202\0224\Dataset with CHAOS and LLU\source\CHAOS-resize\mask"
    sr = SliceResizer()
    for i in os.listdir(path_cur_study):
        if "(x)" not in i and ".zip" not in i:
            sr.load_trg_sl(os.path.join(path_cur_study, i))
            sr.resize_slices()
            sr.save(os.path.join(path_cur_study_save, i))
