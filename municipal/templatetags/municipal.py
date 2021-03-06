# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django import template

register = template.Library()

@register.simple_tag
def verdikt(data, key, end="."):
    """
    Slovni vyjadreni vysledku hlasovani u konkretniho bodu programu.
    """
    tightly = u' těsnou většinou' if data[key]['result_bool'] and data[key]['tightly'] else u''
    yes = u'schválili' if data[key]['result_bool'] else u'neschválili'
    msg = u'Zastupitelé tento záměr%s %s%s' % (tightly, yes, end)
    return msg
