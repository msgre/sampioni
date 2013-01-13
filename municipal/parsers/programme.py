# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

"""
Vyparsuje uzitecne informace z programu jednani zastupitelstva mesta
Valasskeho Mezirici.

Priklad vystupu:

    {'header': {'date': datetime.date(2012, 12, 13),
                'datetime': datetime.datetime(2012, 12, 13, 9, 0),
                'number': u'21',
                'place': u'velká zasedací místnost MěÚ Valašské Meziříčí, budova radnice',
                'time': datetime.time(9, 0),
                'type': u'řádné'},
     'footer': {'date': datetime.date(2012, 12, 5)},
     'items': [{'number': u'1.',
                'proposer': u'Jiří Částečka',
                'title': u'Zahájení - schválení programu - volba ověřovatelů zápisu - volba návrhové komise'},
               {...},
               {'number': u'21.', 'proposer': None, 'title': u'Různé'}]}
"""

import sys
import os
import re
from datetime import datetime, date, time


# --- regexpy
# hlavicka
INVITATION_RE = re.compile(ur'^\s+POZVÁNKA\s*$', re.UNICODE)
TITLE_RE = re.compile(ur'^\s+(\d+)\.\s*(řádné|mimořádné)?\s*zased(á|a)ní Zastupitelstva města', re.UNICODE)
# misto a cas konani v hlavicce
TERM_DATE_RE = re.compile(ur'^\s*Termín\s+zasedání:\s+(\d{1,2})\.\s*(\d{1,2})\.\s+(\d{4})\s*$', re.UNICODE)
PLACE_RE = re.compile(ur'^\s*Místo\s+zasedání:\s+(.+)$', re.UNICODE)
TERM_TIME_RE = re.compile(ur'^\s*Zahájení\s+zasedání:\s+(\d{1,2}):(\d{2})\s+hodin\s*$', re.UNICODE)
# pocatek programu
PROGRAMME_RE = re.compile(ur'^\s*Program:\s$', re.UNICODE)
PROGRAMME_ITEM_RE = re.compile(ur'^(\f)?([\.0-9]+)\s+(.+)$', re.UNICODE)
PROGRAMME_PROPOSER_RE = re.compile(ur'^\s*Předkladatel:(.+)$', re.UNICODE)
# paticka
FOOTER_RE = re.compile(ur'^\s*Valašské\s+Meziříčí\s+(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4}).*$', re.UNICODE)
# strankovani
RE_PAGING = re.compile(ur'^\s{20,}\d+\s*$', re.U)

# --- priblizne pozice radku v dokumentu
# pocet radku z vrsku dokumentu, ve kterych se hleda hlavicka
MAX_HEADER_HEIGHT = 20
# pocet radku ze spodu dokumentu, ve kterych se hleda paticka
MAX_FOOTER_HEIGHT = 20


def parse_header_block(lines):
    """
    Vyparsuje zakladni informace z hlavicky
    """
    data = [line for line in lines[:MAX_HEADER_HEIGHT] if line.strip()]
    if not data or not INVITATION_RE.match(data[0]):
        return None
    out = {'number':None, 'type':None, 'date':None, 'time':None, 'place':None, 'datetime':None}
    for item in data:
        # typ a poradove cislo zastupitelstva
        m = TITLE_RE.match(item)
        if m:
            out['number'] = m.group(1).strip()
            out['type'] = m.group(2).strip()

        # den konani zastupitelstva
        m = TERM_DATE_RE.match(item)
        if m:
            try:
                out['date'] = date(int(m.group(3).strip()), int(m.group(2).strip()), int(m.group(1).strip()))
            except ValueError:
                pass

        # cas konani zastupitelstva
        m = TERM_TIME_RE.match(item)
        if m:
            try:
                out['time'] = time(int(m.group(1).strip()), int(m.group(2).strip()))
            except ValueError:
                pass

        # misto konani zastupitelstva
        m = PLACE_RE.match(item)
        if m:
            out['place'] = m.group(1).strip()

    # poskladani kompletniho datetime objektu
    out['datetime'] = out['date'] and out['time'] and \
                      datetime.combine(out['date'], out['time']) or None

    return out


