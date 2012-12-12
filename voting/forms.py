# -*- coding: utf-8 -*-

from django import forms
from django.utils.safestring import mark_safe

from authority.models import Representative
from .models import RepresentativeVote


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
        self.fields['vote'].widget = InlineRadioSelect(choices=choices)
        self.fields['vote'].initial = RepresentativeVote.REPRESENTATIVE_VOTE_YES

        # predvyplneni zastupitele podle poradoveho cisla policka v inlajnu
        idx = kwargs.get('prefix', '').split('-')
        idx = idx and idx[-1] and idx[-1].isdigit() and idx[-1] or None
        r = Representative.objects.all()
        if idx is not None and int(idx) < len(r):
            idx = int(idx)
            self.fields['representative'].initial = r[idx].id
