"""
Date: 2020.03.31.
Programmer: MH
Description: Code for Tumor type diagnosis Based on RNN
"""
import math
import time
import pandas as pd
import numpy as np

import tensorflow as tf

from tensorflow.keras import Sequential, Input, callbacks, Model
from tensorflow.keras.models import model_from_json
from tensorflow.keras.layers import RNN, LSTM, GRU, ConvLSTM2D, Dense, Lambda, TimeDistributed, SimpleRNN
from sklearn.model_selection import train_test_split
import ast

from tensorflow.keras.optimizers import Adam

from miaas.lirads import constant


class LesionTypeClassifier:
    """
    Class of Diagnosing Tumor type using Feature Progress
    """
    def __init__(self):
        """
        To initialize variables
        """
        self.n_classes = 9
        self.n_phases = 4
        self.epochs = 500
        self.batch_size = 25
        self.n_tumor_types = 5  #1
        self.model = Sequential()
        pd.set_option("display.max_rows", None, "display.max_columns", None)    # To print whole contents in data frame
        pd.set_option('expand_frame_repr', False)
        self.labels = {0: "Calcification", 1: "Capsule", 2: "CentralScar", 3: "Hypoattenuating",
                       4: "NoAPHE", 5: "Nodular", 6: "NonrimAPHE", 7: "Unenhanced", 8: "Washout"}

    def load_data(self):
        """
        To load data from local
        :return:
        """
        # Code for CSV file
        # self.data = pd.read_csv("../dataset/Tumor_Type_Progression/data.csv")
        # self.data = pd.read_csv("../dataset/Tumor_Type_Progression/data_final.csv")
        # self.data = pd.read_csv("../dataset/Tumor_Type_Progression/data_final_add_more.csv")
        # self.data = self.data.iloc[:, 4:9]      # To choose only the parts of features and labels
        # self.features, self.labels = self.data.iloc[:, :4], self.data.iloc[:, -1]
        # self.labels = self._change_labels_to_num(self.labels)
        # self.features = self._change_to_list(self.features)

        # Code for loading TSV file
        # self.data = pd.read_csv(r"E:\1. Lab\Daily Results\2021\2108\0811\Dataset\Tumor Type Classification\data ver2.tsv", sep='\t', header=0)
        # self.data = self.data.iloc[:, 1:6]  # To choose only the parts of features and labels (Label[3], features[4, 5, 6, 7])
        # self.features, self.labels = self.data.iloc[:, 1:5], self.data.iloc[:, 0]   # To get Features and labels
        # self.labels = self._change_labels_to_num(self.labels)       # To change
        # self.features = self._change_to_list_for_tsv(self.features)
        # self.train_x, self.test_x, self.train_y, self.test_y = train_test_split(self.features, self.labels,
        #                                                                         test_size=0.4, shuffle=True, random_state=42)
        # print(d)

        self.data = pd.read_csv(r"E:\1. Lab\Daily Results\2022\2201\0125\04. Tumor Type Classification\train.tsv", sep='\t',header=0)
        # self.data = self.data.sample(frac=1).reset_index(drop=True)
        # self.data = self.data.iloc[:,1:6]  # To choose only the parts of features and labels (Label[3], features[4, 5, 6, 7])
        self.train_x, self.train_y = self.data.iloc[:, 4:8], self.data.iloc[:, 0]  # To get Features and labels
        self.train_y = self._change_labels_to_num(self.train_y)  # To change
        self.train_x = self._change_to_list_for_tsv(self.train_x)

        self.data = pd.read_csv(r"E:\1. Lab\Daily Results\2022\2201\0125\04. Tumor Type Classification\test.tsv", sep='\t',header=0)
        # self.data = self.data.sample(frac=1).reset_index(drop=True)
        # self.data = self.data.iloc[:,1:6]  # To choose only the parts of features and labels (Label[3], features[4, 5, 6, 7])
        self.test_x, self.test_y = self.data.iloc[:, 4:8], self.data.iloc[:, 0]  # To get Features and labels
        self.test_y = self._change_labels_to_num(self.test_y)  # To change
        self.test_x = self._change_to_list_for_tsv(self.test_x)

    def generate_batches(self):
        """
        To generate batch for handling multiple size of confidence rate list
        :return: list, batches that consists of training set and test set
        """
        self.data = pd.read_csv(r"E:\1. Lab\Daily Results\2021\2108\0811\Dataset\Tumor Type Classification\data.tsv", sep='\t', header=0)
        self.data = self.data.iloc[:, 1:6]      # To choose only the parts of features and labels
        self.features, self.labels = self.data.iloc[:, 1:5], self.data.iloc[:, 0]
        self.labels = self._change_labels_to_num(self.labels)
        self.features = self._change_to_list_for_tsv(self.features)


    def _change_to_list(self, df):
        result = []
        for i in range(len(df.iloc[:, 0])):
            row = []
            for j in range(len(df.iloc[i, :])):
                row.append(np.array(ast.literal_eval(df.iloc[i, j])))
            result.append(row)
        df_result = np.array(result)

        return df_result

    def _change_labels_to_num(self, labels):
        result = []
        names = labels.copy()
        for i in constant.TumorType:
            labels = labels.replace(i.name, i.value)
        for i in range(len(labels)):
            r = [0]*self.n_tumor_types

            r[labels[i]] = 1
            result.append(r)
            print(i, names[i], labels[i], result[-1])
        result = np.array(result)
        # for i in labels:
        #     result.append(i)
        # result = np.array(result)
        return result

    def _change_to_list_for_tsv(self, df):
        result = []
        for i in range(len(df.iloc[:, 0])):
            row = []
            for j in range(len(df.iloc[i, :])):
                # try:
                s = df.iloc[i, j]
                if type(s) == str:
                    r = self._make_list(s)
                    row.append(r)

            result.append(row)
        df_result = np.array(result)

        return df_result

    def _make_list(self, s):
        """
        To make list from string
        :param s: string, list of confidence rates
        :return: list,
        """
        s = s.split("[")[1]
        s = s.split("]")[0]

        result = []
        for d in s.split(". "):
            result.append(float(d))
        return result

    def define_structure(self):
        self.model = Sequential()
        self.model.add(LSTM(self.n_phases, activation="tanh", input_shape=(None, self.n_classes)))
        self.model.add(Dense(self.n_tumor_types, activation='softmax'))

        # input = Input(shape=(None, self.n_classes))
        # o, h, c = LSTM(self.n_phases, activation='tanh', return_state=True)(input)
        # o = SimpleRNN(None, activation='tanh')(input)
        # output = Dense(self.n_tumor_types, activation='softmax')(o)
        # self.model = Model(inputs=input, outputs=output)

        self.model.compile(loss="categorical_crossentropy", optimizer=Adam(lr=0.0005), metrics=['accuracy'])
        # self.model.compile(loss="binary_crossentropy", optimizer='adam',
        #                    metrics=['accuracy', tf.keras.metrics.Precision(name="precision"),
        #                             tf.keras.metrics.Recall(name="recall"), tf.keras.metrics.FalsePositives(name="false_positive"),
        #                             tf.keras.metrics.FalseNegatives(name="false_negative")])
        self.model.summary()

    def train(self):
        start_time = time.time()

        # self.history = self.model.fit(self.train_x, self.train_y, batch_size=1, epochs=self.epochs,
        #                               validation_data=([self.test_x], self.test_y), )
        checkpoint_path = r"./backup/tumor_type_classifier, mri/tumor_type_classifier_{epoch:05d}.h5"
        cp_callback = callbacks.ModelCheckpoint(filepath=checkpoint_path, save_weights_only=False, verbose=1, period=1)
        tb_callback = callbacks.TensorBoard(log_dir=r"./backup/tumor_type_classifier, mri/log", histogram_freq=1)

        self.history = self.model.fit(self.train_x, self.train_y, epochs=self.epochs, batch_size=self.batch_size,
                                      validation_data=(self.test_x, self.test_y), callbacks=[cp_callback, tb_callback])
        print("Elapsed Time: ", int(time.time()-start_time), "Seconds")

    def predict(self, features):
        result = self.model.predict(features)
        return result

    def save_model(self):
        m_json = self.model.to_json()
        with open(r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\models\Tumor_Type_Classification_RNN\model_1_rnn.json', 'w') as json_file:
            json_file.write(m_json)
        self.model.save(r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\models\Tumor_Type_Classification_RNN\model_1_rnn_mri.h5')

    def load_model(self):
        json_file = open(r'E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\models\Tumor_Type_Classification_RNN\model_1_rnn.json', 'r')
        # json_file = open('..\\models\\Tumor_Type_Progression\\model_1_rnn.json', 'r')
        # json_file = open('..\\models\\Tumor_Type_Progression\\model_1_None.json', 'r')
        self.model = json_file.read()
        json_file.close()
        self.model = model_from_json(self.model)

        # self.model.load_weights(r"E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\util\backup\tumor_type_classifier\tumor_type_classifier_00200.h5")
        self.model.load_weights(r"E:\1. Lab\Projects\Medical Image Analytics System\mias_with_lirads\mias\miaas\lirads\util\backup\tumor_type_classifier, mri\tumor_type_classifier_00295.h5")
        # self.model.load_weights("..\\models\\Tumor_Type_Progression\\weight_1_rnn.h5")
        # self.model.load_weights("..\\models\\Tumor_Type_Progression\\weight_1_None.h5")
        self.model.compile(loss='categorical_crossentropy',  optimizer=Adam(lr=0.0005), metrics=['accuracy'])
        # self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        # self.model.summary()

    def get_tumor_type(self, result):
        id = np.argmax(result)
        # id = round(result[0][0])
        print(id)
        return {"id": id, "Tumor Type": constant.TumorType(id), "wholeConf":result}


if __name__ == '__main__':
    tpd = LesionTypeClassifier()
    tpd.load_data()
    tpd.define_structure()
    # tpd.train()
    # tpd.save_model()

    tpd.load_model()

    data = [[
        [0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1]
             ],
        [
            [0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 1]
        ],
        [
            [0,0,0,1,0,0,0,0,0],
            [0,0,0,1,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,1]
        ],
        [
            [1.550020278795472e-07, 5.5071168454061995e-08, 8.959763378843125e-08, 0.9205795584945008,
             1.6341530644872364e-06, 8.656126899708738e-08, 0.01405459630787467, 8.469006573808002e-08,
             0.17221032480908263],
            [1.6830057229006673e-07, 9.702100305296137e-08, 8.683280861010445e-08, 0.7816197477313145,
             3.8776669016523024e-07, 6.107429714741208e-08, 0.07107445970672992, 9.020180712380041e-08,
             0.25856387025909316],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [3.8270862603440035e-07, 1.3518639576659553e-07, 9.465504469119423e-08, 0.05908140527297974,
             6.29299348964274e-08, 4.1250830733474687e-07, 4.4019473949674645e-05, 1.6452806885780547e-07,
             0.978549861907959]
        ]
    ]
    data = [[
        [0, 0, 0, 0, 0, 0, 0.9997, 0, 0],
        [0.0006, 0.0002, 0.0003, 0.0026, 0.0001, 0.0006, 0.9999, 0.0001, 0.0001],
        [0, 0, 0, 0.0001, 0, 0.0001, 0.9825, 0, 0.0009],
        [0.0003, 0, 0, 0, 0, 0, 0.9997, 0, 0.0001]
    ], [
        [0.0005, 0.0003, 0.0006, 0.009, 0, 0.0004, 0.8145, 0.0078, 0.0005],
        [0.0006, 0.0006, 0.0026, 0.0001, 0.0001, 0.0004, 0.9999, 0.0006, 0.0004],
        [0.0002, 0.0001, 0.0004, 0.0054, 0, 0.0002, 0.0003, 0.0001, 0.9909],
        [0.0002, 0.0003, 0.0002, 0.0309, 0, 0.0005, 0.0406, 0, 0.8491]
    ], [
        [0.0048, 0.0064, 0.0061, 0.1031, 0.0002, 0.0025, 0.0658, 0.9444, 0.0036],
        [0.0017, 0.0016, 0.0018, 0.1484, 0, 0.0016, 0.9347, 0.0026, 0.0082],
        [0.0015, 0.0016, 0.0012, 0, 0.0002, 0.0015, 0.6172, 0.0001, 0.9981],
        [0.0011, 0.0004, 0.001, 0, 0.003, 0.0008, 0.1458, 0.0002, 0.9793]
    ], [
        [0.0036, 0.0023, 0.001, 1, 0.0005, 0.0022, 0.0002, 0.0007, 0, ],
        [0.0029, 0.0026, 0.001, 1, 0.0008, 0.003, 0.0197, 0.0007, 0, ],
        [0.0039, 0.001, 0.0008, 1, 0.0001, 0.0015, 0.0002, 0.0009, 0.0004],
        [0.0011, 0.0012, 0.0009, 1, 0.0001, 0.0006, 0, 0.0006, 0, ]
    ], [
        [0.0002, 0.0004, 0.0002, 0.8947, 0.0001, 0.0008, 0.09,   0, 0.0057],
        [0.0006, 0.0004, 0.0005, 0.0028, 0, 0.0004, 0.994, 0.0003, 0.0025],
        [0.0015, 0.0006, 0.0011, 0.9985, 0.0017, 0.0014, 0.0006, 0.0017, 0.0083],
        [0.0005, 0.0012, 0.0007, 0.9915, 0.0001, 0.0006, 0.0028, 0.001, 0.0024]
    ], [
        [0.0009, 0.0021, 0.0013, 0.9999, 0.003, 0.0011, 0.0007, 0.0025, 0.0001],
        [0.0013, 0.002, 0.0029, 0.0004, 0.9808, 0.0015, 0.0446, 0.0001, 0.0079],
        [0.0051, 0.001, 0.0011, 1, 0.0001, 0.0016, 0.0002, 0.0016, 0.0149],
        [0.0004, 0.0002, 0.0003, 0.0225, 0.0002, 0.0003, 0.0083, 0, 0.9314]
    ]
    ]
    result = tpd.predict(data)
    print(result)
    for i in result:
        print(tpd.get_tumor_type(i))


    #
    # tpd.load_model()
    # data = [[[0.00000, 0.19943, 0.00000, 0.00000, 0.00000, 0.00000, 0.00002, 1.00000, 0.00000],
    #     [0.00000, 0.31063, 0.00000, 0.00011, 0.00000, 0.00000, 0.08663, 0.00012, 0.00338],
    #          [0.00000, 0.99973, 0.00196, 0.00002, 0.00000, 0.00003, 0.00630, 0.00003, 0.00007],
    #     [0.00000, 0.06142, 0.00010, 0.00000, 0.00000, 0.00004, 0.16014, 0.00019, 0.01393],
    # ]]
    # # data = [[[0.00000, 0.00050, 0.00000, 0.00054, 0.00000, 0.00000, 0.09201, 1.0000, 0.00001],
    # #     [0.00000, 0.00001, 0.00000, 0.00000, 0.00000, 0.00000, 0.99989, 0.00054, 0.00003],
    # #     [0.00000, 0.00007, 0.00001, 0.00001, 0.00000, 0.00003, 0.00758, 0.00000, 0.99975],
    # #     [0.00000, 0.99994, 0.00001, 0.00000, 0.00065, 0.00000, 0.00003, 0.00121, 0.00040]
    # # ]]
    # print(tpd.predict(data))

    # print(len(tpd.model.get_weights()))
    # print(tpd.model.layers[0].output)
    # print(tpd.model.get_layer(index=1))
    # print([tpd.model.layers[0].input, tpd.model.layers[1].output])
    # data = [[[8.891e-01, 0.669e-01, 8.748e-01, 4.140e-02, 1.570e-02],
    #         [9.884e-01, 1.169e-01, 9.745e-01, 6.910e-02, 2.330e-02],
    #         [9.889e-01, 0.559e-01, 9.273e-01, 7.730e-02, 1.700e-02],
    #         [9.883e-01, 1.336e-01, 9.378e-01, 7.460e-02, 0.730e-02]],
    #
    #         [[4.680e-02, 9.625e-01, 3.860e-01, 9.674e-01, 4.700e-03],
    #          [7.680e-02, 6.522e-01, 4.419e-01, 1.803e-01, 9.954e-01],
    #          [5.460e-02, 7.479e-01, 2.121e-01, 3.716e-01, 9.984e-01],
    #          [4.430e-02,9.890e-01, 3.614e-01, 9.723e-01, 3.570e-02]],
    #
    #         [[9.060e-02, 9.319e-01, 9.779e-01, 1.339e-01, 5.000e-04],
    #          [9.490e-02, 9.377e-01, 9.794e-01, 1.783e-01, 6.000e-04],
    #          [9.060e-02, 9.319e-01, 9.779e-01, 1.339e-01, 5.000e-04],
    #          [9.490e-02, 9.377e-01, 9.794e-01, 1.783e-01, 6.000e-04]],
    #
    #         [[1.013e-01, 9.415e-01, 8.522e-01, 6.648e-01, 1.800e-03],
    #          [5.770e-02, 4.377e-01, 1.041e-01, 1.543e-01, 1.000e+00],
    #          [2.450e-02, 5.054e-01, 1.100e-01, 1.406e-01, 1.000e+00],
    #          [7.090e-02, 2.700e-01, 8.970e-02, 1.692e-01, 1.000e+00]]
    # ]

    # data = [[[0.00014269351959228516, 0.0008907318115234375, 0.0017977356910705566, 0.001090407371520996, 0.7774741649627686, 0.0124015212059021, 0.0047570765018463135, 0.0005503296852111816, 0.10258907079696655],
    #          [0.0013817250728607178, 0.0003587007522583008, 0.0022447705268859863, 0.000646442174911499, 0.00042504072189331055, 0.0007336735725402832, 0.729873538017273, 0.001232832670211792, 0.022673452273011208],
    #          [0.0002327561378479004, 0.0009062588214874268, 0.0003070831298828125, 0.0004570186138153076, 0.0003897547721862793, 0.0009983181953430176, 0.9935452342033386, 0.00036084651947021484, 0.006552666891366243],
    #          [5.3882598876953125e-05, 0.0363619327545166, 0.0016061961650848389, 0.1852993369102478, 0.10823121666908264, 0.00019308924674987793, 0.5056161880493164, 0.0044442713260650635, 0.0005840439698658884]],
    #         ]
    # print(tpd.predict(data)[0][0])
    # data = [[
    #          [3.5583973e-05, 9.9994862e-01, 2.3841858e-07, 8.9406967e-07, 3.7401915e-05, 2.9802322e-07, 8.5532665e-06, 0.0000000e+00, 3.7835594e-03],
    #          [3.3587217e-05, 1.5825033e-05, 2.3347139e-04, 8.1360340e-06, 5.6624413e-07, 5.2756071e-04, 9.9998391e-01, 9.9999487e-01, 7.6607540e-07],
    #          [1.5348196e-05, 1.4042854e-04, 2.4610758e-04, 2.5755167e-04, 3.5166740e-06, 2.9802322e-07, 1.2353659e-03, 3.5375357e-05, 9.9995959e-01],
    #          [3.5583973e-05, 9.9994862e-01, 2.3841858e-07, 8.9406967e-07, 3.7401915e-05, 2.9802322e-07, 8.5532665e-06, 0.0000000e+00, 3.7835594e-03]
    #          ]
    # # ]
    # data = [
    #     # [
    #     #  [7.385015487670898e-05, 2.5063753128051758e-05, 4.470348358154297e-07, 3.5762786865234375e-07,
    #     #   0.005365967750549316, 4.172325134277344e-07, 0.0001163482666015625, 0.0, 0.9967888593673706],
    #     # [0.0003695189952850342, 0.0018980801105499268, 0.0016337037086486816, 0.026500970125198364,
    #     #   0.0009382367134094238, 0.012093782424926758, 0.6899341940879822, 0.9886564016342163, 0.030088340863585472],
    #     #  [1.7821788787841797e-05, 2.7954578399658203e-05, 2.980232238769531e-07, 8.919835090637207e-05,
    #     #   0.0003082454204559326, 0.0, 0.001228630542755127, 1.8477439880371094e-06, 0.998661994934082],
    #     #  [7.385015487670898e-05, 2.5063753128051758e-05, 4.470348358154297e-07, 3.5762786865234375e-07,
    #     #   0.005365967750549316, 4.172325134277344e-07, 0.0001163482666015625, 0.0, 0.9967888593673706]]
    # # ]
    #     [
    #         # Hemangioma
    #         [0, 0.001, 0, 0, 0.992, 0, 0.07, 0.003, 0.001],
    #         [0, 0.003, 0, 0, 0.001, 0, 0.995, 0.01, 0.001],
    #         [0, 0.001, 0, 0, 0, 0, 0.998, 0.001, 0],
    #         [0, 0, 0, 0.001, 0, 0, 0.987, 0, 0],
    #
    #     ],
    #     [
    #         # FNH
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 1, 0, 0, 0, 0.134, 0.01, 0],
    #         [0, 0, 0.993, 0, 0, 0, 0.026, 0, 0.005],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0]
    #     ],
    #     [
    #         # Adenoma
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0.0006, 0.001166, 0.00061, 0.991321, 0.004005, 0.000241, 0.599792, 0.046208, 0.007444],
    #         [0.003941, 4e-06, 0.000469, 0.250889, 5e-05, 1.4e-05, 0.098638, 0.0005, 0.018261],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0]
    #     ],
    #     [
    #         # Adenoma
    #         # [0.0056, 0.001, 0.0032, 0.0016, 0.3634, 0.0006, 0.0036, 0.0004, 0.8402],
    #         # [0.003, 0.002666667, 0.000666667, 0.183666667, 0.001, 0, 0.128833333, 0.007666667, 0.181166667],
    #         # [0.0035, 0.003166667, 0.004333333, 0.092333333, 0, 0, 0.0455, 0.0015, 0.195833333],
    #         # [0.0036, 0.0006, 0.0008, 0.001, 0, 0, 0.053, 0, 0.5546]
    #         [0.015, 0.001, 0.004, 0.002, 0.192, 0.001, 0.003, 0.001, 0.869],
    #         [0.001, 0.001, 0.001, 0.991, 0.004, 0, 0.6, 0.046, 0.007],
    #         [0.004, 0, 0, 0.251, 0, 0, 0.099, 0.001, 0.018],
    #         [0.003, 0.001, 0.001, 0.001, 0, 0, 0.045, 0, 0.518]
    #     ],
    #     [
    #         # Ardenoma
    #         [0.001, 0.001, 0, 0, 0.74, 0.001, 0.005, 0, 0.8],
    #         [0.001, 0.001, 0.001, 0.991, 0.004, 0, 0.6, 0.046, 0.007],
    #         [0.004, 0, 0, 0.251, 0, 0, 0.099, 0.001, 0.018],
    #         [0.001, 0.001, 0, 0, 0, 0, 0.083, 0, 0.771]
    #     ],
    #     [
    # #         # FLHCC
    #         [1, 0, 1, 0, 0, 0, 0, 0, 0],
    #         [1, 0.001, 1, 0, 0, 0, 0.065, 0, 0],
    #         [1, 0.001, 0.995, 0, 0.001, 0, 0.004, 0, 0],
    #         [1, 0, 0.401, 0, 0.007, 0, 0.006, 0, 0]
    #     ],
    # #     # HCC
    # #     [[0.0020509064197540283, 0.0011729300022125244, 0.0003275871276855469, 0.0003013312816619873,
    # #       0.2315058410167694, 0.0011326372623443604, 0.00330430269241333, 7.298588752746582e-05, 0.9697589874267578],
    # #      [0.0015854239463806152, 0.0018890798091888428, 0.0005820095539093018, 0.012301474809646606,
    # #       0.0014027655124664307, 0.0002945065498352051, 0.9873108863830566, 0.993931233882904, 0.0009126506629399955],
    # #      [0.007437914609909058, 0.0107288658618927, 0.003703683614730835, 0.008452832698822021, 0.0036210715770721436,
    # #       0.0006792545318603516, 0.05043107271194458, 0.0010408461093902588, 0.625346302986145],
    # #      [0.0020509064197540283, 0.0011729300022125244, 0.0003275871276855469, 0.0003013312816619873,
    # #       0.2315058410167694, 0.0011326372623443604, 0.00330430269241333, 7.298588752746582e-05, 0.9697589874267578]],
    # #     [
    # #         [0, 0.198, 0.001, 0, 0, 0, 0.159, 0.001, 0.022],
    # #         [0, 0, 0.001, 0.003, 0, 0, 0.991, 1, 0.001],
    # #         [0.001, 0, 0, 0, 0, 0, 0.009, 0, 0.83],
    # #         [0, 0.198, 0.001, 0, 0, 0, 0.159, 0.001, 0.022],
    # #     ],
    # #     [
    # #         [0.002, 0.034, 0, 0.002, 0.095, 0.001, 0.007, 0, 0.828],
    # #         [0, 0.001, 0, 0.03, 0.001, 0, 0.976, 1, 0.01],
    # #         [0.002, 0.281, 0.002, 0.022, 0.001, 0, 0.046, 0, 0.257],
    # #         [0.002, 0.034, 0, 0.002, 0.095, 0.001, 0.007, 0, 0.828]
    # #         # [0, 0, 0, 0, 0, 0, 0.004, 0, 1],
    # #         # [0.343, 0, 1, 0, 0.019, 0, 0, 0.385, 0],
    # #         # [0.01, 0.006, 0.99, 0.001, 0, 0.033, 0, 0, 0.439],
    # #         # [0, 0, 0, 0, 0, 0, 0.004, 0, 1]
    # #     ]
    #
    #     [
    #         [0, 0.001, 0, 0.03, 0.001, 0, 0.976, 1, 0.01],
    #         [0.002, 0.281, 0.002, 0.022, 0.001, 0, 0.046, 0, 0.257],
    #         [0.002, 0.034, 0, 0.002, 0.095, 0.001, 0.007, 0, 0.828],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0]
    #     ],
    #     [
    #         [0.01, 0, 0.001, 0.022, 0.001, 0, 0.99, 1, 0.001],
    #         [0.013, 0.004, 0.003, 0.007, 0.002, 0.001, 0.018, 0.001, 0.751],
    #         [0.001, 0, 0, 0, 0.208, 0, 0.003, 0, 0.969],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0]
    #     ],
    #     [
    #         [0.000, 0.001, 0.000, 0.032, 0.001, 0.000, 0.976, 1, 0.01],
    #         [0.002, 0.281, 0.002, 0.022, 0.001, 0.000, 0.046, 0, 0.257],
    #         [0.002, 0.034, 0.000, 0.002, 0.095, 0.001, 0.007, 0, 0.828],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0]
    #     ],
    #     [
    #         [0.002, 0.002, 0.0005, 0.012, 0.0014, 0.0003, 0.98, 0.99, 0.0009],
    #         [0.007, 0.01, 0.004, 0.008, 0.004, 0.0007, 0.05, 0.001, 0.63],
    #         [0.002, 0.001, 0.0003, 0.0003, 0.23, 0.001, 0.003, 0.00007, 0.97],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0]
    #     ]
    # ]
    #
    # labels = ["Hemangioma", "FNH", "Adenoma", "Adenoma", "Adenoma", "FLHCC", "HCC", "HCC", "HCC", "HCC"]
    # data = [
    #     [[0, 0, 0, 0, 0, 0, 0, 0, 0],
    #      [0.00010031461715698242, 0.00086250901222229, 6.687641143798828e-05, 0.029576003551483154,
    #       0.0014820396900177002, 9.524822235107422e-05, 0.9763943552970886, 0.9996423721313477, 0.00986401829868555],
    #      [0.002316683530807495, 0.2805525064468384, 0.0017493367195129395, 0.02231171727180481, 0.0014745891094207764,
    #       0.00011709332466125488, 0.04596292972564697, 0.00027945637702941895, 0.25714486837387085],
    #      [0.0020180344581604004, 0.03442835807800293, 0.00027999281883239746, 0.0016794204711914062,
    #       0.09513503313064575, 0.0014788508415222168, 0.006976425647735596, 3.9696693420410156e-05, 0.827508270740509]]
    # ]
    #
    # data = [
    #     [[0, 0, 0, 0, 0, 0, 0, 0, 0],
    #      [1.9553304e-04, 6.8855882e-03, 1.7544627e-04, 3.9130688e-02, 1.2274981e-03,
    #       2.9653311e-05, 8.9364427e-01, 9.9733353e-01, 2.4445960e-02],
    #      [1.6105562e-02, 1.1430383e-02, 2.8870404e-03, 1.2363195e-03, 4.5302510e-04,
    #       2.3865700e-04, 2.8646207e-01, 4.8768520e-04, 2.2125176e-01],
    #      [4.48632240e-03, 6.17522001e-03, 6.67482615e-04, 9.35286283e-04,
    #       1.22744024e-01, 2.82171369e-03, 2.15485692e-02, 4.75645065e-05, 7.14385271e-01]
    #      ]
    # ]
    #
    # result = tpd.predict([data])
    # print(result)
    #
    # data = [
    #     [[6.7436695e-04, 4.2173266e-04, 1.9255280e-04, 5.6678057e-04, 3.5126209e-02,
    #       2.9018521e-04, 3.0455241e-01, 1.3437867e-04, 3.6414793e-01],
    #      [1.9527078e-03, 2.4676323e-05, 5.1617622e-05, 1.1861324e-04, 1.0669231e-05,
    #       1.2140572e-03, 9.2574036e-01, 1.5202165e-04, 6.7632568e-01],
    #      [6.0954690e-04, 2.9802322e-07, 1.0907650e-05, 1.6987324e-06, 4.4703484e-07,
    #       7.1465969e-05, 9.6962661e-01, 7.3969364e-05, 5.3469145e-01],
    #      [7.7307224e-05, 1.5228987e-05, 6.6637993e-05, 1.6689301e-05, 6.1392784e-06,
    #       5.8412552e-06, 8.4683907e-01, 7.1823597e-06, 9.8040164e-02]
    #      ]
    # ]
    #
    # print(type(data), type(data[0]), type(data[0][0]), type(data[0][0][0]))
    # # result = tpd.predict([data])
    # # print(result)
    #
    # #
    # # for i in range(len(data)):
    # #     result = tpd.predict([[data[i]]])
    # #     print(result)
    # #     print("Origianl Label: ", labels[i])
    # #     print(tpd.get_tumor_type(result))
    # #     print("==="*20, "\n\n")
    #
    #
    # # print(tpd.features, tpd.labels)
    # # x, y = tpd.test_x, tpd.test_y
    # # x, y = tpd.test_x, tpd.test_y
    # # y_pred = tpd.predict(tpd.labels)
    # # y_pred = tpd.predict(tpd.test_x)
    # # print(tpd.test_y)
    # # print(y_pred)
    # # y_true = np.where(tpd.test_y == 1)[1]
    # # print()
    # # # ["Hemangioma", "FNH", "Adenoma", "FLHCC", "HCC"]
    # # print(metrics.confusion_matrix(y_true, y_pred, labels=[0,1,2,3,4]))
    # # print(metrics.classification_report(y_true, y_pred, labels=[0,1,2,3,4]))
    #
    # # d = {'PatientID': [1, 2], 'TakenTime': [1, 2], 'sliceNum': [1, 2],
    # #      'ConfRatesPP': [[0.9889, 0.1559, 0.9773, 0.0673, 0.027], [0.9889, 0.1559, 0.9773, 0.0673, 0.027]],
    # #      'ConfRatesAP': [[0.9889, 0.1559, 0.9773, 0.0673, 0.027], [0.9889, 0.1559, 0.9773, 0.0673, 0.027]],
    # #      'ConfRatesPVP': [[0.9889, 0.1559, 0.9773, 0.0673, 0.027], [0.9889, 0.1559, 0.9773, 0.0673, 0.027]],
    # #      'ConfRatesDP': [[0.9889, 0.1559, 0.9773, 0.0673, 0.027], [0.9889, 0.1559, 0.9773, 0.0673, 0.027]],
    # #      'Type': [2, 4]}
    # # df = pd.DataFrame(d)
    # # data = df.iloc[:, 4:9]
    # # features, labels = df.iloc[:, :4], df.iloc[:, -1]
    # #
    # # print(features.shape, type(features))

