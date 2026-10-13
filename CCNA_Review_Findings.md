# CCNA Notes: Review Findings

Checked against the Cisco 200-301 v1.1 blueprint (`ccna-200-301-v1.1/200301CCNAv1.1.pdf`) and standard Cisco behaviour.
Nothing has been changed yet. This is a list of proposed corrections.

Confidence: **High** = sure. **Medium** = check against your video before changing.

---

## A. Errors in `CCNA_5.docx` (fix these)

| # | Where | Problem | Correct | Conf. |
|---|---|---|---|---|
| 1 | Part 1, Spine-leaf diagram | Says "all spines link together" | Spines do **not** connect to each other. Every leaf connects to every spine. | High |
| 2 | Part 10, STP timers, Convergence line | "Blocking → Listening (15s) → Learning (15s) → Forwarding = 50 seconds" (adds up to 30) | 50s = Max Age 20 + Listening 15 + Learning 15 | High |
| 3 | STP, Root Bridge Election | "Bridge ID = Priority + MAC" | Bridge ID = Priority + **VLAN ID (system ID ext.)** + MAC. Priority moves in steps of **4096**. VLAN 1 default shows 32769. | High |
| 4 | STP, Root Bridge Election | Tie-breakers missing | Add: lowest root path cost, then lowest sender Bridge ID, then lowest sender port ID. | High |
| 5 | STP commands | `spanning-tree mode rapid-pvst` missing | Cisco default is PVST+. This command turns on Rapid PVST+, which is exactly what exam item 2.5 tests. Also add `root primary` = priority 24576, `root secondary` = 28672. | High |
| 6 | STP, BPDU Filter table | "BPDU Filter disables the port" | Filter never disables a port. With global filter, receiving a BPDU turns off PortFast and the filter on that port; BPDU Guard then err-disables it. | Medium |
| 7 | STP commands table | `spanning-tree guard root` missing | Add it. It is mentioned in the text but not in the table. | High |
| 8 | CCNA_vs_RealWorld, Null0 section | "AD 80 … loses to internal EIGRP (90)" | Lower AD wins, so 80 **beats** EIGRP (90), OSPF (110), RIP (120). It only loses to connected (0), static (1), eBGP (20). | High |
| 9 | Exam ref labels | RIP/EIGRP labelled **3.3** | 3.3 is static routing only. RIP, EIGRP and BGP are **not on the v1.1 exam**. Keep as extra reading, relabel. | High |
| 10 | Exam ref labels | OSPF block labelled 3.3 | Should be **3.4** | High |
| 11 | Exam ref labels (Part 13) | "6.7 Terraform and Ansible" | **6.6** (6.7 is JSON) | High |
| 12 | Exam ref labels (Part 13) | "6.4 Cisco SD-Access and DNA Centre" | That content fits **6.3**. 6.4 is **AI (generative/predictive) and machine learning**, which has no notes at all. | High |
| 13 | Part 13, Puppet/Chef | Chef listed as declarative | Chef is procedural (Ruby). Puppet is declarative. Puppet/Chef are not on v1.1 (only Ansible and Terraform). | Medium |
| 14 | Acronyms (Part 13) | SDA = "another name for SDN" | SDA = **Software-Defined Access** (Cisco SD-Access). | High |
| 15 | Acronyms (Wireless) | "WPA2 – Current wireless security standard" | Contradicts the WPA3 bullet. WPA3 is newest; WPA2 is still widely used. | High |
| 16 | Part 11, DNS | `google.com → 8.8.8.8` | 8.8.8.8 is Google's DNS server, not google.com's address. Use e.g. `google.com → 142.250.x.x`. | High |
| 17 | Security, AAA commands | `show authentication` | Not a real IOS command. `radius-server host` / `tacacs-server host` are deprecated (newer IOS uses `radius server <name>`). AAA config is not tested; 5.8 is concepts only. | High |
| 18 | CLI shortcuts | Ctrl+C listed as "exit config mode" | Standard is **Ctrl+Z** (or `end`). | Medium |
| 19 | Ethernet frame | "Max frame 1518" and "26 bytes overhead" | 1518 excludes preamble+SFD (8 bytes); 26 includes them. Say which. | High |
| 20 | EtherChannel (2.4) | Layer 2 only | Blueprint says **Layer 2 and Layer 3** EtherChannel. Add L3 (no switchport, IP on the port-channel). | High |

## B. Leftover or messy text

