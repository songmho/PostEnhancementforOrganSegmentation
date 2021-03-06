"""
Date: 2020.03.31.
Programmer: MH
Description: Code for extracting tumor features based on CNN
"""
import csv
import locale
import math
import os
import time
from datetime import datetime

import pandas as pd

import cv2
import tensorflow as tf
from tensorflow.keras import Input, Model, callbacks
from tensorflow.keras.models import model_from_json
from tensorflow.keras.layers import Dropout, Dense, Activation, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.preprocessing import MultiLabelBinarizer
from tensorflow.keras.optimizers import Adam


class LesionImagingFeatureClassifier:
    def __init__(self):
        """
        To initialize variables
        """
        self.epochs = 300
        self.batch_size = 80    # Previous: , 20
        self.th_confidence = 0.7
        # self.IMAGE_DIMS = (32, 32, 1)
        # self.IMAGE_DIMS = (64, 64, 1)
        self.IMAGE_DIMS = (80, 80, 1)
        self.labels = ["Calcification", "Capsule", "CentralScar", "Hypoattenuating", "NoAPHE", "Nodular","NonrimAPHE","Unenhanced","Washout"]
        self.n_classes = len(self.labels)
        self.model = Sequential()
        # K.set_image_dim_ordering('tf')
        # config = tf.ConfigProto()
        # config.gpu_options.allow_growth = True
        # session = tf.Session(config=config)

    def define_structure_new(self, dim):
        """
        To define modified CNN Structure
        """
        self.IMAGE_DIMS = dim
        input = Input(shape=(self.IMAGE_DIMS[1], self.IMAGE_DIMS[0], 1))
        x = Conv2D(1, (2, 2), strides=1, padding="valid", activation="relu")(input)
        x = Conv2D(2, (2, 2), strides=1, padding="valid", activation="relu")(x)
        x = MaxPooling2D(pool_size=2)(x)

        x = Conv2D(2, (2, 2), strides=1, padding="valid", activation="relu")(x)
        x = Conv2D(4, (2, 2), strides=1, padding="valid", activation="relu")(x)
        x = MaxPooling2D(pool_size=2)(x)
        x = Conv2D(4, (2, 2), strides=1, padding="valid", activation="relu")(x)
        x = Conv2D(8, (2, 2), strides=2, padding="valid", activation="relu")(x)

        x = Flatten()(x)
        out = Dense(self.n_classes, activation="sigmoid")(x)
        self.model = Model(inputs=input, outputs=out)   # To define structure using input layer and output layer
        self.model.compile(loss="binary_crossentropy", optimizer=Adam(lr=0.01),
                           metrics=['accuracy', tf.keras.metrics.Precision(name="precision"),
                                    tf.keras.metrics.Recall(name="recall"), tf.keras.metrics.FalsePositives(name="false_positive"),
                                    tf.keras.metrics.FalseNegatives(name="false_negative")])  # To compile the structure
        # self.model.summary()        # To print information of each layer
    def define_structure_ver2(self, dims):
        """
        To define CNN Structure
        :return: None
        """
        self.IMAGE_DIMS = dims
        chanDim = -1
        input = Input(shape=(self.IMAGE_DIMS[1], self.IMAGE_DIMS[0], 1))    # Input layer
        x = Conv2D(32, (3, 3), padding="same")(input)   # (128, 128, 1) -> (128, 128, 32)
        x = Activation("relu")(x)                       # To transform values using activation function (ReLU)
        x = BatchNormalization(axis=chanDim)(x)         # To normalize data
        x = MaxPooling2D(pool_size=(3, 3))(x)           # To reduce size of data (128, 128, 32) -> (42, 42, 32)
        x = Dropout(0.25)(x)                            # To dropout # of neurons

        # (CONV => RELU) * 2 => POOL
        x = Conv2D(64, (3, 3), padding="same")(x)       # (42, 42, 32) -> (42, 42, 64)
        x = Activation("relu")(x)                       # To transform values using activation function (ReLU)
        x = BatchNormalization(axis=chanDim)(x)         # To normalize data
        x = Conv2D(64, (3, 3), padding="same")(x)       # (42, 42, 64) -> (42, 42, 64)
        x = Conv2D(64, (3, 3), padding="same")(x)       # (42, 42, 64) -> (42, 42, 64)
        x = Activation("relu")(x)                       # To transform values using activation function (ReLU)
        x = BatchNormalization(axis=chanDim)(x)         # To normalize data
        x = MaxPooling2D(pool_size=(2, 2))(x)           # To reduce size of data (42, 42, 64) -> (21, 21, 64)
        x = Dropout(0.25)(x)                            # To dropout # of neurons

        # (CONV => RELU) * 2 => POOL
        x = Conv2D(128, (3, 3), padding="same")(x)       # (21, 21, 64) -> (21, 21, 128)
        x = Activation("relu")(x)                        # To transform values using activation function (ReLU)
        x = BatchNormalization(axis=chanDim)(x)          # To normalize data
        x = Conv2D(128, (3, 3), padding="same")(x)       # (21, 21, 128) -> (21, 21, 128)
        x = Activation("relu")(x)                        # To transform values using activation function (ReLU)
        x = BatchNormalization(axis=chanDim)(x)          # To normalize data
        x = MaxPooling2D(pool_size=(2, 2))(x)            # To reduce size of data (21, 21, 128) -> (10, 10, 128)
        x = Dropout(0.25)(x)                             # To dropout # of neurons

        # first (and only) set of FC => RELU layers
        x = Flatten()(x)                                # To make feature map to plat (10, 10, 128) -> (12800)
        x = Dense(1024)(x)                              # To reduce the number of features (12800) -> (1024)
        x = Activation("relu")(x)                       # To transform values using activation function (ReLU)
        x = BatchNormalization()(x)                     # To normalize data
        x = Dropout(0.5)(x)                             # To dropout # of neurons

        # softmax classifier
        x = Dense(self.n_classes)(x)                    # To reduce the number of features (1024) -> (9)
        out = Activation("sigmoid")(x)                  # To transform values using activation function (ReLU)
        self.model = Model(inputs=input, outputs=out)   # To define structure using input layer and output layer

        self.model.compile(loss="binary_crossentropy", optimizer=Adam(lr=0.0005),
                           metrics=['accuracy', tf.keras.metrics.Precision(name="precision"),
                                    tf.keras.metrics.Recall(name="recall"), tf.keras.metrics.FalsePositives(name="false_positive"),
                                    tf.keras.metrics.FalseNegatives(name="false_negative")])  # To compile the structure
        self.model.summary()        # To print information of each layer
    def define_structure(self):
        """
        To define CNN Structure
        :return: None
        """

        chanDim = -1
        input = Input(shape=(self.IMAGE_DIMS[1], self.IMAGE_DIMS[0], 1))    # Input layer
        x = Conv2D(32, (3, 3), padding="same")(input)   # (128, 128, 1) -> (128, 128, 32)
        x = Activation("relu")(x)                       # To transform values using activation function (ReLU)
        x = BatchNormalization(axis=chanDim)(x)         # To normalize data
        x = MaxPooling2D(pool_size=(3, 3))(x)           # To reduce size of data (128, 128, 32) -> (42, 42, 32)
        x = Dropout(0.25)(x)                            # To dropout # of neurons

        # (CONV => RELU) * 2 => POOL
        x = Conv2D(64, (3, 3), padding="same")(x)       # (42, 42, 32) -> (42, 42, 64)
        x = Activation("relu")(x)                       # To transform values using activation function (ReLU)
        x = BatchNormalization(axis=chanDim)(x)         # To normalize data
        x = Conv2D(64, (3, 3), padding="same")(x)       # (42, 42, 64) -> (42, 42, 64)
        x = Conv2D(64, (3, 3), padding="same")(x)       # (42, 42, 64) -> (42, 42, 64)
        x = Activation("relu")(x)                       # To transform values using activation function (ReLU)
        x = BatchNormalization(axis=chanDim)(x)         # To normalize data
        x = MaxPooling2D(pool_size=(2, 2))(x)           # To reduce size of data (42, 42, 64) -> (21, 21, 64)
        x = Dropout(0.25)(x)                            # To dropout # of neurons

        # (CONV => RELU) * 2 => POOL
        x = Conv2D(128, (3, 3), padding="same")(x)       # (21, 21, 64) -> (21, 21, 128)
        x = Activation("relu")(x)                        # To transform values using activation function (ReLU)
        x = BatchNormalization(axis=chanDim)(x)          # To normalize data
        x = Conv2D(128, (3, 3), padding="same")(x)       # (21, 21, 128) -> (21, 21, 128)
        x = Activation("relu")(x)                        # To transform values using activation function (ReLU)
        x = BatchNormalization(axis=chanDim)(x)          # To normalize data
        x = MaxPooling2D(pool_size=(2, 2))(x)            # To reduce size of data (21, 21, 128) -> (10, 10, 128)
        x = Dropout(0.25)(x)                             # To dropout # of neurons

        # first (and only) set of FC => RELU layers
        x = Flatten()(x)                                # To make feature map to plat (10, 10, 128) -> (12800)
        x = Dense(1024)(x)                              # To reduce the number of features (12800) -> (1024)
        x = Activation("relu")(x)                       # To transform values using activation function (ReLU)
        x = BatchNormalization()(x)                     # To normalize data
        x = Dropout(0.5)(x)                             # To dropout # of neurons

        # softmax classifier
        x = Dense(self.n_classes)(x)                    # To reduce the number of features (1024) -> (9)
        out = Activation("sigmoid")(x)                  # To transform values using activation function (ReLU)
        self.model = Model(inputs=input, outputs=out)   # To define structure using input layer and output layer

        self.model.compile(loss="binary_crossentropy", optimizer=Adam(lr=0.0005),
                           metrics=['accuracy', tf.keras.metrics.Precision(name="precision"),
                                    tf.keras.metrics.Recall(name="recall"), tf.keras.metrics.FalsePositives(name="false_positive"),
                                    tf.keras.metrics.FalseNegatives(name="false_negative")])  # To compile the structure
        self.model.summary()        # To print information of each layer

    def load_data_new(self, path=r"E:\1. Lab\Daily Results\2022\2201\0117\data for classifying tumor image features from 5 studies\Increasing Size-ESRGAN", scaled=True):
        """
        To load subsets from local
        """
        # To load training set
        path_train = os.path.join(path, "Training Set")
        df_train = pd.read_csv(os.path.join(path, "train.csv"))
        self.train_x = []
        self.train_y = []

        for i in os.listdir(path_train):
            img = cv2.imread(os.path.join(path_train, i), cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, (self.IMAGE_DIMS[1], self.IMAGE_DIMS[0]))
            img = img_to_array(img)
            self.train_x.append(img)
        self.train_y = np.array(df_train.iloc[:, 7:16])

        # path_val = os.path.join(path, "val")
        # df_val = pd.read_csv(os.path.join(path, "val.csv"))
        # self.val_x = []
        # self.val_y = []
        # for i in os.listdir(path_val):
        #     img = cv2.imread(os.path.join(path_val, i), cv2.IMREAD_GRAYSCALE)
        #     img = cv2.resize(img, (self.IMAGE_DIMS[1], self.IMAGE_DIMS[0]))
        #     img = img_to_array(img)
        #     self.val_x.append(img)
        # self.val_y = np.array(df_val.iloc[:, 7:16])


        path_test = os.path.join(path, "Test Set")
        df_test = pd.read_csv(os.path.join(path, "test.csv"))
        self.test_x = []
        self.test_y = []
        for i in os.listdir(path_test):
            img = cv2.imread(os.path.join(path_test, i), cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, (self.IMAGE_DIMS[1], self.IMAGE_DIMS[0]))
            img = img_to_array(img)
            self.test_x.append(img)
        self.test_y = np.array(df_test.iloc[:, 7:16])

        img_gen = ImageDataGenerator()
        img_gen_origin = ImageDataGenerator()
        if scaled:
            self.train_x = np.array(self.train_x, dtype="float32") / 255
        else:
            self.train_x = np.array(self.train_x, dtype="float32")
        self.train_y = np.array(self.train_y, dtype="float64")
        # self.val_x = np.array(self.test_x, dtype="float32")
        # self.val_y = np.array(self.test_y, dtype="float64")
        if scaled:
            self.test_x = np.array(self.test_x, dtype="float32") / 255
        else:
            self.test_x = np.array(self.test_x, dtype="float32")
        self.test_y = np.array(self.test_y, dtype="float64")
        self.train_data_gen = img_gen.flow(self.train_x, self.train_y, batch_size=self.batch_size)
        self.test_data_gen = img_gen_origin.flow(self.test_x, self.test_y, batch_size=self.batch_size)
        self.num_total_train = len(self.train_x)
        self.num_total_test = len(self.test_x)

    def load_data(self):
        """
        To load dataset and split dataset
        :return: None
        """
        data_loc = r"F:\Dataset\LLU Dataset for Sub Data (Image Features)\Images"
        data = []
        labels = []

        # To load data from local
        for i in os.listdir(data_loc):
            f_path = os.path.join(data_loc, i)
            for j in os.listdir(os.path.join(data_loc, i)):
                img_path = os.path.join(f_path, j)
                image = cv2.imread(img_path)    ## To load image data
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)     # To change image color to gray scale
                image = cv2.resize(image, (self.IMAGE_DIMS[1], self.IMAGE_DIMS[0]))     # To resize (128, 128)
                image = img_to_array(image)     # To change image to array
                data.append(image)              # To store image data
                label = i.split("_")    # To make labels list splitting current file name
                labels.append(label)            # To save labels

        data = np.array(data)
        labels = np.array(labels)
        mlb = MultiLabelBinarizer()
        labels = mlb.fit_transform(labels)
        self.n_classes = len(mlb.classes_)
        for (i, label) in enumerate(mlb.classes_):
            self.labels.append(label)
        (self.train_x, self.test_x, self.train_y, self.test_y) = train_test_split(data, labels,
                                                                                  test_size=0.2, random_state=42)
        img_gen = ImageDataGenerator()
        img_gen_normal = ImageDataGenerator()
        self.train_data_gen = img_gen.flow(self.train_x, self.train_y, batch_size=self.batch_size)
        self.test_data_gen = img_gen_normal.flow(self.test_x, self.test_y, batch_size=self.batch_size)
        self.num_total_train = len(self.train_x)
        self.num_total_test = len(self.test_x)

    def get_labels(self):
        """
        To return labels of current data
        :return:
        """
        return self.labels

    def compute_performance(self):
        y_pred = []
        for x in self.train_x:
            y_pred.append((self.predict(x)[0]>self.th_confidence))
            # print(y_pred[-1])
        print("[Training Set]")
        print("Accuracy: ", accuracy_score(self.train_y, y_pred))
        print("Precision: ", precision_score(self.train_y, y_pred, pos_label="positive", average='micro'))
        print("Recall: ", recall_score(self.train_y, y_pred, pos_label="positive", average='micro'))

        y_pred = []
        for x in self.test_x:
            y_pred.append((self.predict(x)[0]>self.th_confidence))
            # print(y_pred[-1])
        print("[Test Set]")
        print("Accuracy: ", accuracy_score(self.test_y, y_pred))
        print("Precision: ", precision_score(self.test_y, y_pred, pos_label="positive", average='micro'))
        print("Recall: ", recall_score(self.test_y, y_pred, pos_label="positive", average='micro'))

    def train(self, cur_case, i):
        """
        To train model using the defined structure and the loaded dataset
        :return:
        """
        start_time = time.time()
        checkpoint_path = r"E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\util\backup\tumor_img_feature_classifier, mris\Case "+str(i)+" for Solution 4-2"+"\\"+cur_case+"\\tumor_image_feature_classifier_{epoch:05d}.h5"
        cp_callback = callbacks.ModelCheckpoint(filepath=checkpoint_path, save_weights_only=False, verbose=1, period=5)

        tb_callback = callbacks.TensorBoard(log_dir=r"E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\util\backup\tumor_img_feature_classifier, mris\Case "+str(i)+" for Solution 4-2"+"\\"+cur_case+"\\log", histogram_freq=1)
        self.history = self.model.fit_generator(
            self.train_data_gen,
            epochs=self.epochs,
            validation_data=(self.train_x, self.train_y),
            steps_per_epoch=math.ceil(self.num_total_train/self.batch_size),
            validation_steps=math.ceil(self.num_total_test/self.batch_size),
            callbacks=[cp_callback, tb_callback]
        )
        print("Elapsed Time: ", int(time.time()-start_time), "Seconds")

    def predict(self, test_imgs):
        """
        To predict imaging features about input image
        :param test_imgs: image, Lesion Image
        :return: List, List of Confidence Score about  Imaging features
        """
        # if len(test_imgs[0,0,:])>1:
        #     test_imgs = cv2.cvtColor(test_imgs, cv2.COLOR_BGR2GRAY)
        # t =  np.array(test_imgs*255, dtype=np.uint8)
        # cv2.imshow("test", t)
        # print(t.dtype, t.shape, np.unique(t))
        # cv2.waitKey()
        # image = cv2.resize(test_imgs, (128, 128))
        image = cv2.resize(test_imgs, (self.IMAGE_DIMS[1], self.IMAGE_DIMS[0]))
        image = img_to_array(image)
        image = np.expand_dims(image, axis=0)
        result = self.model.predict(x=image)        # To predict labels about test set image

        return result

    def save_model(self,i):
        """
        To save trained model
        :return:
        """
        m_json = self.model.to_json()
        with open(r"E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\util\backup\tumor_img_feature_classifier, mris\Case "+str(i)+" for Solution 4-2"+"\\model_binary_sigmoid.json", 'w') as json_file:
            json_file.write(m_json)     # To save trained model
        d = datetime.now()
        # self.model.save(r"E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\models\Tumor_Image_Features_Classification\mri\tumor_image_feature_classifier_"+str(self.epochs)+"_2022-01-24a.h5") # To save weight

    def load_model(self, k=None, i=250, cur_case=None):
        """
        To load saved model
        :return:
        """

        if k == "CT":
            json_file = open(r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\models\Tumor_Image_Features_Classification\model_binary_sigmoid.json', 'r')
            self.model = json_file.read()   # To load json file
            json_file.close()
            self.model = model_from_json(self.model)    # To convert json file to model
            # self.model.load_weights(r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\models\Tumor_Image_Features_Classification\weight_binary_sigmoid_'+str(self.epochs)+".h5") # To load weight
            # self.model.load_weights(r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\util\backup\tumor_img_feature_classifier, prv\tumor_image_feature_classifier_00101.h5') # To load weight
            self.model.load_weights(r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\util\backup\tumor_img_feature_classifier\model\tumor_image_feature_classifier_00230.h5') # To load weight

        else:   # MRI
            # json_file = open(r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\util\backup\tumor_img_feature_classifier, mris\Case '+cur_case.split("-")[1]+' for Solution 4-2'+'\\model_binary_sigmoid.json', 'r')
            json_file = open(r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\models\Tumor_Image_Features_Classification\mri\model_binary_sigmoid.json', 'r')
            self.model = json_file.read()   # To load json file
            json_file.close()
            self.model = model_from_json(self.model)    # To convert json file to model
            self.model.load_weights(r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\models\Tumor_Image_Features_Classification\mri\tumor_image_feature_classifier_00260_selected.h5') # To load weight
            # self.model.load_weights(r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\util\backup\tumor_img_feature_classifier\model\tumor_image_feature_classifier_mri_00250.h5') # To load weight
            # self.model.load_weights(r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\models\Tumor_Image_Features_Classification\mri\tumor_image_feature_classifier_00300.h5') # To load weight
            # self.model.load_weights(r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\util\backup\tumor_img_feature_classifier\0124a\tumor_image_feature_classifier_01000.h5') # To load weight



            # self.model.load_weights(r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\util\backup\tumor_img_feature_classifier\0124c\tumor_image_feature_classifier_'+str(i).zfill(5)+'.h5') # To load weight
            # self.model.load_weights(r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\util\backup\tumor_img_feature_classifier\0124c\tumor_image_feature_classifier_00750.h5') # To load weight


            # self.model.load_weights(r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\util\backup\tumor_img_feature_classifier, mris\Case '+cur_case.split("-")[1]+' for Solution 4-2'+"\\"+cur_case+'\\tumor_image_feature_classifier_'+str(i).zfill(5)+'.h5') # To load weight

            # self.model.load_weights(r"E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\util\backup\tumor_img_feature_classifier\tumor_image_feature_classifier_"+str(k).zfill(5)+".h5")
        self.model.compile(optimizer=Adam(lr=0.0005), loss='binary_crossentropy', metrics=['accuracy'])  # To compile model stacked
        # self.model.summary()
        # self.model.make_predict_function()

    def get_features(self, confs):
        """
        To get imaging features from confidence scores
        :param confs: list, list of confidence scores
        :return: imaging features returning higher value than threshold
        """
        high_labels, labels, pick_labels = [], [], []
        for i in range(len(confs)):
            if confs[i] >= self.th_confidence:      # If the confidence score is higher than threshold
                high_labels.append(i)       # ID of selected imaging features
                labels.append(self.labels[i])   # labels of selected imaging features
                pick_labels.append(confs[i])    # confidence score of selected imaging features
        if len(labels) == 0:
            high_labels.append(np.argmax(confs))
            labels.append(self.labels[np.argmax(confs)])
            pick_labels.append(confs[np.argmax(confs)])
        return {"High Id": high_labels, "Labels": labels, 'ConfidenceScores': pick_labels, "WholeConf": confs}


def extract_major_features(list_features):
    labels = ["Calcification",
              "Capsule",
              "CentralScar",
              "Hypoattenuating",
              "NoAPHE",
              "Nodular",
              "NonrimAPHE",
              "Unenhanced",
              "Washout"]
    dict_count = {}
    dict_result = {}
    th_conf = 0.6
    for i in labels:
        dict_count[i] = 0
        dict_result[i] = 0
    for fs in list_features:    # a Series
        for conf in range(len(fs["WholeConf"])):
            if fs["WholeConf"][conf] > th_conf:
                dict_count[labels[conf]] += 1

    selected_features = []
    for k, v in dict_count.items():
        if v >= int(len(dict_count.keys())/2):
            selected_features.append(list(dict_count.keys()).index(k))

    selected_list = []
    for f_id in range(len(list_features)):    # a Series
        fs = list_features[f_id]
        for l in selected_features:
            if fs["WholeConf"][l]>th_conf:
                selected_list.append(f_id)

    selected_list = list(set(selected_list))
    for f_id in selected_list:
        for k in range(len(list_features[f_id]["WholeConf"])):
            dict_result[labels[k]] += list_features[f_id]["WholeConf"][k]

    for k, v in dict_result.items():
        dict_result[k] = round(v/len(selected_list),3)

    return dict_result


if __name__ == '__main__':
    gpus = tf.config.list_physical_devices('GPU')
    tf.config.experimental.set_memory_growth(gpus[0], True)
    labels = ["Calcification",
              "Capsule",
              "CentralScar",
              "Hypoattenuating",
              "NoAPHE",
              "Nodular",
              "NonrimAPHE",
              "Unenhanced",
              "Washout"]

    lfc = LesionImagingFeatureClassifier()
    # lfc.define_structure()
    # lfc.define_structure_new()
    # for i in ["1", "2", "3", "4"]:
    # for i in ["4"]:
    #     if i=="1":
    #         dim = (32, 32, 1)
    #     elif i == "2":
    #         dim = (64, 64, 1)
    #     elif i == "3":
    #         dim = (80, 80, 1)
    #     else:
    #         dim = (128, 128, 1)
    #     # lfc.define_structure_ver2(dim)
    #     # data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification\Dataset (Margin 30px)", True)
    #     # lfc.train("Case H-"+i, i)
    #     #
    #     # lfc.define_structure_ver2(dim)
    #     # data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification\Dataset (Margin 15px)", True)
    #     # lfc.train("Case G-"+i, i)
    #     #
    #     # lfc.define_structure_ver2(dim)
    #     # data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification\Dataset (Margin 7px)", True)
    #     # lfc.train("Case F-"+i, i)
    #     # lfc.save_model(i)
    #     #
    #     # lfc.define_structure_ver2(dim)
    #     # data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification\Dataset (Margin 2px)", True)
    #     # lfc.train("Case E-"+i, i)
    #
    #     # lfc.define_structure_ver2(dim)
    #     # data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification\Dataset (Margin 30px)", False)
    #     # lfc.train("Case D-"+i, i)
    #
    #     lfc.define_structure_ver2(dim)
    #     data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification\Dataset (Margin 15px)", False)
    #     lfc.train("Case C-"+i, i)
    #
    #     lfc.define_structure_ver2(dim)
    #     data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification\Dataset (Margin 7px)", False)
    #     lfc.train("Case B-"+i, i)
    #
    #     lfc.define_structure_ver2(dim)
    #     data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification\Dataset (Margin 2px)", False)
    #     lfc.train("Case A-"+i, i)

    # data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2201\0129\Tumor Image Type Dataset\Dataset (Margin 30px)", True)
    # for i in range(200, 90, -10):
    #     print("["+str(i)+"]")
    #     lfc.load_model("MRI", i, "Case H-2")
    #     lfc.compute_performance()
    #     print("\n\n")

    # start_num = 300
    # end_num = 100
    # for k in ["1", "2", "3","4"]:
    #     if k=="1":
    #         dim = (32, 32, 1)
    #     elif k == "2":
    #         dim = (64, 64, 1)
    #     elif k == "3":
    #         dim = (80, 80, 1)
    #     else:
    #         dim = (128, 128, 1)
    #
    #     print("<<Case H-"+k+">>")
    #     lfc.define_structure_new(dim)
    #     data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification\Dataset (Margin 30px)", True)
    #     for i in range(start_num, end_num, -10):
    #         print("["+str(i)+"]")
    #         lfc.load_model("MRI", i, "Case H-"+k)
    #         lfc.compute_performance()
    #         print("\n\n")
    #     lfc.define_structure_new(dim)
    #     print("<<Case G-"+k+">>")
    #     data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification\Dataset (Margin 15px)", True)
    #     for i in range(start_num, end_num, -10):
    #         print("["+str(i)+"]")
    #         lfc.load_model("MRI", i, "Case G-"+k)
    #         lfc.compute_performance()
    #         print("\n\n")
    #
    #     print("<<Case F-"+k+">>")
    #     lfc.define_structure_new(dim)
    #     data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification\Dataset (Margin 7px)", True)
    #     for i in range(start_num, end_num, -10):
    #         print("["+str(i)+"]")
    #         lfc.load_model("MRI", i, "Case F-"+k)
    #         lfc.compute_performance()
    #         print("\n\n")
    #
    #     print("<<Case E-"+k+">>")
    #     lfc.define_structure_new(dim)
    #     data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification\Dataset (Margin 2px)", True)
    #     for i in range(start_num, end_num, -10):
    #         print("["+str(i)+"]")
    #         lfc.load_model("MRI", i, "Case E-"+k)
    #         lfc.compute_performance()
    #         print("\n\n")
    #
    #     print("<<Case D-"+k+">>")
    #     lfc.define_structure_new(dim)
    #     data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification\Dataset (Margin 30px)", False)
    #     for i in range(start_num, end_num, -10):
    #         print("["+str(i)+"]")
    #         lfc.load_model("MRI", i, "Case D-"+k)
    #         lfc.compute_performance()
    #         print("\n\n")
    #     print("<<Case C-"+k+">>")
    #     lfc.define_structure_new(dim)
    #     data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification\Dataset (Margin 15px)", False)
    #     for i in range(start_num, end_num, -10):
    #         print("["+str(i)+"]")
    #         lfc.load_model("MRI", i, "Case C-"+k)
    #         lfc.compute_performance()
    #         print("\n\n")
    #
    #     print("<<Case B-"+k+">>")
    #     lfc.define_structure_new(dim)
    #     data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification\Dataset (Margin 7px)", False)
    #     for i in range(start_num, end_num, -10):
    #         print("["+str(i)+"]")
    #         lfc.load_model("MRI", i, "Case B-"+k)
    #         lfc.compute_performance()
    #         print("\n\n")
    #
    #     print("<<Case A-"+k+">>")
    #     lfc.define_structure_new(dim)
    #     data = lfc.load_data_new(r"E:\1. Lab\Daily Results\2022\2202\0204\Tumor Image Feature Classification\Dataset (Margin 2px)", False)
    #     for i in range(start_num, end_num, -10):
    #         print("["+str(i)+"]")
    #         lfc.load_model("MRI", i, "Case A-"+k)
    #         lfc.compute_performance()
    #         print("\n\n")


    lfc.load_model("MRI")
    np.set_printoptions(suppress=True)
    p = r"E:\1. Lab\Daily Results\2022\2202\0216\tumor images - 15px"
    for i in os.listdir(p):
        if not os.path.isdir(os.path.join(p, i)):
            continue
        for j in os.listdir(os.path.join(p, i)):
            cur_tumor = cv2.imread(os.path.join(p, i, j), cv2.IMREAD_GRAYSCALE)
            cur_tumor = cv2.resize(cur_tumor, (lfc.IMAGE_DIMS[1], lfc.IMAGE_DIMS[0]))     # To resize (128, 128)
            cur_tumor = img_to_array(cur_tumor)     # To change image to array
            result = lfc.predict(cur_tumor/255)
            features = lfc.get_features(result[0])
            print(j, "    ", features["Labels"], features["ConfidenceScores"], np.round(features["WholeConf"], 4))

    #
    # # path =r"E:\1. Lab\Daily Results\2022\2201\0117\data for classifying tumor image features\val"
    # # for i in os.listdir(path):
    # #     img = cv2.imread(os.path.join(path, i), cv2.IMREAD_GRAYSCALE)
    # #     result = lfc.predict(img)
    # #     print(result)
    #
    # # lfc.train()
    # # lfc.save_model()
    #
    # #
    # # float_formatter = "{:.5f}".format
    # # np.set_printoptions(formatter={'float_kind': float_formatter})
    # #
    # # p_root = r"E:\1. Lab\Daily Results\2021\2108\0811\Dataset\Tumor Image Features Test"
    # # # p_root = r"F:\Dataset\LLU Dataset for Sub Data (Image Features)\Images"
    # # # list_data = {lfc.labels[0]:0, lfc.labels[1]:0, lfc.labels[2]:0, lfc.labels[3]:0, lfc.labels[4]:0,
    # # #              lfc.labels[5]:0, lfc.labels[6]:0, lfc.labels[7]:0, lfc.labels[8]:0}
    # #
    # # list_label_data = []
    # # for i in os.listdir(p_root):
    # #     list_cur_feature = i.split("_")
    # #     cur_list = []
    # #     for l in list_cur_feature:
    # #         cur_list.append(labels.index(l))
    # #     for j in os.listdir(os.path.join(p_root, i)):
    # #         list_label_data.append(cur_list)
    # # print(len(list_label_data))
    # # list_label_data_mb = []
    # # for i in list_label_data:
    # #     cur_list = []
    # #     for j in range(len(labels)):
    # #         if j in i:
    # #             cur_list.append(1)
    # #         else:
    # #             cur_list.append(0)
    # #     list_label_data_mb.append(cur_list)
    # #
    # # # mlb = MultiLabelBinarizer()
    # # # list_label_data_mb = mlb.fit_transform(list_label_data)
    # # lfc.load_model()
    # # p = r"F:\Dataset\LLU Dataset for Sub Data (Image Features)\tumor_image"
    # # results = {"target":[], "conf":[], "result":[]}
    # # for i in os.listdir(p):
    # #     for j in os.listdir(os.path.join(p, i)):
    # #         img = cv2.imread(os.path.join(p, i, j))
    # #         img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # #         img = img.reshape((img.shape[0], img.shape[1]))
    # #         results['target'].append(j)
    # #         results['conf'].append(lfc.predict(img)[0])
    # #         prd = lfc.get_features(lfc.predict(img)[0])
    # #         results['result'].append(prd["Labels"])
    # #         print(i, j, results["target"][-1], results["conf"][-1], results["result"][-1])
    # #
    # # results = pd.DataFrame(results)
    # # results.to_csv(r"E:\1. Lab\Daily Results\2021\2109\0907\result.csv")
    # #
    # # for k in range(5, 255, 5):
    # #     # list_data = {lfc.labels[0]:0, lfc.labels[1]:0, lfc.labels[2]:0, lfc.labels[3]:0, lfc.labels[4]:0,
    # #     #              lfc.labels[5]:0, lfc.labels[6]:0, lfc.labels[7]:0, lfc.labels[8]:0}
    # #     list_data_mb = []
    # #     for i in os.listdir(p_root):
    # #         if "json" in i:
    # #             continue
    # #         for j in os.listdir(os.path.join(p_root, i)):
    # #             img = cv2.imread(os.path.join(p_root, i, j))
    # #             img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # #             img = img.reshape((img.shape[0], img.shape[1]))
    # #             prd = lfc.get_features(lfc.predict(img)[0])
    # #             list_cur = []
    # #             for l in range(len(prd["WholeConf"])):
    # #                 if prd["WholeConf"][l] > 0.5:
    # #                     list_cur.append(l)
    # #
    # #             list_d = []
    # #             for a in range(len(labels)):
    # #                 if a in list_cur:
    # #                     list_d.append(1)
    # #                 else:
    # #                     list_d.append(0)
    # #             list_data_mb.append(list_d)
    # #         # list_data.append(list_d)
    # #                     # list_data[lfc.labels[l]] += 1
    # #     print("[", str(k).zfill(3), "]")
    # #     list_label_data_mb = np.array(list_label_data_mb)
    # #     list_data_mb = np.array(list_data_mb)
    # #
    # #     # list_data_mb = mlb.fit_transform(list_data)
    # #     print("Accuracy: ", metrics.accuracy_score(list(list_label_data_mb), list(list_data_mb)))
    # #     print("Precision: ", metrics.precision_score(list(list_label_data_mb), list(list_data_mb), average='samples'))
    # #     print("Recall: ", metrics.recall_score(list(list_label_data_mb), list(list_data_mb), average='samples'))
    # #     print("\n\n")
    #
    #
    #
    #
    #
    # #     for aa in os.listdir(p_root):
    # #         print(aa)
    # #         for i in os.listdir(os.path.join(p_root, aa)):
    # #             list_data = {lfc.labels[0]:0, lfc.labels[1]:0, lfc.labels[2]:0, lfc.labels[3]:0, lfc.labels[4]:0,
    # #                          lfc.labels[5]:0, lfc.labels[6]:0, lfc.labels[7]:0, lfc.labels[8]:0}
    # #             list_d = []
    # #             for j in os.listdir(os.path.join(p_root, aa, i)):
    # #                 img = cv2.imread(os.path.join(p_root, aa, i, j))
    # #                 img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # #                 img = img.reshape((img.shape[0], img.shape[1]))
    # #                 print(type(img), img.dtype, img.shape)
    # #                 prd = lfc.get_features(lfc.predict(img)[0])
    # #                 # print(prd["WholeConf"])
    # #                 list_d.append(prd)
    # #                 for k in range(len(prd["WholeConf"])):
    # #                     if prd["WholeConf"][k]>0.5:
    # #                         list_data[lfc.labels[k]]+=1
    # #             list_d = extract_major_features(list_d)
    # #             # print(i, "    ",  len(os.listdir(os.path.join(p_root, aa, i))), "    ", list_data)
    # #             # print("        ", list_d )
    # #         print("\n\n")
    # #         break
    # #     break
    #
    #
    #     # p_root = r"E:\1. Lab\Daily Results\2021\2108\0811\Dataset\Tumor Image Features Test"
    #     # data = {"name":[], "org":[], "prd":[], "result":[]}
    #     # tp_t, total_t = 0, 0
    #     # for i in os.listdir(p_root):
    #     #     cur_lbs = i.split("_")
    #     #     for j in os.listdir(os.path.join(p_root, i)):
    #     #         img = cv2.imread(os.path.join(p_root, i, j))
    #     #         img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #     #         img = img.reshape((img.shape[0], img.shape[1]))
    #     #         prd = lfc.get_features(lfc.predict(img)[0])
    #     #
    #     #         data["name"].append(j)
    #     #         data["org"].append(",".join(cur_lbs))
    #     #         data["prd"].append(",".join(prd["Labels"]))
    #     #         data["result"].append(cur_lbs==prd["Labels"])
    #     #         if cur_lbs == prd["Labels"]:
    #     #             tp_t +=1
    #     #         else:
    #     #             print(j, i, prd["Labels"],  prd["ConfidenceScores"])
    #     #         total_t +=1
    #     # try:
    #     #     diff = tp_t/total_t
    #     # except:
    #     #     diff = 0.0
    #     # print(str(k)+"  : "+ str(round(diff, 3))+"    "+ str(tp_t)+"    "+ str(total_t))
    #
    #
    #
    #
    #
    #
    # #
    # #
    # # # To initialize imaging features classification and lesion type classification
    # # ttc = LesionImagingFeatureClassifier()
    # # tpd = LesionTypeClassifier()
    # #
    # # # To load model and data of lesion image features classifier
    # # ttc.load_data()
    # # ttc.load_model()
    # #
    # # # ttc.compute_performance()
    # # # To load model and data of lesion type classifier
    # # # tpd.load_data()
    # # # tpd.load_model()
    # # root = r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor"
    # #
    # # results = {"LesionType":[], "StudyID":[], "SliceID":[],"Plain_0":[], "Plain_1":[], "Plain_2":[], "Plain_3":[], "Plain_4":[], "Plain_5":[], "Plain_6":[], "Plain_7":[], "Plain_8":[]
    # #            , "AP_0": [], "AP_1":[], "AP_2":[], "AP_3":[], "AP_4":[], "AP_5":[], "AP_6":[], "AP_7":[], "AP_8":[]
    # #            , "PVP_0": [], "PVP_1":[], "PVP_2":[], "PVP_3":[], "PVP_4":[], "PVP_5":[], "PVP_6":[], "PVP_7":[], "PVP_8":[]
    # #            , "DP_0": [], "DP_1":[], "DP_2":[], "DP_3":[], "DP_4":[], "DP_5":[], "DP_6":[], "DP_7":[], "DP_8":[]}
    # # for ltype in os.listdir(root):
    # #     loc_type = root+"\\"+ltype
    # #     lesion_type = ltype.split(" ")[1]
    # #     for study in os.listdir(loc_type):
    # #         loc_study = loc_type+"\\"+study
    # #         for lesion_id in os.listdir(loc_study):
    # #             loc_lesion_id = loc_study +"\\"+lesion_id
    # #             predicted_result = {"Plain": [0,0,0,0,0,0,0,0,0],
    # #                                 "AP": [0,0,0,0,0,0,0,0,0],
    # #                                 "PVP": [0,0,0,0,0,0,0,0,0],
    # #                                 "DP": [0,0,0,0,0,0,0,0,0]}
    # #             for phase in os.listdir(loc_lesion_id):
    # #                 lesion_phase =phase.split(' ')[1].split("_")[2]
    # #                 img = cv2.imread(loc_lesion_id+"\\"+phase)
    # #                 result = ttc.predict(img)
    # #                 predicted_result[lesion_phase] = result[0].tolist()
    # #             for v in predicted_result:
    # #                 for i in range(len(predicted_result[v])):
    # #                     try:
    # #                         results[v+"_"+str(i)].append(round(predicted_result[v][i],3))
    # #                     except:
    # #                         results[v+"_"+str(i)].append(None)
    # #             results["LesionType"].append(lesion_type)
    # #             results["StudyID"].append(study)
    # #             results["SliceID"].append(lesion_id)
    # #
    # #             print(predicted_result)
    # # r = pd.DataFrame.from_dict(results)
    # # r.to_csv(".\\Results, 0718a.csv")
    # # # root = r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\4 HCC\3\3"       # Location for HCC
    # # # data = {'Plain': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'AP': [], "PVP": [], "DP": []}  # Dict for Confidence score
    # # # for i in os.listdir(root):      # To load lesion images
    # # #     img = cv2.imread(root+"\\"+i)   # To load a lesion image
    # # #     lesion_type = i.split("_")[0].split(" ")[1]     # To get lesion type from folder name
    # # #     phase = i.split("_")[2].split(" ")[0]           # To get taken phase of the lesion
    # # #     result = ttc.predict(img)                       # To predict imaging features from the image
    # # #     print(str(lesion_type)+" ("+str(phase)+") : "+str(result))
    # # #     if i.split(' ')[1].split("_")[2] == 'Plain':
    # # #         data['Plain'] = result[0].tolist()
    # # #     elif i.split(' ')[1].split("_")[2] == 'AP':
    # # #         data['AP'] = result[0].tolist()
    # # #     elif i.split(' ')[1].split("_")[2] == 'PVP':
    # # #         data['PVP'] = result[0].tolist()
    # # #     elif i.split(' ')[1].split("_")[2] == 'DP':
    # # #         data['DP'] = result[0].tolist()
    # # #
    # # # result = []
    # # # for i in data:
    # # #     result.append(data[i])  # To sort data following acquired phase
    # # # result = [result]
    # #
    # #
    # #
    # #
    # # # list_types = tpd.predict([result])    # To make 4D array for input data
    # # # type_str = tpd.get_tumor_type(list_types)   # To return lesion type using confdience score
    # # # print(list_types, type_str)
    # #
    # #
    # # # idx = 0
    # # # for tts in os.listdir(root):
    # # #     for study in os.listdir(root+"\\"+tts):
    # # #         for t in os.listdir(root+"\\"+tts+"\\"+study):
    # # #             data = {'Plain': [], 'AP': [], "PVP": [], "DP": []}
    # # #             idx += 1
    # # #             for i in os.listdir(root+"\\"+tts+"\\"+study+"\\"+t):
    # # #                 img = cv2.imread(root+"\\"+tts+"\\"+study+"\\"+t+"\\"+i)
    # # #                 result = ttc.predict(img)
    # # #                 if i.split(' ')[1].split("_")[2] == 'Plain':
    # # #                     data['Plain'] = result
    # # #                 elif i.split(' ')[1].split("_")[2] == 'AP':
    # # #                     data['AP'] = result
    # # #                 elif i.split(' ')[1].split("_")[2] == 'PVP':
    # # #                     data['PVP'] = result
    # # #                 elif i.split(' ')[1].split("_")[2] == 'DP':
    # # #                     data['DP'] = result
    # # #             # print(
    # # #             #     "Tumor Type,Study,Tumor ID, Calcification,Capsule,CentralScar,HaloCapsule,Hypoattenuating,NoAPHE,Nodular,NonrimAPHE,Washout")
    # # #
    # # #             print(idx, "\t", str(study), "\t", str(t),"\t", tts.split(' ')[1], end="")
    # # #             for d in data:
    # # #                 if data[d] is not None:
    # # #                     if len(data[d]) > 0:
    # # #                         print("\t ["+",".join(data[d])+"]", end="")
    # # #             print()
    # # #
    # #
    # #     # r = {'Plain': None, "AP": None, "PVP": None, "DP": None}
    # #     # for d in data:
    # #     #     for i in range(len(data[d])):
    # #     #         print(",".join(data[d][i]))
    # #     # print()
    # # #
    # # # for l in [
    # # #             # [r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\0 Hemangioma\1\0 Hemangioma_1_Plain 3_1.png",
    # # #            # r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\0 Hemangioma\1\0 Hemangioma_1_AP 3_1.png",
    # # #            # r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\0 Hemangioma\1\0 Hemangioma_1_PVP 3_1.png",
    # # #            # r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\0 Hemangioma\1\0 Hemangioma_1_DP 3_1.png"],
    # # #           #
    # # #           # [r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\1 FNH\1\1 FNH_1_AP 1_0.png",
    # # #           #  r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\1 FNH\1\1 FNH_1_AP 1_0.png",
    # # #           #  r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\1 FNH\1\1 FNH_1_PVP 1_0.png",
    # # #           #  r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\1 FNH\1\1 FNH_1_PVP 1_0.png"],
    # # #
    # # #           # [r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\2 Adenoma\2\2 Adenoma_2_Plain 1_0.png",
    # # #           #  r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\2 Adenoma\2\2 Adenoma_2_AP 1_0.png",
    # # #           #  r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\2 Adenoma\2\2 Adenoma_2_PVP 1_0.png",
    # # #           #  r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\2 Adenoma\2\2 Adenoma_2_DP 1_0.png"],
    # # #
    # # #           # [r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\3 FLHCC\3\3 FLHCC_3_Plain 1.jpg",
    # # #           #  r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\3 FLHCC\3\3 FLHCC_3_AP 1.jpg",
    # # #           #  r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\3 FLHCC\3\3 FLHCC_3_PVP 1.jpg",
    # # #           #  r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\3 FLHCC\3\3 FLHCC_3_DP 1.jpg"],
    # # #           #
    # # #           # [
    # # #           #     r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\4 HCC\2\4 HCC_2_AP 2_0.png",
    # # #           #     r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\4 HCC\2\4 HCC_2_PVP 2_0.png",
    # # #           #     r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\4 HCC\2\4 HCC_2_DP 2_0.png"
    # # #           # ],
    # # #         # [
    # # #         #     r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\4 HCC\2\4 HCC_2_AP 3_0.png",
    # # #         #     r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\4 HCC\2\4 HCC_2_PVP 3_0.png",
    # # #         #     r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\4 HCC\2\4 HCC_2_DP 3_0.png"
    # # #         # ],
    # # #
    # # #         [
    # # #             r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\4 HCC\3\4 HCC_3_DP 4_0.png",
    # # #             r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\4 HCC\3\4 HCC_3_AP 4_0.png",
    # # #             r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\4 HCC\3\4 HCC_3_PVP 4_0.png",
    # # #             r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor\4 HCC\3\4 HCC_3_DP 4_0.png"
    # # #         ],
    # # #           ]:
    # # #
    # # #     cls_result = []
    # # #     for loc in l:
    # # #         img = cv2.imread(loc)
    # # #         result = ttc.predict(img)
    # # #         print(result)
    # # #         print(ttc.get_features(result[0]))
    # # #         cls_result.append(result[0].tolist())
    # # #         # for i in range(len(result[0])):
    # # #         #     print(labels[i], ": ", float(result[0][i]))
    # # #         print("\n============================\n")
    # # #     print(cls_result)
    # # # labels = ttc.get_labels()
    # # # results = []
    # #
    # #
    # # #     tpd.load_model()
    # # #     results.append(tpd.predict([[cls_result]]))
    # # # for r in results:
    # # #     print(constant.TumorType(np.argmax(r)).name, r)
    # #
    # # # data = [[[8.891e-01, 0.669e-01, 8.748e-01, 4.140e-02, 1.570e-02],
    # # #          [9.884e-01, 1.169e-01, 9.745e-01, 6.910e-02, 2.330e-02],
    # # #          [9.889e-01, 0.559e-01, 9.273e-01, 7.730e-02, 1.700e-02],
    # # #          [9.883e-01, 1.336e-01, 9.378e-01, 7.460e-02, 0.730e-02]],
    # # #
    # # #         [[4.680e-02, 9.625e-01, 3.860e-01, 9.674e-01, 4.700e-03],
    # # #          [7.680e-02, 6.522e-01, 4.419e-01, 1.803e-01, 9.954e-01],
    # # #          [5.460e-02, 7.479e-01, 2.121e-01, 3.716e-01, 9.984e-01],
    # # #          [4.430e-02, 9.890e-01, 3.614e-01, 9.723e-01, 3.570e-02]],
    # # #
    # # #         [[9.060e-02, 9.319e-01, 9.779e-01, 1.339e-01, 5.000e-04],
    # # #          [9.490e-02, 9.377e-01, 9.794e-01, 1.783e-01, 6.000e-04],
    # # #          [9.060e-02, 9.319e-01, 9.779e-01, 1.339e-01, 5.000e-04],
    # # #          [9.490e-02, 9.377e-01, 9.794e-01, 1.783e-01, 6.000e-04]],
    # # #
    # # #         [[1.013e-01, 9.415e-01, 8.522e-01, 6.648e-01, 1.800e-03],
    # # #          [5.770e-02, 4.377e-01, 1.041e-01, 1.543e-01, 1.000e+00],
    # # #          [2.450e-02, 5.054e-01, 1.100e-01, 1.406e-01, 1.000e+00],
    # # #          [7.090e-02, 2.700e-01, 8.970e-02, 1.692e-01, 1.000e+00]]
    # # #
    # #
    # # # data_loc = r"D:\1. Lab\Dataset\Liver\Radiopedia\Types of Tumor"
    # # # d = {'PatientID': [], 'TakenTime': [], 'sliceNum': [], 'data': []}
    # # # d = {"id":[], "slice": [], "tumor":[], "phase":[],  'data':[], 'type': []}
    # # # # d = {'fname':[], "data":[]}
    # # # # To load data from loacal
    # # # for i in os.listdir(data_loc):
    # # #     type_path = os.path.join(data_loc, i)
    # # #     for j in os.listdir(type_path):
    # # #         id_path = os.path.join(type_path, j)
    # # #         for t in os.listdir(id_path):
    # # #             print(i)
    # # #             d['type'].append(i.split(' ')[1])
    # # #             d['id'].append(j)
    # # #             img_path = os.path.join(id_path, t)
    # # #             print(img_path)
    # # #             slice= t.split('_')[2]
    # # #             d['slice'].append(slice.split(' ')[1])
    # # #             if len(t.split('_')) == 4:
    # # #                 d['tumor'].append(t.split('_')[3].split(".")[0])
    # # #             else:
    # # #                 d['tumor'].append(1)
    # # #             d['phase'].append(slice.split(' ')[0])
    # # #             image = cv2.imread(img_path)  ## To be changed following image type
    # # #             image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # # #             image = cv2.resize(image, (128, 128))
    # # #             image = img_to_array(image)
    # # #             image = np.expand_dims(image, axis=0)
    # # #             result = ttc.predict(image)
    # # #
    # # #             d['data'].append(result[0].tolist())
    # # #
    # # #
    # # #     print("\n\n\n\n")
    # # #         # for data in result[0]:
    # # #         #     r.append(round(float(data), 4))
    # # #         # d['data'].append(r)
    # # #
    # # # df = pd.DataFrame(d)
    # # # df.to_csv("./data.csv")
