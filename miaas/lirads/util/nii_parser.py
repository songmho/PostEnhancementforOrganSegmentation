"""
Date: 2021. 05. 25.
Programmer: MH
Description: Code for Parsing NII file generating dataset
"""
import os
import random
import shutil

import nibabel as nib
import cv2
import numpy as np
import json


class NIIParser:
    def __init__(self):
        self.file_path = ""
        self.window = {"abdomen":{"ww":400,"wc":40}, "liver":{"ww":160,"wc":60}, "pancreas":{"ww":131.4,"wc":41.4},
                       "spleen":{"ww":175.5,"wc":20.8}, "portal_vein": {"ww":305.6,"wc":38}, "lung":{"ww":1600,"wc":-600}}

    def set_file_path(self, path):
        self.file_path = path

    def set_mask_file_path(self, path):
        self.mask_file_path = path

    def set_save_folder(self, path_save_img):
        self.path_save_img = path_save_img

    def set_save_folder_mask(self, path_save_img_mask):
        self.path_save_img_mask = path_save_img_mask

    def load_slice(self, organ="abdomen"):
        """
        To load CT slice in a nii file
        :param organ: string, target organ to be able to regularize window
        :return:
        """
        self.cur_slices = []
        img = nib.load(os.path.join(self.file_path))
        self.img_data = img.get_fdata()
        self.img_header = img.header

        self.scl_slope = 1.0
        self.scl_inter = 0
        for i in range(self.img_header.get_data_shape()[2]):
            cur_img = self.img_data[:, ::-1, self.img_header.get_data_shape()[2]-(i+1)]     # To need to change direction of series
            if np.max(cur_img)/1000 >10:
                cur_img = cur_img/10
                cur_img = cur_img[:, ::-1]
            cur_img = np.rot90(cur_img, 1)
            cur_img = self.scl_slope*cur_img + self.scl_inter
            cur_window = self.window[organ]
            ww = cur_window["ww"]
            wc = cur_window["wc"]
            ymin = 0
            ymax = 255
            cur_img = np.reshape(cur_img, (512, 512, 1))
            # To convert color depth applying numpy where method (To reduce computation time)
            idx_high = cur_img >= wc + ww / 2
            idx_low = cur_img <= wc - ww / 2

            cur_img = np.where(idx_high, ymax, cur_img)
            cur_img = np.where(idx_low, ymin, cur_img)
            cur_img = np.where(~idx_high & ~idx_low, ((cur_img - wc) / ww + 0.5) * (ymax - ymin) + ymin, cur_img)
            cur_img = cur_img.astype(np.uint8)
            self.cur_slices.append(cur_img)

    def load_mask(self):
        """
        TO load mask data from a nii file
        :return:
        """
        img = nib.load(os.path.join(self.mask_file_path))
        self.img_data = img.get_fdata()
        self.img_header = img.header
        self.cur_livers = []
        self.cur_tumors = []

        for i in range(self.img_header.get_data_shape()[2]):
            cur_img = self.img_data[:, :, self.img_header.get_data_shape()[2] - (i + 1)]     # To need to change direction of series
            cur_img = np.rot90(cur_img, 1)

            print(np.unique(cur_img))

            cur_liver_img = np.array(np.where(cur_img>0, 255, 0), dtype=np.uint8)
            cur_tumor_img = np.array(np.where(cur_img==4, 255, 0), dtype=np.uint8)        # To need to change considering tumor or liver label number
            self.cur_livers.append(cur_liver_img)
            self.cur_tumors.append(cur_tumor_img)

    def set_current_id(self, id):
        self.cur_id = id

    def set_current_phase(self, phase):
        self.cur_phase = phase

    def save_slice(self):
        """
        To save CT slices in a CT series
        :return:
        """
        for i in range(len(self.cur_slices)):
            cv2.imwrite(os.path.join(self.path_save_img, self.cur_id+"_"+self.cur_phase+"_"+str(i+1).zfill(5)+".png"), self.cur_slices[i])

    def save_mask(self, target):
        """
        To save mask data
        :param target: string, "liver" or "tumor"
        :return:
        """
        if target == "liver":
            for i in range(len(self.cur_livers)):
                cv2.imwrite(os.path.join(self.path_save_img_mask, self.cur_id+"_"+self.cur_phase+"_"+str(i + 1).zfill(5) + ".png"), self.cur_livers[i])
        else:
            for i in range(len(self.cur_tumors)):
                cv2.imwrite(os.path.join(self.path_save_img_mask, self.cur_id+"_"+self.cur_phase+"_"+str(i + 1).zfill(5) + ".png"), self.cur_tumors[i])


