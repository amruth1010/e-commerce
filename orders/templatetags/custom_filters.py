from django import template

register = template.Library()

@register.filter(name='currency')
def currency(value):
    """Format the value as currency (INR)"""
    return f'₹{value:.2f}'

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiply value by arg"""
    return value * arg
