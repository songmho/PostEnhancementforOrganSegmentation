"""
Date: 2022. 01. 25.
Programmer: MH
Description: Code for resize the tumor image (png) using image processing and deep learning method
"""

import cv2
import os
import numpy as np


class TumorImgResizer:
    def __init__(self):
        self.__path = r""
        self.__list_tumor_imgs = []
        self.__list_f_names = []

    def set_path(self, path):
        self.__path = path

    def load_tumor_imgs(self):
        """
        To load images from local
        """
        for i in os.listdir(self.__path):
            self.__list_tumor_imgs.append(cv2.imread(os.path.join(self.__path, i), cv2.IMREAD_GRAYSCALE))
            self.__list_f_names.append(i)

    def rotate(self):
        for i in range(len(self.__list_tumor_imgs)):
            self.__list_tumor_imgs[i] = self.__list_tumor_imgs[i][::-1, ::-1]

    def resize_normal(self, rate=2.0):
        """
        To resize tumor images using openCV image resizing method
        :param rate: float, resizing rate
        """
        for i in range(len(self.__list_tumor_imgs)):
            self.__list_tumor_imgs[i] = cv2.resize(self.__list_tumor_imgs[i], dsize=(0, 0),
                                                   fx=rate, fy=rate, interpolation=cv2.INTER_CUBIC)

    def save_img(self, path):
        """
        To save resized images to local
        """
        for i in range(len(self.__list_f_names)):
            cv2.imwrite(os.path.join(path, self.__list_f_names[i]), self.__list_tumor_imgs[i])


if __name__ == '__main__':
    p_img = r"E:\1. Lab\Daily Results\2022\2201\0117\Resolution Increasement\mask - Tumor\7953100_03092017"
    p_save = r"E:\1. Lab\Daily Results\2022\2201\0117\Resolution Increasement\mask - Tumor\7953100_03092017"

    tir = TumorImgResizer()

    for i in os.listdir(p_img):
        print(i)
        tir.set_path(os.path.join(p_img, i))
        tir.load_tumor_imgs()
        tir.rotate()
        # tir.resize_normal(4)
        tir.save_img(os.path.join(p_save, i))