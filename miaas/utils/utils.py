import math


def standardDeviation(values, option):
    if len(values) < 2:
        return None
    sd = 0.0
    diff_sum = 0.0

    meanValue = sum(values, 0.0) / len(values)

    for i in range(0, len(values)):
        diff = values[i] - meanValue
        diff_sum += diff * diff

    sd = math.sqrt(diff_sum / (len(values) - option))
    return sd