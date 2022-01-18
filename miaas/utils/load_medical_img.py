"""
Date: 2021. 09. 23.
Programmer: MH
Description: Code for loading medical image file
"""
import numpy as np
from pydicom import dcmread
import os
import cv2
import mritopng


"""
class for Loading Medical Images 
"""
class MedicalImageLoader:
    def __init__(self, p_m, p_s):
        self.path_mi = p_m  # Path for a Study
        self.path_save = p_s
        self.__extension = None
        self.__img_type = None
        self.__study = []
        self.__mi_info = []
        self.__mi_slices = []

    def find_extension(self):
        """
        To find extension
        """
        p_srs = os.path.join(self.path_mi, os.listdir(self.path_mi)[0])
        p_sl = os.path.join(p_srs, os.listdir(p_srs)[0])
        _, self.__extension = os.path.splitext(p_sl)
        self.__extension = self.__extension.replace(".", "")

    def load_mis(self):
        """
        To load medical image considering local file format
        """
        if self.__extension == "dcm":
            for i in os.listdir(self.path_mi):
                p_srs = os.path.join(self.path_mi, i)
                self.__study.append({})
                if i == "Ground":
                    continue
                for j in os.listdir(p_srs):
                    img = dcmread(os.path.join(p_srs, j))   # To load image
                    self.__study[-1][img[0x0020, 0x0013].value]=img
                # sorted(self.__study[-1].items())
                # self.__study[-1] = list(self.__study[-1].values())
    def find_mi_type(self):
        """
        To find Input Medical Image Type
        """
        # Modality: 0x0008, 0x0060  // MR, CT
        # Series Description: 0x0008, 103E  // acquired series
        # Body Part Examined: 0018, 0015  // ABDOMEN
        # Acquisition Number: 0020, 0012
        # Instance Number: 0020, 0013
        # Instance Number: 0020, 0013
        # Window Center: 134
        # Window Width: 350
        if self.__extension == "dcm":
            for srs in self.__study:
                if srs == "Ground":
                    continue
                self.__mi_info.append({})
                print(self.__study.index(srs))
                for i, sl in srs.items():
                    self.__mi_info[-1][sl[0x0020, 0x0013].value] = {"modality":sl[0x0008, 0x0060].value,
                                                                    "series description": sl[0x0008, 0x103E].value,
                                                                    "examined": sl[0x018, 0x0015].value,
                                                                    # "acquisition number": sl[0x0020, 0x0012].value,
                                                                    "instance number": sl[0x0020, 0x0013].value,
                                                                    "window center": sl[0x0028, 0x1050].value,
                                                                    "window width": sl[0x0028, 0x1051].value,
                                                                    # "voxel": sl[0x0028, 0x0030].value,
                                                                    }
                self.__mi_info[-1] = dict(sorted(self.__mi_info[-1].items()))
                # self.__mi_info[-1]=list(self.__mi_info[-1].values())
        else:
            pass

    def convert_mi_by_color_depth(self):
        rescale_slope = 1
        rescale_intercept = 0
        for i in range(len(self.__study)):
            if i == "Ground":
                continue
            self.__mi_slices.append({})
            for j in list(self.__study[i].keys()):
                cur_sl = self.__study[i][j].pixel_array
                center = float(self.__mi_info[i][j]["window center"])
                width = float(self.__mi_info[i][j]["window width"])
                cur_sl = rescale_slope*cur_sl + rescale_intercept
                ymin = 0
                ymax = 255
                # print(np.array(cur_sl).shape)
                cur_sl = np.reshape(cur_sl, (np.array(cur_sl).shape[0], np.array(cur_sl).shape[1], 1))
                idx_high = cur_sl >= center+width/2
                idx_low = cur_sl <= center-width/2

                cur_sl = np.where(idx_high, ymax, cur_sl)
                cur_sl = np.where(idx_low, ymin, cur_sl)

                cur_sl = np.where(~idx_high & ~idx_low, ((cur_sl-center)/width+0.5)*(ymax-ymin)+ymin, cur_sl)
                cur_sl = cur_sl.astype(np.uint8)
                self.__mi_slices[-1][self.__mi_info[i][j]["instance number"]]= cur_sl

            self.__mi_slices[-1] = dict(sorted(self.__mi_slices[-1].items()))
            # self.__mi_slices[-1] = list(self.__mi_slices[-1].values())

    def get_extension(self):
        return self.__extension

    def display_slices(self):
        for i in range(len(self.__mi_slices)):
            for j in range(len(self.__mi_slices[i])):
                cv2.imshow("Display", self.__mi_slices[i][j])
                cv2.waitKey()

    def play_slices(self):
        for i in range(len(self.__mi_slices)):
            for j in range(len(self.__mi_slices[i])):
                cv2.imshow("Display", self.__mi_slices[i][j])
                cv2.waitKey(10)

    def save(self):
        for i in range(len(self.__mi_slices)):
            os.mkdir(os.path.join(self.path_save , str(i)))
            for j,k in self.__mi_slices[i].items():
                # cur_j = len(list(self.__mi_slices[i].items()))-int(j)+1
                cur_j = j
                cv2.imwrite(os.path.join(self.path_save, str(i), str(cur_j).zfill(5)+".png"), k)

    def save_mritopng(self):
        for i in os.listdir(self.path_mi):
            mritopng.convert_folder(os.path.join(self.path_mi, i), os.path.join(self.path_save, i),)



