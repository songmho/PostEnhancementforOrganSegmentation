import math

import datetime
import pytz

from miaas import constants


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


timezone_kr = pytz.timezone('Asia/Seoul')


def timestamp_to_date_string(timestamp, time=True):
    if time:
        try:
            return datetime.datetime.fromtimestamp(int(timestamp) // 1000) \
                .replace(tzinfo=pytz.utc).astimezone(timezone_kr) \
                .strftime('%m/%d/%y %H:%M')
        except ValueError as e:
            return (datetime.datetime(1970, 1, 1) + datetime.timedelta(int(timestamp) // 1000))\
                .replace(tzinfo=pytz.utc).astimezone(timezone_kr) \
                .strftime('%m/%d/%y  %H:%M')
    else:
        try:
            return datetime.datetime.fromtimestamp(int(timestamp) // 1000) \
                .replace(tzinfo=pytz.utc).astimezone(timezone_kr) \
                .strftime('%m/%d/%y')
        except ValueError as e:
            return (datetime.datetime(1970, 1, 1) + datetime.timedelta(int(timestamp) // 1000))\
                .replace(tzinfo=pytz.utc).astimezone(timezone_kr) \
                .strftime('%m/%d/%y')


def get_interpretation_status(status):
    status = int(status)
    return constants.INTPRT_STATUS.get(status, '-')


def timestamp_to_datetime_string(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp) // 1000) \
        .replace(tzinfo=pytz.utc).astimezone(timezone_kr) \
        .strftime('%Y-%m-%d %H:%M')