class SinglePhaseNIIParser:
    def __init__(self):

        self.window = {"abdomen":{"ww":400,"wc":40}, "liver":{"ww":160,"wc":60}, "pancreas":{"ww":131.4,"wc":41.4},
                       "spleen":{"ww":175.5,"wc":20.8}, "portal_vein": {"ww":305.6,"wc":38}, "lung":{"ww":1600,"wc":-600}}

    def set_mask_file_path(self, path):
        self.mask_file_path = path
        print(self.mask_file_path)

    def set_save_file_path(self, path):
        self.save_path = path

    def load_mask(self):
        """
        TO load mask data from a nii file
        :return:
        """
        img = nib.load(os.path.join(self.mask_file_path))
        self.img_data = img.get_fdata()
        self.img_header = img.header
        self.cur_livers = []
        self.cur_tumors = []

        print(self.img_header.get_data_shape())

        # print(self.img_data.shape)
        for i in reversed(range(self.img_header.get_data_shape()[2])):
            # cur_img = self.img_data[:, ::-1, self.img_header.get_data_shape()[2] - (i + 1)]     # To need to change direction of series (x, y, z)
            cur_img = self.img_data[::-1, :, i]     # To need to change direction of series (z, y, x) for kidney
            cur_img = np.rot90(cur_img, 3)
            #
            # print(cur_img.shape, "   ", np.unique(cur_img))
            cur_liver_img = cur_img
            cur_liver_img = np.array(np.where((cur_img >0) & (cur_img!=4), 255, 0), dtype=np.uint8)
            self.cur_livers.append(cur_liver_img)
            # self.cur_tumors.append(cur_tumor_img)
            # cv2.imshow("asdfasdf", cur_liver_img)
            # cv2.waitKey(1)



    def load_slice(self, organ="abdomen"):
        """
        To load CT slice in a nii file
        :param organ: string, target organ to be able to regularize window
        :return:
        """
        self.cur_slices = []
        img = nib.load(os.path.join(self.mask_file_path))
        self.img_data = img.get_fdata()
        self.img_header = img.header

        self.scl_slope = 1.0
        self.scl_inter = 0

        print(self.img_header.get_data_shape())

        for i in range(self.img_header.get_data_shape()[2]):

            # cur_img = self.img_data[:, ::-1, self.img_header.get_data_shape()[2]-(i+1)]     # To need to change direction of series (x, y, z)
            cur_img = self.img_data[:, ::-1, self.img_header.get_data_shape()[2]-i-1]     # To need to change direction of series (z, y, x) for kidney
            print(np.unique(cur_img))
            # if np.max(cur_img)/1000 > 10:
            #     cur_img = cur_img/10
            #     cur_img = cur_img[::-1, ::-1]
            cur_img = np.rot90(cur_img, 1)
            print(np.max(cur_img), np.min(cur_img))
            cur_img = self.scl_slope*cur_img + self.scl_inter
            print(np.max(cur_img), np.min(cur_img))
            cur_window = self.window[organ]
            ww = cur_window["ww"]
            wc = cur_window["wc"]
            ymin = 0
            ymax = 255
            cur_img = np.reshape(cur_img, (512, 512, 1))
            # To convert color depth applying numpy where method (To reduce computation time)
            idx_high = cur_img >= wc + ww / 2
            idx_low = cur_img <= wc - ww / 2

            cur_img = np.where(idx_high, ymax, cur_img)
            print(np.max(cur_img), np.min(cur_img))
            cur_img = np.where(idx_low, ymin, cur_img)
            print(np.max(cur_img), np.min(cur_img))
            cur_img = np.where(~idx_high & ~idx_low, ((cur_img - wc) / ww + 0.5) * (ymax - ymin) + ymin, cur_img)
            print(np.max(cur_img), np.min(cur_img))
            cur_img = cur_img.astype(np.uint8)
            print(np.max(cur_img), np.min(cur_img))
            print("\n\n\n")
            self.cur_slices.append(cur_img)
            # cv2.imshow("asdfasdf", cur_img)
            # cv2.waitKey(5)

    def save_slice(self):
        """
        To save CT slices in a CT series
        :return:
        """
        for i in range(len(self.cur_slices)):
            cv2.imwrite(os.path.join(self.save_path, str(i + 1).zfill(5) + ".png"), self.cur_slices[i])

    def save_mask(self):

        """
        To save CT slices in a CT series
        :return:
        """
        for i in range(len(self.cur_livers)):
            cv2.imwrite(os.path.join(self.save_path, str(i + 1).zfill(5) + ".png"), self.cur_livers[i])


