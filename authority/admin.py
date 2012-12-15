# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Party, Person, Term, Representative, PersonSynonym


class PersonSynonymAdmin(admin.ModelAdmin):
    list_display = ('nick', 'person', )
    list_editable = ('person', )


admin.site.register(Party)
admin.site.register(Person)
admin.site.register(PersonSynonym, PersonSynonymAdmin)
admin.site.register(Term)
admin.site.register(Representative)