def find_programme_block(lines):
    """
    Vrati radky ktere popisuji program zastupitelstva.
    """
    top_index = [idx for idx, line in enumerate(lines[:MAX_HEADER_HEIGHT]) \
                 if PROGRAMME_RE.match(line)]
    bottom_index = [idx for idx, line in enumerate(lines[-MAX_FOOTER_HEIGHT:]) \
                    if FOOTER_RE.match(line)]
    if len(top_index) and len(bottom_index):
        return [i for i in lines[top_index[0]+1:-(MAX_FOOTER_HEIGHT-bottom_index[0])] \
                if i.strip()]
    return None


def parse_footer_block(lines):
    """
    Vyparsuje zakladni informace z paticky.

    NOTE: paticka nema moc exaktni format, nekdy se tam objevuji poznamky,
    jindy ne; spokojim se s vyzobnutim udaje o tom, kdy byl program vystaven
    """
    # najdeme pocatek paticky
    bottom_index = [idx for idx, line in enumerate(lines[-MAX_FOOTER_HEIGHT:]) \
                    if FOOTER_RE.match(line)]
    if not len(bottom_index):
        return None

    # vyparsujeme data z ni
    data = [line for line in lines[-(MAX_FOOTER_HEIGHT-bottom_index[0]):] if line.strip()]
    out = {'date':None}
    for item in data:
        # typ a poradove cislo zastupitelstva
        m = FOOTER_RE.match(item)
        if m:
            try:
                out['date'] = date(int(m.group(3).strip()), int(m.group(2).strip()), int(m.group(1).strip()))
            except ValueError:
                pass

    return out


def parse_items(lines):
    """
    Vyparsuje konkretni body programu.
    """
    # pozice bodu
    anchors = [idx for idx, line in enumerate(lines) if PROGRAMME_ITEM_RE.match(line)]

    # syrove bloky po jednotlivych bodech
    blocks = []
    for idx in range(len(anchors)-1):
        blocks.append(lines[anchors[idx]:anchors[idx+1]])
    blocks.append(lines[anchors[idx+1]:])

    # preciznejsi vyparsovani udaju z bloku
    out = []
    for block in blocks:
        data = [i.strip() for i in block if i.strip()]
        if not len(data):
            continue
        item = {'proposer':None, 'number':None, 'title':None}

        # predkladatel
        proposer_found = False
        m = PROGRAMME_PROPOSER_RE.match(data[-1])
        if m:
            item['proposer'] = m.group(1).strip()
            proposer_found = True

        # cislo bodu
        m = PROGRAMME_ITEM_RE.match(data[0])
        item['number'] = m.group(2).strip()

        # titulek bodu
        title = [m.group(3)]
        if proposer_found:
            title.extend(data[1:-1])
        else:
            title.extend(data[1:])
        item['title'] = u" ".join([i.strip() for i in title])
        out.append(item)

    return out


def strip_paging(lines):
    """
    Odstrani z dokumentu radky oznacujici cislo stranky a jmeno dokumentu.
    """
    anchors = [idx for idx, line in enumerate(lines) if RE_PAGING.match(line)]
    return [line for idx, line in enumerate(lines) if idx not in anchors]


def parse_programme(lines):
    """
    Vyparsuje udaje z programu konani zastupitelstva.
    """
    lines = [i.decode('utf-8') for i in lines]
    header = parse_header_block(lines)
    footer = parse_footer_block(lines)
    programme = find_programme_block(lines)
    programme = strip_paging(programme)
    items = parse_items(programme)
    return {'header':header, 'footer':footer, 'items':items}


if __name__ == "__main__":
    # osetreni vstupu z command lajny
    if len(sys.argv) < 2:
        print 'zadej jmeno TXT souboru'
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
    out = parse_programme(lines)
    from pprint import pprint
    pprint(out)
