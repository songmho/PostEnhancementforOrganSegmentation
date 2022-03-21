"""
Date: 2022. 03. 12.
Programmer: MH
Description: Code for Hepatic segments Segmentator class
"""
from miaas.lirads.util.mrcnn_hepatic_segs import HepaticSegSegmentatorMRCNN
import numpy as np

class HepaticSegmentsSegmentator:
    def __init__(self, type):
        self.type = type    # Segmentation Algorithm Type (MASKRCNN / UNET)
        self.path_model = r""

    def load_model(self):
        if self.type == "MRCNN": # The Type is MASKRCNN
            self.hepatic_segements_model = HepaticSegSegmentatorMRCNN()
            self.path_model = r"F:\model_save\hepatic_segments\hepatic_segments20220312T1652\mask_rcnn_hepatic_segments_00800.h5"
            self.hepatic_segements_model.initialize_structure("inference", path=self.path_model)
            pass
        else:   # The Type is UNET
            pass

    def predict(self, srs):
        result_srs = []
        if self.type == "MRCNN": # The Type is MASKRCNN
            for i in srs:
                rst = self.hepatic_segements_model.segment(i)
                result_srs.append(rst)
        else:   # The Type is UNET
            pass
        return result_srs