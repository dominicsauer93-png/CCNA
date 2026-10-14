# Change log

Every edit made to the study documents, with the text before and after.

- `study-notes/originals/` = the files exactly as you uploaded them.
- `study-notes/` = the edited versions (plus `CCNA_Lab_Companion.docx`, which is new).

**To revert everything:** copy the file from `originals/` over the edited one.
**To revert one change:** open the edited file and put back the "Before" text from the tables below.

Not changed anywhere (as you asked, the RIP/EIGRP/Puppet/Chef/SD-Access sections were left as they are): tracker status marks (✅ 🔄 ⚠) on existing rows, BGP commands, BPDU Filter table wording, Chef wording, TCAM/CAM wording.

## 1. CCNA.docx

### 1a. Accuracy fixes and clean-up
| Where | Before | After |
|---|---|---|
| Part 1, Spine-leaf diagram | [Spine 1]--------[Spine 2] <- all spines link together | [Spine 1]          [Spine 2] <- spines do NOT link to each other |
| STP timers, Convergence line | Blocking → Listening (15s) → Learning (15s) → Forwarding = 50 seconds total. | Max Age expires (20s) → Listening (15s) → Learning (15s) → Forwarding = 50 seconds total. A newly enabled port has no Max Age wait: 30 seconds. |
| Root Bridge Election, Bridge ID | Bridge ID = Bridge Priority (default 32768) + MAC address. Lowest wins. | … + VLAN ID (system ID extension) + MAC address. Priority changes in steps of 4096; the default shows as 32769 for VLAN 1. |
| Root Bridge Election | — | Added 3 bullets: root primary = 24576 / secondary = 28672; root port tie-breakers; designated port tie-breakers |
| STP intro bullet | Classic STP = IEEE 802.1D. Runs on all switches by default across all vendors. | … appended: Cisco switches default to PVST+; enable Rapid PVST+ with spanning-tree mode rapid-pvst. |
| STP commands table | — | Added rows: spanning-tree mode rapid-pvst; spanning-tree guard root |
| STP Toolkit, Root Guard and Loop Guard | "Confirmed: the earlier note above about a “Root Filter” matches Loop Guard exactly…" (bullet) | (bullet deleted) |
| STP Toolkit, Root Guard and Loop Guard | Two further STP toolkit features, introduced briefly here — full command coverage to follow when studied in depth. | Two further STP toolkit features. |
| Native VLAN bullets | "switchport trunk native vlan <vlan-id>Native VLAN configuration:" and "show interfaces trunkVerify native VLAN:" | Label first, then the command: "Native VLAN configuration: switchport trunk native vlan <vlan-id>" and "Verify native VLAN: show interfaces trunk" |
| RIP exam-ref bar | Exam ref: 3.3 — Dynamic routing protocols (RIP overview) | Not on v1.1 exam: RIP — dynamic routing background (blueprint 3.3 is static routing only) |
| EIGRP exam-ref bar | Exam ref: 3.3 — Configure and verify EIGRP | Not on v1.1 exam: EIGRP — dynamic routing background (blueprint 3.3 is static routing only) |
| OSPFv2 exam-ref bar | Exam ref: 3.3 — Configure and verify OSPFv2 for single area | Exam ref: 3.4 — Configure and verify single area OSPFv2 |
| Part 13 exam-ref bar | Exam ref: 6.7 — Terraform and Ansible — Automation and Programmability | Exam ref: 6.6 — Configuration management: Ansible and Terraform (Puppet and Chef are not on the v1.1 exam) |
| SDN exam-ref bar | Exam ref: 6.3 — Software-Defined Networking \| 6.4 — Cisco SD-Access and DNA Centre | Exam ref: 6.3 — Controller-based, software-defined architecture (overlay, underlay, fabric) \| Cisco SD-Access and DNA Centre as the worked example |
| Acronyms (Part 13), SDA row | Software-Defined Architecture — Another name for SDN / controller-based networking. | Software-Defined Access — Cisco SD-Access: SDN-based automation of campus LANs, controlled by DNA Centre. |
| Acronyms (Wireless), WPA2 row | Current wireless security standard (AES-CCMP). | Widely used wireless security standard (AES-CCMP). WPA3 is the newest. |
| Wireless Security bullet, WPA2 | WPA2 — Current standard. Uses AES-CCMP. Significantly stronger. | WPA2 — Most widely used standard. Uses AES-CCMP. Significantly stronger. |
| DNS bullet | (e.g. google.com → 8.8.8.8) | (e.g. google.com → 142.250.x.x) |
| AAA commands table | show authentication row | (row deleted — not a real IOS command) |
| AAA commands table, radius/tacacs rows | …server for authentication. | … appended: Older syntax; newer IOS uses radius server <name> / tacacs server <name>. |
| Ethernet frame note | Max Ethernet frame = 1518 bytes (1522 with VLAN tag). Preamble+SFD+Dst+Src+Type+FCS = 26 bytes overhead. | … counted from Destination to FCS — preamble + SFD (8 bytes) are not counted. Header + trailer overhead = 18 bytes; 26 bytes including preamble + SFD. |
| EtherChannel, after "Member interfaces must match" | — | New bullet: Layer 3 EtherChannel (no switchport on members and port-channel, IP on the port-channel) |
| EtherChannel/switching commands table | — | Added row: no switchport |
| Part 7, after DSCP table | Empty bullet | (deleted) |
| OSPF gap box (3.4) | ⚠ GAP — 3.4: Single Area OSPFv2 (Add notes from video when studied) / Cover: neighbor adjacencies, DR/BDR election, router ID, point-to-point vs broadcast, full OSPF config. | ⚠ GAP — 3.4: Single Area OSPFv2 — remaining topics / Cover (still to add): cost and reference bandwidth, hello/dead timers, neighbour states, DR/BDR election, network types, adjacency requirements. Basics are in the OSPFv2 section above. |
| Terraform bullet | …Cisco platforms including Catalyst Centre, ACI, and IOS XE. | …Cisco platforms including DNA Centre (now Catalyst Center), ACI, and IOS XE. |
| Part 13 acronym table | Second "IaC \| IaC tool types" row | (row deleted — duplicate) |
| Part 13, before the REST/JSON gap box | — | New gap box: ⚠ GAP — 6.4: AI (generative and predictive) and machine learning in network operations |
| Coverage tracker | One row: 6.1–6.7 Automation and Programmability 🔄 | Four rows: 6.1–6.3 🔄; 6.4 ⚠; 6.5, 6.7 ⚠; 6.6 🔄 |

