# -*- coding: utf-8 -*-

from rest_framework import serializers

from authority.models import Term
from .models import Programme, ProgrammeItem


class MunicipalSerializer(object):
    """
    TODO: spolecne veci
    """
    def _validate_term(self):
        kwargs = self.context['view'].kwargs
        term = Term.objects.filter(pk=int(kwargs['term']))
        if term.count() != 1:
            raise serializers.ValidationError("Non-existing Term %s" % kwargs['term'])

    def _validate_programme(self):
        kwargs = self.context['view'].kwargs
        programme = Programme.objects.filter(pk=int(kwargs['programme']))
        if programme.count() != 1:
            raise serializers.ValidationError("Non-existing Programme %s" % kwargs['programme'])


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ('id', 'valid_from', 'valid_to', )
        read_only_fields = ('id', )


class ProgrammeSerializer(MunicipalSerializer, serializers.ModelSerializer):
    class Meta:
        model = Programme
        fields = ('id', 'order', 'type', 'date')
        read_only_fields = ('id', )

    def validate(self, attrs):
        self._validate_term()
        return attrs


class ProgrammeItemSerializer(MunicipalSerializer, serializers.ModelSerializer):
    class Meta:
        model = ProgrammeItem
        fields = ('id', 'item', 'title', 'htitle', 'description_orig', 'programme')
        read_only_fields = ('id', )

    def validate(self, attrs):
        self._validate_term()
        self._validate_programme()
        return attrs
