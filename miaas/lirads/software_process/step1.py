"""
Date: 2020. 10. 13.
Programmer: MH
Description: Code for step 1. segment Liver Region
"""
import scipy

from software_process.livers import LiverSegmenter
import numpy as np
import cv2
from scipy.spatial import distance


class LiverRegionSegmentor:
    def __init__(self):
        self.ml_liver_seg = LiverSegmenter()

    def load_model(self):
        """
        To load model
        :return:
        """

    def segment_liver(self, set_ct_a):
        """
        To segment liver region (Task 1)
        :return:
        """
        result = self.ml_liver_seg.segment(set_ct_a)
        return result

    def discard_slices(self, set_ct_a_liver, set_ct_a_seg):
        """
        To discard CT slices not having liver regions (Task 2)
        :return:
        """

    def generate_mask_from_points(self, slice_width, slice_height, points_x=None, points_y=None, points=None):
        """
        To generate mask for annotated liver region
        :param slice_width: int, width for target CT slice
        :param slice_height: int, height for target CT slice
        :param points_x: list, list of x axis for whole points
        :param points_y:list, list of y axis for whole points
        :param points: list, list of whole points, if it is None, points_x and points_y are applied.
        :return: nparray, mask including liver region
        """
        mask = np.zeros((slice_height, slice_width), np.uint8)
        # To
        if points is None:  # points_x and points_y are not None
            if points_x is None and points_y is None:  # If there is no points
                return mask

            # To make points list using points_x and points_y
            points = []
            for i in range(len(points_x)):
                points.append([points_x[i], points_y[i]])
            points = np.array([points], dtype=np.int32)
            try:
                cv2.fillPoly(mask, points, (255, 255, 255))     # To add polygon
            except:
                return mask
        else:   # points is not None (points_x and points_y are None)
            try:
                cv2.fillPoly(mask, points, (255, 255, 255))     # To add polygon
            except:
                return mask
        return mask

    def compute_dice_coef(self, original, predicted):
        """
        To compute dice coefficient
        DSC = 2|X ^ Y|/ |X|+|Y|
        :param original: ndarray, mask having annotated liver region by human
        :param predicted: ndarray, mask having segmented liver region by model
        :return: dsc, double, 0..1
        """
        area_org = self.compute_area(original)
        area_prd = self.compute_area(predicted)

        # area_inter = area_pred-((area_org+area_prd)-area_org)
        area_union = original+predicted
        area_union = np.where(area_union < 255, 0, area_union)
        area_union = np.where(area_union >= 255, 255, area_union)

        area_only_pred = area_union-original
        area_only_pred = np.where(area_only_pred < 255, 0, area_only_pred)
        area_only_pred = np.where(area_only_pred >= 255, 255, area_only_pred)

        if area_org > 0:
            area_inter = predicted - area_only_pred        # (area of whole Original - the area having only original)
            area_inter = np.where(area_inter<=0, 0, area_inter)
            area_inter = np.where(area_inter>=255, 255, area_inter)

            area_inter = self.compute_area(area_inter)
        else:
            area_inter = 0      # If original is None, the union result must be zero.
        try:
            dsc = 2*area_inter / (area_org+area_prd)
        except:
            dsc = 0
        return dsc

    def compute_match_shape(self, org, prd):
        """
        To compute hu moments
        :param org: list, list of points
        :param prd: list, list of points
        :return:
        """
        set_contour = {}
        try:
            num_org_regions = len(org[0])
        except:
            num_org_regions = 0
        try:
            num_seg_regions = len(prd[0])
        except:
            num_seg_regions = 0
        if num_seg_regions == 0 or num_org_regions == 0:
            return 0

        result = cv2.matchShapes(org[0], prd[0], cv2.CONTOURS_MATCH_I1, 0.0)
        return result

    def compute_contour_difference(self, org, prd):
        """
        To compute difference of two contours from annotated (original) and segmented (Predicted)

        :param org: list, lists of points, [contours_obj1, ..., ...] contours_obj# = [[x1, y1], [x2, y2],..,..]
        :param prd: list, lists of points, [contours_obj1, ..., ...] contours_obj# = [[x1, y1], [x2, y2],..,..]
        """
        try:
            num_org_regions = len(org)
            area_org = cv2.contourArea(org[0])
        except:
            num_org_regions = 0
            area_org = 0
        try:
            num_seg_regions = len(prd)
            area_seg = cv2.contourArea(prd[0])
        except:
            num_seg_regions = 0
            area_seg = 0

        if area_org >= area_seg:
            list_small = prd
            list_big = org
        else:
            list_small = org
            list_big = prd
        if (num_org_regions == 0 and num_seg_regions != 0) or (num_org_regions != 0 and num_seg_regions == 0):
            return np.inf
        elif num_org_regions == 0 and num_seg_regions == 0:
            return 0
        else:   # # of Original Regions >=1 and # of predicted Results >= 1
            sum_dist = 0
            for l_b in range(len(list_big)):    # # of Big > 1
                img_src = np.zeros((512, 512), np.uint8)
                mask_src = cv2.drawContours(img_src, np.array([list_big[l_b]]), -1, (255), thickness=cv2.FILLED)
                for i in range(len(list_small)):
                    img_trg = np.zeros((512, 512))
                    mask_trg = cv2.drawContours(img_trg, np.array([list_small[i]]), -1, (255),  thickness=cv2.FILLED)
                    intersect = self.compute_intersection(mask_src, mask_trg)
                    if intersect > 0.5:
                        for p_src in list_big[l_b]:
                            p_trg, dist = self.compute_closest_point(p_src, list_small[i])
                            sum_dist += dist

            return sum_dist/len(list_big[0])

    def compute_intersection(self, org, trg):
        """
        To compute intersection
        :param org: array,
        :param trg: array,
        :return:
        """
        sum = org+trg
        sum = np.where(sum<=0, 0, sum)
        sum = np.where(sum>=255, 255, sum)
        sum = np.sum(sum)

        area_org = np.sum(org)
        area_trg = np.sum(trg)
        print(sum, area_org, area_trg)
        area_result = 1 - (sum - area_org)/sum

        return area_result

    def get_center(self, cnt):
        """
        To compute center from contour
        :param cnt: list, contour
        :return: tuple, (center x, center y)
        """
        moment = cv2.moments(cnt)
        cx = int(moment["m10"]/moment["m00"])
        cy = int(moment["m01"]/moment["m00"])
        return (cx, cy)

    def compute_shortest_dist(self, contour, center):
        """
        To compute the longest distances
        :param contour: list, contour
        :param center: tuple, (center x, center y)
        :return: double, the shortest distance
        """
        shrt_dist = np.inf
        for p_c in contour:
            dist = distance.cdist(np.array(p_c), np.array([center]))
            if shrt_dist < dist:
                shrt_dist = dist

        return shrt_dist

    def compute_closest_point(self, p_src, p_list):
        """
        To compute the closest point in a contour from a point in other contour
        :param p_src: list, source point [x, y]
        :param p_list: list, list of list, [[x, y], [x2, y2], ...]
        :return: list, a point returned the shortest distance between p_from and the point
                 double, the shortest distance
        """
        if len(np.array(p_list).shape)>2:
            p_targets = p_list
            p_list = []
            # the shape is (X, 1, 2)
            for p_trg in p_targets:
                p_list.append(p_trg[0]) # To change the shape to (X, 2)

        dists = distance.cdist(np.array(p_src), p_list)
        short_idx = dists.argmin()
        short_dist = min(dists)
        return p_list[short_idx], short_dist[0]

    def compute_area(self, mask):
        """
        To compute area of the liver part in slice
        :param mask: ndarray, ndarray having segmented liver region
        :return: int, the number of pixels for liver region
        """
        if len(mask.shape) == 3:
            mask = mask[:,:,0]
        if mask.dtype == bool:
            mask = np.where(mask==True, 255, mask)
            mask = np.where(mask==False, 0, mask)

        area = np.sum(mask)   # To add whole elements values
        return area

    def compute_overlap_rate(self, sl1, sl2):
        """
        To compute overlapped rate between two Slices
        :param sl1: ndarray, mask of current CT slice
        :param sl2: ndarray, mask of previous CT slice
        :return: double, 0..1
        """
        sl1 = sl1["masks"]
        sl2 = sl2["masks"]
        area_sl1 = self.compute_area(sl1)
        area_sl2 = self.compute_area(sl2)
        # sl1 = np.uint8(sl1)
        # sl2 = np.uint8(sl2)

        area_sum = sl1 + sl2
        area_sum = self.compute_area(area_sum)
        if area_sl1 >= area_sl2:
            area_big = area_sl1
            area_small = area_sl2
        else:
            area_big = area_sl2
            area_small = area_sl1
        try:
            overlap_rate = 1 - ((area_sum-area_big)/area_small)
        except:
            overlap_rate = 0
        return overlap_rate

    def compute_change_rate(self, sl1, sl2):
        """
        To compute change rate
        :param sl1: ndarray, mask of current CT slice
        :param sl2: ndarray, mask of previous CT slice
        :return: double, change range
        """
        sl1 = sl1["masks"]
        sl2 = sl2["masks"]

        area_sl1 = self.compute_area(sl1)
        area_sl2 = self.compute_area(sl2)

        if area_sl1 == 0:
            return 0

        change_rate = (area_sl2-area_sl1)/area_sl1
        return change_rate


class LiverSegmentDetector:
    def __init__(self):
        pass

    def load_model(self):
        """
        To load segment detection model
        :return:
        """

    def segment_liver_region(self, set_ct_b):
        """
        To detect liver regions (Task 3)
        :param set_ct_b: images
        :return:
        """
