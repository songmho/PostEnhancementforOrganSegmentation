from django import template
from django.utils.html import escapejs
import json, datetime, pytz
from miaas import constants
import logging

register = template.Library()

logging.basicConfig(
    format="[%(name)s][%(asctime)s] %(message)s",
    handlers=[logging.StreamHandler()],
    level=logging.INFO
)
logger = logging.getLogger(__name__)


@register.filter(name='get_range')
def get_range(number):
    return range(number)


@register.filter(name='get_range2')
def get_range2(number):
    return range(1, number + 1)


@register.filter(name='get_range_from_to')
def get_range_from_to(fr, to):
    return range(fr, to)


@register.filter(name='get_range_from_to2')
def get_range_from_to2(fr, to):
    return range(fr, to + 1)


@register.filter(name='get_page_num')
def get_page_num(item_count, items_per_page):
    page_num = item_count // items_per_page
    if item_count % items_per_page != 0:
        page_num += 1
    return page_num


@register.filter(name='get_interpretation_status')
def get_interpretation_status(status):
    status = int(status)
    return constants.INTPRT_STATUS.get(status, '-')


@register.filter(name='intpr_level_string')
def intpr_level_string(level):
    level = int(level)
    return constants.LEVEL_STRING[level]


@register.filter(name='jsonstr')
def to_jsonstr(dict):
    return escapejs(json.dumps(dict))


timezone_kr = pytz.timezone('Asia/Seoul')


@register.filter(name='datetime_string')
def timestamp_to_datetime_string(timestamp):
    try:
        return datetime.datetime.fromtimestamp(int(timestamp) // 1000) \
            .replace(tzinfo=pytz.utc).astimezone(timezone_kr) \
            .strftime('%m/%d/%y %H:%M')

    except ValueError as e:
        return (datetime.datetime(1970, 1, 1) + datetime.timedelta(int(timestamp) // 1000))\
            .replace(tzinfo=pytz.utc).astimezone(timezone_kr) \
            .strftime('%m/%d/%y')


@register.filter(name='date_string')
def timestamp_to_datetime_string(timestamp):
    try:
        return datetime.datetime.fromtimestamp(int(timestamp) // 1000) \
            .replace(tzinfo=pytz.utc).astimezone(timezone_kr) \
            .strftime('%m/%d/%y')

    except ValueError as e:
        return (datetime.datetime(1970, 1, 1) + datetime.timedelta(int(timestamp) // 1000))\
            .replace(tzinfo=pytz.utc).astimezone(timezone_kr) \
            .strftime('%m/%d/%y')


@register.filter(name='is_list')
def is_list(arr):
    return isinstance(arr, list)


@register.filter(name='list_size')
def list_size(arr):
    return len(arr)


@register.filter(name='list_get')
def list_get(arr, pos):
    return arr[pos]


@register.filter(name='is_empty')
def is_empty(collection):
    if isinstance(collection, list):
        return len(collection) == 0
    return None


@register.filter(name='plus')
def plus(value, plus):
    return value + plus


@register.filter(name='less_string')
def less_string(value):
    return value[:80] + "..."
