# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django import forms
from django.utils.safestring import mark_safe

from .models import ProgrammeHTitle, ProgrammeHDescription, ProgrammeItem


class ProgrammeItemInlineForm(forms.ModelForm):
    class Meta:
        model = ProgrammeItem
        fields = ('item', 'title', 'description_orig')

    def __init__(self, *args, **kwargs):
        super(ProgrammeItemInlineForm, self).__init__(*args, **kwargs)
        self.fields['item'].widget = forms.TextInput(attrs={'class': 'span2'})
        self.fields['title'].widget = forms.Textarea(attrs={'rows': '4', 'class':'span12'})

    def clean_item(self):
        return ProgrammeItem.normalize_item(self.cleaned_data.get('item', u''))

    def clean_title(self):
        return ProgrammeItem.normalize_title(self.cleaned_data.get('title', u''))


class ProgrammeHTitleForm(forms.ModelForm):
    """
    Formular pro zadani srozumitelneho titulku k bodu programu.
    """
    class Meta:
        model = ProgrammeHTitle
        fields = ('htitle', )

    def __init__(self, item, *args, **kwargs):
        self.item = item
        super(ProgrammeHTitleForm, self).__init__(*args, **kwargs)
        self.fields['htitle'].widget = forms.Textarea(attrs={'class': 'span12', 'rows': '3'})

    def clean_htitle(self):
        data = self.cleaned_data.get('htitle', '')
        return data and data.strip() or None

    def save(self, *args, **kwargs):
        obj = ProgrammeHTitle.objects.create(htitle=self.cleaned_data['htitle'], \
                                             item=self.item)
        return obj


class ProgrammeHDescriptionForm(forms.ModelForm):
    """
    Formular pro zadani obsahu k bodu programu.
    """
    class Meta:
        model = ProgrammeHDescription
        fields = ('hdescription', )

    def __init__(self, item, *args, **kwargs):
        self.item = item
        super(ProgrammeHDescriptionForm, self).__init__(*args, **kwargs)
        self.fields['hdescription'].widget = forms.Textarea(attrs={'class': 'span12', 'rows': '10'})

    def clean_hdescription(self):
        data = self.cleaned_data.get('hdescription', '')
        return data and data.strip() or None

    def save(self, *args, **kwargs):
        obj = ProgrammeHDescription.objects.create(hdescription=self.cleaned_data['hdescription'], \
                                                   item=self.item)
        return obj
