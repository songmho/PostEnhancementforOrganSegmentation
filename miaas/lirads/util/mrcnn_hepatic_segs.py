"""
Date: 2022. 03. 14.
Programmer: MH
Description: Code for segmenting Hepatic segments using Mask RCNN
"""
import json
import os
# os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT_DIR = r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\util'
sys.path.append(ROOT_DIR)  # To find local version of the library
from mrcnn.config import Config
from mrcnn import model as modellib, utils


class HepaticSegSegmentatorMRCNN:
    def __init__(self):
        self.train_set = None
        self.test_set = None
        self.path_pre_trained_weight = r""
        self.path_model = r"F:\model_save\hepatic_segments"
        self.path_coco_model = r"E:\1. Lab\Projects\Wrinkle Segmentation\Model\COCO\mask_rcnn_coco.h5"
        self.epoch = 1000

    def load_dataset(self, path_anno_train, path_anno_test, path_img_train, path_img_test):
        """
        To load training set and test set from local
        """
        self.train_set = HepaticSegSubset()
        self.train_set.load_data(path_anno_train, path_img_train, True)
        self.train_set.prepare()
        print("Done to load training set")

        self.test_set = HepaticSegSubset()
        self.test_set.load_data(path_anno_test, path_img_test, False)
        self.test_set.prepare()
        print("Done to load validation set")

    def initialize_structure(self, mode="training", version="coco", path=None):
        """
        To initialize segmentation structure
        """
        self.config = HepaticSegmentsSegmentorConfig()
        self.segmentor = modellib.MaskRCNN(mode=mode, config=self.config, model_dir=self.path_model)
        if mode == "training":
            if version == "coco":
                self.segmentor.load_weights(self.path_coco_model, by_name=True, exclude=["mrcnn_class_logits", "mrcnn_bbox_fc", "mrcnn_bbox", "mrcnn_mask"])
            else:
                self.segmentor.load_weights(self.segmentor.find_last(), by_name=True)
                # self.segmentor.load_weights(r"F:\SELab\700.... PROJECTS\2022.02, Liver Cancer Diagnosis System with LI-RADS\6. Machine Learning Models\02. Tumor Segmentation\mask_rcnn_tumor_000070.h5", by_name=True)
        else:
            if path is None:
                self.segmentor.load_weights(self.segmentor.find_last(), by_name=True)
            else:
                self.segmentor.load_weights(path, by_name=True)

    def train(self):
        self.segmentor.train(self.train_set, self.test_set, learning_rate=self.config.LEARNING_RATE, epochs=self.epoch, layers="heads")

    def segment(self, img):
        results = self.segmentor.detect([img])
        result = results[0]
        discarded_ids = []
        # for i in range(len(result["class_ids"])):
        #     if result["scores"][i] < 0.5:
        #         discarded_ids.append(i)
        #         continue
        # for i in reversed(discarded_ids):
        #     result["rois"] = np.delete(result["rois"], i)
        #     result["class_ids"] = np.delete(result["class_ids"], i)
        #     result["scores"] = np.delete(result["scores"], i)
        #     result["masks"] = np.delete(result["masks"], i)
        return result



class HepaticSegmentsSegmentorConfig(Config):
    # Give the configuration a recognizable name
    # NAME = "face_trouble"
    # # Train on 1 GPU and 1 image per GPU. Batch size is 1 (GPUs * images/GPU).
    # GPU_COUNT = 1
    # IMAGES_PER_GPU = 1
    # # Number of classes (including background)
    # NUM_CLASSES = 1 + 1  # background + 1 (6 classes for face trouble)
    # # image size
    # IMAGE_MIN_DIM = 576
    # IMAGE_MAX_DIM = 576
    # # LEARNING_RATE = 0.0005              # 0.0005
    # LEARNING_RATE = 0.001              # 0.0005
    # # STEPS_PER_EPOCH = 3    # Number of steps per epoch
    # STEPS_PER_EPOCH = 35       # Number of steps per epoch
    # VALIDATION_STEPS = 1
    # BACKBONE = 'resnet101'    # resnet101 following original setting
    # # TODO: resnet50
    # RPN_ANCHOR_SCALES = (9, 18, 36, 72, 144)
    # # RPN_ANCHOR_SCALES = (16, 32, 64, 128, 256)
    # RPN_NMS_THRESHOLD = 0.5
    # USE_MINI_MASK = False
    # # TRAIN_ROIS_PER_IMAGE = 500
    # TRAIN_ROIS_PER_IMAGE = 250
    # DETECTION_MIN_CONFIDENCE = 0.5
    # ROI_POSITIVE_RATIO = 0.33
    # DETECTION_NMS_THRESHOLD = 0.3
    # MAX_GT_INSTANCES = 100
    # POST_NMS_ROIS_INFERENCE = 200
    # POST_NMS_ROIS_TRAINING = 500
    # RPN_ANCHOR_RATIOS = [0.5, 1, 2]
    # MINI_MASK_SHAPE = (8, 8)  # (height, width) of the mini-mask




    # Give the configuration a recognizable name
    NAME = "hepatic_segments"
    # Train on 1 GPU and 1 image per GPU. Batch size is 1 (GPUs * images/GPU).
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    # Number of classes (including background)
    NUM_CLASSES = 1 + 9  # background + 1 (6 classes for face trouble)
    # image size
    IMAGE_MIN_DIM = 512
    IMAGE_MAX_DIM = 512
    # LEARNING_RATE = 0.0005              # 0.0005
    LEARNING_RATE = 0.001              # 0.0005
    STEPS_PER_EPOCH = 20    # Number of steps per epoch
    VALIDATION_STEPS = 1
    BACKBONE = 'resnet101'    # resnet101 following original setting
    RPN_ANCHOR_SCALES = (32, 64, 128, 256, 512)
    RPN_NMS_THRESHOLD = 0.7
    TRAIN_ROIS_PER_IMAGE = 500
    DETECTION_MIN_CONFIDENCE = 0.7
    ROI_POSITIVE_RATIO = 0.7
    DETECTION_NMS_THRESHOLD = 0.3
    MAX_GT_INSTANCES = 100
    RPN_ANCHOR_RATIOS = [0.5, 1, 2]