class JsonGenerator:
    def convert_mask_to_coordinates(self, path_mask):
        """
        To convert mask data to coordinates
        :param path_mask: string, Mask File Path
        :return:
        """
        result = {}
        for i in os.listdir(path_mask):
            if "png" in i or "jpg" in i:
                cur_mask = cv2.imread(os.path.join(path_mask, i), cv2.IMREAD_GRAYSCALE)
                contours, hierarchy = cv2.findContours(cur_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
                masks = []
                for c in contours:
                    list_x = []
                    list_y = []
                    for d in c:
                        x = int(d[0][0])
                        y = int(d[0][1])
                        list_x.append(x)
                        list_y.append(y)
                    masks.append((list_x, list_y))
                result[i] = masks
        return result

    def generate_json_file(self, data, path_img, target):
        """
        To generate json file for training mask RCNN model
        :param data: dict, data for coordinates
        :param path_img: str, path for image
        :param target: str, target for the json file
        :return:
        """
        result = {}
        for d in list(data.keys()):
            path_cur_slice = os.path.join(path_img, d)
            result[d+str(os.stat(path_cur_slice).st_size)] = {
                "filename": d,
                "size": int(os.stat(path_cur_slice).st_size),
                "regions": [],
                "file_attributes": {}
            }
            for m in data[d]:
                result[d + str(os.stat(path_cur_slice).st_size)]["regions"].append({
                    "shape_attributes":{
                        "name":"polygone",
                        "all_points_x": m[0],
                        "all_points_y": m[1]
                    }, "region_attributes": {}
                })

        with open(os.path.join(path_img, target+".json"), "w") as json_file:
            json.dump(result, json_file, indent=4)


class ImageSplitter:
    def __init__(self):
        self.path_img = r""
        self.path_label = r""
        self.list_trues = []
        self.list_falses = []
        self.list_train = []
        self.list_test = []
        self.path_save = r"E:\1. Lab\Dataset\Liver\By MD\converted\combined"

    def set_path_img(self, p):
        self.path_img = p

    def set_path_label(self, p):
        self.path_label = p

    def set_path_save(self, p):
        self.path_save = p

    def check_t_f(self):
        for i in os.listdir(self.path_label):
            img = cv2.imread(os.path.join(self.path_label, i))
            if len(np.unique(img))>1:
                self.list_trues.append(i)
            else:
                self.list_falses.append(i)

    def split_data(self):
        random.shuffle(self.list_trues)
        random.shuffle(self.list_falses)

        self.list_train = self.list_trues[:int(len(self.list_trues)*0.7)]
        self.list_test = self.list_trues[int(len(self.list_trues)*0.7):]

        self.list_train.extend(self.list_falses[:int(len(self.list_falses)*0.7)])
        self.list_test.extend(self.list_falses[int(len(self.list_falses)*0.7):])

    def save_files(self):
        for i in self.list_train:   #  data for training
            shutil.copy(os.path.join(self.path_img, i), os.path.join(self.path_save, "img", "train", i))
            shutil.copy(os.path.join(self.path_label, i), os.path.join(self.path_save, "liver", "train", i))

        for i in self.list_test:   #  data for test
            shutil.copy(os.path.join(self.path_img, i), os.path.join(self.path_save, "img", "val", i))
            shutil.copy(os.path.join(self.path_label, i), os.path.join(self.path_save, "liver", "val", i))


if __name__ == '__main__':
    # nii_parser = NIIParser()
    # # cur_data = "1604844"
    # cur_data = "7006698"
    # nii_parser.set_current_id(cur_data)
    # for phase in [ "p"]:
    #     nii_parser.set_current_phase(phase)
    #     file_path = os.path.join(r"E:\1. Lab\Dataset\Liver\By MD\original", cur_data,"series",cur_data + phase + "_image.nii")
    #     save_path_img = os.path.join(r"E:\1. Lab\Dataset\Liver\By MD\converted", cur_data, "img")
    #     nii_parser.set_file_path(file_path)
    #     nii_parser.set_save_folder(save_path_img)
    #     nii_parser.load_slice(organ="abdomen")
    #     nii_parser.save_slice()
    #     for target in ["liver", "tumor"]:
    #         mask_file_path = os.path.join(r"E:\1. Lab\Dataset\Liver\By MD\original", cur_data, "label", cur_data+phase+".nii")
    #         path_mask = os.path.join(r"E:\1. Lab\Dataset\Liver\By MD\converted", cur_data, target)
    #         nii_parser.set_mask_file_path(mask_file_path)
    #         nii_parser.set_save_folder_mask(path_mask)
    #         nii_parser.load_mask()
    #         nii_parser.save_mask(target)

            # data = nii_parser.convert_mask_to_coordinates(os.path.join(path_mask, target, phase))
            # nii_parser.generate_json_file(data, save_path_img, target)


    # img_splitter = ImageSplitter()
    # img_splitter.set_path_img(r"E:\1. Lab\Dataset\Liver\By MD\converted\7006698\img")
    # img_splitter.set_path_label(r"E:\1. Lab\Dataset\Liver\By MD\converted\7006698\liver")
    # img_splitter.set_path_save(r"E:\1. Lab\Dataset\Liver\By MD\converted\combined")
    # img_splitter.check_t_f()
    # img_splitter.split_data()
    # img_splitter.save_files()
    #
    # jg = JsonGenerator()
    # path_img = r"E:\1. Lab\Dataset\Liver\By MD\converted\combined\img"
    # path_mask = r"E:\1. Lab\Dataset\Liver\By MD\converted\combined\liver"
    # for i in ["train", "val"]:
    #     result = jg.convert_mask_to_coordinates(os.path.join(path_mask, i))
    #     jg.generate_json_file(result, os.path.join(path_img, i), "liver")

    spnp = SinglePhaseNIIParser()
    path_root = r"D:\Daily Result\2304\0428\segmentation result - MedSeg (with range)"
    path_save_root_img = r"D:\Daily Result\2304\0428\segmentation result - MedSeg (with range) - png"
    # path_save_root_mask = r"E:\2. Project\Python\kits21\kits21\mask"

    # for id in os.listdir(path_root):
    path = os.path.join(path_root)
    path_save_img = os.path.join(path_save_root_img)
    # path_save_mask = os.path.join(path_save_root_mask, i)
    # os.mkdir(path_save)
    for f in os.listdir(path):
        # path_cur_save = os.path.join(path_save, f.split(".")[0])
        path_cur_save_img = os.path.join(path_save_img, f)
        # path_cur_save_mask = os.path.join(path_save_mask)
        if not os.path.isdir(path_cur_save_img):
            os.mkdir(path_cur_save_img)
        # if not os.path.isdir(path_cur_save_mask):
        #     os.mkdir(path_cur_save_mask)
        spnp.set_mask_file_path(os.path.join(path, f))
        # if f == "aggregated_AND_seg.nii.gz":
        #     print("MASK: ", end="")
        #     # spnp.set_save_file_path(path_cur_save_mask)
        #     # spnp.load_mask()
        #     # spnp.save_mask()
        # elif f == "imaging.nii.gz":
        print("IMG : ", end="")
        spnp.set_save_file_path(path_cur_save_img)
        spnp.load_mask()
        spnp.save_mask()
        print("================================")
