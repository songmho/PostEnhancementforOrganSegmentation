"""
Date: 2020. 09. 22.
Programmer: MH
Description: Code for measuring similarity of two input data (CT Slices, lesions, ...)
"""
import numpy as np
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.layers import *
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from skimage import transform
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
import tensorflow.compat.v1 as tf
from keras import backend as K
from tensorflow.python.keras.backend import clear_session
tf.disable_v2_behavior()



config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.InteractiveSession(config=config)


class SimilarityMeasurer:
    def __init__(self):
        self.weight_path = "E:\\1. Lab\\Projects\\Medical Image Analytics System\\mias_with_lirads\\mias\\miaas\\lirads\\models\\similarity_measurer\\deepranking-v2-150000.h5"
        self.prepare_model()

    def prepare_model(self):
        """
        To prepare model 
        :return: 
        """
        self.model = self.__define_model_structure()
        self.model.load_weights(self.weight_path)

    def clear_session(self):
        clear_session()

    def predict(self, img):
        """
        To predict embedding value
        :param img: ndarray, target image
        :return: double, float
        """
        img = img_to_array(img).astype("float64")
        img = transform.resize(img, (224, 224))
        img *= 1. / 255
        img = np.expand_dims(img, axis=0)
        result = self.model.predict([img, img, img])[0]
        return result

    def compute_distance(self, src, trg):
        """
        To compute distance between two embedding values about input images
        :param src: ndarray, source image
        :param trg: ndarray, target image
        :return:
        """
        emb1 = self.predict(src)
        emb2 = self.predict(trg)

        distance = sum([(emb1[i] - emb2[i])**2 for i in range(len(emb1))])**0.5

        return distance

    def __define_model_structure(self):
        """
        To define model structure
        :return:
        """
        convnet_model = self.convnet_model()
        first_input = Input(shape=(224, 224, 3))
        first_conv = Conv2D(96, kernel_size=(8, 8),strides=(16,16), padding='same')(first_input)
        first_max = MaxPool2D(pool_size=(3, 3),strides = (4, 4),padding='same')(first_conv)
        first_max = Flatten()(first_max)
        first_max = Lambda(lambda  x: K.l2_normalize(x,axis=1))(first_max)

        second_input = Input(shape=(224,224,3))
        second_conv = Conv2D(96, kernel_size=(8, 8),strides=(32,32), padding='same')(second_input)
        second_max = MaxPool2D(pool_size=(7,7),strides = (2,2),padding='same')(second_conv)
        second_max = Flatten()(second_max)
        second_max = Lambda(lambda  x: K.l2_normalize(x,axis=1))(second_max)

        merge_one = concatenate([first_max, second_max])

        merge_two = concatenate([merge_one, convnet_model.output])
        emb = Dense(4096)(merge_two)
        l2_norm_final = Lambda(lambda  x: K.l2_normalize(x,axis=1))(emb)

        final_model = Model(inputs=[first_input, second_input, convnet_model.input], outputs=l2_norm_final)

        return final_model

    def convnet_model(self):
        vgg_model = VGG16(weights=None, include_top=False)
        x = vgg_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(4096, activation='relu')(x)
        x = Dropout(0.6)(x)
        x = Dense(4096, activation='relu')(x)
        x = Dropout(0.6)(x)
        x = Lambda(lambda  x_: K.l2_normalize(x,axis=1))(x)
        convnet_model = Model(inputs=vgg_model.input, outputs=x)
        return convnet_model