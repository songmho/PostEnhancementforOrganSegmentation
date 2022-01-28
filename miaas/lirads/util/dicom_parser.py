"""
Date: 2022. 01. 24.
Programmer: MH
Description: Code for Generating Normal Images from DICOM or NII
"""
import cv2
import numpy as np
import pydicom
import nibabel as nib
import os
from miaas.utils.slice_resizer import SliceResizer



class ImageConverter:
    def __init__(self, format):
        self.format = format    # DICOM or NII
        self.org_dcm = None
        self.org_nii = None
        self.cur_slope = 1
        self.cur_inter = 0
        self.slice_resizer = SliceResizer()

    def load_data(self, path):
        """
        To load a series
        """
        self.list_sl = []
        if self.format == "DICOM":
            self.org_dcm = {}
            for i in os.listdir(path):
                sl = pydicom.dcmread(os.path.join(path, i))
                self.org_dcm[str(sl[0x0020, 0x0013].value).zfill(5)] = sl

            self.org_dcm = sorted(self.org_dcm.items(), key=lambda item: item[0], reverse=True)
            self.org_dcm = dict(self.org_dcm)

        elif self.format == "NII":
            self.org_nii = nib.load(path)

    def convert_slice(self):
        """
        To convert slices applying window
        """
        if self.format == "DICOM":
            for key, sl in self.org_dcm.items():
                img = sl.pixel_array

                if (0x0028, 0x1052) in sl.keys():
                    rescale_intercept = float(sl[0x0028, 0x1052].value)
                else:
                    rescale_intercept = 0
                if (0x0028, 0x1053) in sl.keys():
                    rescale_slope = float(sl[0x0028, 0x1053].value)
                else:
                    rescale_slope = 1
                if type(sl[0x0028, 0x1051].value) == pydicom.valuerep.DSfloat:  # If ww is set to only a number
                    ww = float(sl[0x0028, 0x1051].value)
                else:  # if ww is set to two numbers
                    ww = float(sl[0x0028, 0x1051].value[0])
                if type(sl[0x0028, 0x1050].value) == pydicom.valuerep.DSfloat:  # if wc is set to only a number
                    wc = float(sl[0x0028, 0x1050].value)
                else:  # if wc is set to two numbers
                    wc = float(sl[0x0028, 0x1050].value[0])
                img = rescale_slope*img + rescale_intercept
                ymin = 0
                ymax = 255
                y, x = img.shape[0], img.shape[1]
                img = np.reshape(img, (y, x, 1))
                # To convert color depth applying numpy where method (To reduce computation time)
                idx_high = img >= wc + ww / 2
                idx_low = img <= wc - ww / 2
                img = np.where(idx_high, ymax, img)
                img = np.where(idx_low, ymin, img)
                img = np.where(~idx_high & ~idx_low, ((img - wc) / ww + 0.5) * (ymax - ymin) + ymin, img)
                # if (img.shape[0], img.shape[1]) != (512, 512):
                #     self.list_sl.append(self.slice_resizer.resize(img))
                # else:
                self.list_sl.append(img)

        elif self.format == "NII":
            for i in range(self.org_nii.header.get_data_shape()[2]):
                img = self.org_nii.get_fdata()[::-1, ::-1, i]
                img = self.cur_slope*img + self.cur_inter

                ww = 0
                wc = 0
                ymin = 0
                ymax = 255
                y, x = img.shape[0], img.shape[1]
                print(x, y)
                img = np.reshape(img, (y, x, 1))
                # To convert color depth applying numpy where method (To reduce computation time)
                # idx_high = img >= wc + ww / 2
                # idx_low = img <= wc - ww / 2
                # img = np.where(idx_high, ymax, img)
                # img = np.where(idx_low, ymin, img)
                # img = np.where(~idx_high & ~idx_low, ((img - wc) / ww + 0.5) * (ymax - ymin) + ymin, img)

                cur_max = np.max(img)
                cur_min = np.min(img)
                unique = np.unique(img)
                img = np.array(np.where(img > 0, (img-cur_min)/(cur_max-cur_min)*255,0), np.uint8)
                print(img.shape)
                # if (img.shape[0], img.shape[1]) != (512, 512):
                #     self.list_sl.append(self.slice_resizer.resize(img))
                # else:
                img = img[:, ::-1, ::-1]
                img = np.array(list(zip(*img)))[::-1]
                self.list_sl.append(img)

    def convert_mask(self):
        self.list_sl = []
        for i in range(self.org_nii.header.get_data_shape()[2]):
            img = self.org_nii.get_fdata()[::-1, :, i]
            img = np.array(list(zip(*img))[::-1])
            img = np.array(np.where((img >0) & (img!=4), 255, 0), dtype=np.uint8)
            img = np.expand_dims(img, axis=-1)
            # if (img.shape[0], img.shape[1]) != (512, 512):
            #     self.list_sl.append(self.slice_resizer.resize(img))
            # else:
            self.list_sl.append(img)

    def save_srs(self, path):
        """
        To save converted slices
        """
        for i in range(len(self.list_sl)):
            cv2.imwrite(os.path.join(path, str(len(self.list_sl)-i).zfill(5)+".png"), self.list_sl[i])


if __name__ == '__main__':
    ic = ImageConverter("NII")
    path_srs = r"D:\Dataset\LLU Dataset\7953100_11162016 (MR)\02. Label\02. Tumor"
    path_save_srs = r"D:\Dataset\LLU Dataset\7953100_11162016 (MR)\02. Label\04. PNG\02. Tumor Origin"
    for i in os.listdir(path_srs):
        if not os.path.isdir(os.path.join(path_save_srs, i)):
            os.mkdir(os.path.join(path_save_srs, i))
        ic.load_data(os.path.join(path_srs, i))
        ic.convert_mask()
        # ic.convert_slice()
        ic.save_srs(os.path.join(path_save_srs, i))
