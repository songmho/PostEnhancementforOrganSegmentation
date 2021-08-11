"""
Date: 0201. 07. 28.
Programmer: MH
Description: Code for Grouping CT slices & Tumor Data
"""
import os
import cv2
import numpy as np
from pydicom import dcmread
import nibabel as nib
from slice_similarity_measurer import SimilarityMeasurer

class CTSLGrouper:
    """
    To consider similarity of segmented results
    """
    def __init__(self):
        self.mask_similarity_measurer = SimilarityMeasurer()
        self.mask_similarity_measurer.prepare_model()
        self.path = r""
        self.series = {}

    def load_series_img(self, path):
        # p = r"E:\1. Lab\Daily Results\2021\2107\0728\LLU Dataset\09. 1668171\01. Image\1668171-v"
        #
        # for i in os.listdir(p):
        #     path_i = os.path.join(p, i)
        #     img = cv2.imread(path_i)
        #     img = np.where(img>180, img, 0)
        #     cv2.imwrite(os.path.join(r"E:\1. Lab\Daily Results\2021\2107\0728\LLU Dataset\09. 1668171\05. Others 2", i), img)
        pass

    def load_series_dcm(self, path):
        self.series = {}
        for i in os.listdir(path):
            self.series[i] = []
            phases = {}
            for j in os.listdir(os.path.join(path, i)):
                ds = dcmread(os.path.join(path, i, j))
                phases[str(ds[0x0020, 0x0013].value).zfill(5)] = float(ds[0x0020, 0x1041].value)
                # print(j, ds[0x0020, 0x1041].value, ds[0x0020, 0x0013])
            phases = sorted(phases.items())
            self.series[i] = phases

        for i in self.series.keys():
            print(i)
            for j in self.series[i]:
                print("   "+str(j[1]))
            print()

    def load_series_nii(self, path):
        self.series = {}
        ww, wc = 400, 210
        ymin, ymax = 0, 255
        for i in os.listdir(path):
            imgs = nib.load(os.path.join(path, i)).get_fdata()
            sls = []
            for j in range(len(imgs[0, 0, :])-1, -1, -1):
                sl = imgs[:, ::-1, j]
                sl = np.rot90(sl, 1)

                sl = np.reshape(sl, (512, 512, 1))
                idx_high = sl >= wc+ww/2
                idx_low = sl <= wc-ww/2
                sl = np.where(idx_high, ymax, sl)
                sl = np.where(idx_low, ymin, sl)
                sl = np.where(~(idx_high | idx_low), ((sl-wc)/ww+0.5)*(ymax-ymin)+ymin, sl)
                sl = np.where(sl>50, sl, 0)
                sl = np.array(sl, dtype=np.uint8)

                # cv2.imshow("wi", sl)
                # cv2.waitKey()
                sls.append(sl)
            self.series[i] = sls

    def load_series(self, path):
        self.series = {}
        for i in os.listdir(path):
            self.series[i] = []
            for j in os.listdir(os.path.join(path, i)):
                img = cv2.imread(os.path.join(path, i, j))
                # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                self.series[i].append(img)

    def compare_similarity_dcm(self):
        """
        To consider slice location information in DICOM header
        """
        keys = list(self.series.keys())
        list_results = {}
        for k in keys:
            list_results[k] = len(self.series[k])

        trg_srs_id = -1
        smaller = 1000000
        for k in range(1, len(list_results)):
            if list_results[keys[k]] != list_results[keys[k-1]]:
                if list_results[keys[k]] < list_results[keys[k-1]]:
                    if smaller < list_results[keys[k]]:
                        smaller = list_results[keys[k]]
                        trg_srs_id = k
                else:
                    if smaller < list_results[keys[k-1]]:
                        smaller = list_results[keys[k-1]]
                        trg_srs_id = k-1

        if trg_srs_id == -1:
            trg_srs_id = 0

        other_keys = keys
        del other_keys[trg_srs_id]

        results = []
        for i in self.series[keys[trg_srs_id]]:
            cur_trg_sl_loc = i[1]
            cur_result = [i]
            for j in other_keys:
                # To find smallest difference.
                small_diff = 1000000
                selected_j_sl = -1
                for k in self.series[j]:
                    if np.abs(cur_trg_sl_loc-k[1]) < small_diff:
                        selected_j_sl = k
                        small_diff = np.abs(cur_trg_sl_loc-k[1])
                cur_result.append(selected_j_sl)
            results.append(cur_result)
        return results

    def compare_similarity_nii(self):
        """
        To consider shape of spine bone in each CT slice in different CT series
        """
        list_total_trg = list(self.series.values())[0]
        self.groups = []

        for i in range(1, len(self.series.values())):
            list_cur_trg = list(self.series.values())[i]
            diff = len(list_cur_trg) - len(list_total_trg)


            for j in range(len(list_total_trg)):
                img1 = list_total_trg[j]
                img1 = np.where(img1>0, 255, 0)
                mx_diff = j+diff
                if mx_diff > len(list_total_trg):
                    mx_diff = len(list_total_trg)

                maximum, id = -1, -1
                for k in range(j, mx_diff):
                    img2 = list_cur_trg[k]
                    img2 = np.where(img2>0, 255, 0)
                    if maximum < np.count_nonzero(np.bitwise_and(img1, img2)):
                        maximum = np.count_nonzero(np.bitwise_and(img1, img2))
                        id = j

                self.groups.append([i, id, maximum])

            criteria = {}
            for i in range(1, len(self.groups)):
                cur_cri = self.groups[i][1] - self.groups[i-1][1]
                if cur_cri not in list(criteria.keys()):
                    criteria[cur_cri] = 1
                else:
                    criteria[cur_cri] += 1
            criteria = dict(sorted(criteria.items(), key=lambda item: item[1]))
            trg_criterion = list(criteria.keys())[-1]

            list_trg = []
            diff = self.groups[0][1] - self.groups[0][0]

            for i in range(1, len(self.groups)):
                if self.groups[i][1] != self.groups[i][0] + diff:
                    list_trg.append(self.groups[i])
                else:
                    if len(list_trg) <= 1:
                        list_trg = []
                        list_trg.append(self.groups[i])
                    else:
                        list_trg.append(self.groups[i])
                        del list_trg[0]

                        trg_id = list_trg[-1][1]
                        del list_trg[-1]
                        for k in range(len(list_trg)):
                            self.groups[i - (k + 1)] = [self.groups[i - (k + 1)][0], trg_id - (k + 1), 0]

            if len(list_trg) > 1:
                if list_trg[-1][0] + diff == list_trg[-1][1]:
                    # To repeat from -1 to 0
                    for k in range(1, len(list_trg)):
                        self.groups[len(self.groups) - k] = [self.groups[len(self.groups) - k][0],
                                                           self.groups[len(self.groups) - k][0] + diff, 0]
                else:
                    # To repeat from 0 to max
                    for k in range(len(list_trg) - 1, 0, -1):
                        self.groups[len(self.groups) - k] = [self.groups[len(self.groups) - k][0],
                                                           self.groups[len(self.groups) - k][0] + diff, 0]