### 1b. Added after the first round (port table, 802.11 table, acronym de-duplication)
| Where | Before | After |
|---|---|---|
| Part 2, after the TCP vs UDP table | — | New table: Common well-known port numbers (18 rows: FTP, SSH, Telnet, SMTP, TACACS+, DNS, DHCP, TFTP, HTTP, POP3, NTP, IMAP, SNMP, HTTPS, Syslog, RADIUS, CAPWAP) |
| Part 10, Wireless: 802.11 & Wi-Fi standards | Heading with no list under it | New table: 802.11 standards at a glance (802.11, b, a, g, n, ac, ax, be) |
| Acronym table (duplicates removed) | Rows: AAA, RADIUS, TACACS+, NGFW, NGIPS | (rows removed — already defined in an earlier section) |
| Acronym table (duplicates removed) | Rows: NAT, PAT, QoS, DSCP | (rows removed — already defined in an earlier section) |
| Acronym table (duplicates removed) | Rows: STP | (rows removed — already defined in an earlier section) |
| Acronym table (duplicates removed) | Rows: CoS, CDP | (rows removed — already defined in an earlier section) |
| Acronym table (all rows duplicates) | Table with: CIDR, IANA | (table and its label removed — acronyms are defined earlier) |
| Acronym table (duplicates removed) | Rows: MTU | (rows removed — already defined in an earlier section) |
| Acronym table (duplicates removed) | Rows: IP | (rows removed — already defined in an earlier section) |
| Acronym table (duplicates removed) | Rows: ICMP, PING, MAC | (rows removed — already defined in an earlier section) |
| Acronym table (duplicates removed) | Rows: PDU | (rows removed — already defined in an earlier section) |
| Acronym table (duplicates removed) | Rows: IEEE, IETF | (rows removed — already defined in an earlier section) |

