from django import template
import json

register = template.Library()

#Filter usage: {{ var|foo:"bar" }}

@register.filter(name='get_range')
def get_range(number):
    return range(number)

@register.filter(name='get_range2')
def get_range2(number):
    return range(1, number+1)

@register.filter(name='get_page_num')
def get_page_num(item_count, items_per_page):
    page_num = item_count // items_per_page
    if item_count % items_per_page != 0:
        page_num += 1
    return page_num

itprt_status = {
    0: 'Interpreted',
    1: 'Waiting Interpretation',
    2: 'Candidate Waiting',
    3: 'Finding Physician',
}

@register.filter(name='get_interpretation_status')
def get_interpretation_status(status):
    status = int(status)
    return itprt_status.get(status, '-')
