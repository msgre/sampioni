# -*- coding: utf-8 -*-

from django import forms
from .models import RepresentativeVote
from authority.models import Representative


class RepresentativeVoteInlineForm(forms.ModelForm):
    class Meta:
        model = RepresentativeVote

    def __init__(self, *args, **kwargs):
        super(RepresentativeVoteInlineForm, self).__init__(*args, **kwargs)
        choices = self.fields['vote'].choices[1:]
        self.fields['vote'].widget = forms.RadioSelect(choices=choices)
        self.fields['vote'].initial = RepresentativeVote.REPRESENTATIVE_VOTE_YES

        # predvyplneni zastupitele podle poradoveho cisla policka v inlajnu
        idx = kwargs.get('prefix', '').split('-')
        idx = idx and idx[-1] and idx[-1].isdigit() and idx[-1] or None
        r = Representative.objects.all()
        if idx is not None and int(idx) < len(r):
            idx = int(idx)
            self.fields['representative'].initial = r[idx].id
