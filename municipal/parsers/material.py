# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

"""
Rozparsuje material zastupitelstva Valasskeho Mezirici.

Pouziti:

    f = open('material.txt')
    lines = f.readlines()
    f.close()
    print parse(lines)

Priklad vystupu:

    {
     # spolecne informace
     'number': "20",                                # poradove cislo zasedani zastupitelstva
     'item_number': "1",                            # poradove cislo materialu
     'date': datetime(2012,11,1),                   # datum konani zastupitelstva
     'proposer': "Jiri Castecka",                   # predkladatel materialu
     'processor': "Ing. Zdenek Stuenik",            # kdo material zpracoval
     'multiple': True,                              # flag rikajici, ze v materialu je vice podbodu

     # jednotlive body materialu
     'subitems': [{'title': "Lorem ipsum...",       # nazev bodu
                   'number': "1",                   # cislo bodu
                   'report': "Lorem ipsum...",      # duvodova zprava
                   'attachment': "Lorem ipsum...",  # prilohy
                   'proposal': "Lorem ipsum...",    # navrh usneseni
                   'raw': ["..", "..", ...]},       # syrova data, ze kterych byl bod vyparsovan
                  # dalsi bod...
                  {...}]}
"""

import sys
import os
import re
from datetime import datetime, date, time

# TODO: relativni import, je to mirne modifikovany kod z ../parser.py
from markdownofier import convert_to_markdown

# --- regexpy
# hlavicka
MATERIAL_RE = re.compile(ur'^\s+MATERIÁL\s*$', re.UNICODE)
ITEM_RE = re.compile(ur'^\s+bod\s+č.\s+(\d+)\s*$', re.UNICODE)
NUMBER_RE = re.compile(ur'^Číslo\s+zasedání:\s+(\d+)\.?\s*$', re.UNICODE)
TERM_DATE_RE = re.compile(ur'^Termín\s+zasedání:\s+(\d{1,2})\.\s*(\d{1,2})\.\s+(\d{4})\s*$', re.UNICODE)
PROPOSER_RE = re.compile(ur'^Předkládá:(.+)$', re.UNICODE)
PROCESSOR_RE = re.compile(ur'^(Zpracoval\(a\):)(\s+)(.+)$', re.UNICODE)

# titulky
TITLE_RE = re.compile(ur'^Název:\s+(.+)$', re.UNICODE)
SUBTITLE_RE = re.compile(ur'^(\d+)\.\s+(.+)$', re.UNICODE)

# kotvy v obsahu
REPORT_RE = re.compile(ur'^\s*A\.\s+Důvodová\s+zpráva:\s*$', re.UNICODE)
ATTACHMENT_RE = re.compile(ur'^\s*B\.\s+Přílohy:\s*$', re.UNICODE)
PROPOSAL_RE = re.compile(ur'^\s*C\.\s+Návrh\s+na\s+usnesení:\s*$', re.UNICODE)

# paticka na konci stranky
FOOTER_RE = re.compile(ur'^\s+\D{5,}$')
PAGING_RE = re.compile(ur'^\s+\d+$', re.U)

# limity radku
MAX_HEADER_HEIGHT = 20 # hlavicka by nemela byt delsi nez 20 radku
SUBTITLE_OFFSET   = 15 # titulek nebude od Duvodove zpravy dal nez 15 radku zpet
MAX_FOOTER_HEIGHT = 30 # paticka nebude vyssi nez 30 radku


def parse_header_block(lines):
    """
    Vyparsuje zakladni informace z hlavicky.
    """
    data = [line for line in lines[:MAX_HEADER_HEIGHT] if line.strip()]
    if not data or not MATERIAL_RE.match(data[1]):
        return None
    out = {'item_number':None, 'number':None, 'date':None, 'proposer':None,
           'processor':None}
    processor_line_idx = None
    processor_indent = None
    for idx, item in enumerate(data):
        # cislo bodu
        m = ITEM_RE.match(item)
        if m:
            out['item_number'] = m.group(1).strip()

        # cislo jednani zastupitelstva
        m = NUMBER_RE.match(item)
        if m:
            out['number'] = m.group(1).strip()

        # den konani zastupitelstva
        m = TERM_DATE_RE.match(item)
        if m:
            try:
                out['date'] = date(int(m.group(3).strip()), int(m.group(2).strip()), int(m.group(1).strip()))
            except ValueError:
                pass

        # predkladatel
        m = PROPOSER_RE.match(item)
        if m:
            out['proposer'] = m.group(1).strip()

        # zpracovali
        m = PROCESSOR_RE.match(item)
        if m:
            out['processor'] = [m.group(3).strip()]
            processor_line_idx = idx
            processor_indent = len(m.group(1)) + len(m.group(2))

    # domlasknuti zpracovatelu
    if processor_line_idx and processor_line_idx+1 < len(data):
        for idx in range(processor_line_idx+1, MAX_HEADER_HEIGHT):
            if data[idx].strip() and \
               len(data[idx][:processor_indent].strip()) == 0 :
                out['processor'].append(data[idx].strip())
            else:
                break
        out['processor'] = u" ".join(out['processor'])

    return out