- STP section: *"Confirmed: the earlier note above about a 'Root Filter' matches Loop Guard…"* is chat leftover. Delete it.
- STP section: *"introduced briefly here — full command coverage to follow"* is stale. Loop Guard is now fully covered.
- Part 7: empty bullet under the DSCP table.
- Native VLAN: `switchport trunk native vlan <vlan-id>Native VLAN configuration:` and `show interfaces trunkVerify native VLAN:` have labels run into the command.
- Part 13 acronym table: `IaC` appears twice (second row is a description, not an acronym).
- "OSPF" heading under Part 9 still has a **GAP box** ("Single Area OSPFv2") even though OSPF notes already exist above it. Keep one OSPF section. Real gaps: cost/reference bandwidth, hello/dead timers, neighbour states, DR/BDR, network types, adjacency requirements.
- Uses "DNA Centre" in most places but "Catalyst Centre" once. Pick one.
- Routing key-commands table includes BGP commands. Not on exam.

## C. Tracker (✅) overclaims

| Item | Status now | Why it is too high |
|---|---|---|
| 5.3–5.4 | ✅ | No `line console/vty`, `login`, `username … secret`, `login local` config. 5.4 is one bullet (MFA); password management/complexity/certificates/biometrics are missing. |
| 5.9–5.10 | ✅ | 4 bullets only. No SAE, GCMP, PMF, Personal vs Enterprise (802.1X) comparison. |
| 1.3–1.4 | ✅ | No 1.3.b (shared media vs point-to-point). |
| 6.1–6.7 | 🔄 | 6.4 AI/ML has no notes. Split the row. |
| 2.4 | ✅ | Missing Layer 3 EtherChannel (see A20). |

## D. Course simplifications (match the video, but not exactly true)

- "MAC table is held in TCAM": the MAC table is in **CAM**. TCAM holds ACL/QoS/routing lookups.
- "5 GHz channels don't overlap": true only for 20 MHz channels; bonded channels overlap.
- "Lightweight APs connect to access ports": true for Local mode; FlexConnect/Bridge modes need trunks.
- "EIGRP only IGP with unequal-cost load balancing": fine for CCNA.

---

## E. Community notes (`ccna-community-notes/`)

**What they are:** one person's notes on Jeremy's IT Lab *Complete CCNA 200-301* course (same playlist you follow), Days 1–63. They look like the **v1.0-era cut** of it.

**Evidence they are not v1.1:**
- Day 63 is Ansible/Puppet/Chef. v1.1 dropped Puppet/Chef and added Terraform.
- No Terraform and no AI/ML anywhere (searched).
- They say Root Guard/Loop Guard "probably aren't needed" and have no BPDU Filter. Your doc has full coverage, so either the playlist was updated after these notes, or the extras came from elsewhere. Not confirmed (YouTube is not reachable from this session).
- **Decision:** your own video notes take priority over these notes. The blueprint is the authority on what is tested.

**Limits:**
- 882 images are linked from GitHub rather than stored in the repo. Tables, configs and command outputs (e.g. NTP has 34, Wireless Configuration 50) are not in the text, so I cannot verify those parts.

**Accuracy (read in full: STP 2, OSPF 1–3, FHRP, NAT 1–2, NTP, SNMP, Syslog, Port Security, DHCP Snooping, DAI, IPv6 1–3. Checked by search: spine-leaf, TCAM, Chef, cables, PoE.)** Mostly correct. Where they disagree with your doc, **they are right** on spine-leaf and the 50s STP timing. Errors found:

| File | Problem | Correct |
|---|---|---|
| First_Hop_Redundancy_Protocols | "FHRPs are non-preemptive" | HSRP preempt is off by default, but **VRRP preempt is on by default**. Not true of all FHRPs. |
| NTP | "R1 preferred because its stratum is HIGHER" | **Lower** stratum number is better. |
| OSPF_Part3 | MTU mismatch "can still become neighbours" | Routers get stuck in ExStart/Exchange and never reach Full. |
| OSPF_Part3 | Lists Frame Relay/X.25 | Obsolete; not tested. |
| OSPF_Part2 | `R1(config-router)# bandwidth` | `bandwidth` is an **interface** command (`config-if`). |
| IPv6_Part1 | `R1(config) # no shutdown` | Should be `config-if`. |
| Several | Typos ("Designation", "SOLICITED-MODE", "COMPLIMENTARY") | Cosmetic. |

**Not covered by these notes at all (v1.1):** Terraform, AI/ML, Layer 3 EtherChannel, BPDU Filter, wireless GUI WPA2-PSK details beyond images.

**Not yet checked:** the other ~50 files.

---

## F. Suggested order

1. Fix section A (all high-confidence items).
2. Clean up section B.
3. Correct the tracker (section C).
4. Add missing blueprint items: 6.4 AI/ML, Layer 3 EtherChannel, 5.3/5.4 config, `rapid-pvst`.
5. Fill gaps (OSPF first, then FHRP, NAT, NTP, SNMP, Syslog, L2 security, IPv6, IPsec), using your videos as the source and the community notes only as a cross-check.
