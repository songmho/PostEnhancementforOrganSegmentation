"""
Date: 2020.12.04.
Programmer: MH
Description: Code for loading medical image
"""

import os
import pydicom
import cv2
import numpy as np


class MedicalImageLoader:
    """
    CLass for loading medical image
    """

    set_med_type = ["PNG", "JPG", "DCM", "NII"]


    def __init__(self):
        self.setCT_a = {}
        self.set_med_img = {}
        self.set_med_info = {}
        self.med_type = ""
        self.path_medimg = ""
        self.path_info = ""
        self.voxels = {}

    def set_path(self, img_path, info_path=None):
        """
        To set image's path
          ...
        :param path: str, path of medical images
        :return:
        """
        self.path_medimg = img_path
        if info_path is None:
            self.path_info = img_path
        else:
            self.path_info = info_path

    def check_extension(self):
        """
        To check the medical image's extension
        To consider following folder structure for a patient
        patient_name
          L Study
            L Series 1
              L Slice 1
              ...
              L Slice K
            ...
            L Series n
              L Slice 1
              ...
              L Slice K
          ...

        :return:
        """
        mi = {"n_studies": 0, "n_series": [], "n_slices": []}
        list_studies = os.listdir(self.path_medimg)
        mi['n_studies'] = len(list_studies)
        for study in list_studies:
            list_series = os.listdir(os.path.join(self.path_medimg, study))
            mi['n_series'].append(len(list_series))
            mi['n_slices'].append([])
            for series in list_series:
                list_slices = os.listdir(os.path.join(self.path_medimg, study, series))
                mi['n_slices'][-1].append(len(list_slices))
                for slice in list_slices:
                    n, ext = os.path.splitext(slice)
                    if self.path_info != self.path_medimg:
                        self.med_type = ext[1:]
                        break
                    else:
                        if os.path.join(self.path_medimg, series, slice) != self.path_info:
                            self.med_type = ext[1:]
                            break

    def load_medical_img(self):
        """
        To load medical images
        :return:
        """
        if self.med_type.lower() == ("png" or "jpg"):
            self._load_medical_img_normal()
        elif self.med_type.lower() == "dcm":
            self.__load_medical_img_dcm()
        elif self.med_type.lower() == "nii":
            self.__load_medical_img_nii()
        else:
            pass

    def __load_medical_img_dcm(self):
        for study in os.listdir(self.path_medimg):
            self.set_med_img[study] = {}
            for series in os.listdir(os.path.join(self.path_medimg, study)):
                self.set_med_img[study][series] = []
                for slice in os.listdir(os.path.join(self.path_medimg, study, series)):
                    try:
                        dcm = pydicom.dcmread(os.path.join(self.path_medimg, study, series, slice))
                        self.set_med_img[study][series].append(dcm)
                        self.voxels[series] = float(dcm[0x0028, 0x0030].value[0])
                    except:
                        pass    # To pass loading file whose extension is not *.dcm.

    def _load_medical_img_normal(self):
        for study in os.listdir(self.path_medimg):
            self.set_med_img[study] = {}
            for series in os.listdir(os.path.join(self.path_medimg, study)):
                self.set_med_img[study][series] = []
                for slice in os.listdir(os.path.join(self.path_medimg, study, series)):
                    self.set_med_img[study][series].append(cv2.imread(os.path.join(self.path_medimg, study, series, slice)))

    def __load_medical_img_nii(self):
        pass

    def convert_color_depth(self):
        """
        To convert color depth
        :return:
        """
        if self.med_type.lower() == ("png" or "jpg"):
            pass
        elif self.med_type.lower() == "dcm":
            self.__convert_color_depth_dcm()
        else:
            pass

    def __convert_color_depth_dcm(self):
        for std_name, studies in self.set_med_img.items():
            self.setCT_a[std_name] = {}
            for series, slices in studies.items():
                list_cur_series = []
                for dc in slices:
                    img = dc.pixel_array
                    s = int(dc.RescaleSlope)
                    b = int(dc.RescaleIntercept)
                    img = s * img + b

                    ww = dc[0x0028, 0x1051].value[0]
                    wc = dc[0x0028, 0x1050].value[0]
                    ymin = 0
                    ymax = 255
                    img = np.reshape(img, (512, 512, 1))
                    # To convert color depth applying numpy where method (To reduce computation time)
                    idx_high = img >= wc+ww/2
                    idx_low = img <= wc-ww/2
                    img = np.where(idx_high, ymax, img)
                    img = np.where(idx_low, ymin, img)
                    img = np.where(~idx_high & ~idx_low, ((img-wc)/ww+0.5)*(ymax-ymin)+ymin, img)
                    list_cur_series.append(img.astype(np.uint8))
                self.setCT_a[std_name][series] = list_cur_series

    def arrange_data(self):
        """
        To arrange image data and clinical information
        :return:
        """

    def get_setCT_a(self):
        return self.setCT_a

    def get_med_type(self):
        return self.med_type


if __name__ == '__main__':
    mil = MedicalImageLoader()
    print("Set Path")
    mil.set_path(r"E:\1. Lab\Dataset\Liver\LiverCTCancerArchive\Custom, DICOM\TCGA-DD-A4NL")
    print("Task 1. Checking Type of Medical Image")
    mil.check_extension()
    print(mil.get_med_type())
    print("Task 2. Loading Medical Image")
    mil.load_medical_img()
    print("Task 3. Converting Medical Image Color Depth")
    mil.convert_color_depth()
    for name, studies in mil.set_med_img.items():
        print(name)
        for series, slices in studies.items():
            print(series, ": ", len(slices))
