# Change log

Every edit made to the study documents, with the text before and after.

- `study-notes/originals/` = the files exactly as you uploaded them.
- `study-notes/` = the edited versions.

**To revert everything:** copy the file from `originals/` over the edited one.
**To revert one change:** open the edited file and put back the "Before" text from the tables below.

Not changed anywhere: tracker status marks (✅ 🔄 ⚠) on existing rows, BGP commands, BPDU Filter table wording, Chef wording, TCAM/CAM wording.

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