class TumorGrouper:
    """
    To consider inclusive relationship of segmented tumors in nearby CT slices
    """
    def __init__(self, path):
        self.path = path
        self.grp_tumors = {}    # {0:[[id, mask_sub],[id, mask_sub],... ], 1: ...}

    def group_tumor(self):
        for i in os.listdir(self.path):
            cur_img = cv2.imread(os.path.join(self.path, i))
            if len(np.unique(cur_img)) == 1:    # Empty
                continue
            cur_sub_segs = self.__get_sub_seg_data(cur_img)
            count = 0
            for cur_msk in cur_sub_segs:
                count+=1
                is_contained = False
                for j in self.grp_tumors.keys():
                    # cur_id = int(i.split("_")[1].split(".")[0])     # To be changed considering index format
                    cur_id = int(i.split(".")[0])     # To be changed considering index format
                    list_del = []
                    list_del_id = []
                    for k in range(len(self.grp_tumors[j])-1, -1, -1):
                        # prv_id = int(self.grp_tumors[j][k][0].split("_")[1].split(".")[0])  # To be changed considering index format
                        prv_id = int(self.grp_tumors[j][k][0].split(".")[0])  # To be changed considering index format
                        if cur_id-prv_id == 1:
                            if len(list_del_id) == 0:
                                if self.__check_overlapped(self.grp_tumors[j][k][1], cur_msk):
                                    self.grp_tumors[j].append([i, cur_msk])
                                is_contained = True
                            else:
                                if self.__check_overlapped(self.grp_tumors[j][k][1], cur_msk):
                                    for del_id in list_del_id:
                                        del self.grp_tumors[j][del_id]
                                    list_del.append(cur_msk)
                                    self.grp_tumors[j][k].append([i, self.__combine_masks(list_del)])
                                    is_contained = True
                                else:
                                    is_contained = False
                            break
                        elif cur_id-prv_id == 0:
                            list_del_id.append(k)
                            list_del.append(self.grp_tumors[j][k][1])
                        else:
                            break
                if not is_contained:
                    self.grp_tumors[len(self.grp_tumors)] = [[i, cur_msk]]

    def get_grp_tumors(self):
        return self.grp_tumors

    def __combine_masks(self, list_mask):
        mask_result = np.zeros(list_mask[0].shape)
        for i in list_mask:
            mask_result+= i
        return mask_result

    def __check_overlapped(self, m1, m2):
        num_overlapped = np.count_nonzero(np.bitwise_and(m1, m2))
        return num_overlapped>0

    def __get_sub_seg_data(self, img):
        """
        To return each section of segmented tumors
        """
        results = []
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cur_cnt, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for i in cur_cnt:
            new_mask = np.zeros(img.shape)
            results.append(np.array(cv2.drawContours(new_mask, [i], -1, color=255, thickness=cv2.FILLED), dtype=np.uint8))
        return results

