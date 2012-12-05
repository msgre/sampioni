# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django import template

register = template.Library()


@register.filter
def emdasher(value):
    """
    Nahradi - za em dash;
    """
    return unicode(value).replace(u'-', u'—')


@register.filter
def endasher(value):
    """
    Nahradi - za en dash;
    """
    return unicode(value).replace(u'-', u'–')


@register.filter
def grammar(count, variants):
    """
    Sklonovadlo.

    Pouziti:
        {{ some_count }}&nbsp;{{ some_count|grammar:"0=hernách,1=herně,?=hernách" }}
    """
    variants = [[y.strip() for y in i.strip().split('=')] for i in variants.split(',')]
    variants = dict([(i[0] == '?' and i[0] or int(i[0]), i[1]) for i in variants])
    for k in sorted(variants.keys()):
        if k == '?':
            return variants[k]
        elif count <= k:
            return variants[k]
