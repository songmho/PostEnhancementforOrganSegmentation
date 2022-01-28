"""
Date: 2020.12.04.
Programmer: MH
Description: Code for loading medical image
"""

import os
import pydicom
import cv2
import numpy as np
import nibabel as nib
from miaas.lirads.constant import ImageType
from miaas.utils.slice_resizer import SliceResizer

class MedicalImageLoader:
    """
    CLass for loading medical image
    """

    set_med_type = ["PNG", "JPG", "DCM", "NII"]


    def __init__(self):
        self.setCT_a = {}
        self.setMed_img = {}
        self.set_med_info = {}
        self.med_type = ""
        self.path_medimg = ""
        self.path_info = ""
        self.voxels = {}
        self.acquisition_date = ""

        self.ww_liver = 400
        self.wc_liver = 40
        self.slice_resizer = SliceResizer()

    def initialize(self):
        self.setCT_a = {}
        self.setMed_img = {}
        self.set_med_info = {}
        self.med_type = ""
        self.path_medimg = ""
        self.path_info = ""
        self.voxels = {}
        self.acquisition_date = ""

    def set_path(self, img_path, info_path=None):
        """
        To set image's path
          ...
        :param path: str, path of medical images
        :return:
        """
        self.path_medimg = img_path
        print("PATH_MEDIMG: ", self.path_medimg)
        if info_path is None:
            self.path_info = img_path
        else:
            self.path_info = info_path

    def check_mi_type(self):
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
        :return:
        """
        print(">>>> ", self.path_medimg)
        list_studies = os.listdir(self.path_medimg)
        for std in list_studies:
            list_series = os.listdir(os.path.join(self.path_medimg, std))
            for srs in list_series:
                if os.path.isdir(os.path.join(self.path_medimg, std, srs)): # dicom or normal images
                    list_slices = os.listdir(os.path.join(self.path_medimg, std, srs))
                    for sl in list_slices:
                        ext = sl.split(".")[1:]
                        self.med_type = ext
                else:                       # NII
                    ext = srs.split(".")[1:]
                    self.med_type = ext
        if "nii" in self.med_type: self.med_type = ImageType.NII
        elif "dcm" in self.med_type: self.med_type = ImageType.DCM
        else: self.med_type = ImageType.NORMAL
        print("    Type of Current Medical Image: ", self.med_type)

        # mi = {"n_studies": 0, "n_series": [], "n_slices": []}
        # list_studies = os.listdir(self.path_medimg)
        # mi['n_studies'] = len(list_studies)
        # for study in list_studies:
        #     list_series = os.listdir(os.path.join(self.path_medimg, study))
        #     mi['n_series'].append(len(list_series))
        #     mi['n_slices'].append([])
        #     for series in list_series:
        #         list_slices = os.listdir(os.path.join(self.path_medimg, study, series))
        #         mi['n_slices'][-1].append(len(list_slices))
        #         for slice in list_slices:
        #             n, ext = os.path.splitext(slice)
        #             if self.path_info != self.path_medimg:
        #                 self.med_type = ext[1:]
        #                 break
        #             else:
        #                 if os.path.join(self.path_medimg, series, slice) != self.path_info:
        #                     self.med_type = ext[1:]
        #                     break
        # print(">>>> ", self.med_type)

    def load_medical_img(self):
        """
        To load medical images
        :return:
        """
        if self.med_type == ImageType.NORMAL:
            self.__load_medical_img_normal()
        elif self.med_type == ImageType.DCM:
            self.__load_medical_img_dcm()
        elif self.med_type == ImageType.NII:
            self.__load_medical_img_nii()
        else:
            pass

    def __load_medical_img_dcm(self):
        for study in os.listdir(self.path_medimg):
            self.setMed_img[study] = {}
            for series in os.listdir(os.path.join(self.path_medimg, study)):
                cur_srs = None
                for slice in os.listdir(os.path.join(self.path_medimg, study, series)):
                    # try:
                    dcm = pydicom.dcmread(os.path.join(self.path_medimg, study, series, slice))
                    if (0x0028, 0x1052) in dcm.keys():
                        rescaleIntercept = float(dcm[0x0028, 0x1052].value)
                    else:
                        rescaleIntercept = 0
                    if (0x0028, 0x1053) in dcm.keys():
                        rescaleSlope = float(dcm[0x0028, 0x1053].value)
                    else:
                        rescaleSlope = 1
                    if dcm[0x0008, 0x103E].value not in self.setMed_img[study].keys():
                        if str(dcm[0x0008, 0x0060].value) is "CT":
                            if "w/o" in str(dcm[0x0008, 0x103E].value).lower() or "pre" in str(dcm[0x0008, 0x103E].value).lower() or "plain" in str(dcm[0x0008, 0x103E].value).lower() or "non con" in str(dcm[0x0008, 0x103E].value).lower():
                                if "PLAIN" not in self.setMed_img[study].keys():
                                    self.setMed_img[study]["PLAIN"] = {}
                                    cur_srs = "PLAIN"
                            elif "art" in str(dcm[0x0008, 0x103E].value).lower() or "arterial" in str(dcm[0x0008, 0x103E].value).lower() or "ap" in str(dcm[0x0008, 0x103E].value).lower():
                                if "ARTERIAL" not in self.setMed_img[study].keys():
                                    self.setMed_img[study]["ARTERIAL"] = {}
                                    cur_srs = "ARTERIAL"
                            elif "pv" in str(dcm[0x0008, 0x103E].value).lower() or "venous" in str(dcm[0x0008, 0x103E].value).lower() or "pvp" in str(dcm[0x0008, 0x103E].value).lower():
                                if "VENOUS" not in self.setMed_img[study].keys():
                                    self.setMed_img[study]["VENOUS"] = {}
                                    cur_srs = "VENOUS"
                            elif "delay" in str(dcm[0x0008, 0x103E].value).lower() or "dp" in str(dcm[0x0008, 0x103E].value).lower():
                                if "DELAY" not in self.setMed_img[study].keys():
                                    self.setMed_img[study]["DELAY"] = {}
                                    cur_srs = "DELAY"
                            else:
                                if series not in list(self.setMed_img[study].keys()):
                                    self.setMed_img[study][series] = {}
                                    cur_srs = series
                        else:
                            if series not in list(self.setMed_img[study].keys()):
                                self.setMed_img[study][series] = {}
                                cur_srs = series
                    if type(dcm[0x0028, 0x1051].value) == pydicom.valuerep.DSfloat:  #If ww is set to only a number
                        cur_ww = float(dcm[0x0028, 0x1051].value)
                    else:               # if ww is set to two numbers
                        cur_ww = float(dcm[0x0028, 0x1051].value[0])
                    if type(dcm[0x0028, 0x1050].value) == pydicom.valuerep.DSfloat: # if wc is set to only a number
                        cur_wc = float(dcm[0x0028, 0x1050].value)
                    else:               # if wc is set to two numbers
                        cur_wc = float(dcm[0x0028, 0x1050].value[0])
                    info = {"voxel": float(dcm[0x0028, 0x0030].value[0]), "acq_date": str(dcm[0x0008, 0x0022].value),
                            "slice_location": float(dcm[0x0020, 0x1041].value), "ww":cur_ww,
                            "wc":cur_wc, "rescaleIntercept":float(rescaleIntercept),
                            "rescaleSlope":float(rescaleSlope)}
                    self.acquisition_date = str(dcm[0x0008, 0x0022].value)
                    self.voxels = float(dcm[0x0028, 0x0030].value[0])
                    self.setMed_img[study][cur_srs][str(dcm[0x0020, 0x0013].value).zfill(5)] = {"image": dcm.pixel_array, "info":info}
                    self.ww_liver = cur_ww
                    self.wc_liver = cur_wc
                    self.rescale_intercept = rescaleIntercept
                    self.rescale_slope = rescaleSlope
                # except:
                #     pass    # To pass loading file whose extension is not *.dcm.
                print("       >>",cur_srs,"    ",series,  len(list(self.setMed_img[study][cur_srs])))

                # self.setMed_img[study][cur_srs] = sorted(self.setMed_img[study][cur_srs])
                tup = sorted(self.setMed_img[study][cur_srs].items())
                self.setMed_img[study][cur_srs] = dict((x, y) for x, y in tup)
                # self.setMed_img[study][cur_srs] = list(self.setMed_img[study][cur_srs].values())

    def __load_medical_img_normal(self):
        for study in os.listdir(self.path_medimg):
            self.setMed_img[study] = {"plain":[], "arterial":[], "venous":[], "delay":[]}
            for series in os.listdir(os.path.join(self.path_medimg, study)):
                self.setMed_img[study][series] = []
                for sl_id in range(len(os.listdir(os.path.join(self.path_medimg, study, series)))):
                    slice = os.listdir(os.path.join(self.path_medimg, study, series))[sl_id]
                    info = {"voxel": 0.878906, "acq_date": study.split("_")[1], "slice_location": sl_id}
                    self.setMed_img[study][series].append({"image": cv2.imread(os.path.join(self.path_medimg, study, series, slice)),
                                                            "info": info})
        self.ww_liver = 400
        self.wc_liver = 40
        self.rescale_intercept = -1024
        self.rescale_slope = 1

    def __load_medical_img_nii(self):
        for study in os.listdir(self.path_medimg):
            self.setMed_img[study] = {"plain": [], "arterial": [], "venous": [], "delay": []}
            for series in os.listdir(os.path.join(self.path_medimg, study)):
                cur_srs_data = nib.load(os.path.join(self.path_medimg, study, series))
                cur_srs_data = cur_srs_data.get_fdata()
                cur_srs_data = cur_srs_data[:, :, ::-1]
                result = []

                for sl in range(len(cur_srs_data[0, 0, :])):
                    cur_sl = np.array(cur_srs_data[:, :, sl])
                    cur_sl = np.array(np.rot90(cur_sl, 1), np.int)
                    info = {"voxel": 0.878906, "acq_date": study.split("_")[1], "slice_location": sl}
                    result.append({"image": cur_sl, "info": info})

                cur_srs_data = np.array(result)
                self.setMed_img[study][series.split(".")[0]] = cur_srs_data
        self.ww_liver = 400
        self.wc_liver = 40
        self.rescale_intercept = -1024
        self.rescale_slope = 1

    def convert_color_depth(self):
        """
        To convert color depth
        :return:
        """
        if self.med_type == ImageType.NORMAL:
            pass
        elif self.med_type == ImageType.DCM:
            self.__convert_color_depth_dcm()
        elif self.med_type == ImageType.NII:
            self.__convert_color_depth_nii()

    def __load_normal_imgs(self):
        for std_name, studies in self.setMed_img.items():
            self.setCT_a[std_name] = {}
            for series, slices in studies.items():
                list_cur_series = {}
                for dc in slices.keys():
                    list_cur_series[dc] = slices[dc]
                self.setCT_a[std_name][series] = list_cur_series

    def __convert_color_depth_dcm(self):
        for std_name, studies in self.setMed_img.items():
            self.setCT_a[std_name] = {}
            for series, slices in studies.items():
                list_cur_series = {}
                k=0
                for dc in slices.keys():
                    img = slices[dc]["image"]
                    s = int(slices[dc]["info"]["rescaleSlope"])
                    b = int(slices[dc]["info"]["rescaleIntercept"])
                    img = s * img + b

                    ww = slices[dc]["info"]["ww"]
                    wc = slices[dc]["info"]["wc"]
                    ymin = 0
                    ymax = 255
                    y, x = img.shape[0], img.shape[1]
                    img = np.reshape(img, (y, x, 1))
                    # To convert color depth applying numpy where method (To reduce computation time)
                    idx_high = img >= wc+ww/2
                    idx_low = img <= wc-ww/2
                    img = np.where(idx_high, ymax, img)
                    img = np.where(idx_low, ymin, img)
                    img = np.where(~idx_high & ~idx_low, ((img-wc)/ww+0.5)*(ymax-ymin)+ymin, img)
                    if (img.shape[0], img.shape[1]) != (512, 512):
                        img = self.slice_resizer.resize(img)
                    list_cur_series[dc] = img.astype(np.uint8)
                    cv2.imwrite(os.path.join(r"E:\1. Lab\Daily Results\2022\2201\0121\result\step1", std_name+"_"+series+"_"+str(k).zfill(5)+".png"), list_cur_series[dc])
                    k+=1
                self.setCT_a[std_name][series] = list_cur_series
                print("       >>", series, "    ", len(self.setCT_a[std_name][series]))

    def __convert_color_depth_nii(self):
        for std_name, studies in self.setMed_img.items():
            self.setCT_a[std_name] = {}
            for series, slices in studies.items():
                list_cur_series = {}
                for idx in slices.keys():
                    img = slices[idx]["image"]
                    s = int(slices[idx]["info"]["rescaleSlope"])
                    b = int(slices[idx]["info"]["rescaleIntercept"])
                    img = s * img + b

                    ww = slices[idx]["info"]["ww"]
                    wc = slices[idx]["info"]["wc"]
                    ymin = 0
                    ymax = 255
                    img = np.reshape(img, (512, 512, 1))
                    idx_high = img >= wc+ww/2
                    idx_low = img <= wc-ww/2
                    img = np.where(idx_high, ymax, img)
                    img = np.where(idx_low, ymin, img)
                    img = np.where(~idx_high & ~idx_low, ((img-wc)/ww+0.5)*(ymax-ymin)+ymin, img)
                    list_cur_series[idx] = img.astype(np.uint8)
                self.setCT_a[std_name][series] = list_cur_series

    def arrange_data(self):
        """
        NO REQUIRED
        To arrange image data and clinical information. the method is for dicom
        Acquisition Date [(0x0008), (0x0022)], Series Description [(0x0008), (0x103E)], Instance Number [(0x0020), (0x0013)],
        Slice Location [(0x0020), (0x1041)], Pixel Spacing [(0x0028), (0x0030)], Window Center [(0x0028), (0x1050)],
        Window Width [(0x0028), (0x1051)], Rescale Intercept [(0x0028), (0x1052)], Rescale Slope [(0x0028), (0x1053)],
        :return:
        """

    def get_setMed_img(self):
        return self.setMed_img

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
    for name, studies in mil.setMed_img.items():
        print(name)
        for series, slices in studies.items():
            print(series, ": ", len(slices))
