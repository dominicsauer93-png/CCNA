"""Build the OneNote copy-paste page from a Claude Docs HTML export of the SOPs doc.

Usage:
  python3 sops/build_onenote.py <export.json|export.html>
      Build the page. export.json = the raw export tool result ({"data": {"bytes_b64": ...}});
      a plain .html fragment also works.
  python3 sops/build_onenote.py --mark-copied
      Record the current pages as copied into OneNote (after Dom confirms), so the next build
      only flags pages that changed after this point.
  python3 sops/build_onenote.py --baseline-from <old Network_SOPs_OneNote.html>
      Set the copied baseline from an earlier version of the built page.

Writes sops/Network_SOPs_OneNote.html: one card per OneNote page with a "Copy this page" button,
marked NEW or UPDATED against sops/onenote_copied.json (what is already in OneNote), and
sops/onenote_pages.json: the same pages for Add-SOPsToOneNote.ps1 (Microsoft Graph upload).
"""
import hashlib
import base64
import html as H
import json
import os
import re
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Network_SOPs_OneNote.html")
PAGES_JSON = os.path.join(os.path.dirname(OUT), "onenote_pages.json")
COPIED_JSON = os.path.join(os.path.dirname(OUT), "onenote_copied.json")
START_PAGES = ("SOP list", "Page template")
BADGE = {"new": "NEW: copy this page", "updated": "UPDATED: copy again and replace the old page"}


def page_hash(page_html):
    return hashlib.sha1(re.sub(r"\s+", " ", page_html).strip().encode("utf-8")).hexdigest()


def mark_status(pages):
    copied = json.load(open(COPIED_JSON, encoding="utf-8")) if os.path.exists(COPIED_JSON) else {}
    for pg in pages:
        pg["hash"] = page_hash(pg["html"])
        old = copied.get(pg["title"])
        pg["status"] = "new" if old is None else ("updated" if old != pg["hash"] else "same")
    return pages


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
    sections, nav, cards, todo, last = [], [], [], [], None
    for i, pg in enumerate(pages):
        if pg["section"] != last:
            last = pg["section"]
            sections.append(last)
            nav.append(f'<li class="sec">{H.escape(last)}</li>')
        st = pg["status"]
        tag = f' <span class="tag {st}">{st.upper()}</span>' if st != "same" else ""
        nav.append(f'<li><a href="#p{i}">{H.escape(pg["title"])}</a>{tag}</li>')
        if st != "same":
            todo.append(f'<li><span class="tag {st}">{st.upper()}</span> <a href="#p{i}">{H.escape(pg["title"])}</a>'
                        f' <span class="where">({H.escape(pg["section"])})</span></li>')
        badge = f'<div class="badge {st}">{BADGE[st]}</div>' if st != "same" else ""
        cards.append(
            f'<section class="card {st}" id="p{i}"><div class="bar"><span class="where">OneNote section: '
            f'<b>{H.escape(pg["section"])}</b> &nbsp;·&nbsp; Page: <b>{H.escape(pg["title"])}</b></span>'
            f'<button onclick="copyPage(\'c{i}\',this)">Copy this page</button></div>{badge}'
            f'<div class="content" id="c{i}">{pg["html"]}</div></section>'
        )
    todo_box = (f'<div class="todo"><b>{len(todo)} page(s) to copy</b> (new or changed since your last copy):'
                f'<ul>{"".join(todo)}</ul></div>') if todo else \
        '<div class="todo done-all"><b>Everything is up to date.</b> No pages to copy.</div>'
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
.tag{{display:inline-block;font-size:8pt;font-weight:bold;padding:1px 6px;border-radius:3px;color:#fff;vertical-align:middle;}}
.tag.new{{background:#2e7d32;}} .tag.updated{{background:#c77700;}}
.badge{{margin:10px 0 0;padding:8px 12px;font-weight:bold;border-radius:4px;}}
.badge.new{{background:#e8f5e9;color:#1b5e20;border:1px solid #2e7d32;}}
.badge.updated{{background:#fff4e0;color:#8a4f00;border:1px solid #c77700;}}
.card.new{{border:2px solid #2e7d32;}} .card.updated{{border:2px solid #c77700;}}
.todo{{background:#fff;border-left:4px solid #c77700;padding:12px 16px;margin-bottom:16px;}}
.todo ul{{margin:6px 0 0 0;padding:0;list-style:none;}} .todo li{{padding:2px 0;}}
.todo.done-all{{border-left-color:#2e7d32;}}
@media (max-width:600px){{nav ul{{columns:1;}}}}
</style></head><body><div class="wrap">
<div class="how"><b>How to move these into OneNote</b><ol>
<li>In OneNote, make a notebook <b>Network SOPs</b> with these sections: {", ".join(H.escape(s) for s in sections)}.</li>
<li>Click <b>Copy this page</b> on a card below.</li>
<li>In OneNote, add a new page in the section shown on the card, click in the page body and press <b>Ctrl+V</b>. Type the page name from the card as the title.</li>
<li>Repeat for each card marked <b>NEW</b> or <b>UPDATED</b>. For UPDATED, paste over the old page's content.</li></ol></div>
{todo_box}
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


def split_built(path):
    """Pages from an earlier built Network_SOPs_OneNote.html (cards)."""
    built = open(path, encoding="utf-8").read()
    cards = re.findall(r'Page: <b>(.*?)</b>.*?<div class="content" id="c\d+">(.*?)</div></section>', built, re.S)
    return {H.unescape(t): page_hash(c) for t, c in cards}


if __name__ == "__main__":
    if sys.argv[1] == "--mark-copied":
        pages = json.load(open(PAGES_JSON, encoding="utf-8"))
        json.dump({pg["title"]: pg["hash"] for pg in pages}, open(COPIED_JSON, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(f"Marked {len(pages)} pages as copied -> {COPIED_JSON}")
        sys.exit()
    if sys.argv[1] == "--baseline-from":
        base = split_built(sys.argv[2])
        json.dump(base, open(COPIED_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"Baseline: {len(base)} pages -> {COPIED_JSON}")
        sys.exit()
    pages = mark_status(split_pages(inline_styles(load(sys.argv[1]))))
    open(OUT, "w", encoding="utf-8").write(render(pages))
    # OneNote's page API ignores <code>; use a monospace span instead. The heading is dropped
    # because the page title carries it.
    graph = [
        {"section": pg["section"], "title": pg["title"], "status": pg["status"], "hash": pg["hash"],
         "html": re.sub(r"<code[^>]*>(.*?)</code>", r'<span style="font-family:Consolas">\1</span>',
                        re.sub(r"^<h[23][^>]*>.*?</h[23]>", "", pg["html"], flags=re.S), flags=re.S)}
        for pg in pages
    ]
    json.dump(graph, open(PAGES_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for pg in pages:
        print(f'{pg["status"]:8} {pg["section"]} | {pg["title"]}')
    print(f"{len(pages)} pages -> {OUT}")
