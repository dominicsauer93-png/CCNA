# CCNA repo — working rules

## CCNA vs Real World notes (`real-world/`)

- Source of truth is `real-world/CCNA_vs_RealWorld.md`. After editing it, rebuild the Word copy with `node real-world/build_docx.js` and commit both.
- Workflow: Dom brings a real work issue → explain it plainly in chat first → only add it to the doc once Dom confirms.
- Entry format:
  - `## <Title>`
  - `**📊 Level:** <CCNA / CCNP / Vendor / On-the-job / Beyond> — <one line on which part sits where, with blueprint refs>`
  - `***🧠 What CCNA already gave me:*** *<prior CCNA knowledge>*` — or `**⚙ Work reference —** <why it's included>` when there's no CCNA tie-in yet
  - `**🔧 What's actually happening:** <the real situation, bullets per mechanism>`
  - `**Takeaway / next action**` then the summary
  - Tables for command / OID / reference lists.
- Tone: concise, plain language, factual, pitched at an experienced IT professional.

## Sanitise everything from work (mandatory)

Before anything Dom sends goes into the repo, strip real identifiers and use generic placeholders:

| Real detail | Replace with |
| --- | --- |
| IP addresses / subnets | Generic RFC 1918 examples (e.g. `10.10.4.0/22`, `192.168.10.1`) that keep the same prefix length/maths |
| Hostnames / device naming conventions | `SW-ACCESS-01`, `SW-CORE-01`, `RTR-EDGE-01`, etc. |
| Internal URLs / domains | `repo.example.internal`, `example.com` |
| Internal system / service names | Generic role names (e.g. `CACHE-SRV`) |
| Org-specific VLAN IDs | Generic IDs (10, 20, 30…) or `VLAN X` |
| Site, school, department, people names | Omit or use a generic role |

Keep vendor, model and software version info unless it identifies the organisation. When chatting, explain using the generic versions too.

## SOPs (OneNote)

- Working copy: Claude Docs doc "SOPs" — https://claude.ai/code/artifact/5936acb8-0b87-4214-8526-8d0b33b6d2ab
- Structure: SOP list + Page template, then sections Device upgrades / Configuration changes / Backups and restores / New device installs / Troubleshooting / Reference. Generic (any model, Cisco + Aruba) SOP first in each section, model-specific ones below. Add each new SOP to the SOP list table.
- Export for OneNote: `sops/Network_SOPs_OneNote.html` — one card per OneNote page with a "Copy this page" button. Regenerate it after SOP changes: export the doc tab as HTML with the docs export tool, then `python3 sops/build_onenote.py <saved-export-file>` (also writes `sops/onenote_pages.json` for `sops/Add-SOPsToOneNote.ps1`, which uploads pages via Microsoft Graph). Dom confirmed this paste workflow works.
