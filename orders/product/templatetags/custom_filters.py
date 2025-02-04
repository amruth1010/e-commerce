from django import template

register = template.Library()

@register.filter
def make_range(value):
    """Returns a range of numbers."""
    return range(value)
