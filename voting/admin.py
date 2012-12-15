# -*- coding: utf-8 -*-

import re

from django import forms
from django.utils import simplejson
from django.http import HttpResponse
from django.contrib import admin
from django.conf.urls import patterns, url
from django.template.defaultfilters import slugify

import dateutil.parser

from authority.models import Term, PersonSynonym
from municipal.models import Programme, ProgrammeItem
from shared.utils import replace_multiple_whitechars
from .models import RepresentativeVoting, RepresentativeVote, PublicVote
from .forms import RepresentativeVoteInlineForm, DecisionInlineForm, RepresentativeVotingForm
from .parser import parse
from municipal.models import Decision


class RepresentativeVoteInline(admin.TabularInline):
    extra = 25
    max_num = 25
    model = RepresentativeVote
    form = RepresentativeVoteInlineForm

class DecisionInline(admin.StackedInline):
    extra = 0
    model = Decision
    form = DecisionInlineForm


ITEM_RE = re.compile(r'^([\. 0-9]+).*')
CONFUSED_RE = re.compile(r'zmatecne')

class ParserError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg).encode('utf-8')


class RepresentativeVotingAdmin(admin.ModelAdmin):
    inlines = [
        DecisionInline,
        RepresentativeVoteInline,
    ]
    form = RepresentativeVotingForm
    save_on_top = True
    fieldsets = (
        (None, {
            'fields': ('term', 'programme_order', 'item_number', 'order', 'description', 'confused')
        }),
    )
    list_display = ('item', 'order', 'confused')
    list_filter = ('item__programme__term', 'item__programme', 'confused')
    ordering = ('item__programme__created', 'order', )

    def save_model(self, request, obj, form, change):
        obj.item = ProgrammeItem.objects.get(id=form.cleaned_data['item'])
        obj.save()

    def get_urls(self):
        urls = super(RepresentativeVotingAdmin, self).get_urls()
        admin_urls = patterns('',
            (r'^parse/$', self.admin_site.admin_view(self.parse))
        )
        return admin_urls + urls

    def parse(self, request):
        """
        TODO:
        """
        content = request.POST.get('voting-content', '')
        voting = {'error': True}
        if content and len(content.strip()):
            try:
                raw = parse(content.encode('utf-8').split('\n'))
            except:
                pass
            try:
                voting = self.neco(raw)
            except ParserError as e:
                voting['errors'] = e.msg

        return HttpResponse(simplejson.dumps(voting), mimetype="application/json")

    def neco(self, data):
        """
        TODO:
        """

        if len(data) != 1:
            # vyparsovalo se vice nez jen jedno hlasovani
            return # TODO:

        data = data[0]

        # nalezeni volebniho obdobi
        date = dateutil.parser.parse(data['datetime'])
        term = Term.objects.valid(date)
        if len(term) != 1:
            raise ParserError(u'Pro datum %s se nepodařilo najít volební období.' % date)
        term = term[0]

        # nalezeni programu zastupitelstva
        programme = Programme.objects.filter(term=term, order=data['session'])
        if len(programme) != 1:
            raise ParserError(u'Nepodařil se najít program č.%i pro volební období %s.' % (data['session'], date))
        programme = programme[0]

        # nalezeni bodu v programu zastupitelstva
        m = ITEM_RE.search(data['title'])
        if not m:
            raise ParserError(u'Nepodařilo se zjistit číslo projednávaného bodu z titulku %s.' % (data['title'], ))

        item = ProgrammeItem.normalize_item(m.group(1))
        pitem = ProgrammeItem.objects.filter(item=item, programme=programme)
        if len(pitem) != 1:
            raise ParserError(u'Nepodařil se najít projednávaný bod %s v programu %s.' % (item, programme))
        pitem = pitem[0]

        # slo o zmatecne jednani?
        confused = bool(CONFUSED_RE.search(slugify(data['note']).lower()))

        # zakladni sada hodnot k hlasovani
        out = {
            'term': term.id,
            'programme_order': programme.order,
            'item_number': pitem.item,
            'order': data['voting_number'].strip(),
            'description': data['note'],
            'confused': confused,
            'voting': {}
        }

        # zpracovani vlastniho hlasovani zastupitelu
        errors = []
        for vote in data['peoples']:
            ps = PersonSynonym.objects.filter(nick=replace_multiple_whitechars(vote['man']))
            if not ps.exists():
                ps = PersonSynonym.objects.create(nick=vote['man'])
            else:
                ps = ps[0]

            if not ps.person:
                errors.append(u'Neznámý identifikátor %s. Přiřaď k němu v administrici konkrétního člověka a pak spusť parser znovu.' % (vote['man']))
                continue

            representatives = ps.person.representatives.filter(term=term)
            if len(representatives) != 1:
                if len(representatives) > 1:
                    errors.append(u'K identifikátoru %s je přiřazeno více ruzných zastupitelů: %s' % (vote['man'], list(representatives)))
                else:
                    errors.append(u'K identifikátoru %s není přiřazena žádný zastupitel.' % (vote['man'], ))
                continue

            _vote = RepresentativeVote.parse(vote['vote'])
            if not _vote:
                errors.append(u'Neznámý typ hlasu: %s' % _vote)
                continue

            out['voting'][representatives[0].id] = _vote

        if errors:
            raise ParserError(u'Chyby během parsování hlasů: %s' % '\n'.join(errors))

        return out


admin.site.register(RepresentativeVoting, RepresentativeVotingAdmin)
admin.site.register(PublicVote)
