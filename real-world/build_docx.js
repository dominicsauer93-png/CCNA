// Builds CCNA_vs_RealWorld.docx from CCNA_vs_RealWorld.md.
// Usage: node real-world/build_docx.js
// Supports the subset of Markdown the notes use: #/## headings, paragraphs,
// "- " bullets, pipe tables, ``` code blocks, ***bold italic***, **bold**,
// *italic*, `code` and [links](url).
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, LevelFormat, ExternalHyperlink,
} = require("docx");

const SRC = path.join(__dirname, "CCNA_vs_RealWorld.md");
const OUT = path.join(__dirname, "CCNA_vs_RealWorld.docx");

const FONT = "Calibri";
const MONO = "Consolas";
const TABLE_WIDTH = 9026; // A4 with 1" margins, in DXA

function inline(text, base = {}) {
  const runs = [];
  const re = /\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`|\*\*\*([^*]+)\*\*\*|\*\*([^*]+)\*\*|\*([^*]+)\*/g;
  let last = 0, m;
  const plain = (t, o = {}) => runs.push(new TextRun({ text: t, font: FONT, ...base, ...o }));
  while ((m = re.exec(text))) {
    if (m.index > last) plain(text.slice(last, m.index));
    if (m[1]) {
      runs.push(new ExternalHyperlink({
        link: m[2],
        children: [new TextRun({ text: m[1], style: "Hyperlink", font: FONT, ...base })],
      }));
    } else if (m[3]) plain(m[3], { font: MONO, size: 19 });
    else if (m[4]) plain(m[4], { bold: true, italics: true });
    else if (m[5]) plain(m[5], { bold: true });
    else if (m[6]) plain(m[6], { italics: true });
    last = re.lastIndex;
  }
  if (last < text.length) plain(text.slice(last));
  return runs;
}

const splitRow = (line) => line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());

function buildTable(rows) {
  const header = splitRow(rows[0]);
  const body = rows.slice(2).map(splitRow);
  const n = header.length;
  // Weight column widths by content length, with a floor so short columns stay readable.
  const lens = header.map((h, i) => Math.max(h.length, ...body.map((r) => (r[i] || "").length)));
  const weights = lens.map((l) => Math.max(Math.min(l, 90), 18));
  const total = weights.reduce((a, b) => a + b, 0);
  const widths = weights.map((w) => Math.floor((w / total) * TABLE_WIDTH));
  widths[n - 1] += TABLE_WIDTH - widths.reduce((a, b) => a + b, 0);
  const border = { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const cell = (text, i, head) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA },
    borders,
    shading: head ? { type: ShadingType.CLEAR, color: "auto", fill: "DCE6F1" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ children: inline(text, { size: 19, ...(head ? { bold: true } : {}) }) })],
  });
  return new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, i, true)) }),
      ...body.map((r) => new TableRow({ children: header.map((_, i) => cell(r[i] || "", i, false)) })),
    ],
  });
}

function build(md) {
  const lines = md.split("\n");
  const out = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.trim()) continue;
    if (line.startsWith("```")) {
      const code = [];
      while (++i < lines.length && !lines[i].startsWith("```")) code.push(lines[i]);
      code.forEach((c, k) => out.push(new Paragraph({
        shading: { type: ShadingType.CLEAR, color: "auto", fill: "F2F2F2" },
        spacing: { before: k === 0 ? 120 : 0, after: k === code.length - 1 ? 120 : 0 },
        children: [new TextRun({ text: c || " ", font: MONO, size: 18 })],
      })));
    } else if (line.startsWith("## ")) {
      out.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: inline(line.slice(3)) }));
    } else if (line.startsWith("# ")) {
      out.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: inline(line.slice(2)) }));
    } else if (line.startsWith("- ")) {
      out.push(new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: inline(line.slice(2)) }));
    } else if (line.startsWith("|")) {
      const rows = [];
      while (i < lines.length && lines[i].startsWith("|")) rows.push(lines[i++]);
      i--;
      out.push(buildTable(rows));
      out.push(new Paragraph({ children: [] }));
    } else {
      out.push(new Paragraph({ children: inline(line) }));
    }
  }
  return out;
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: 21 }, paragraph: { spacing: { after: 120 } } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, color: "1F3864", font: FONT },
        paragraph: { spacing: { before: 0, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: "2E74B5", font: FONT },
        paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 1,
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2E74B5", space: 2 } } } },
    ],
  },
  numbering: {
    config: [{ reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
      style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }],
  },
  sections: [{
    properties: { page: { margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    children: build(fs.readFileSync(SRC, "utf8")),
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUT, buf);
  console.log("Wrote " + OUT);
});
