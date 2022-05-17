import hashlib

from django import template

register = template.Library()


@register.filter
def md5(str2hash: str) -> str:
    return hashlib.md5(str(str2hash).encode()).hexdigest()


@register.filter
def danger_type_class(type):
    if type == 2:
        return 'text-danger'


@register.simple_tag
def danger_value_class(value, past=False):
    if value and float(value) < 0 and not past:
        return 'text-danger'
