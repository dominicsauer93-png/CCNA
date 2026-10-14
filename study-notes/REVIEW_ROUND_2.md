# Review round 2 — CCNA.docx (65 pages)

**Status: all of section A and all of section B applied on 2026-10-14, with A4 as the print choice (see CHANGELOG.md, section 1f). The other print options (10 pt text, lighter shading, a new page for each Part) were not applied.**

Only items I am certain about are in section A.

How it was checked: a full re-read of the current text, plus automated checks of colours, borders, bullets, spelling variants, duplicate text and the contents list.

## A. Errors and inconsistencies to fix

| # | Where | Problem | Proposed fix |
|---|---|---|---|
| 1 | STP → BPDUs | "Switches send Hello BPDUs out **all interfaces** every 2 seconds." BPDUs are sent from designated ports (the root bridge originates them, other switches relay them on their designated ports). Ports that are blocking, and root ports, do not send them. The same document says this correctly under Root Bridge Election and RSTP. | "Switches send Hello BPDUs out their designated ports every 2 seconds (the root bridge originates them)." |
| 2 | EIGRP → network command | Garbled sentence: "Unlike RIP, EIGRP can accept a classless address with a mask if you don't specify one, it assumes classful (/8, /16, /24)." | "Unlike RIP, EIGRP accepts a network with a wildcard mask. If you leave the mask out, it assumes the classful network (/8, /16 or /24)." |
| 3 | Part 9 → Route Codes, and the routing table components table | Lists L, C, S, O, D only. RIP is covered in the notes, so **R** (RIP) is missing. | Add "R — RIP — learned via RIP". |
| 4 | Part 5 → Passwords | "enable secret … Uses MD5 encryption." MD5 is a hash, not reversible encryption. `service password-encryption` is also weak (reversible, "Type 7"). | "enable secret — stored as a hash (MD5 in the course). service password-encryption — weak, reversible; it only hides passwords from a quick glance." |
| 5 | Part 14 → Cue words table | "CDP (Cisco) / LLDP (any vendor)" — leftover wording. | "LLDP (vendor-neutral)". |
| 6 | Part 13 / Part 18 | "SD-WAN … vManage" — vManage has been renamed SD-WAN Manager. | "vManage (now called SD-WAN Manager)". |
| 7 | Style: borders | Two tables have no gridlines: the EIGRP acronym table and the administrative-distance table (Static Routes). Your rule is that every table has borders. | Add borders. |
| 8 | Style: borders | 14 "Key Commands" tables have dark-green borders. Your style notes say grey (BFBFBF) borders and no green. | Change to grey. |
| 9 | Style: box colour | The "Extended ACE syntax reminder" box is pale blue with dark navy text. Other reminder boxes are blue with white text. | Match the others. |

## B. Better ways to organise it

1. **Part 9 order and the duplicate OSPF heading.** The order now is RIP → EIGRP → OSPFv2 → Routing Fundamentals → Static Routes → a second "OSPF" heading with the gap box → FHRP. A better order: Routing Fundamentals → Route Codes → Route Selection → Static Routes → RIP → EIGRP → OSPFv2 (with the "remaining topics" box inside it) → FHRP. This also removes the second 3.4 heading.
2. **One routing command table.** The OSPF, EIGRP and BGP commands appear in the section tables and again in the "Key Commands" table after Static Routes. Keep the protocol commands with their protocol and keep only the static-route and `show ip route` commands in that table.
3. **Blueprint index.** Add a table: blueprint objective → Part → page. The tracker shows status but not where the notes are.
4. **Title block.** Add "Last updated: <date>" under the title so printed copies can be told apart.
5. **Printing.**
   - Table text is 9 pt, which is small on paper. 10 pt would be easier to read daily.
   - The dark boxes use a lot of ink. A print version with lighter shading is possible.
   - Starting each Part on a new page makes it easy to slip in extra printed pages later, at the cost of some blank space.
   - If you print on A4, the page size should change from US Letter.
6. **Real-world link.** Add a one-line "Real-world:" pointer at the end of a Part when `CCNA_vs_RealWorld.docx` has a related entry. Three exist now: storm control ↔ STP, hybrid ports ↔ VLANs and trunks, Null0 routes ↔ static routing.

## C. Things to check against Jeremy's videos (not changed)

- BPDU Filter table wording (global vs per-interface behaviour).
- Chef described as declarative.
- 5.3–5.4, 5.9–5.10 and 1.3–1.4 show ✅ but have little content.
- "MAC table is held in TCAM": the MAC table is normally described as CAM; TCAM is used for ACLs and QoS. The course text may be a simplification.

## D. Checked and fine

- Spelling: UK/Australian spelling is used consistently in the prose. The US spellings that appear are official names ("Authentication, Authorization, Accounting") or a US term in the blueprint.
- No empty bullets, no bullet-less list paragraphs, no duplicate bullets.
- The contents list, the footer page numbers and the Part numbering (1–18) match.
- Part numbers used in cross-references ("Part 2", "Part 10") are correct.
