# -*- coding: utf-8 -*-

from django import forms
from django.utils.safestring import mark_safe

from authority.models import Representative, Term
from municipal.models import Decision, ProgrammeItem, Programme
from .models import RepresentativeVote, RepresentativeVoting


class InlineRadioSelect(forms.RadioSelect):
    """
    Humpolacka, ale fungujici, uprava RadioSelectu. Namisto ul-li seznamu
    to bude jen sada labelu a inputu, ktere se v adimnistraci vykresli
    do radku.
    """
    def render(self, name, value, attrs=None, choices=()):
        out = super(InlineRadioSelect, self).render(name, value, attrs, choices)
        out = out.replace('<li>', '').replace('</li>', '').replace('<ul>', '').replace('</ul>', '')
        out = out.replace('<label', '<label style="width:auto;margin-right:20px"')
        return mark_safe(out)


class RepresentativeVoteInlineForm(forms.ModelForm):
    class Meta:
        model = RepresentativeVote

    def __init__(self, *args, **kwargs):
        super(RepresentativeVoteInlineForm, self).__init__(*args, **kwargs)
        choices = self.fields['vote'].choices[1:]
        self.fields['vote'].choices = choices
        self.fields['vote'].widget = InlineRadioSelect(choices=choices)

        # predvyplneni zastupitele podle poradoveho cisla policka v inlajnu
        idx = kwargs.get('prefix', '').split('-')
        idx = idx and idx[-1] and idx[-1].isdigit() and idx[-1] or None
        r = Representative.objects.all()
        if idx is not None and int(idx) < len(r):
            idx = int(idx)
            self.fields['representative'].initial = r[idx].id


class RepresentativeVotingForm(forms.ModelForm):
    term = forms.ChoiceField(label=u"Volební období")
    programme_order = forms.CharField(label=u"Číslo programu")
    item_number = forms.CharField(label=u"Bod programu")

    class Meta:
        model = RepresentativeVoting
        exclude = ('item', )

    def __init__(self, *args, **kwargs):
        super(RepresentativeVotingForm, self).__init__(*args, **kwargs)
        self.fields['order'].widget = forms.TextInput(attrs={'class': 'span1'})
        self.fields['term'].choices = [(i.id, unicode(i)) for i in Term.objects.all()]
        self.fields['term'].widget = forms.Select(choices=self.fields['term'].choices, \
                                                  attrs={'class': 'span6'})
        if self.instance:
            self.fields['term'].initial = self.instance.item.programme.term.id
            self.fields['programme_order'].initial = self.instance.item.programme.order
            self.fields['item_number'].initial = self.instance.item.item

    def clean(self):
        data = self.cleaned_data.copy()

        # 3 policka ve formiku mi definuji konkretni bod programu
        term = Term.objects.get(id=int(data.pop('term')))
        programme = Programme.objects.get(term=term, order=data.pop('programme_order'))
        item = ProgrammeItem.objects.get(programme=programme, item=data.pop('item_number'))
        data['item'] = item.id
        self.cleaned_data['item'] = item.id

        return data


class DecisionInlineForm(forms.ModelForm):
    class Meta:
        model = Decision

    def clean_title(self):
        return Decision.normalize_title(self.cleaned_data.get('title', u''))
