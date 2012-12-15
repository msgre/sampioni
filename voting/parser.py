# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

"""
TODO:
- pridavam odstranovac strankovani a hlasovani_*
- volnejsi regexp na vytazeni datumu/casu z titulku
- podrobnejsi parsovani poznamky v paticce
    - nyni z tama vytahuju kod bodu programu
    - +poznamku (nekdy to je pekny maras!)


pdftotext -layout -nopgbrk -enc UTF-8 -q hlasovani_20101216.pdf
http://bit.ly/barcamp-vim
    fuzzyfinder
    ma nastaveno ukladani kdyz ztrati focus
    nerdcommander
"""

import sys
import re
import os
from pprint import pprint
from datetime import datetime

from django.utils.dateformat import format

# dulezite kotvy v dokumentu, kterych se chytam
ANCHOR_RE = re.compile(ur'(\d+)\.\s*(řádné|mimořádné)?\s*zased(á|a)ní Zastupitelstva města', \
                       re.UNICODE)
DELIMITER_RE = re.compile(ur'_{10,}', re.UNICODE)
VOTE_RESULT_RE = re.compile(ur'HLASOVÁNÍ č.\s*([.0-9 ]+)\s*-\s*(NESCHVÁLENO|SCHVÁLENO)')
NUMBER_AND_VOTE_RE = re.compile(ur'(\d+)\s*(.+)')

# format datumu uvnitr
DATE_FORMAT = '%d.%m.%Y %H:%M:%S'
DATE_FORMAT_ALT = '%d.%m.%Y'

# dulezite pozice v radku s hlasovanim, napr:
# ----------------------------------------------------------------------
# 0         1         2         3         4         5         6
# 0123456789012345678901234567890123456789012345678901234567890123456789
# ----------------------------------------------------------------------
#  PhDr. Ladislav Baletka                   ČSSD       11 Nepřítomen

VOTES_NAME_POS = 40
VOTES_PARTY_POS = 52
VOTES_PEOPLE_LIMIT = 2

# Referencni vstup hlasovani, ke kteremu se vztahuji komentare ve funkcich:
#
#                  36. řádné zasedání Zastupitelstva města
#                          předsedá: Jiří Částečka
#                         HLASOVÁNÍ č. 1 - SCHVÁLENO
#                             19.11.2009 9:11:16
#                          1. 1. Schválení programu
#   ______________________________________________________________________
#     Ing. Petr Daniš                          ČSSD       11 Pro
#     Ing. Jaroslav Bernkopf                   ODS        10 Pro
#     Ing. Irena Brouwerová                    ODS        9   Pro
#     Jiří Částečka                            ODS        2   Pro
#     MVDr. Jarmil Dobeš                       NEZ        19 Pro
#     MUDr. Libuše Dvořáková                   KDU-ČSL    18 Nehlasoval
#     Ing. Tomáš Jelínek                       KDU-ČSL    17 Pro
#     Ing. Josef Kalus                         KSČM       34 Pro
#     Mgr. Milan Kardoš                        NEZ        20 Pro
#     MUDr. Miroslav Krchňák                   ČSSD       12 Pro
#     Jiří Nauš                                ODS        26 Pro
#     Mgr. Dagmar Lacinová                     ČSSD       1   Pro
#     MUDr. Milan Leckeši                      ODS        7   Nehlasoval
#     Karel Mikuš                              SNK        25 Pro
#     Ing. Bohdan Mikušek                      KDU-ČSL    27 Pro
#     Vladimír Místecký                        KSČM       22 Pro
#     Vlastislav Navrátil                      TOP 09     24 Pro
#     Bc. Vítězslav Nesvadba                   KSČM       21 Nehlasoval
#     Ing. Marek Netolička                     ODS        6   Pro
#     Ing. Jan Odstrčil                        ODS        5   Nehlasoval
#     Mgr. Jiří Pernický                       NEZ        3   Pro
#     Mgr. Zdeněk Petroš                       ČSSD       13 Pro
#     Mgr. Jan Trčka                           ODS        4   Pro
#     Ing. Daniel Vodák                        ČSSD       14 Pro
#     Ing. Josef Vrátník                       KDU-ČSL    15 Pro
#   ______________________________________________________________________
#   Ke schválení bylo potřeba 13 hlasů
#   Celkem zastupitelů: 25
#   Pro: 21 (84%) Proti: 0 (0%) Zdrželo se: 0 (0%)       Nehlasoval: 4 (16%)
#   Hlasování o navržených změnách programu.


def sh_escape(s):
   """
   Escape jmena souboru (soubory ze zastupitelstva obsahuji maras znaky).
   """
   return s.replace("(","\\(").replace(")","\\)").replace(" ","\\ ")


def convert_pdf(pdf_filename):
    """
    Zavola externi program pdftotext a prevede zadane PDFko do formatovaneho
    TXT vystupu.

    Vraci cestu k vystupnimu TXT souboru.
    """
    # prevod PDF na txt
    txt_filename = "%s.txt" % os.path.splitext(pdf_filename)[0]
    os.system('pdftotext -layout -nopgbrk -enc UTF-8 -q  %s' % sh_escape(pdf_filename))
    return txt_filename


