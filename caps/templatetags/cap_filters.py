from django import template
import json

register = template.Library()

@register.filter

def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def to_json(value):
    # Converts python objects into JSON objects
    # for the buyout modal
    return json.dumps(value)