Acronym rule used: the first time an acronym appears it stays; later repeats of the same acronym were removed. Acronyms.docx remains the full master list.

### 1c. Command selection guide, and a fix to my earlier edit
| Where | Before | After |
|---|---|---|
| New "Part 14 — Choosing the Right Command" (after Part 13, before the tracker) | — | Six rules for picking a command; "what do you need to know → best command" table (19 rows); which mode a command goes in; reading interface status; look-alike pairs; cue words → protocol or feature; common traps in quiz answers. To remove: delete everything from the "Part 14" heading down to the "Exam Topic Coverage Tracker" heading. |
| 6.4 AI/ML gap box, "Cover:" line | My earlier edit made this line a large Heading 1 by mistake | Fixed: now a normal small red "Cover:" line like the other gap boxes |

### 1d. Navigation, reference parts and review table (CCNA.docx)
| Where | Before | After |
|---|---|---|
| Top of document | Title only | Added a clickable "Contents" list (Parts and topics, with page numbers) and a page break before Part 1. To refresh page numbers in Word: right-click the list → Update Field. To remove: delete from the "Contents" label to the page break. |
| Footer | None | Added footer: "CCNA Exam v1.1 (200-301) — Study Notes" and "Page X of Y". Footer distance changed from 708 to 360 so it fits in the margin. |
| 37 sub-headings that were only bold text | Not in the Word navigation pane or contents | Converted to real headings (Heading 3; the 7 in Part 14 are Heading 2). Same look. They are: 802.11 & Wi-Fi standards; Shared medium, half-duplex & CSMA/CA; Signal coverage & propagation; Radio frequency (RF) basics; Wi-Fi bands & channels; Service sets (IBSS / BSS / ESS / MBSS); Distribution System (DS); Additional AP operating modes; 802.11 frame format; 802.11 association process; AP deployment models; Autonomous APs; Lightweight APs & Split-MAC architecture; Cloud-based APs (Meraki); WLAN configuration on the WLC (GUI); Topology & connections; WLC ports vs interfaces; Creating a WLAN — security (GUI); What an ACL is; How ACLs work; ACL types; Wildcard masks & entry ordering; Standard ACL commands (IOS); Extended ACLs; What an extended ACE matches; Extended ACL command syntax; Editing ACLs — sequence numbers & resequencing; Why automate; Logical planes (data / control / management); CPU vs ASIC (hardware forwarding); Six rules for picking the command; What do you need to know? → best command; Which mode does the command go in?; Reading interface status (show ip interface brief); Look-alike pairs — what is the difference?; Cue words → protocol or feature; Common traps in quiz answers. |
| Heading 1 and 2 paragraphs | — | Added hidden bookmarks so the contents entries can link to them. |
| New Part 15 — Defaults and Numbers | — | Timers, administrative distance, addresses and protocol numbers, limits and defaults. |
| New Part 16 — Reading Command Output | — | Sample output with notes for: show ip route, show ip interface brief, show interfaces status, show mac address-table, show interfaces trunk, show spanning-tree, show etherchannel summary, show ip ospf neighbor. |
| New Part 17 — Troubleshooting | — | Bottom-up method, the ping ladder, and a symptom → cause → check → fix table (17 rows). |
| New Part 18 — Domain Cheat Sheets | — | One page per exam domain, built only from topics already in the notes, with a "Still to add" line for the gaps. |
| Exam Topic Coverage Tracker heading | No page break | Page break before it (so the Domain 6 sheet stays on its own page). |
| New "Review Status" section at the end | — | Table of how far to trust each Part, known open items, and a blank "Lab-tested?" column for you. |
To remove Parts 15–18 and Review Status: delete from each "Part 15" … "Part 18" heading down to the next heading, and the Review Status section at the end.

