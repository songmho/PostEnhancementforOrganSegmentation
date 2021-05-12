"""
Date: 2020. 10. 13.
Programmer: MH
Description: Code for classes related to lesion
"""

import util.mrcnn.model as modellib
from backup import lesion
import numpy as np


class LesionSegmenter:
    def __init__(self):
        TUMOR_SEG_MODEL_DIR = "..\\models\\tumor_segment\\logs"
        TUMOR_SEG_WEIGHT_DIR = "..\\models\\tumor_segment\\mask_rcnn_lesion_0100.h5"

        self.config = lesion.LesionConfig()

        self.tumor_detector = modellib.MaskRCNN(mode='inference',
                                                model_dir=TUMOR_SEG_MODEL_DIR,
                                                config=self.config)  # To use segmentation based on CNN
        self.tumor_detector.load_weights(TUMOR_SEG_WEIGHT_DIR, by_name=True)
        self.tumor_class_names = ['None', 'Lesion']
        self.margin = 15

    def detect(self, img):
        results = self.tumor_detector.detect([img], verbose=0)
        return results
        # result = results[0]
        # rois = result['rois']
        # final_rois = []
        # for i in range(len(rois)):
        #     roi = rois[i]
        #     final_rois.append(img[roi[0] - self.margin:roi[2] + self.margin, roi[1] - self.margin:roi[3] + self.margin])
        # result['rois'] = final_rois
        # try:
        #     result['roi'] = rois[0]
        # except:
        #     result['roi'] = []
        # return result

    def _change_mask_img_type(self, msk):
        """
        To chagne type of input ndarray (mask result)
        :param msk:
        :return:
        """
        # if msk.shape != (512, 512, 1):
        #     msk = np.zeros(shape=(512, 512, 1))
        msk = np.where(msk==True, 255, msk)
        msk = np.where(msk==False, 0, msk)

        msk = np.uint8(msk)
        print(msk.shape)
        if msk.shape[2] > 1:
            msk_def = msk[:,:,0]
            for i in range(1, msk.shape[2]):
                msk_def += msk[:,:,i]
            msk = msk_def
            msk[msk>=255] = 255
            msk[msk<255] = 0

        elif msk.shape[2] == 0:
            msk = np.zeros((512, 512, 1))
        # if len(msk.shape) == 2:
        #     pass
        # elif len(msk.shape) == 3:
        #     msk = cv2.cvtColor(msk, cv2.COLOR_BGR2GRAY)
        return msk