if __name__ == '__main__':
    # p = r"F:\Dataset\Liver TUmor Dataset (Medical Decathlon)\labels\cancer"
    # for i in range(10):
    #     tg = TumorGrouper(os.path.join(p, str(i).zfill(3)))
    #     tg.group_tumor()
    #     dic_tumors = tg.get_grp_tumors()
    #     print(i, "    ", len(dic_tumors.keys()), len(dic_tumors[0]))
    #     for k in dic_tumors.keys():
    #         print("  ", k, len(dic_tumors[k]))
    #         for j in dic_tumors[k]:
    #             print("   ",j[0], end="")
    #         print()
    #     print()

    csg = CTSLGrouper()
    # csg.load_series_dcm(os.path.join(r"E:\1. Lab\Daily Results\2021\2107\0728\LLU Dataset\03. 7083077\00. DICOM\7083077_10302013_original\1.3.6.1.4.1.23849.2896420169.169.1637596314390516481"))
    # print(csg.compare_similarity_dcm())

    csg.load_series_nii(r"E:\1. Lab\Daily Results\2021\2107\0728\LLU Dataset\09. 1668171\01. Image\nii")
    csg.compare_similarity_nii()
    # csg.load_series(os.path.join(r"E:\1. Lab\Daily Results\2021\2107\0728\LLU Dataset\03. 7083077\03. Labels_Liver"))
    # print(csg.compare_similarity())

    # for i in os.listdir(r"E:\1. Lab\Daily Results\2021\2107\0728\LLU Dataset"):
    #     print(i)
    #     # csg.load_series(os.path.join(r"E:\1. Lab\Daily Results\2021\2107\0728\LLU Dataset", i, "03. Labels_Liver"))
    #     # dic = csg.compare_similarity()
    #     # for i in dic.keys():
    #     #     print(i, dic[i])
    #     print()