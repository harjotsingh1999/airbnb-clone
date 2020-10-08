from django import template

register = template.Library()


@register.filter()
def capitalize_filter(value):
    print(value)
    return value.capitalize()
