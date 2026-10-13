#!/usr/bin/env python3
"""Report commands and acronyms that are in CCNA.docx but missing from the
master Acronyms.docx / Basic_Configuration_Commands.docx (and the reverse for commands).

Usage:  python3 check_docs_in_sync.py [folder-with-the-docx-files]
Needs only the Python standard library.
"""
import re, sys, zipfile, html, os

folder = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..')

def tables(path):
    xml = zipfile.ZipFile(path).read('word/document.xml').decode('utf8')
    out = []
    for t in re.findall(r'<w:tbl>.*?</w:tbl>', xml, re.S):
        rows = []
        for r in re.findall(r'<w:tr[ >].*?</w:tr>', t, re.S):
            cells = [html.unescape(''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', c))).strip()
                     for c in re.findall(r'<w:tc>.*?</w:tc>', r, re.S)]
            rows.append(cells)
        out.append(rows)
    return out

def cmd_key(text):
    text = text.replace('**', '').strip().lower()
    keep = []
    for tok in text.split():
        if tok[0] in '<[{(' or tok.startswith('{'):
            break
        keep.append(tok)
    return ' '.join(keep)

def commands(path, header_word='Command'):
    found = {}
    for rows in tables(path):
        if rows and rows[0] and rows[0][0].strip().lower().startswith(header_word.lower()):
            for r in rows[1:]:
                if r and r[0] and len(r) > 1 and r[1]:
                    for alt in r[0].split(' / '):
                        found.setdefault(cmd_key(alt), alt.strip())
    return found

def acronyms(path):
    found = {}
    for rows in tables(path):
        if rows and rows[0] and rows[0][0].strip().lower() == 'acronym':
            for r in rows[1:]:
                if r and r[0]:
                    found.setdefault(r[0].strip().lower(), r[0])
    return found

ccna = os.path.join(folder, 'CCNA.docx')
cmds = os.path.join(folder, 'Basic_Configuration_Commands.docx')
acr = os.path.join(folder, 'Acronyms.docx')

c_main, c_master = commands(ccna), commands(cmds)
a_main, a_master = acronyms(ccna), acronyms(acr)

print('== Commands in CCNA.docx but NOT in Basic_Configuration_Commands.docx ==')
miss = [v for k, v in c_main.items() if k not in c_master]
print('\n'.join('  ' + m for m in sorted(miss)) or '  (none)')
print('\n== Commands in Basic_Configuration_Commands.docx but NOT in a CCNA.docx command table (informational: shortcuts and some commands appear in CCNA.docx as bullets) ==')
miss = [v.replace('**', '') for k, v in c_master.items() if k not in c_main]
print('\n'.join('  ' + m for m in sorted(miss)) or '  (none)')
print('\n== Acronyms in CCNA.docx but NOT in Acronyms.docx ==')
miss = [v for k, v in a_main.items() if k not in a_master]
print('\n'.join('  ' + m for m in sorted(miss)) or '  (none)')
print('\n== Acronyms in Acronyms.docx but NOT in CCNA.docx (informational) ==')
miss = [v for k, v in a_master.items() if k not in a_main]
print('\n'.join('  ' + m for m in sorted(miss)) or '  (none)')
