"""
Date: 2020. 10. 13.
Programmer: MH
Description: Code for ML models related to Liver
"""

import cv2
from tensorflow.python.keras.backend import clear_session

import miaas.lirads.util.mrcnn.model as modellib
from miaas.lirads.util import liver
import numpy as np
import pydicom


class LiverSegmenter:
    def __init__(self):
        self.liver_class_names = ['None', 'Liver']
        self.margin = 15
        self.config = liver.LiverConfig()


    def load_model(self):
        LIVER_SEG_MODEL_DIR = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\mias_with_lirads\\mias\\miaas\\lirads\\models\\liver_segment\\logs"
        LIVER_SEG_WEIGHT_DIR = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\mias_with_lirads\\mias\\miaas\\lirads\\models\\liver_segment\\mask_rcnn_liver_0100.h5"


        self.liver_detector = modellib.MaskRCNN(mode='inference',
                                                model_dir=LIVER_SEG_MODEL_DIR,
                                                config=self.config)  # To use segmentation based on CNN
        self.liver_detector.load_weights(LIVER_SEG_WEIGHT_DIR, by_name=True)

    def clear_session(self):
        """
        To clear session for segmenting objects
        The method is for running segmentation code in web service.
        :return:
        """
        clear_session()

    def segment(self, img):
        results = self.liver_detector.detect([img], verbose=0)
        result = results[0]
        rois = result['rois']
        final_rois = []
        for i in range(len(rois)):
            roi = rois[i]
            final_rois.append(img[roi[0] - self.margin:roi[2] + self.margin, roi[1] - self.margin:roi[3] + self.margin])
        result['rois'] = final_rois
        try:
            result['roi'] = rois[0]
        except:
            result['roi'] = []
        return result

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
        # if len(msk.shape) == 2:
        #     pass
        # elif len(msk.shape) == 3:
        #     msk = cv2.cvtColor(msk, cv2.COLOR_BGR2GRAY)

        if msk.shape[2] > 1:
            msk_def = msk[:,:,0]
            for i in range(1, msk.shape[2]):
                msk_def += msk[:,:,i]
            msk = msk_def
            msk[msk>=255] = 255
            msk[msk<255] = 0
        elif msk.shape[2] == 0:
            msk = np.zeros((512, 512, 1))
        return msk


if __name__ == '__main__':

    # for file in os.listdir("E:\\1. Lab\\Dataset\\Liver\\LiverCTCancerArchive\\Custom, DICOM\\TCGA-DD-A4NL\\07-11-2001\\2 Venous\\"):

    dc = pydicom.dcmread("E:\\1. Lab\\Dataset\\Liver\\LiverCTCancerArchive\\Custom, DICOM\\TCGA-DD-A1EH\\06-29-2001\\3 Delay\\000001.dcm")
    img = dc.pixel_array
    print("Dicom Pixel Array Type: ", img.dtype)
    img1 = img.astype(np.uint8)
    print(img1)
    print(img1.shape, img1.dtype)
    cv2.imwrite("Delay.png", img1)
    cv2.imshow("TEST", img1)
    cv2.waitKey(0)

    # s = int(dc.RescaleSlope)
    # b = int(dc.RescaleIntercept)
    # img = s*img + b
    #
    # img1 = img.astype(np.uint8)
    # print(img1)
    # print(img1.shape, img1.dtype)
    # cv2.imshow("TEST", img1)
    # cv2.waitKey(0)
    #
    # ww = dc[0x0028, 0x1051].value[0]
    # wc = dc[0x0028, 0x1050].value[0]
    # print(ww, wc)
    #
    # ymin = 0
    # ymax = 255
    # print(img.shape)
    # img = np.reshape(img, (512, 512, 1))
    # for j in range(len(img)):
    #     for k in range(len(img[j])):
    #         x = img[j][k][0]
    #         img[j][k][0] = (ymax-ymin)/(1+np.exp(-4*((x-wc)/ww)))+ymin
    #         # if x <= wc - ww/2:
    #         #     img[j][k][0] = ymin
    #         # elif x > wc+ww/2:
    #         #     img[j][k][0] = ymax
    #         # else:
    #         #     img[j][k][0] = int(((x-wc)/ww+0.5)*(ymax-ymin)+ymin)
    #
    # # img = np.clip(img, wc - (ww/2), wc+(ww/2))
    # print("Dicom Pixel Array Type: ", img.dtype)
    # img = img.astype(np.uint8)
    # print(img.shape, type(img[0][0][0]))
    # cv2.imwrite(".\\CT.jpg", img)
    # cv2.imshow("TEST", img)
    # cv2.waitKey(0)
    #
    # # img = cv2.imread("E:\\1. Lab\\Dataset\\Liver\\LiverCTCancerArchive\\Custom, IMG\\TCGA-DD-A4NL\\07-11-2001\\2 Venous\\"+file)
    # # # img = img[:,:,0]
    # # # print(img[0][0])
    # # img = np.reshape(img, (512, 512, 1))
    # ls = LiverSegmenter()
    # result = ls.segment(img)
    # print(result["masks"].shape)
    # r = result['masks']*255
    # r = r.astype(np.uint8)
    # print(type(r))
    # # cv2.imwrite("..\\Liver_Detection_result\\png\\CT\\"+file+".jpg", img)
    # # try:
    # #     cv2.imwrite("..\\Liver_Detection_result\\png\\Detect\\"+file+".jpg", r)
    # # except:
    # #     pass
    # cv2.imshow("TEST2", r)
    # cv2.waitKey(0)
