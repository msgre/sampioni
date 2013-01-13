# -*- coding: utf-8 -*-

"""
TODO:
- budu nejak resit zalamovani odstavcu?
- na cem si vytluce hubu
    - 5, slozity dokument
    - 7, nejaky slozity dokument
    - 11, v druhem bloku orizne obsah zleva
"""

import re

MATERIALY_BEGIN_RE = re.compile(ur'^\s*A.\s*Důvodová zpráva:?\s*$')
MATERIALY_END_RE = re.compile(ur'^\s*B.\s*Přílohy:?\s*$')


def get_description(lines):
    """
    Najde popis v materialu.

    Vysvetleni: hleda usek mezi nadpisem "A. Duvodova zprava" a "B. Prilohy".
    Vsecko ostatni me nezajima, resim to na webu jinak (vetsinou tyto informace
    mam z jinych zdroju).
    """
    # najdeme zacatek obsahu
    begin = [idx for idx, l in enumerate(lines) if MATERIALY_BEGIN_RE.match(l)]
    if not begin:
        raise Neco(u'Nepodařilo se mi nalézt počátek bloku s obsahem.')
    begin = begin[0]

    # najdeme konec obsahu
    end = [idx for idx, l in enumerate(lines) if MATERIALY_END_RE.match(l)]
    if not end:
        raise Neco(u'Nepodařilo se mi nalézt konec bloku s obsahem.')
    end = end[0]

    # vyzobneme si obsah
    return lines[begin+1:end]


PAGING_RE = re.compile(r'^\s{30,}\d+\s*$')

def get_blocks(lines):
    """
    Rozdeli obsah podle stranek.

    Vysvetleni: formatovani textu se po prechodu na dalsi stranku casto zmeni.
    Je proto treba text rozdelit na bloky podle stranek a formatovani pak
    nad nimi resit samostatne.
    """
    # nalezneme v obsahu cisla stranek
    page_marks = [idx for idx, l in enumerate(lines) if PAGING_RE.match(l)]

    # rozdelime obsah na bloky podle stranek
    blocks, from_pm = [], 0
    for pm in page_marks:
        blocks.append(lines[from_pm:pm])
        from_pm = pm + 1
    blocks.append(lines[from_pm:])
    blocks = [i for i in blocks if len(i)]

    return blocks


INDENT_RE = re.compile(r'^(\s+)\S.+$')

def align_block(block):
    """
    V zadanem bloku nalezne nejmensi odsazeni od leveho kraje a pak o nej
    kazdy z radku zkrati.
    """
    indents = [len(INDENT_RE.match(l).group(1)) for l in block if INDENT_RE.match(l)]
    min_indent = [i for i in indents if i > 0]
    min_indent = min(min_indent) if min_indent else 0
    return [i[min_indent:] if not i[:min_indent].strip() else i for i in block]


HEADINGS_RE = re.compile(r'^A\.\d+\s+(.+)$')

def format_headings(block, markdown_prefix='###'):
    """
    Hleda v obsahu nadpisy typu "A.0 Shrnuti", "A.1 Popis opatreni", apod
    a naformatuje je jakozto Markdown nadpisy.
    """
    out = []
    for idx, line in enumerate(block):
        m = HEADINGS_RE.match(line)
        if m:
            out.append(u'%s %s' % (markdown_prefix, m.group(1)))
            if idx+1 < len(block) and block[idx+1].strip():
                out.append('')
        else:
            out.append(line)
    return out


LISTS_RE = re.compile(ur'^(\s*)(-|−)([^-−].+)$')

def format_lists(block):
    """
    Najde a preformatuje odrazkove seznamy.
    """
    bullets = {idx: len(LISTS_RE.match(l).group(1)) \
               for idx, l in enumerate(block) if LISTS_RE.match(l)}
    levels = {level:idx for idx, level in enumerate(sorted(set(bullets.values())))}

    item, item_level, bullet_level, out = False, 0, 0, []
    for idx, line in enumerate(block):
        if idx in bullets:
            bullet_level = bullets[idx]
            item_level = levels[bullet_level]
            if not item and idx > 0 and len(block[idx-1].strip()):
                out.append('')
            item = True
        elif item and \
             ((bullet_level and len(line[:bullet_level].strip())) or \
              (bullet_level == 0 and not len(line.strip()))):
            item = False
            if idx+1 < len(block) and len(block[idx+1].strip()):
                out.append('')

        if item:
            if idx in bullets:
                m = LISTS_RE.match(line)
                out.append("%s* %s" % (u' '*(item_level*4), m.group(3).strip()))
            else:
                out.append(u"%s%s" % (u' '*((item_level*4)+2), line[bullet_level:].strip()))
        else:
            out.append(line)

    return out


# 1. nebo 1)  ale nenasleduje zatim 1.2 (aby to nechytalo datumy na zacatku radku)
NUMB_LIST_RE = re.compile(ur'^(\s*)(\d{,2}(\.|\)))(?!\s*\d+\.\d*\d+)(.+)$')

def format_numb_list(block):
    """
    Najde a preformatuje ciselne seznamy.
    """
    bullets = {idx: len(NUMB_LIST_RE.match(l).group(1)) \
               for idx, l in enumerate(block) if NUMB_LIST_RE.match(l)}
    levels = {level:idx for idx, level in enumerate(sorted(set(bullets.values())))}

    item, item_level, bullet_level, out = False, 0, 0, []
    for idx, line in enumerate(block):
        if idx in bullets:
            bullet_level = bullets[idx]
            item_level = levels[bullet_level]
            if not item and idx > 0 and len(block[idx-1].strip()):
                out.append('')
            item = True
        elif item and \
             ((bullet_level and len(line[:bullet_level].strip())) or \
              (bullet_level == 0 and not len(line.strip()))):
            item = False
            if idx+1 < len(block) and len(block[idx+1].strip()):
                out.append('')

        if item:
            if idx in bullets:
                m = NUMB_LIST_RE.match(line)
                out.append("%s1. %s" % (u' '*(item_level*4), m.group(4).strip()))
            else:
                out.append(u"%s%s" % (u' '*((item_level*4)+3), line[bullet_level:].strip()))
        else:
            out.append(line)

    return out


MULTIPLE_NEWLINES_RE = re.compile('\n{3,}')

def join_blocks(blocks):
    """
    Spoji bloky (stranky) do jedineho textu.
    """
    # odstranime prazdne radky ze zacatku a konce bloku
    temp = []
    for block in blocks:
        _block = u'\n'.join(block).strip().split('\n')
        temp.append(_block)

    prev_block = None
    out = []
    for block in temp:
        if not prev_block:
            out.append(u'\n'.join(block))
            prev_block = block
            continue
        if prev_block and prev_block[-1] and prev_block[-1][0] == ' ':
            block.insert(0, '')
        out.append(u'\n'.join(block))

    _out = u'\n'.join(out)
    return MULTIPLE_NEWLINES_RE.sub('\n\n', _out)


def convert_to_markdown(lines):
    """
    Prozene nahrubo vyparsovany text z PDFka nasimi filtry, ktere se jej
    snazi pripodobnit markdown syntaxi. Neni to ale optimalni, ne vzdycky
    to vyjde.
    """
    # description = get_description(lines)
    blocks = get_blocks(lines)
    out = []
    for block in blocks:
        item = align_block(block)
        item = format_headings(item)
        item = format_lists(item)
        item = format_numb_list(item)
        out.append(item)
    return join_blocks(out)