def parse_head(block):
    """
    Vytahne informace z "hlavicky" hlasovani, napr:

        {'chairman': u'Jiří Částečka',
         'datetime': '2008-01-02T10:30:00.000123',
         'result': u'SCHVÁLENO',
         'session': 36,
         'title': u'1. 1. Schválení programu',
         'voting_number': u'1 '}
    """
    out = {}
    m = ANCHOR_RE.search(block[0])
    out['session'] = int(m.group(1))
    out['chairman'] = block[1][block[1].find(u':')+1:].strip()
    m = VOTE_RESULT_RE.search(block[2])
    voting_number, result = m.groups()
    out['voting_number'], out['result'] = voting_number, result
    try:
        out['datetime'] = format(datetime.strptime(block[3].strip(), DATE_FORMAT), "c")
    except ValueError:
        out['datetime'] = format(datetime.strptime(block[3].strip(), DATE_FORMAT_ALT), "c")
    out['title'] = block[4].strip()
    return out


RE_NOTE_CODE = re.compile(r'(Z\s+\d+/\d+)')

def parse_tail(block):
    """
    TODO:

    Vytahne informaci z paticky hlasovani, napr:

        {'note': u'Hlasování o navržených změnách programu.'}


    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/01
    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/23, bod 1.
    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/23, bod 2.
    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/24, bod 1.
    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/24, bod 2.
    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/24, bod 3. o navrženém předsedovi Investičního výboru
    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/24, bod 3. o navrženém předsedovi Investičního výboru
    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/24, bod 3. o navrženém předsedovi Finančního výboru
    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/24, bod 3. o navrženém předsedovi Bc. Vítězslavu
    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/24, bod 3. o navrženém předsedovi Sociálně zdravotního
    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/24, bod 3. o navrženém předsedovi Výboru školství Mgr.
    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/24, bod 3. o navrženém předsedovi Výboru kultury Ing.
    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/24, bod 3. o navrženém předsedovi Výboru sportu a
    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/24, bod 3. o navrženém předsedovi Výboru životního
    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/24, bod 3. o navrženém předsedovi Dopravního výboru
    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/24, bod 3. o navrženém předsedovi Výboru pro územní
    ./hlasovani_20061116.txt:Hlasování o usnesení Z 2/24, bod 3. o navrženém předsedovi Výboru správy majetku
    ./hlasovani_20061116.txt:Hlasování o usneseních Z 2/26 až Z 2/37
    ./hlasovani_20061212.txt:Hlasování o usnesení č. Z 3/01
    ./hlasovani_20061212.txt:Hlasování o usnesení č. Z 3/4
    ./hlasovani_20061212.txt:Hlasování o usnesení č. Z 3/21, bod 1., schválení žádosti č. 196
    ./hlasovani_20061212.txt:Hlasování o usnesení č. Z 3/21, bod 2., protinávrh - schválení žádosti č. 194
    ./hlasovani_20061212.txt:Hlasování o usnesení č. Z 3/21, bod 2., neschválení žádosti č. 194
    ./hlasovani_20061212.txt:Hlasování o usnesení č. Z 3/21, bod 2., neschválení žádosti č. 197
    ./hlasovani_20061212.txt:Hlasování o usnesení č. Z 3/21, bod 3
    ./hlasovani_20070125.txt:Hlasování o usnesení č. Z 4/32 bod 3.
    ./hlasovani_20070308.txt:Hlasování o usnesení č. Z 5/04 dle upraveného návrhu
    ./hlasovani_20070308.txt:Hlasování o usnesení č. Z 5/04, přiřazení částky ve výši 10 tis. Kč oddílu

    """
    line = block[-1].strip()
    codes = [i.split(u'/') for i in RE_NOTE_CODE.findall(line)]
    codes_note = ''
    if codes:
        parts = line.split(u'/'.join(codes[-1]))
        if len(parts) > 1:
            codes_note = parts[-1].strip().strip(',')
    codes = [u"%s/%02i" % (i[0], int(i[1])) for i in codes]
    return {
        'note': line,
        'codes': codes,
        'codes_note': codes_note
    }


