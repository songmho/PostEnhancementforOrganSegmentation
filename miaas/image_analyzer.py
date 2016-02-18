from __future__ import division

from pprint import pprint

import pandas as pd
import pywt
import json
import numpy as np
import miaas.utils.bwr as bwr
from miaas.utils.utils import *
import time
import matplotlib.pyplot as plt

# Error Sentences
ERROR_INVALID = "Invalid measurements are acquired."
ERROR_GENDER = "Gender isn't entered"
ERROR_HEIGHT = "Height isn't entered."
ERROR_BIRTHDAY = "Birthday isn't entered"


class ImageInterpreter:
    def __init__(self):
        pass

    def check_meas_validity(self, meas_set):
        if len(meas_set) == 0:
            error_message = "No Data"
            return True, error_message
        return False, "No Error"

    def analyze_context(self, meas_set):
        pass


class ECGInterpreter(ImageInterpreter):
    class ECG():
        def __init__(self):
            self.p = {'peak': 0, 'onset': 0, 'offset': 0}
            self.q = {'peak': 0, 'onset': 0, 'offset': 0}
            self.r = {'peak': 0, 'onset': 0, 'offset': 0}
            self.s = {'peak': 0, 'onset': 0, 'offset': 0}
            self.t = {'peak': 0, 'onset': 0, 'offset': 0}

        def __repr__(self):
            return "P_peak = %s, Q_peak = %s, R_peak = %s, S_peak = %s, T_peak = %s \n" \
                   "P_onset = %s, Q_onset = %s, R_onset = %s, S_onset = %s, T_onset = %s \n" \
                   "P_offset = %s, Q_offset = %s, R_offset = %s, S_offset = %s, T_offset = %s \n" \
                   % (self.p['peak'], self.q['peak'], self.r['peak'], self.s['peak'], self.t['peak'],
                      self.p['onset'], self.q['onset'], self.r['onset'], self.s['onset'], self.t['onset'],
                      self.p['offset'], self.q['offset'], self.r['offset'], self.s['offset'], self.t['offset'])

        def check(self):
            waves = [self.p, self.q, self.r, self.s, self.t]
            value = 1
            for wave in waves:
                value *= wave['peak'] * wave['onset'] * wave['offset']
            if value == 0:
                return False
            else:
                return True

    def __init__(self):
        super().__init__()

    def delineate_ecg(self, data):
        # nested functions
        def moving_average(array, window):
            res = []
            if len(array) < window:
                return None
            for i in range(0, len(array)):
                if i < window:
                    res.append(sum(array[0:window]) / window)
                elif len(array) - i < window:
                    res.append(sum(array[len(array) - (window):len(array)]) / window)
                else:
                    res.append(sum(array[i - window:i + window]) / (window * 2))
            return np.asarray(res)

        def find_modulus(coef, threshold, peak=None, sinus_rhythms=None, direction='backward', window=100):
            peaks = []
            res = []
            if peak is not None:
                for ecg in sinus_rhythms:
                    peaks.append(getattr(ecg, peak)['peak'])

            if len(peaks) > 0 and direction == 'forward':
                temp = []
                for peak in peaks[::-1]:
                    front = peak - window
                    if front <= 0:
                        front = 0
                    for i in range(peak, front, -1):
                        if abs(coef[i]) > threshold:
                            temp.append([i, coef[i]])
                    res = sorted(temp, reverse=False)

            elif len(peaks) > 0 and direction == 'backward':
                temp = []
                for peak in peaks:
                    back = peak + window
                    if back >= len(coef) - 1:
                        back = len(coef)
                    for i in range(peak, back):
                        if abs(coef[i]) > threshold:
                            temp.append([i, coef[i]])
                    res = sorted(temp, reverse=False)
            else:
                for i in range(0, len(coef), 1):
                    if abs(coef[i]) > threshold:
                        res.append([i, coef[i]])

            modulus = np.asarray(res, list)
            return modulus

        def find_maximas(modulus):
            temp = None
            maximas = []
            minimas = []
            for i in range(0, len(modulus) - 1):
                if temp is None:
                    if modulus[i + 1][1] - modulus[i][1] > 0:
                        temp = True  # increase
                    elif modulus[i + 1][1] - modulus[i][1] < 0:
                        temp = False  # decrease
                    continue

                if modulus[i + 1][1] - modulus[i][1] > 0:
                    if temp == False:
                        minimas.append(modulus[i][0])
                    temp = True  # increase
                elif modulus[i + 1][1] - modulus[i][1] < 0:
                    if temp == True:
                        maximas.append(modulus[i][0])
                    temp = False  # decrease

            return sorted(maximas), sorted(minimas)

        def find_zero_crossings(modulus, window=15):
            def find_zero(x1, y1, x2, y2):
                return x1 - (x2 - x1) / (y2 - y1) * y1

            zero_crossings = []
            temp = None
            thr = 0.1
            for i in range(0, len(modulus)):
                if temp is None:
                    if modulus[i][1] > 0:
                        temp = [True, modulus[i][1]]  # Plus
                    else:
                        temp = [False, modulus[i][1]]  # Minus
                    continue
                if modulus[i][1] > 0:
                    if temp[0] is False and abs(temp[1] - modulus[i][1]) > thr and modulus[i][0] - modulus[i - 1][
                        0] < window:
                        zero_crossings.append(find_zero(modulus[i - 1][0], temp[1], modulus[i][0], modulus[i][1]))
                    temp = [True, modulus[i][1]]
                elif modulus[i][1] < 0:
                    if temp[0] is True and abs(temp[1] - modulus[i][1]) > thr and modulus[i][0] - modulus[i - 1][
                        0] < window:
                        zero_crossings.append(find_zero(modulus[i - 1][0], temp[1], modulus[i][0], modulus[i][1]))
                    temp = [False, modulus[i][1]]
            return zero_crossings

        def rms(array):
            return np.sqrt((array ** 2).mean())

        def detect_peak(signals, zero_crossing, forward_window, backward_window, type='max'):
            center = int(zero_crossing)
            if type == 'max':
                return int(
                    np.argmax(signals[center - forward_window:center + backward_window]) + center - forward_window)
            else:
                return int(
                    np.argmin(signals[center - forward_window:center + backward_window]) + center - forward_window)

        # create wavelet
        wavelet = pywt.Wavelet('db1')
        # pre-processing
        coeffs = pywt.swt(data[:, 1], wavelet, 5, start_level=0)
        denoised_ecg = coeffs[2][0] + coeffs[2][1]
        (baseline, denoised_ecg) = bwr.bwr(denoised_ecg)
        signals = moving_average(denoised_ecg, 3)
        # ECG delineation
        coeffs = pywt.swt(signals, wavelet, 5, start_level=0)
        sinus_rhythms = []
        # threshold values
        e_qrs_1 = 1.7 * rms(coeffs[4][1])
        r_qrs_post = 0.09 * max(abs(coeffs[3][1]))
        e_qrs_3 = rms(coeffs[2][1])
        e_qrs_4 = rms(coeffs[1][1]) * 0.5
        e_t = 0.15 * rms(coeffs[1][1])
        e_p = 0.15 * rms(coeffs[1][1])
        # r waves
        modulus1 = find_modulus(coeffs[4][1], e_qrs_1)
        zero_crossings = find_zero_crossings(modulus1)
        for zc in zero_crossings:
            ecg = self.ECG()
            ecg.r['peak'] = detect_peak(signals, zc, 3, 3)
            for i in range(ecg.r['peak'], 0, -1):
                if signals[i] * signals[i - 1] < 0:
                    ecg.r['onset'] = i
                    ecg.q['offset'] = i
                    break
            for i in range(ecg.r['peak'], len(signals) - 1):
                if signals[i] * signals[i + 1] < 0:
                    ecg.r['offset'] = i
                    ecg.s['onset'] = i
                    break
            sinus_rhythms.append(ecg)
        window = int((sinus_rhythms[1].r['peak'] - sinus_rhythms[0].r['peak']) / 2)
        # s waves
        modulus2 = find_modulus(coeffs[3][1], r_qrs_post, peak='r', sinus_rhythms=sinus_rhythms)
        zero_crossings = find_zero_crossings(modulus2, window=15)
        for ecg in sinus_rhythms:
            for zero_crossing in zero_crossings:
                if ecg.r['peak'] < zero_crossing:
                    ecg.s['peak'] = detect_peak(signals, zero_crossing, 1, 4, 'min')
                    for i in range(ecg.s['peak'], len(signals) - 1):
                        if signals[i] * signals[i + 1] < 0:
                            ecg.s['offset'] = i
                            break
                    break

        # q waves
        modulus2 = find_modulus(coeffs[3][1], r_qrs_post, peak='r', sinus_rhythms=sinus_rhythms, direction='forward',
                                window=window)
        maximas, minimas = find_maximas(modulus2)
        for ecg in sinus_rhythms:
            idx = 0
            for minima in minimas:
                if minima < ecg.r['peak']:
                    idx = minima
                else:
                    break
            ecg.q['peak'] = detect_peak(signals, idx, 10, 1, 'min')
            for i in range(ecg.q['peak'], 0, -1):
                if signals[i] * signals[i - 1] < 0:
                    ecg.q['onset'] = i
                    break
        # t waves
        modulus4 = find_modulus(coeffs[1][1], e_t, peak='s', sinus_rhythms=sinus_rhythms, window=window)
        zero_crossings = find_zero_crossings(modulus4, window=15)

        for ecg in sinus_rhythms:
            tem_points = []
            back = ecg.s['peak'] + window
            if back >= len(signals) - 1:
                back = len(signals) - 1

            for zero_crossing in zero_crossings:
                if ecg.s['peak'] <= zero_crossing < back:
                    tem_points.append(zero_crossing)
                elif back < zero_crossing:
                    break
            if len(tem_points) >= 2:
                ecg.t['peak'] = int(
                    np.argmax(signals[tem_points.copy()[0]:tem_points.copy()[1]]) + tem_points.copy()[0])
                ecg.t['onset'] = int(tem_points.copy()[0])
                ecg.t['offset'] = int(tem_points.copy()[1])

        # p waves
        modulus4 = find_modulus(coeffs[1][1], e_p, peak='q', sinus_rhythms=sinus_rhythms, direction='forward',
                                window=window)
        zero_crossings = find_zero_crossings(modulus4, window=10)

        for ecg in sinus_rhythms[::-1]:
            temp_points = []
            front = ecg.q['peak'] - window
            if front <= 0:
                front = 0
            for zero_crossing in zero_crossings[::-1]:
                if front <= zero_crossing <= ecg.q['peak']:
                    temp_points.append(zero_crossing)
                elif zero_crossing < front:
                    break
            if len(temp_points) >= 2:
                ecg.p['peak'] = int(
                    np.argmax(signals[temp_points.copy()[-1]:temp_points.copy()[-2]]) + temp_points.copy()[-1])
                ecg.p['onset'] = int(temp_points.copy()[-1])
                ecg.p['offset'] = int(temp_points.copy()[-2])

        ab_sinus_rhythms = []
        for ecg in sinus_rhythms:
            if not ecg.check():
                ab_sinus_rhythms.append(ecg)
        for ecg in ab_sinus_rhythms:
            sinus_rhythms.remove(ecg)
        plt.plot(signals, color='k')
        for ecg in sinus_rhythms:
            plt.annotate("P_peak", xy=(ecg.p['peak'], signals[ecg.p['peak']]),
                         xytext=(ecg.p['peak'], signals[ecg.p['peak']]), fontsize=10)
            plt.annotate("P_onset", xy=(ecg.p['onset'], signals[ecg.p['onset']]),
                         xytext=(ecg.p['onset'], signals[ecg.p['onset']]), fontsize=10)
            plt.annotate("P_offset", xy=(ecg.p['offset'], signals[ecg.p['offset']]),
                         xytext=(ecg.p['offset'], signals[ecg.p['offset']]), fontsize=10)
            plt.plot(ecg.p['peak'], signals[ecg.p['peak']], marker='v', color='b')
            plt.plot(ecg.p['onset'], signals[ecg.p['onset']], marker='>', color='b')
            plt.plot(ecg.p['offset'], signals[ecg.p['offset']], marker='<', color='b')

            plt.annotate("Q_peak", xy=(ecg.q['peak'], signals[ecg.q['peak']]),
                         xytext=(ecg.q['peak'], signals[ecg.q['peak']]), fontsize=10)
            plt.annotate("Q_onset", xy=(ecg.q['onset'], signals[ecg.q['onset']]),
                         xytext=(ecg.q['onset'], signals[ecg.q['onset']]), fontsize=10)
            plt.annotate("Q_offset", xy=(ecg.q['offset'], signals[ecg.q['offset']]),
                         xytext=(ecg.q['offset']-0.1, signals[ecg.q['offset']]-0.1), fontsize=10)
            plt.plot(ecg.q['peak'], signals[ecg.q['peak']], marker='v', color='g')
            plt.plot(ecg.q['onset'], signals[ecg.q['onset']], marker='>', color='g')

            plt.annotate("R_peak", xy=(ecg.r['peak'], signals[ecg.r['peak']]),
                         xytext=(ecg.r['peak'], signals[ecg.r['peak']]), fontsize=10)
            plt.annotate("R_onset", xy=(ecg.r['onset'], signals[ecg.r['onset']]),
                         xytext=(ecg.r['onset'], signals[ecg.r['onset']]), fontsize=10)
            plt.annotate("R_offset", xy=(ecg.r['offset'], signals[ecg.r['offset']]),
                         xytext=(ecg.r['offset'], signals[ecg.r['offset']]), fontsize=10)

            plt.plot(ecg.r['peak'], signals[ecg.r['peak']], marker='v', color='r')
            plt.plot(ecg.r['onset'], signals[ecg.r['onset']], marker='d', color='r')
            plt.plot(ecg.r['offset'], signals[ecg.r['offset']], marker='d', color='r')

            plt.annotate("S_peak", xy=(ecg.s['peak'], signals[ecg.s['peak']]),
                         xytext=(ecg.s['peak'], signals[ecg.s['peak']]), fontsize=10)
            plt.annotate("S_onset", xy=(ecg.s['onset'], signals[ecg.s['onset']]),
                         xytext=(ecg.s['onset']-0.1, signals[ecg.s['onset']]-0.1), fontsize=10)
            plt.annotate("S_offset", xy=(ecg.s['offset'], signals[ecg.s['offset']]),
                         xytext=(ecg.s['offset'], signals[ecg.s['offset']]), fontsize=10)

            plt.plot(ecg.s['peak'], signals[ecg.s['peak']], marker='v', color='c')
            plt.plot(ecg.s['offset'], signals[ecg.s['offset']], marker='<', color='c')

            plt.annotate("T_peak", xy=(ecg.t['peak'], signals[ecg.t['peak']]),
                         xytext=(ecg.t['peak'], signals[ecg.t['peak']]), fontsize=10)
            plt.annotate("T_onset", xy=(ecg.t['onset'], signals[ecg.t['onset']]),
                         xytext=(ecg.t['onset'], signals[ecg.t['onset']]), fontsize=10)
            plt.annotate("T_offset", xy=(ecg.t['offset'], signals[ecg.t['offset']]),
                         xytext=(ecg.t['offset'], signals[ecg.t['offset']]), fontsize=10)
            plt.plot(ecg.t['peak'], signals[ecg.t['peak']], marker='v', color='y')
            plt.plot(ecg.t['onset'], signals[ecg.t['onset']], marker='>', color='y')
            plt.plot(ecg.t['offset'], signals[ecg.t['offset']], marker='<', color='y')
        plt.show()
        return sinus_rhythms

    def interprete(self, context):
        ret, error_message = self.check_meas_validity(context)
        if ret:
            return None
        # delineate ecg waves
        sinus_rhythms = self.delineate_ecg(context)
        # diagnose extracted features
        if len(sinus_rhythms) == 0:
            return None
        # from a view point of duration each heart activities
        P_duration = 0
        P_height = 0
        Q_duration = 0
        Q_height = 0
        R_duration = 0
        R_height = 0
        S_duration = 0
        S_height = 0
        T_duration = 0
        T_height = 0
        PR_interval = 0
        QRS_complex = 0
        QT_interval = 0
        PR_segment = 0
        ST_segment = 0

        RR_intervals = []
        rhythm_irregularity = 0
        temp_value = 0
        for ecg in sinus_rhythms:
            P_duration += context[ecg.p['offset']][0] - context[ecg.p['onset']][0]
            P_height += abs(
                context[ecg.p['peak']][1] - (context[ecg.p['offset']][1] + context[ecg.p['offset']][1]) * 0.5)

            Q_duration += context[ecg.q['offset']][0] - context[ecg.q['onset']][0]
            Q_height += abs(
                context[ecg.q['peak']][1] - (context[ecg.q['offset']][1] + context[ecg.q['offset']][1]) * 0.5)

            R_duration += context[ecg.r['offset']][0] - context[ecg.r['onset']][0]
            R_height += abs(
                context[ecg.r['peak']][1] - (context[ecg.r['offset']][1] + context[ecg.r['offset']][1]) * 0.5)

            S_duration += context[ecg.s['offset']][0] - context[ecg.s['onset']][0]
            S_height += abs(
                context[ecg.s['peak']][1] - (context[ecg.s['offset']][1] + context[ecg.s['offset']][1]) * 0.5)

            T_duration += context[ecg.t['offset']][0] - context[ecg.t['onset']][0]
            T_height += abs(
                context[ecg.t['peak']][1] - (context[ecg.t['offset']][1] + context[ecg.t['offset']][1]) * 0.5)

            PR_interval += context[ecg.q['onset']][0] - context[ecg.p['onset']][0]
            QRS_complex += context[ecg.s['offset']][0] - context[ecg.q['onset']][0]
            QT_interval += context[ecg.t['offset']][0] - context[ecg.q['onset']][0]

            PR_segment += (context[ecg.p['offset']][1] + context[ecg.q['onset']][1]) * 0.5
            ST_segment += (context[ecg.s['offset']][1] + context[ecg.t['onset']][1]) * 0.5

            if temp_value == 0:
                temp_value = context[ecg.r['peak']][0]
            else:
                RR_intervals.append(context[ecg.r['peak']][0] - temp_value)

        P_duration /= len(sinus_rhythms)
        P_height /= len(sinus_rhythms)

        Q_duration /= len(sinus_rhythms)
        Q_height /= len(sinus_rhythms)

        R_duration /= len(sinus_rhythms)
        R_height /= len(sinus_rhythms)

        S_duration /= len(sinus_rhythms)
        S_height /= len(sinus_rhythms)

        T_duration /= len(sinus_rhythms)
        T_height /= len(sinus_rhythms)

        PR_interval /= len(sinus_rhythms)
        QRS_complex /= len(sinus_rhythms)
        QT_interval /= len(sinus_rhythms)

        PR_segment /= len(sinus_rhythms)
        ST_segment /= len(sinus_rhythms)
        rhythm_irregularity = standardDeviation(RR_intervals, 0)
        max_duration = np.mean(RR_intervals)
        max_height = R_height + S_height
        # handle the exception that the length of ECG measurements is too short
        if type(rhythm_irregularity) is None:
            return None
        # diagnose the category and the score
        ab_classes = []
        category = ""
        score = 0
        count = 0
        if P_duration < 120:
            score += 1
        else:
            score += (max_duration - P_duration) / (max_duration - 120)
            ECG_IRREGULARITIES[0].probability = 1-(max_duration - P_duration) / (max_duration - 120)
            ab_classes.append(ECG_IRREGULARITIES[0])
        count += 1
        if P_height < 0.25:
            score += 1
        else:
            score += (max_height - P_height) / (max_height - 0.25)
            ECG_IRREGULARITIES[0].probability = 1-(max_height - P_height) / (max_height - 0.25)
            ab_classes.append(ECG_IRREGULARITIES[0])
        count += 1
        if Q_duration < 40:
            score += 1
        else:
            score += (max_duration - Q_duration) / (max_duration - 40)
            ECG_IRREGULARITIES[0].probability = 1 - (max_duration - Q_duration) / (max_duration - 40)
            ab_classes.append(ECG_IRREGULARITIES[1])
        count += 1
        if Q_height < 0.25:
            score += 1
        else:
            score += (max_height - Q_height) / (max_height - 0.25)
            ECG_IRREGULARITIES[1].probability = 1-(max_height - Q_height) / (max_height - 0.25)
            ab_classes.append(ECG_IRREGULARITIES[1])
        count += 1
        if T_height < 0.5:
            score += 1
        else:
            score += (max_height - T_height) / (max_height - 0.5)
            ECG_IRREGULARITIES[3].probability = 1-(max_height - T_height) / (max_height - 0.5)
            ab_classes.append(ECG_IRREGULARITIES[3])
        count += 1
        if 120 < PR_interval < 300:
            score += 1
        elif 120 > PR_interval:
            score += PR_interval / 120
        else:
            score += (max_duration - PR_interval) / (max_duration - 300)

        count += 1
        if 80 < QRS_complex < 320:
            score += 1
        elif 80 > QRS_complex:
            score += QRS_complex / 80
            ECG_IRREGULARITIES[5].probability = 1-QRS_complex / 80
            ab_classes.append(ECG_IRREGULARITIES[5])
        else:
            score += (max_duration - QRS_complex) / (max_duration - 320)
            ECG_IRREGULARITIES[5].probability = 1-(max_duration - QRS_complex) / (max_duration - 320)
            ab_classes.append(ECG_IRREGULARITIES[5])
        count += 1
        if QT_interval < 440:
            score += 1
        else:
            score += (max_duration - QT_interval) / (max_duration - 440)
        count += 1
        if rhythm_irregularity < 300:
            score += 1
        else:
            ECG_IRREGULARITIES[4].probability = ((max_duration-rhythm_irregularity)/(max_duration-300))/100
            ab_classes.append(ECG_IRREGULARITIES[4])
        count += 1
        score /= count

        if score > 1:
            score = 1
        elif score < 0:
            score = 0
        idx=0
        temp=0
        for i in range(0, len(ab_classes)):
            if temp==0:
                temp=ab_classes[i].probability
                continue
            if temp<ab_classes[i].probability:
                temp=ab_classes[i].probability
                idx=i

        summary = {'score':score, 'irregularity':ab_classes[idx].irregularity,'related_diseases':ab_classes[idx].diseases, "probability":ab_classes[idx].probability}
        return summary