### 1e. Labs moved out, and an accuracy pass (you asked for only information I am certain of)
| Where | Before | After |
|---|---|---|
| Part 18 — Lab Companion | Eight labs inside CCNA.docx | Moved to a separate file, `CCNA_Lab_Companion.docx`. The cheat sheets became Part 18 and the Review Status table was renumbered. |
| STP bullet, rapid-pvst row (CCNA.docx and Basic_Configuration_Commands.docx), Part 15, Part 18 cheat sheet | "Cisco switches default to PVST+" | "Classic Catalyst switches (for example the 2960) default to PVST+" and "check yours with show spanning-tree summary". Newer platforms may differ and I could not confirm them. |
| Part 15, STP port costs | "Short (Cisco default) … Long (RSTP scale)" | "Classic STP … RSTP scale". The claim about which scale Cisco uses by default was removed. |
| Part 16, show spanning-tree notes | A "Cost note" about the default cost scale | Removed. |
| Part 15, limits table | Row: "ECMP paths 4 by default, up to 32 (depends on IOS)" | Row removed (not certain). |
| Part 16 | No label on the sample output | Added: samples were typed by hand and your device will differ. |
| Part 16, show etherchannel summary note | "(s) suspended — usually a config mismatch or incompatible modes (passive/passive, auto/auto)" | "(s) = suspended. Members whose settings do not match the others can be suspended; (I) = stand-alone, not bundled." |
| Part 16, show mac address-table note | "…again and again = a loop" | "…usually points to a Layer 2 loop" |
| Part 17, ping ladder and table | "Ping works one way only = no return route" | "Often no return route (an ACL on the way back is another cause)" |
| Part 17, EtherChannel row | "Mismatched … passive+passive, auto+auto, on+active" | "Settings that do not match the other members or the other switch; incompatible modes …" |
| Part 14, show interfaces row | "The only command with error counters" | "Shows the error counters (CRC, collisions) plus duplex and speed" (other commands, such as show interfaces counters errors, also show errors) |
| Part 14, Part 15, Part 18: CDP wording | "CDP is Cisco only / CDP only sees Cisco devices" | "CDP is Cisco-proprietary; LLDP is the vendor-neutral standard" |
| RIP and EIGRP exam-ref bars | "Not on v1.1 exam: …" | "Not listed in the v1.1 blueprint: …" (Cisco says other topics may appear, so "not on the exam" was too strong.) |
| Part 13 exam-ref bar | "(Puppet and Chef are not on the v1.1 exam)" | "(Puppet and Chef are not named in the v1.1 blueprint)" |
| DNS bullet | "(e.g. google.com → 142.250.x.x)" | "(e.g. google.com → an IPv4 address)" |
| 802.11 table, 802.11be row, Year | 2024 | — (the exact year is unclear, so it was left out) |
| Basic_Configuration_Commands.docx, show ip access-lists row | "(show access-lists lists all ACL types)" | Comparison removed |

## 2. CCNA_vs_RealWorld.docx
| Where | Before | After |
|---|---|---|
| Null0 section, Administrative distance bullet | AD 80 beats OSPF (110) and RIP (120) but loses to internal EIGRP (90) and eBGP (20). | AD 80 beats internal EIGRP (90), OSPF (110) and RIP (120) but loses to connected (0), static (1) and eBGP (20). |

