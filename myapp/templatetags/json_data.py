# -*- coding:utf-8 -*-
import logging
import json
from django import template
logger = logging.getLogger(__name__)


# add filter
register = template.Library()


class JsondataNode(template.Node):
    def __init__(self, nodelist, name):
        self.nodelist = nodelist
        self.name = name

    def render(self, context):
        data = self.nodelist.render(context)
        try:
            logger.debug("jsondata: name=%s data=%r")
            context[self.name] = json.loads(data)
        except Exception as e:
            logger.warn(repr(e), exc_info=True)
            raise template.TemplateSyntaxError(
                'Invalid jsondata: name=%r data=%r' % self.name, data
            )
        return ''


@register.tag("jsondata")
def do_jsondata(parser, token):
    """
    {% jsondata name="person" %}
    {"name": "foo", "age": 10}
    {% endfor %}

    # is equivalent to
    # context["person"] = {"name": "foo", "age": 20}
    """
    nodelist = parser.parse(('endjsondata',))
    tokens = token.split_contents()
    parser.delete_first_token()
    if len(tokens) != 2:
        raise template.TemplateSyntaxError("'%r' tag requires at least 1 arguments." % tokens[0])
    if tokens[1].startswith("name="):
        name = tokens[1][len("name="):]
    name = name.strip("'").strip('"')
    return JsondataNode(nodelist, name)
