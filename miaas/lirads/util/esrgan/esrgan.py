"""
Date: 2022. 01. 28.
Programmer: MH
Description: Code for training ESRGAN model and magnifying input images' resolution 4 times
"""
import os
import os.path as osp
import glob
import cv2
import numpy as np
import torch
import RRDBNet_arch as arch

class ESRGAN:
    def __init__(self):
        self.path_model = r"E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\models\esrgan\RRDB_ESRGAN_x4.pth"
        self.model = None
        self.device = torch.device("cuda")

    def load_model(self):
        """
        To load model from local
        """
        self.model = arch.RRDBNet(3, 3, 64, 23, gc=23)
        self.model.load_state_dict(torch.load(self.path_model), strict=True)
        self.model.eval()
        self.model = self.model.to(self.device)

    def magnify(self, img):
        """
        To magnify input image's resolution
        """
        if len(img.shape) == 2 or img.shape[2] == 1:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        if np.max(img) > 1.0:
            img = img * 1.0 / 255

        img = torch.from_numpy(np.transpose(img[:, :, [2, 1, 0]], (2, 0, 1))).float()
        img_lr = img.unsqueeze(0)
        img_lr = img_lr.to(self.device)

        with torch.no_grad():
            output = self.model(img_lr).data.squeeze().float().cpu().clamp_(0, 1).numpy()
        output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
        output = np.array((output * 255.0).round(), np.uint8)
        output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
        return output
