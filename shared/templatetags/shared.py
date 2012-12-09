# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django import template

import ttag

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


@register.filter
def key(item, key):
    return item.get(key, None)


class Variable(ttag.helpers.AsTag):
    """
    Vlozi vyraz do kontextu sablony pod zadanym nazvem.

    Priklad:
        {% variable product_variants|numkey:form.variant_id.value as product_variant %}

        V kontextu se objevi promenna {{ product_variant }} jejiz obsah bude
        roven {{ product_variants|numkey:form.variant_id.value }}
    """
    expression = ttag.Arg()

    def output(self, data):
        return data['expression']

register.tag(Variable)