def parse_content(lines):
    """
    Vyparsuje obsah a titulky.
    """
    anchors = [idx for idx, line in enumerate(lines) if REPORT_RE.match(line)]
    subtitles, out = [], []
    for idx in anchors:
        for ydx in range(SUBTITLE_OFFSET):
            m = SUBTITLE_RE.match(lines[idx-ydx])
            if m:
                item = {'title': [m.group(2)], 'number': m.group(1)}
                item['title'].extend(lines[idx-ydx+1:idx-1])
                item['title'] = u" ".join([i.strip() for i in item['title'] if i.strip()])
                subtitles.append(item)
                out.append((idx-ydx, idx-1))
                break
            m = TITLE_RE.match(lines[idx-ydx])
            if m:
                item = {'title': [m.group(1)]}
                item['title'].extend(lines[idx-ydx+1:idx-1])
                item['title'] = u" ".join([i.strip() for i in item['title'] if i.strip()])
                subtitles.append(item)
                out.append((idx-ydx, idx-1))
                break
    if len(anchors) > 1:
        anchors = [(out[i][1], out[i+1][0]) for i in range(len(out)-1)]
        anchors.append((out[-1][1], len(lines)-1))
    else:
        anchors = [(anchors[0], len(lines)-1)]

    # vytvorime bloky po jednotlivych podbodech
    blocks = [lines[anchor[0]:anchor[1]] for anchor in anchors]

    # v kazdem bloku najdeme usek se zpravou, prilohami a navrhem usneseni
    out = []
    for ydx, block in enumerate(blocks):
        report_idx, attachment_idx, proposal_idx = None, None, None
        for idx, line in enumerate(block):
            if REPORT_RE.match(line) and report_idx is None:
                report_idx = idx
            elif ATTACHMENT_RE.match(line) and attachment_idx is None:
                attachment_idx = idx
            elif PROPOSAL_RE.match(line) and proposal_idx is None:
                proposal_idx = idx

        subitem = {'report':None, 'attachment':None, 'proposal':None}
        if report_idx is not None and attachment_idx is not None and \
           proposal_idx is not None:
            # nasli jsme vsechny 3 dulezite useky
            subitem['report'] = convert_to_markdown(block[report_idx+1:attachment_idx])
            subitem['attachment'] = convert_to_markdown(block[attachment_idx+1:proposal_idx])
            subitem['proposal'] = convert_to_markdown(block[proposal_idx+1:])

        subitem['raw'] = block
        subitem.update(subtitles[ydx])
        out.append(subitem)

    return out


def strip_footer(lines):
    """
    Odstrihne paticku stranky, ve ktere se vyskytuje jmeno cloveka, ktery
    material zpracoval.
    """
    #import ipdb; ipdb.set_trace()
    last_idx = len(lines) - 1
    footer_found, footer_idx = False, None

    for idx in range(MAX_FOOTER_HEIGHT):
        line = lines[last_idx-idx].rstrip()
        if not line:
            if footer_found:
                break
            continue
        m = PAGING_RE.match(line)
        if m:
            if footer_found:
                break
            continue
        m = FOOTER_RE.match(line)
        if m:
            footer_found = True
            footer_idx = last_idx-idx

    return lines[:footer_idx] if footer_idx is not None else lines


def parse(lines):
    """
    Rozparsuje material zastupitelstva Valasskeho Mezirici.
    """
    lines = [i.decode('utf-8').rstrip() for i in lines]
    lines = strip_footer(lines)

    out = parse_header_block(lines)
    out['subitems'] = parse_content(lines)
    out['multiple'] = len(out['subitems']) > 1

    return out


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

    out = parse(lines)
    from pprint import pprint
    pprint(out)
