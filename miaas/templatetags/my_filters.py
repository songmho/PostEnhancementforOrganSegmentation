from django import template

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