if __name__ == '__main__':
    # path_dcm = r"D:\Dataset\LLU Dataset\6218843_07202017 (MR)\01. Original Study\Original Dicom File"
    # path_save = r"D:\Dataset\LLU Dataset\6218843_07202017 (MR)\01. Original Study\img"
    # # for srs in os.listdir(path_dcm):
    # #     os.mkdir(os.path.join(path_save, srs))
    # #     print(srs)
    #     # for sl in os.listdir(os.path.join(path_dcm, srs)):
    # path_mi = os.path.join(path_dcm)
    # path_cur_save = os.path.join(path_save)
    # mil = MedicalImageLoader(path_mi, path_cur_save)
    # mil.find_extension()
    # mil.load_mis()
    # mil.find_mi_type()
    # mil.convert_mi_by_color_depth()
    # mil.save()
    # mil.save_mritopng()

    # path_root = r"D:\Dataset\Dataset\Liver\CHAOS\CHAOS_Train_Sets\Train_Sets\MR"
    # path_save = r"E:\1. Lab\Daily Results\2021\2109\0924\CHAOS_Train"
    # for case in os.listdir(path_root):
    #     # print(os.path.join(path_root, case))
    #     os.mkdir(os.path.join(path_save, case))
    #     path_case = os.path.join(path_root, case)
    #     for srs in os.listdir(path_case):
    #         if "T2SPIR" == srs:
    #             path_cur = os.path.join(path_case, srs)
    #             os.mkdir(os.path.join(path_save, case, srs))
    #
    #             path_mi = path_cur
    #             # path_mi = r"D:\Dataset\LLU Dataset\8082200_08312017 (Uploading), MR\01. Original CT Study\ANON11442"
    #             path_cur_save = os.path.join(path_save, case, srs)
    #             print(path_cur, path_cur_save)
    #             mil = MedicalImageLoader(path_mi, path_cur_save)
    #             mil.find_extension()
    #             # print(mil.get_extension())
    #             mil.load_mis()
    #             mil.find_mi_type()
    #             mil.convert_mi_by_color_depth()
    #             # mil.play_slices()
    #             mil.save()
    #     print()


    path_root = r"D:\Dataset\LLU Dataset\6487537_05292016 (MR)\01. Original Image\01. DICOM"
    path_save = r"D:\Dataset\LLU Dataset\6487537_05292016 (MR)\01. Original Image\03. PNG 2"
    # for srs in os.listdir(path_root):
        # os.mkdir(os.path.join(path_save, srs))
        # for sl in os.listdir(os.path.join(path_root, srs)):
    mil = MedicalImageLoader(os.path.join(path_root), os.path.join(path_save))
    mil.find_extension()
    mil.load_mis()
    mil.find_mi_type()
    mil.convert_mi_by_color_depth()
    mil.save()



    # path_mi = r"D:\Dataset\Dataset\Liver\CHAOS\CHAOS_Train_Sets\Train_Sets\MR\1\T1DUAL\DICOM_anon"
    # # path_mi = r"D:\Dataset\LLU Dataset\8082200_08312017 (Uploading), MR\01. Original CT Study\ANON11442"
    # path_save = r"E:\1. Lab\Daily Results\2021\2109\0923\test1"
    # mil = MedicalImageLoader(path_mi, path_save)
    # mil.find_extension()
    # # print(mil.get_extension())
    # mil.load_mis()
    # mil.find_mi_type()
    # mil.convert_mi_by_color_depth()
    # mil.play_slices()
    # mil.save()