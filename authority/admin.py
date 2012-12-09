# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Party, Person, Term, Representative

admin.site.register(Party)
admin.site.register(Person)
admin.site.register(Term)
admin.site.register(Representative)
