from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_limit_value(dictionary, key):
    return dictionary.get(key, '-')


@register.filter
def get_month_value(dictionary, key):
    return dictionary.get(key, 0)


@register.filter
def get_daily_value(dictionary, key):
    return dictionary.get(key, '-')


@register.filter
def get_daily_value_in_category(dictionary, key):
    return dictionary.get(key, '-')
