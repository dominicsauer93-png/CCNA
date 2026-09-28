"""Build the OneNote copy-paste page from a Claude Docs HTML export of the SOPs doc.

Usage: python3 sops/build_onenote.py <export.json|export.html>
  export.json = the raw export tool result ({"data": {"bytes_b64": ...}}); a plain .html fragment also works.
Writes sops/Network_SOPs_OneNote.html: one card per OneNote page, each with a "Copy this page" button,
and sops/onenote_pages.json: the same pages for Add-SOPsToOneNote.ps1 (Microsoft Graph upload).
"""
import base64
import html as H
import json
import os
import re
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Network_SOPs_OneNote.html")
PAGES_JSON = os.path.join(os.path.dirname(OUT), "onenote_pages.json")
START_PAGES = ("SOP list", "Page template")


def load(path):
    raw = open(path, encoding="utf-8").read()
    if raw.lstrip().startswith("{"):
        return base64.b64decode(json.loads(raw)["data"]["bytes_b64"]).decode("utf-8")
    return raw


def inline_styles(h):
    h = re.sub(r' · <span data-atom="mention"[^>]*>[^<]*</span>', "", h)
    h = h.replace("<table>", '<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;border:1px solid #999;">')
    h = h.replace("<th>", '<th style="background:#DCE6F1;text-align:left;border:1px solid #999;">')
    h = h.replace("<td>", '<td style="border:1px solid #999;vertical-align:top;">')
    h = h.replace("<pre>", '<pre style="font-family:Consolas,monospace;font-size:10pt;background:#F2F2F2;padding:8px;">')
    h = h.replace("<code>", '<code style="font-family:Consolas,monospace;font-size:10pt;background:#F2F2F2;">')
    return h


def split_pages(h):
    pages, section = [], None
    for part in re.split(r"(?=<h[123][ >])", h):
        m = re.match(r"<h([123])[^>]*>(.*?)</h\1>", part, re.S)
        if not m or m.group(1) == "1":
            continue
        title = re.sub("<[^>]+>", "", m.group(2))
        if m.group(1) == "2":
            section = title
            if title in START_PAGES:
                pages.append({"section": "Start here", "title": title, "html": part})
            continue
        pages.append({"section": section, "title": title, "html": part})
    return pages


def render(pages):
    sections, nav, cards, last = [], [], [], None
    for i, pg in enumerate(pages):
        if pg["section"] != last:
            last = pg["section"]
            sections.append(last)
            nav.append(f'<li class="sec">{H.escape(last)}</li>')
        nav.append(f'<li><a href="#p{i}">{H.escape(pg["title"])}</a></li>')
        cards.append(
            f'<section class="card" id="p{i}"><div class="bar"><span class="where">OneNote section: '
            f'<b>{H.escape(pg["section"])}</b> &nbsp;·&nbsp; Page: <b>{H.escape(pg["title"])}</b></span>'
            f'<button onclick="copyPage(\'c{i}\',this)">Copy this page</button></div>'
            f'<div class="content" id="c{i}">{pg["html"]}</div></section>'
        )
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Network SOPs</title>
<style>
body{{font-family:Calibri,Arial,sans-serif;font-size:11pt;background:#f4f5f7;color:#1a1a1a;margin:0;padding:16px;}}
.wrap{{max-width:1000px;margin:0 auto;}}
.how{{background:#fff;border-left:4px solid #2E74B5;padding:12px 16px;margin-bottom:16px;}}
.how ol{{margin:6px 0 0 18px;padding:0;}}
nav{{background:#fff;padding:12px 16px;margin-bottom:16px;}}
nav ul{{list-style:none;padding:0;margin:0;columns:2;}} nav li{{padding:2px 0;}}
nav li.sec{{font-weight:bold;margin-top:8px;color:#2E74B5;}}
.card{{background:#fff;margin:0 0 20px;padding:0 16px 16px;border:1px solid #ddd;overflow-x:auto;}}
.bar{{position:sticky;top:0;background:#fff;display:flex;justify-content:space-between;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #eee;flex-wrap:wrap;}}
.where{{font-size:10pt;color:#555;}}
button{{background:#2E74B5;color:#fff;border:0;padding:8px 14px;font-size:11pt;cursor:pointer;border-radius:4px;}}
button.done{{background:#2e7d32;}}
@media (max-width:600px){{nav ul{{columns:1;}}}}
</style></head><body><div class="wrap">
<div class="how"><b>How to move these into OneNote</b><ol>
<li>In OneNote, make a notebook <b>Network SOPs</b> with these sections: {", ".join(H.escape(s) for s in sections)}.</li>
<li>Click <b>Copy this page</b> on a card below.</li>
<li>In OneNote, add a new page in the section shown on the card, click in the page body and press <b>Ctrl+V</b>. Type the page name from the card as the title.</li>
<li>Repeat for each card ({len(pages)} pages).</li></ol></div>
<nav><ul>{"".join(nav)}</ul></nav>
{"".join(cards)}
</div>
<script>
function copyPage(id,btn){{
  var el=document.getElementById(id), r=document.createRange(), s=window.getSelection();
  s.removeAllRanges(); r.selectNodeContents(el); s.addRange(r);
  var ok=false; try{{ok=document.execCommand('copy');}}catch(e){{}}
  s.removeAllRanges();
  btn.textContent=ok?'Copied: paste into OneNote':'Copy failed: select and Ctrl+C';
  btn.className=ok?'done':'';
}}
</script></body></html>"""


if __name__ == "__main__":
    pages = split_pages(inline_styles(load(sys.argv[1])))
    open(OUT, "w", encoding="utf-8").write(render(pages))
    # OneNote's page API ignores <code>; use a monospace span instead. The heading is dropped
    # because the page title carries it.
    graph = [
        {"section": pg["section"], "title": pg["title"],
         "html": re.sub(r"<code[^>]*>(.*?)</code>", r'<span style="font-family:Consolas">\1</span>',
                        re.sub(r"^<h[23][^>]*>.*?</h[23]>", "", pg["html"], flags=re.S), flags=re.S)}
        for pg in pages
    ]
    json.dump(graph, open(PAGES_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for pg in pages:
        print(f'{pg["section"]} | {pg["title"]}')
    print(f"{len(pages)} pages -> {OUT}")
