# -*- coding: utf-8 -*-

from datetime import datetime

from .models import Party, Politician, Term, Representative


def create_term():
    terms = Term.objects.valid().all()
    if not terms.exists():
        # TODO: doplnit realne datumy
        Term.objects.create(valid_from=datetime(2011, 10, 1), \
                            valid_to=datetime(2014, 10, 1))


PARTIES = [
    (u'VV', u'Věci veřejné'),
    (u'ODS', u'Občanská demokratická strana'),
    (u'ČSSD', u'Česká strana sociálně demokratická'),
    (u'KDU-ČSL', u'Křesťanská a demokratická unie - Československá strana lidová'),
    (u'NEZ', u'Nezávislí'),
    (u'TOP09', u'TOP 09'),
    (u'KSČM', u'Komunistická strana Čech a Moravy'),
    (u'BEZPP', u'Bez politiké příslušnosti'),
]

def import_parties():
    for short, title in PARTIES:
        Party.objects.get_or_create(short=short, title=title)

# stav k listopadu 2012
REPRESENTATIVES = [
    (u'Irena',      u'Brouwerová',  u'VV'),
    (u'Otto',       u'Buš',         u'ODS'),
    (u'Jiří',       u'Částečka',    u'ODS'),
    (u'Petr',       u'Daniš',       u'ČSSD'),
    (u'Ladislav',   u'Denk',        u'KDU-ČSL'),
    (u'Jarmil',     u'Dobeš',       u'NEZ'),
    (u'Jiří',       u'Hruška',      u'TOP09'),
    (u'Tomáš',      u'Jelínek',     u'KDU-ČSL'),
    (u'Milan',      u'Knápek',      u'VV'),
    (u'Miroslav',   u'Krchňák',     u'ČSSD'),
    (u'Petr',       u'Urbánek',     u'ČSSD'),
    (u'Milan',      u'Leckeši',     u'ODS'),
    (u'Bohdan',     u'Mikušek',     u'KDU-ČSL'),
    (u'Milena',     u'Medková',     u'ODS'),
    (u'Karel',      u'Mikuš',       u'TOP09'),
    (u'Vladimír',   u'Místecký',    u'KSČM'),
    (u'Vlastislav', u'Navrátil',    u'TOP09'),
    (u'Vítězslav',  u'Nesvadba',    u'BEZPP'),
    (u'Marek',      u'Netolička',   u'ODS'),
    (u'Zdislava',   u'Odstrčilová', u'KDU-ČSL'),
    (u'Jiří',       u'Pernický',    u'NEZ'),
    (u'Zdeněk',     u'Petroš',      u'BEZPP'),
    (u'Jan',        u'Trčka',       u'ODS'),
    (u'Jiří',       u'Varga',       u'KSČM'),
    (u'Daniel',     u'Vodák',       u'ČSSD'),
]

def import_representatives():
    now = datetime.now()
    term = Term.objects.all()[0]

    for first_name, last_name, party in REPRESENTATIVES:
        politician = Politician.objects.filter(first_name=first_name, \
                                               last_name=last_name)
        if not politician.exists():
            politician = Politician.objects.create(first_name=first_name, \
                                                   last_name=last_name)
        else:
            politician = politician[0]

        representative = Representative.objects.valid()\
                                               .filter(party__short=party, \
                                                       politician=politician, \
                                                       term=term)
        if not representative.exists():
            representative = Representative.objects.create(party=Party.objects.get(short=party), \
                                                           politician=politician, \
                                                           term=term, \
                                                           valid_from=now)