def parse_votes(peoples):
    """
    Textovy blok s hlasovanim lidi prevede do strukturovanejsi podoby.

    Vstup:

       ['Ing. Petr Daniš                          ČSSD       11 Pro',
        'Ing. Jaroslav Bernkopf                   ODS        10 Pro',
        'MUDr. Libuše Dvořáková                   KDU-ČSL    18 Nehlasoval',
        'Ing. Josef Kalus                         KSČM       34 Pro']

    Vystup:

        [{'man': u'Ing. Petr Daniš',
          'number': 11,
          'party': u'ČSSD',
          'vote': u'Pro'},
         {'man': u'Ing. Jaroslav Bernkopf',
          'number': 10,
          'party': u'ODS',
          'vote': u'Pro'},
         {'man': u'MUDr. Libuše Dvořáková',
          'number': 18,
          'party': u'KDU-ČSL',
          'vote': u'Nehlasoval'},
         {'man': u'Ing. Josef Kalus',
          'number': 34,
          'party': u'KSČM',
          'vote': u'Pro'}]

    """
    out = []
    if len(peoples) < VOTES_PEOPLE_LIMIT:
        return out
    for line in peoples:
        rec = {}
        rec['man'] = line[:VOTES_NAME_POS].strip()
        rec['party'] = line[VOTES_NAME_POS:VOTES_PARTY_POS].strip()
        m = NUMBER_AND_VOTE_RE.search(line[VOTES_PARTY_POS:])
        number, vote = m.groups()
        rec['number'], rec['vote'] = int(number), vote
        out.append(rec)
    return out


def parse_block(block):
    """
    Parser jednoho bloku s hlasovanim. Vyzobne veskere zajimave informace a
    vrati je v podobe slovniku.

    Vystup:

        {'chairman': u'Jiří Částečka',
         'datetime': '2008-01-02T10:30:00.000123',
         'note': u'Hlasování o navržených změnách programu.',
         'peoples': [{'man': u'Ing. Petr Daniš',
                      'number': 11,
                      'party': u'ČSSD',
                      'vote': u'Pro'},
                     {'man': u'Ing. Jaroslav Bernkopf',
                      'number': 10,
                      'party': u'ODS',
                      'vote': u'Pro'},
                     {'man': u'MUDr. Libuše Dvořáková',
                      'number': 18,
                      'party': u'KDU-ČSL',
                      'vote': u'Nehlasoval'},
                     {'man': u'Ing. Josef Kalus',
                      'number': 34,
                      'party': u'KSČM',
                      'vote': u'Pro'}],
         'result': u'SCHVÁLENO',
         'session': 36,
         'title': u'1. 1. Schválení programu',
         'voting_number': u'1 '}
    """
    # vyzobneme informace pred a po seznamu hlasovani lidi
    out = parse_head(block)
    out.update(parse_tail(block))
    # vyzobneme hlasovani konkretnich lidi
    delimiters = [i for i, n in enumerate(block) if DELIMITER_RE.search(n)]
    if len(delimiters) == 2:
        peoples = [n.strip() \
                   for n in block[delimiters[0]+1:delimiters[1]] \
                   if n.strip()]
    else:
        # blok ma divny format, pravdepodobne neobsahuje informace o hlasovani
        peoples = []
    out['peoples'] = parse_votes(peoples)
    return out


RE_PAGING = re.compile(ur'^\s+Stránka\s+\d+', re.U)
RE_UNDER_PAGING = re.compile(ur'^\s{20,}', re.U)

def strip_paging(lines):
    """
    Odstrani z dokumentu radky oznacujici cislo stranky a jmeno dokumentu.
    """
    anchors = [idx for idx, line in enumerate(lines) if RE_PAGING.match(line)]
    anchors2 = [idx for idx, line in enumerate(lines) if RE_UNDER_PAGING.match(line) and idx - 1 in anchors]
    return [line for idx, line in enumerate(lines) if idx not in anchors and idx not in anchors2]


def parse(_lines):
    """
    Hlavni fce, ktera se postara o rozparsovani celeho vystupu z hlasovani.
    Vrati seznam slovniku, co slovnik to vystup z fce parse_block.
    """
    out = []
    lines = [i.decode('utf-8') for i in _lines]
    lines = strip_paging(lines)
    anchors = [i for i, n in enumerate(lines) if ANCHOR_RE.search(n)]
    if len(anchors) > 1:
        for idx in range(len(anchors) - 1):
            block = [i for i in lines[anchors[idx]:anchors[idx+1]] if i.strip()]
            out.append(parse_block(block))
        block = [i for i in lines[anchors[idx+1]:] if i.strip()]
        out.append(parse_block(block))
    else:
        block = [i for i in lines[anchors[0]:] if i.strip()]
        out.append(parse_block(block))
    return out


def process_document(pdf_filename):
    """
    TODO:
    """
    # prevod PDF na txt
    txt_filename = convert_pdf(pdf_filename)

    # otevreni souboru a jeho parsovani
    f = open(txt_filename)
    lines = f.readlines()
    f.close()

    return parse(lines)


if __name__ == "__main__":
    # osetreni vstupu z command lajny
    if len(sys.argv) < 2:
        print 'zadej jmeno PDFka jako parametr'
        sys.exit()
    if not os.path.exists(sys.argv[1]):
        print '%s neexistuje' % sys.argv[1]
        sys.exit()

    # vypsani jmena souboru, ktery parsujeme
    print '###########', sys.argv[1]

    # otevreni souboru a jeho parsovani
    f = open(sys.argv[1])
    lines = f.readlines()
    f.close()
    out = parse(lines)
    pprint(out)
