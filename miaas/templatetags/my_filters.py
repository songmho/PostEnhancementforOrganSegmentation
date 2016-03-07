from django import template
from django.utils.html import escapejs
import json, datetime, pytz
from miaas import constants

register = template.Library()

#Filter usage: {{ var|foo:"bar" }}

@register.filter(name='get_range')
def get_range(number):
    return range(number)

@register.filter(name='get_range2')
def get_range2(number):
    return range(1, number+1)

@register.filter(name='get_range_from_to')
def get_range_from_to(fr, to):
    return range(fr, to)

@register.filter(name='get_range_from_to2')
def get_range_from_to2(fr, to):
    return range(fr, to+1)

@register.filter(name='get_page_num')
def get_page_num(item_count, items_per_page):
    page_num = item_count // items_per_page
    if item_count % items_per_page != 0:
        page_num += 1
    return page_num

itprt_status = {
    3: 'Finding Physician',
    2: 'Candidate Waiting',
    1: 'Waiting Interpretation',
    0: 'Interpreted',
}

@register.filter(name='get_interpretation_status')
def get_interpretation_status(status):
    status = int(status)
    return itprt_status.get(status, '-')

@register.filter(name='jsonstr')
def to_jsonstr(dict):
    return escapejs(json.dumps(dict))

timezone_kr = pytz.timezone('Asia/Seoul')
@register.filter(name='datetime_string')
def timestamp_to_datetime_string(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp)//1000)\
        .replace(tzinfo=pytz.utc).astimezone(timezone_kr)\
        .strftime('%Y-%m-%d %H:%M')

@register.filter(name='is_list')
def is_list(arr):
    return isinstance(arr, list)