class AbClass():
    def __init__(self, irregularity, diseases):
        self.irregularity = irregularity
        self.diseases = diseases
        self.probability = 0

irregular_p = AbClass("Pathological P Wave",["Atrial Enlargement", "Pericarditis"])
irregular_Q = AbClass("Pathological Q Wave",["Myocardial Infarction", "Cardiomyopathies", "Rotation of the Heart"])
irregular_R = AbClass("Pathological R Wave",["Right Ventricular Hypertrophy", "Right Bundle Branch Block", "Right Ventricular Hypertrophy", "Posterior myocardial infarction", "Left ventricular hypertrophy"])
irregular_T = AbClass("Pathological T Wave",["Hyperkalemia", "Myocardial Ischaemia", "Ventricular Hypertrophy", "Pulmonary Embolism"])
irregular_rhythm = AbClass("Irregular Heart Rhythm",["Cardiac Arrhythmia", "Atrial Fibrillation", "Atrial Flutter", "Multifocal Atrial Tachycardia"])
irregular_QRSC = AbClass("Pathological QRS Complex",["Left or Right Bundle Branch Block", "Electrolyte Disorders", "Posterior myocardial infarction"])
irregular_STS = AbClass("Elevated or Depressed ST Segment",["Acute Myocardial Infraction", "Coronary Vasospasm", "Pericarditis", "Benign Early Repolarization", "Left Bundle Branch Block", "Brugada Syndrome"])
irregular_PRS = AbClass("Elevated or Depressed PR Segment",["Wolf-Parkinson-White Syndrome", "First Degree Atrioventricular Block", "Atrial Infarction", "Pericarditis"])
ECG_IRREGULARITIES = [irregular_p, irregular_Q, irregular_R,irregular_T, irregular_rhythm, irregular_QRSC, irregular_STS, irregular_PRS]

if __name__ == '__main__':
    df=pd.read_csv('../ecg.csv')
    df = df[["0","1"]]
    signals = df.as_matrix()
    pprint(ECGInterpreter().interprete(signals))
    pass
