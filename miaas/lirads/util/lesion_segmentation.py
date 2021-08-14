"""
Date: 2020. 06. 08.
Programmer: MH
Description: Code for segmenting Lesion and Liver part
"""

import tensorflow as tf
from miaas.lirads.util import lesion
from miaas.lirads.util import liver
import numpy as np
import miaas.lirads.util.mrcnn.model as modellib


class LesionOrganSegmenter:
    def __init__(self):
        """
        To initialize variables
        """
        self.LESION_SEG_MODEL_DIR = ".\\models\\tumor_segment\\logs"
        self.LESION_SEG_WEIGHT_DIR = ".\\models\\tumor_segment\\mask_rcnn_lesion_0100.h5"

        self.LIVER_SEG_MODEL_DIR = ".\\models\\liver_segment\\logs"
        self.LIVER_SEG_WEIGHT_DIR = ".\\models\\liver_segment\\mask_rcnn_liver_0100.h5"

        self.init_op = tf.global_variables_initializer()

        self.sess = tf.Session()
        self.sess.run(self.init_op)

    def load_model(self):
        """
        To load saved model
        :return: None
        """
        self.lesion_config = lesion.LesionConfig()

        self.lesion_detector = modellib.MaskRCNN(mode='inference',
                                                 model_dir=self.LESION_SEG_MODEL_DIR,
                                                 config=self.lesion_config)  # To use segmentation based on CNN
        self.lesion_detector.load_weights(self.LESION_SEG_WEIGHT_DIR, by_name=True)
        self.lesion_class_names = ['None', 'Lesion']

        self.liver_config = liver.LiverConfig()

        self.liver_detector = modellib.MaskRCNN(mode='inference',
                                                 model_dir=self.LIVER_SEG_MODEL_DIR,
                                                 config=self.liver_config)  # To use segmentation based on CNN
        self.liver_detector.load_weights(self.LIVER_SEG_WEIGHT_DIR, by_name=True)
        self.liver_class_names = ['None', 'Liver']

    def segment_lesion(self, img):
        """
        To segment lesion part from input image
        :param img: 2Darray, input slice
        :return: dict, {'rois': ,  'class_ids': , 'masks':, 'scores':}
        """
        results = self.lesion_detector.detect([img], verbose=0)
        result = results[0]
        rois = result['rois']
        final_rois = []
        # obs[obs == True] = 255
        # obs[obs == False] = 0
        # print(np.where(result['masks']==True))
        for i in range(len(rois)):
            roi = rois[i]
            final_rois.append(img[roi[0] - 15:roi[2] + 15, roi[1] - 15:roi[3] + 15])
        result['rois'] = final_rois
        result['roi'] = rois

        return result

    def segment_liver(self, img):
        """
        To segment liver part from input image
        :param img: 2Darray, input slice
        :return: dict, {'rois': ,  'class_ids': , 'masks':, 'scores':}
        """
        results = self.liver_detector.detect([img], verbose=0)
        result = results[0]
        rois = result['rois']
        final_rois = []
        for i in range(len(rois)):
            roi = rois[i]
            final_rois.append(img[roi[0] - 15:roi[2] + 15, roi[1] - 15:roi[3] + 15])
        result['rois'] = final_rois
        result['roi'] = rois
        return result

    def check_intersection(self, roi_organ, roi_lesion):
        """
        To check intersection between detected organ and lesion
        :param roi_organ: list, coordinates of detected organ part [y1, x1, y2, x2]
        :param roi_lesion: list, coordinates of detected lesion part [y1, x1, y2, x2]
        :return:
        """
        print(roi_organ, roi_lesion)
        o_y1, o_x1, o_y2, o_x2 = roi_organ[0][0], roi_organ[0][1], roi_organ[0][2], roi_organ[0][3]
        l_y1, l_x1, l_y2, l_x2 = roi_lesion[0][0], roi_lesion[0][1], roi_lesion[0][2], roi_lesion[0][3]
        new_l_y1, new_l_x1, new_l_y2, new_l_x2 = 0, 0, 0, 0
        if ((o_x1 < l_x1 and l_x2 < o_x2) and (o_y1 < l_y1 and l_y2 < o_y2)):   # part of lesion is included at part of organ
            new_l_y1, new_l_x1, new_l_y2, new_l_x2 = l_y1, l_x1, l_y2, l_x2
        else:
            if (l_x2 < o_x1) or (o_x2 < l_x1):  # Not intersected
                new_l_y1, new_l_x1, new_l_y2, new_l_x2 = l_y1, l_x1, l_y2, l_x2
            else:
                if l_x1 < o_x1:     # If left of lesion is smaller than left of organ
                    new_l_x1 = o_x1
                if l_x2 < o_x2:     # If right of lesion is bigger than right of organ
                    new_l_x2 = o_x2
            if (l_y2 < o_y1) or (o_y2 < l_y1):  # Not intersected
                new_l_y1, new_l_x1, new_l_y2, new_l_x2 = l_y1, l_x1, l_y2, l_x2
            else:
                if l_y1 < o_y1:     # If top of lesion is higher than top of organ
                    new_l_y1 = o_y1
                if l_y2 < o_y2:     # If bottom of lesion is lower than bottom of organ
                    new_l_y2 = o_y2

        new_area = np.sqrt((new_l_x2-new_l_x1)**2)*np.sqrt((new_l_y2-new_l_y1)**2)
        lesion_area = np.sqrt((l_x2-l_x1)**2)*np.sqrt((l_y2-l_y1)**2)
        return round(new_area/lesion_area, 2)