class HepaticSegSubset(utils.Dataset):
    def load_data(self, f_anno, path_img, y):
        """Load a subset of the COCO dataset.
        dataset_dir: The root directory of the COCO dataset.
        subset: What to load (train, val, minival, valminusminival)
        year: What dataset year to load (2014, 2017) as a string, not an integer
        class_ids: If provided, only loads images that have the given classes.
            different datasets to the same class ID.
        return_coco: If True, returns the COCO object.
        auto_download: Automatically download and unzip MS-COCO images and annotations
        """
        # Load json from file
        json_file = open(f_anno)
        coco_json = json.load(json_file)
        json_file.close()

        # Add the class names using the base method from utils.Dataset
        source_name = "coco_like"
        for category in coco_json['categories']:
            class_id = category['id']
            class_name = category['name']
            if class_id < 1:
                print('Error: Class id for "{}" cannot be less than one. (0 is reserved for the background)'.format(
                    class_name))
                return

            self.add_class(source_name, class_id, class_name)

        # Get all annotations
        annotations = {}
        for annotation in coco_json['annotations']:
            image_id = annotation['image_id']
            if image_id not in annotations:
                annotations[image_id] = []
            annotations[image_id].append(annotation)
        # if y:
        #     for i in range(280):
        #         if i not in annotations.keys():
        #             annotations[i] = [{}]
        # else:
        #     for i in range(8):
        #         if i not in annotations.keys():
        #             annotations[i] = [{}]


        # Get all images and add them to the dataset
        seen_images = {}
        for image in coco_json['images']:
            image_id = image['id']
            if image_id in seen_images:
                print("Warning: Skipping duplicate image id: {}".format(image))
            else:
                seen_images[image_id] = image
                try:
                    image_file_name = image['file_name']
                    image_width = image['width']
                    image_height = image['height']
                except KeyError as key:
                    print("Warning: Skipping image (id: {}) with missing key: {}".format(image_id, key))
                image_path = os.path.abspath(os.path.join(path_img, image_file_name))
                image_annotations = annotations[image_id]

                # Add the image using the base method from utils.Dataset
                self.add_image(
                    source=source_name,
                    image_id=image_id,
                    path=image_path,
                    width=image_width,
                    height=image_height,
                    annotations=image_annotations
                )

    def generate_mask_data(self, annotation_json, path_save):
        msks = {}
        imgs_dic = {}
        with open(annotation_json, "r") as anno_json:
            a_json = json.load(anno_json)
            imgs = a_json["images"]
            for i in range(len(imgs)):
                imgs_dic[imgs[i]["id"]] = imgs[i]["file_name"]

            annotations = a_json["annotations"]
            for i in range(len(annotations)):
                if annotations[i]["image_id"] not in msks.keys():
                    msks[annotations[i]["image_id"]] = np.zeros((512, 512))

            for i in range(len(annotations)):
                anno = annotations[i]
                segs = anno["segmentation"]
                cur_msk = np.zeros((512, 512))
                for seg in segs:
                    coordinates = []
                    for j in range(0, len(seg), 2):
                        coordinates.append([[int(seg[j]), int(seg[j+1])]])
                    coordinates = np.array(coordinates)
                    cv2.drawContours(cur_msk, contours=[coordinates], contourIdx=-1, color=255, thickness=cv2.FILLED)
                msks[annotations[i]["image_id"]] = msks[annotations[i]["image_id"]] +cur_msk
                msks[annotations[i]["image_id"]] = np.where(msks[annotations[i]["image_id"]] > 0, 255, 0)

        for k, v in msks.items():
            cv2.imwrite(os.path.join(path_save, imgs_dic[k]), v)

    def load_mask(self, image_id):
        """ Load instance masks for the given image.
        MaskRCNN expects masks in the form of a bitmap [height, width, instances].
        Args:
            image_id: The id of the image to load masks for
        Returns:
            masks: A bool array of shape [height, width, instance count] with
                one mask per instance.
            class_ids: a 1D array of class IDs of the instance masks.
        """
        image_info = self.image_info[image_id]
        annotations = image_info['annotations']
        instance_masks = []
        class_ids = []

        for annotation in annotations:
            class_id = annotation['category_id']
            mask = Image.new('1', (image_info['width'], image_info['height']))
            mask_draw = ImageDraw.ImageDraw(mask, '1')
            for segmentation in annotation['segmentation']:
                mask_draw.polygon(segmentation, fill=1)
                bool_array = np.array(mask) > 0
                instance_masks.append(bool_array)
                class_ids.append(class_id)

        mask = np.dstack(instance_masks)
        class_ids = np.array(class_ids, dtype=np.int32)

        return mask, class_ids
