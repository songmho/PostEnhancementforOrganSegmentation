import subprocess
import csv
import pandas as pd
from multiprocessing import *
import os

ascii_suffixes = ["_annotations", "_data", "_header", "_signals"]
file_suffixes = ["_data", "_signals"]


def edf_to_ascii(filepath):
    # For linux server
    # p = subprocess.Popen(['sudo', 'edf2ascii.exe', filepath.encode('ascii', 'ignore')],
    #                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # p.stdin.write("'" + '\n')
    # p.stdin.close()
    p = subprocess.Popen(['edf2ascii.exe', filepath.encode('ascii', 'ignore')],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        # print line
        pass
    p.wait()


def ascii_to_csv(path, name):
    for file_suffix in file_suffixes:
        in_txt = csv.reader(open(path + name + file_suffix + ".txt", "rb"), delimiter=',')
        out_csv = csv.writer(open(path + name + file_suffix + ".csv", "wb"))
        out_csv.writerows(in_txt)


def rename_labels(path, name):
    _signals = pd.read_csv(path + name + file_suffixes[1] + ".csv")
    labels = list(_signals.Label)
    labels.insert(0, "Time")
    _data = pd.read_csv(path + name + file_suffixes[0] + ".csv")
    _data.columns = labels
    _data.index = _data['Time']
    _data.iloc[:1000][labels[1:]].to_csv(path + name + file_suffixes[0] + ".csv")



def delete_other_files(path, name):
    for suffix in ascii_suffixes:
        os.remove(path + name + suffix + ".txt")
    os.remove(path + name + file_suffixes[1] + ".csv")


def edf_to_csv(filepath):
    path, name = os.path.split(filepath)
    path += "/"
    try:
        name = name.split(".")[0]
        p1 = Process(target=edf_to_ascii, args=(filepath,))
        p1.start()
        p1.join(timeout=30)
        p2 = Process(target=ascii_to_csv, args=(path, name))
        p2.start()
        p2.join(timeout=30)
        p3 = Process(target=rename_labels, args=(path, name))
        p3.start()
        p3.join(timeout=30)
        p4 = Process(target=delete_other_files, args=(path, name))
        p4.start()
        p4.join(timeout=30)
    except Exception as e:
        return filepath

    return path + name + file_suffixes[0] + ".csv"

# if __name__ == '__main__':
    # filepath = "./SC4001E0-PSG.edf"
    # edf_to_csv(filepath)
