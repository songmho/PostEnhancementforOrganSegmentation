"""
Date: 2021. 04. 29.
Programmer: DY
Description: Code for Classifying LI-RADS Stage using tumor's input information
            The classification model is based on SVM (support vector machine) classifier.
"""
from _datetime import datetime
import pickle

import pandas as pd
import numpy as np
from pandas.api.types import is_string_dtype, is_bool_dtype
import os

from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder, MinMaxScaler
from sklearn.svm import SVC

from miaas.lirads import constant

class MalignantStageClassifier:
    """
    Class for classifying HCC stage (LR-3, LR-4, and LR-5)
    """
    def __init__(self):
        self.data_path = r"E:\1. Lab\Daily Results\2021\2108\0811\Dataset\Stage Classification"     # To need to be defined (CSV file)

        self.path_model = r"E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\models\staging_classification"

        # encoder for string column
        self.enc_aphe_type = OrdinalEncoder().fit([['Nonrim'], ['No']])
        self.dataset = None  # loaded dataset

    def load_data(self, file_name):
        """
        To load data from the path
        :return: None
        """
        self.dataset = pd.read_csv(os.path.join(self.data_path, file_name), index_col=0)

    def preprocess(self, prediction_data=None):
        """
        To preprocess data considering the SVM model
        :param prediction_data: pandas DataFrame, raw data to predict
        :return: pandas DataFrame, the preprocessed data
        """
        if prediction_data is None:  # for training
            target_data = self.dataset
        else:  # for predicting
            if type(prediction_data) != list:
                target_data = prediction_data
                if "stage" in target_data.columns:  # still including label?
                    target_data = target_data.drop(["stage"], axis=1)  # drop the label
            target_data = prediction_data

        ### Step 1. Delete null/NA data
        pass  # let it empty

        ### Step 2. Convert categorical data to numeric value
        # search the categorical feature
        if prediction_data is not None:
            if type(prediction_data) == list:
                if target_data[0] == "Nonrim": target_data[0] = 1
                else:                          target_data[0] = 0
        else:
            target_data["APHE_Type"] = self.enc_aphe_type.transform(pd.DataFrame(target_data["APHE_Type"]))

        # Step 3. Convert boolean: True for 1, False for 0
        if type(prediction_data) != list:
            for a_ft in target_data.columns:
                if is_bool_dtype(target_data[a_ft]):  # string type?
                    target_data[a_ft] = target_data[a_ft].astype(np.int64)
        else:
            for i in range(len(target_data)):
                if is_bool_dtype(target_data[i]):
                    target_data[i] = int(target_data[i]==True)

        if target_data is None:  # for training
            self.dataset = target_data
            return pd.DataFrame()
        else:  # for predicting
            target_data = list(target_data)
            print(type(target_data), target_data)
            return target_data  # preprocessed data

    def split_data(self, test_size=0.2):
        """
        To split data to training set and test set
        :return: None
        """
        self.X = self.dataset.iloc[:, :-1]
        self.y = self.dataset.iloc[:, -1]
        self.train_X, self.test_X, self.train_y, self.test_y = \
            train_test_split(self.X, self.y, test_size=test_size, random_state=42)

    def train(self):
        """
        To train model using training set
        :return: None
        """
        self.svm_classifier = SVC(kernel="poly", degree=3, C=1.0, coef0=60)
        self.svm_classifier.fit(self.train_X, self.train_y)

    def evaluate_model(self):
        """
        To evaluate model using 3 evaluation index: Accuracy, Precision, and Recall
        if it needs, To create a metric.
        :return: None
        """
        y_pred = self.svm_classifier.predict(self.test_X)
        return {"accuracy": accuracy_score(y_true=self.test_y, y_pred=y_pred),
                "precision": precision_score(y_true=self.test_y, y_pred=y_pred, average=None),
                "recall": recall_score(y_true=self.test_y, y_pred=y_pred, average=None)}

    def save_model(self, model_name=f'MalignantStageClassifier_{datetime.now().strftime("%Y%m%d%H%M%S")}.pkl'):
        """
        To save trained model to the local
        :return: None
        """
        with open(os.path.join(self.path_model, model_name), 'wb') as f:
            pickle.dump(self.svm_classifier, f)

    def load_model(self, model_name="model.pkl"):
        """
        To load model
        :return: None
        """
        with open(os.path.join(self.path_model, model_name), 'rb') as f:
            self.svm_classifier = pickle.load(f)

    def predict(self, input_data):
        """
        To predict stage for input data
        :param input_data: list keeping the order of columns (APHE_Type, Obs_Size, MF_Capsule, MF_Washout,
                            MF_threshold_growth, NumMF)
        :return: ndarray of shape (n_samples,)
        """
        return self.svm_classifier.predict([self.preprocess(input_data)])
        # return self.svm_classifier.predict(input_data)



# Not Yet
class BenignStageClassifier:
    """
    Class for classifying Benign stage (LR-1 and LR-2)
    """
    def __init__(self):
        self.data_path = ""     # To need to be defined
        self.model_path = ""     # To need to be defined

    def load_data(self):
        """
        To load data from the path
        :return:
        """
        pass

    def preprocess(self):
        """
        To preprocess data considering the SVM model
        :return:
        """
        pass

    def split_data(self):
        """
        To split data to training set and test set
        :return:
        """
        pass

    def train(self):
        """
        To train model using training set
        :return:
        """
        pass

    def evaluate_model(self):
        """
        To evaluate model using ...
        :return:
        """
        pass

    def save_model(self):
        """
        To save trained model to the local
        :return:
        """
        pass

    def load_model(self):
        """
        To load model
        :return:
        """
        pass

    def predict(self, data):
        """
        To predict stage for input data
        :param data:
        :return:
        """
        return constant.Stages.LR_1

if __name__ == '__main__':
    stage_classifier = MalignantStageClassifier()
    stage_classifier.load_data("staging_data_nonequal_8000.csv")
    stage_classifier.preprocess()
    stage_classifier.split_data()
    stage_classifier.train()
    print(stage_classifier.evaluate_model())
    # stage_classifier.save_model()
    # stage_classifier.load_model("model.pkl")
    # # stage_classifier.evaluate_model()
    # print(stage_classifier.svm_classifier.predict([[1, 47.11, 0, 1, 0, 1]]))
    # print(stage_classifier.svm_classifier.predict([[1, 41.149, 0, 1, 0, 1]]))