## 3. Basic_Configuration_Commands.docx
| Where | Before | After |
|---|---|---|
| Security: radius-server host | …server for authentication. | …server for authentication. Older syntax; newer IOS uses radius server <name>. |
| Security: tacacs-server host | …server for authentication. | …server for authentication. Older syntax; newer IOS uses tacacs server <name>. |
| Security: row removed | show authentication \| Display authentication status \| Shows the current authentication configuration and status. \| Both | (row deleted — not a real IOS command) |
| Keyboard shortcuts | Ctrl+C \| Exit configuration mode \| Returns to privileged EXEC mode from configuration mode. | Ctrl+Z \| Exit configuration mode \| Returns to privileged EXEC mode from any configuration mode (same as end). |
| Section header "Saving Configurations" | Device column showed "Both" on the header row | Device cell emptied (header row only) |
| New section header row | (none — STP commands sat under "Saving Configurations") | Spanning Tree Commands |
| Spanning Tree: row added | — | spanning-tree mode rapid-pvst |
| Spanning Tree: row added | — | spanning-tree guard root |
| Spanning Tree: row added | — | spanning-tree guard loop |
| Spanning Tree: row added | — | spanning-tree loopguard default |
| Spanning Tree: row added | — | spanning-tree guard none |
| Spanning Tree: row added | — | spanning-tree link-type point-to-point |
| Spanning Tree: row added | — | spanning-tree link-type shared |
| New section header row | — | VLAN Trunk Commands |
| New section header row | — | OSPF Commands (additional) |
| New section header row | — | ACL Commands (additional) |
| New section header row | — | EtherChannel Commands |
| EtherChannel: row added | — | channel-group <number> mode {desirable\|auto\|active\|passive\|on} |
| EtherChannel: row added | — | interface port-channel <number> |
| EtherChannel: row added | — | channel-protocol {pagp\|lacp} |
| EtherChannel: row added | — | port-channel load-balance <mode> |
| EtherChannel: row added | — | no switchport |
| EtherChannel: row added | — | show etherchannel summary |
| EtherChannel: row added | — | show etherchannel port-channel |
| EtherChannel: row added | — | show etherchannel load-balance |

## 4. Acronyms.docx
| Where | Before | After |
|---|---|---|
| Row: Cisco Firepower Management Center | CFMC | FMC |
| Row: SDA | Software-Defined Architecture \| Another name for SDN / controller-based networking (distinct from Cisco SD-Access). | Software-Defined Access \| Cisco SD-Access: SDN-based automation of campus LANs, controlled by DNA Centre. |
| Row: WPA2 | Current standard using AES-CCMP; significantly stronger. | Widely used standard using AES-CCMP; significantly stronger. WPA3 is newer. |
| Stray bullet after table | TCP -Transmission Control Protocol | (deleted — duplicate of the TCP / IP table rows) |
| Stray bullet after table | IP – Internet Protocol | (deleted — duplicate of the TCP / IP table rows) |

### 3b. Basic_Configuration_Commands.docx — rows added to match CCNA.docx
| Where | Before | After |
|---|---|---|
| Routing: row added from CCNA.docx | — | router rip |
| Routing: row added from CCNA.docx | — | version 2 |
| Routing: row added from CCNA.docx | — | no auto-summary |
| Routing: row added from CCNA.docx | — | debug ip rip |
| Routing: row added from CCNA.docx | — | show ip rip database |
| Routing: row added from CCNA.docx | — | show ip protocols |
| Routing: row added from CCNA.docx | — | eigrp router-id <IP> |
| Routing: row added from CCNA.docx | — | show ip eigrp topology |
| Routing: row added from CCNA.docx | — | variance <multiplier> |
| Routing: row added from CCNA.docx | — | ip access-list standard <name> |
| Security: row added from CCNA.docx | — | show ip access-lists |

### 4b. Acronyms.docx — rows added to match CCNA.docx
| Where | Before | After |
|---|---|---|
| Row added from CCNA.docx | — | AS — Autonomous System |
| Row added from CCNA.docx | — | DNA — Digital Network Architecture |
| Row added from CCNA.docx | — | ECMP — Equal Cost Multi-Path |
| Row added from CCNA.docx | — | IS-IS — Intermediate System to Intermediate System |
| Row added from CCNA.docx | — | RIP — Routing Information Protocol |
| Row added from CCNA.docx | — | VM — Virtual Machine |
