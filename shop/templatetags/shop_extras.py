from django import template
register = template.Library()

@register.filter
def average(queryset, field_name):
    values = [getattr(obj, field_name, 0) for obj in queryset]
    if values:
        return sum(values) / len(values)
    return 0