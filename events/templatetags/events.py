# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django import template

register = template.Library()

@register.simple_tag
def verdikt(data, end="."):
    """
    Slovni vyjadreni vysledku hlasovani u konkretniho bodu.
    """
    tightly = u'těsnou většinou' if data['result_bool'] and data['tightly'] else u''
    yes = u'schválili' if data['result_bool'] else u'neschválili'
    msg = u'Zastupitelé tento bod%s %s%s' % (tightly, yes, end)
    return msg
