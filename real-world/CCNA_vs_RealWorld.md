# CCNA vs Real World — Working Notes

*Building on CCNA knowledge as real issues come up on the job — not a blueprint cross-reference.*

Purpose: not about matching this to the CCNA course topic-for-topic. It's about taking what the CCNA has already taught and building on it when something real happens in the network — starting with what I know, then adding what the real situation needed that the course didn't cover, or covered differently to how it actually plays out.

Level tags: **CCNA** = on the 200-301 v1.1 blueprint · **CCNP** = next cert up · **Vendor** = specific to non-Cisco gear · **On-the-job / Beyond** = not in any exam, learned from real work.

All IPs, hostnames, URLs and internal system names are replaced with generic placeholders.

## Broadcast Storms & Storm Control

**📊 Level:** CCNP — Storm Control isn't on the CCNA; the STP side is CCNA (2.5).

***🧠 What CCNA already gave me:*** *STP and why it exists — redundant Layer 2 links without it loop traffic endlessly and crash the network. Also already covered the loop-prevention toolkit: Root Guard, Loop Guard, BPDU Guard/Filter.*

**🔧 What's actually happening:** Storm Control (`storm-control broadcast/multicast/unicast level <%>`) isn't tested on the CCNA at all — checked the official blueprint, no mention. It's a per-port rate-limiter, not a loop-prevention protocol. It's commonly enabled as a baseline hardening step on access ports regardless of STP status, because it catches storms STP can't — a flapping NIC, a misbehaving driver, a misconfigured device, or a security tool flooding broadcasts — none of which are loops STP would ever block.

**Takeaway / next action**

STP is the structural fix (blocks the loop). Storm Control is an independent second layer that rate-limits the symptom, and it works even when there's no loop involved, or when STP hasn't converged yet. Worth having both, and worth knowing they're not doing the same job.

## Real Config Example — Hybrid Port on Non-Cisco Gear

**📊 Level:** CCNA + Vendor — 802.1Q tagging and native VLAN are CCNA (2.1, 2.2); the hybrid port type is vendor-specific and not in any Cisco exam.

A real interface config, from Comware/VRP-family CLI (H3C/HPE/Huawei-style — `undo`, `display`, `port hybrid` are the giveaways). CCNA only teaches Cisco IOS syntax, so this is worth keeping as a reference for when the gear on-site isn't Cisco.

```
Port: GE1/0/8 DOWN auto A H 4
<SW-ACCESS-01>dis current-configuration interface g1/0/8
#
interface GigabitEthernet1/0/8
 port link-type hybrid
 undo port hybrid vlan 1
 port hybrid vlan 20 30 40 to 41 tagged
 port hybrid vlan 10 untagged
 port hybrid pvid vlan 10
 broadcast-suppression pps 3000
 stp edged-port
 poe enable
#
```

| Config line | CCNA equivalent / concept | Note |
| --- | --- | --- |
| `port link-type hybrid` | Access port / Trunk port | Hybrid ports don't map 1:1 to either. A hybrid port can carry some VLANs tagged and others untagged at the same time, chosen per-VLAN. Cisco splits that into two separate port modes. |
| `undo port hybrid vlan 1` | Default VLAN | Removes the port from VLAN 1, the default VLAN here too — same concept as Cisco. |
| `port hybrid vlan 20 30 40 to 41 tagged` | 802.1Q trunk, allowed-VLAN list | Functionally the same as a Cisco trunk's allowed-VLAN list, just set per-VLAN rather than as a single port-wide mode. |
| `port hybrid vlan 10 untagged` | Access VLAN | VLAN 10 leaves untagged on this port — acts like an access port for VLAN 10 while simultaneously trunking 20/30/40/41. Not expressible on one Cisco switchport. |
| `port hybrid pvid vlan 10` | Native VLAN | PVID = which VLAN untagged incoming frames get assigned to. Direct equivalent of Cisco's native VLAN. |
| `broadcast-suppression pps 3000` | Storm Control (see entry above) | Same feature as the Storm Control entry above, different vendor syntax: rate-limits by packets-per-second instead of Cisco's percentage-of-bandwidth. |
| `stp edged-port` | PortFast | Direct equivalent — tells STP to skip straight to forwarding. Same purpose, different name. |
| `poe enable` | PoE | Same concept, same idea as Cisco's `power inline` command. |

**Takeaway / next action**

Biggest gap: CCNA teaches VLAN tagging entirely through Cisco's access/trunk binary. A lot of real gear (H3C, Huawei, and others using Comware/VRP-derived CLIs) uses a more flexible hybrid-port model instead, where tagged/untagged is a per-VLAN setting rather than a whole-port mode. The underlying 802.1Q concepts (tagged/untagged, PVID/native VLAN, allowed VLANs) all carry over directly — it's the port-mode model on top of them that differs.

## Live Issue — Diagnosing an Active Broadcast Storm

**📊 Level:** CCNA + On-the-job — the pieces (STP, MAC table) are CCNA (2.5, 1.13); step-by-step triage is experience/CCNP.

***🧠 What CCNA already gave me:*** *STP exists to prevent the loops that cause broadcast storms. If STP is doing its job, a storm shouldn't be able to build from a loop — so an active storm points at either a gap in STP coverage (a port that bypassed it) or a non-loop cause STP was never going to catch.*

**🔧 What's actually happening:** Broadcast storms happening now. Building on the STP theory, the practical triage sequence is about finding the source fast, not just knowing why storms happen in principle.

Rough triage order, worst-symptom-first:

- Check switch CPU and interface utilization — a storm shows as one or more ports pegged near 100% with mostly broadcast/multicast traffic, and switch CPU climbing from processing it all.
- Check for MAC address flapping — the same MAC address relearning on different ports rapidly is the classic loop signature (a frame looping the network and being seen everywhere).
- Check STP state per port — a port stuck cycling Listening/Learning or generating repeated topology change notifications (TCNs) usually means STP is actively fighting a loop rather than one being cleanly blocked.
- Check for a PortFast/edge-port setting on a link that shouldn't have one — the classic cause is an edge port (skips STP negotiation) that got connected to another switch instead of an end host, defeating the loop protection on that link.
- If nothing points to a loop, treat it as non-loop: a NIC or driver fault flooding broadcasts, a misconfigured device, or something scanning/broadcasting heavily on the segment — this is where storm-control/broadcast-suppression earns its keep as a stopgap while the root cause gets found.

**Takeaway / next action**

Knowing STP prevents loops in theory doesn't tell you where THIS storm is coming from. The practical add-on: triage by symptom (utilization, MAC flapping, STP state, edge-port misconfig) to find the source fast, then use storm-control as a stopgap rather than a fix — it limits the damage, it doesn't remove the cause.

## Static Null Routes (Null0) — Practical / Work Reference

**📊 Level:** CCNA + CCNP — static routes, AD and floating statics are CCNA (3.3); Null0, RTBH and BGP aggregates are CCNP (ENARSI).

**⚙ Work reference —** beyond the CCNA blueprint, but builds on static routing (3.3).

- A static null route points at the Null0 virtual interface, which silently discards any packet sent to it (a "blackhole"). By default the router drops the traffic without sending an ICMP unreachable.
- IOS syntax: `ip route <network> <mask> null0 [AD]` — e.g. `ip route 10.10.4.0 255.255.252.0 null0 80` (the /22 covers 10.10.4.0–10.10.7.255).
- Syntax note: the form `ip route 10.10.4.0/22 nullroute distance 80` mixes conventions — a /22 prefix plus the `distance` keyword is FRR / Arista style; classic Cisco IOS uses a dotted mask, the keyword `Null0`, and a bare trailing AD number.
- Administrative distance: the trailing number is the AD. A static route defaults to AD 1; a higher value (e.g. 80) makes it a floating route, used only when no better route to that prefix exists. AD 80 beats OSPF (110) and RIP (120) but loses to internal EIGRP (90) and eBGP (20).

**Why use a null route**

- Blackholing bad / unwanted traffic — drop a flooded host (often a /32) at Null0 instead of letting the attack saturate the link to the victim (remotely triggered black hole, RTBH); also used for bogon/martian filtering. Cheaper than an ACL for a pure "drop everything to this destination."
- Loop prevention with summarisation — advertising a summary such as 10.10.4.0/22 claims the whole block even though the router may only hold some sub-subnets. A null route for the summary drops packets aimed at the unused parts, instead of letting them follow a default route back upstream and loop. EIGRP and OSPF create this Null0 discard route automatically when you configure manual summarisation.
- Anchoring an aggregate for advertisement (BGP) — a routing protocol won't advertise a prefix that isn't in the routing table. Installing a static null route for the aggregate puts the /22 in the RIB so BGP advertises it as one prefix, while any traffic to the gaps lands on Null0.

**⌨ Null-route syntax (IOS)**

| Command | Purpose |
| --- | --- |
| `ip route <net> <mask> null0` | Discard all traffic to `<net>` (AD 1 by default). |
| `ip route <net> <mask> null0 80` | Same, as a floating route (AD 80) — used only if no better route exists. |

## Virtual Routing and Forwarding (VRF)

**📊 Level:** CCNA + CCNP — CCNA (1.12) only asks you to describe it; configuring VRF-lite is CCNP; MPLS L3VPN is the CCNP Service Provider track.

**⚙ Work reference —** beyond CCNA coverage so far (1.12 Virtualisation fundamentals — VMs, containers, VRF — is still ⚠ not yet studied on the course).

**🔧 What's actually happening:** A physical router normally has one routing table — the Global routing table — and every interface, route, and forwarding decision on the box belongs to it. VRF (Virtual Routing and Forwarding) lets a single router hold more than one routing table at the same time. Each VRF is its own isolated instance: its own interfaces, its own routing table, its own forwarding table. Traffic in one VRF is never forwarded into another — forwarding only ever happens between interfaces that sit in the same VRF.

- Effectively splits one physical router into several logically separate virtual routers, without needing separate hardware per customer or department.
- Each VRF instance has its own routing table, its own set of interfaces (physical or sub-interfaces), and its own forwarding table — completely independent of the Global VRF and of every other VRF on the box.
- Isolation is the whole point: nothing in VRF-A's table can be used to forward VRF-B's traffic unless routes are deliberately leaked between them.

**Why service providers use it**

- A service provider connects many separate customer networks over the same shared infrastructure. Customers commonly use overlapping private IP ranges internally (e.g. two different customers both running 10.0.0.0/8). Without VRF, the provider's routers would have a routing table conflict — one table can't hold two different meanings for "10.0.0.1" and know which customer it belongs to.
- VRF solves this by giving each customer their own VRF instance on the shared router. Each customer's routes stay in their own isolated table, so overlapping addressing between customers is a non-issue.
- From the customer's point of view, their sites simply connect to ports on a router — they have no visibility that other customers are sharing the same physical hardware.
- VRF is also a core building block of MPLS L3VPN — it's the mechanism that lets a provider run many customers' Layer 3 VPNs over one shared MPLS core. VRF alone provides the per-customer routing table isolation; MPLS L3VPN adds MPLS labels plus a control-plane protocol (usually MP-BGP) on top to actually carry each customer's isolated routes across the provider's backbone between sites.

**Takeaway / next action**

Think of VRF as "one router, many independent routing tables" — same hardware, hard isolation between tenants (customers, departments, or security zones). It's the isolation mechanism, not a VPN by itself. Worth being able to spot it in a running-config well before 1.12 covers it — look for `ip vrf <name>` / `vrf definition <name>` (defines the VRF) and `ip vrf forwarding <name>` applied under an interface (assigns that interface into the VRF, which also clears any IP already configured on it).

## SNMP MIBs & OIDs — Cisco Switch Reference

**📊 Level:** CCNA + On-the-job — what SNMP does is CCNA (4.4); individual OIDs and Cisco MIBs are job knowledge, not exam content.

**⚙ Work reference —** beyond CCNA coverage so far (4.4 SNMP — ⚠ not yet studied on the course).

**🔧 What's actually happening:** MIB (Management Information Base) is the tree/dictionary of everything a device can report over SNMP. An OID (Object Identifier) is one specific address in that tree — a dotted string like 1.3.6.1.2.1.1.3.0 — that points at one specific value (uptime, CPU load, an interface's error count, etc). Two branches matter in practice: 1.3.6.1.2.1 (mib-2) is the standard, vendor-neutral branch every SNMP device implements the same way; 1.3.6.1.4.1.9 (enterprises.cisco) is Cisco's own branch, used for anything mib-2 doesn't cover (CPU, memory, temperature, CDP neighbours, VLANs).

**Standard MIB-II — System (1.3.6.1.2.1.1)**

| Object | OID | What it returns |
| --- | --- | --- |
| sysDescr | 1.3.6.1.2.1.1.1.0 | Device description string (model, IOS version) |
| sysUpTime | 1.3.6.1.2.1.1.3.0 | Time since last reboot (in hundredths of a second) |
| sysContact | 1.3.6.1.2.1.1.4.0 | Configured contact string (`snmp-server contact`) |
| sysName | 1.3.6.1.2.1.1.5.0 | Configured hostname |
| sysLocation | 1.3.6.1.2.1.1.6.0 | Configured location string (`snmp-server location`) |

**Standard MIB-II — Interfaces (1.3.6.1.2.1.2.2.1 = ifTable, walk per interface index)**

| Object | OID (append .<ifIndex>) | What it returns |
| --- | --- | --- |
| ifDescr | 1.3.6.1.2.1.2.2.1.2 | Interface name (e.g. GigabitEthernet0/1) |
| ifType | 1.3.6.1.2.1.2.2.1.3 | Interface type code (ethernetCsmacd = 6, etc.) |
| ifSpeed | 1.3.6.1.2.1.2.2.1.5 | Reported speed in bps (unreliable above 4.3Gbps — use ifHighSpeed instead) |
| ifPhysAddress | 1.3.6.1.2.1.2.2.1.6 | Interface MAC address |
| ifAdminStatus | 1.3.6.1.2.1.2.2.1.7 | Configured state: up(1) / down(2) / testing(3) |
| ifOperStatus | 1.3.6.1.2.1.2.2.1.8 | Actual state: up(1) / down(2) / testing(3) |
| ifInOctets | 1.3.6.1.2.1.2.2.1.10 | Bytes received (32-bit counter — wraps on fast links) |
| ifInErrors | 1.3.6.1.2.1.2.2.1.14 | Inbound error count |
| ifOutOctets | 1.3.6.1.2.1.2.2.1.16 | Bytes sent (32-bit counter — wraps on fast links) |
| ifOutErrors | 1.3.6.1.2.1.2.2.1.20 | Outbound error count |

**Standard MIB-II — ifXTable, extended/64-bit (1.3.6.1.2.1.31.1.1.1 — use for anything above ~100Mbps to avoid counter wrap)**

| Object | OID (append .<ifIndex>) | What it returns |
| --- | --- | --- |
| ifName | 1.3.6.1.2.1.31.1.1.1.1 | Short interface name (Gi0/1) |
| ifHCInOctets | 1.3.6.1.2.1.31.1.1.1.6 | Bytes received — 64-bit counter |
| ifHCOutOctets | 1.3.6.1.2.1.31.1.1.1.10 | Bytes sent — 64-bit counter |
| ifHighSpeed | 1.3.6.1.2.1.31.1.1.1.15 | Speed in Mbps (reliable for gigabit+ links) |
| ifAlias | 1.3.6.1.2.1.31.1.1.1.18 | The interface description text (`description` command) |

**Cisco enterprise — CPU (CISCO-PROCESS-MIB, 1.3.6.1.4.1.9.9.109)**

| Object | OID | What it returns |
| --- | --- | --- |
| cpmCPUTotal5secRev | 1.3.6.1.4.1.9.9.109.1.1.1.1.6 | CPU busy % over last 5 seconds |
| cpmCPUTotal1minRev | 1.3.6.1.4.1.9.9.109.1.1.1.1.7 | CPU busy % over last 1 minute |
| cpmCPUTotal5minRev | 1.3.6.1.4.1.9.9.109.1.1.1.1.8 | CPU busy % over last 5 minutes — the one most tools graph |

Older IOS (pre-12.2(3.5)) uses the legacy, non-Rev versions one index earlier: cpmCPUTotal5sec = …1.1.3, cpmCPUTotal1min = …1.1.4, cpmCPUTotal5min = …1.1.5. On a switch with one CPU, index with .1 on the end (e.g. …1.1.1.1.8.1); multi-CPU platforms need a walk of cpmCPUTotalTable and correlation against ENTITY-MIB.

**Cisco enterprise — Memory (CISCO-MEMORY-POOL-MIB, 1.3.6.1.4.1.9.9.48)**

| Object | OID | What it returns |
| --- | --- | --- |
| ciscoMemoryPoolName | 1.3.6.1.4.1.9.9.48.1.1.1.2 | Name of the memory pool (Processor, I/O, etc — indexed) |
| ciscoMemoryPoolUsed | 1.3.6.1.4.1.9.9.48.1.1.1.5 | Bytes currently used in that pool |
| ciscoMemoryPoolFree | 1.3.6.1.4.1.9.9.48.1.1.1.6 | Bytes currently free in that pool |

**Cisco enterprise — Environment: temperature, fans, power (CISCO-ENVMON-MIB, 1.3.6.1.4.1.9.9.13)**

| Object | OID | What it returns |
| --- | --- | --- |
| ciscoEnvMonTemperatureStatusDescr | 1.3.6.1.4.1.9.9.13.1.3.1.2 | Description of each temperature sensor |
| ciscoEnvMonTemperatureStatusValue | 1.3.6.1.4.1.9.9.13.1.3.1.3 | Sensor reading (usually °C) |
| ciscoEnvMonFanStatusDescr | 1.3.6.1.4.1.9.9.13.1.4.1.2 | Description of each fan |
| ciscoEnvMonFanState | 1.3.6.1.4.1.9.9.13.1.4.1.3 | Fan status: normal(1) / warning(2) / critical(3) / shutdown(4) / notPresent(5) / notFunctioning(6) |
| ciscoEnvMonSupplyStatusDescr | 1.3.6.1.4.1.9.9.13.1.5.1.2 | Description of each power supply |
| ciscoEnvMonSupplyState | 1.3.6.1.4.1.9.9.13.1.5.1.3 | Same status codes as fan state, above |

**Cisco enterprise — CDP neighbours (CISCO-CDP-MIB, 1.3.6.1.4.1.9.9.23.1.2.1 = cdpCacheTable)**

| Object | OID | What it returns |
| --- | --- | --- |
| cdpCacheDeviceId | 1.3.6.1.4.1.9.9.23.1.2.1.1.6 | Hostname of the neighbour |
| cdpCacheDevicePort | 1.3.6.1.4.1.9.9.23.1.2.1.1.7 | The neighbour's port connected to this link |
| cdpCachePlatform | 1.3.6.1.4.1.9.9.23.1.2.1.1.8 | Neighbour's hardware platform string |

**Cisco enterprise — VLANs (CISCO-VTP-MIB, 1.3.6.1.4.1.9.9.46)**

| Object | OID | What it returns |
| --- | --- | --- |
| vtpVlanName | 1.3.6.1.4.1.9.9.46.1.3.1.1.4 | VLAN name, indexed by VTP domain and VLAN ID |
| vtpVlanState | 1.3.6.1.4.1.9.9.46.1.3.1.1.2 | operational(1) / suspended(2) / mtuTooBigForDevice(3) / etc |

**Reading the numbers**

- 1.3.6.1.2.1 = iso.org.dod.internet.mgmt.mib-2 — the standard branch, same OID on any vendor's gear.
- 1.3.6.1.4.1.9 = iso.org.dod.internet.private.enterprises.cisco — Cisco's own branch. Other vendors have their own enterprise number under 1.3.6.1.4.1 (e.g. Huawei = 2011, HPE = 11).
- A trailing .0 means the object is scalar (one value, no index — e.g. sysUpTime.0). No trailing zero, or a trailing index, means it's a row in a table (e.g. ifDescr.1, ifDescr.2 — one row per interface).

**Takeaway / next action**

For day-to-day polling on Cisco switches, the shortlist that covers most monitoring needs: sysUpTime, ifOperStatus + ifHCInOctets/ifHCOutOctets per interface, cpmCPUTotal5minRev, ciscoMemoryPoolUsed/Free, and the CISCO-ENVMON-MIB temperature/fan/power objects. Confirm exact indices with an snmpwalk or MIB browser against the actual box before wiring anything into monitoring — table indices (which .N a given interface or sensor lands on) are device-specific and not something to guess from this list.

Sources:

- [SNMPv3 Common Object Identifiers (OIDs) in Catalyst 1200/1300 and CBS250/350 Switches - Cisco](https://www.cisco.com/c/en/us/support/docs/smb/switches/Cisco-Business-Switching/kmgmt3636-snmpv3-common-oids-cbs350.html)
- [Collect CPU Utilization on Cisco IOS Devices with SNMP - Cisco](https://www.cisco.com/c/en/us/support/docs/ip/simple-network-management-protocol-snmp/15215-collect-cpu-util-snmp.html)
- [List of SNMP OID and MIB for Cisco - IT Blog](https://ixnfo.com/en/list-of-snmp-oid-and-mib-for-cisco.html)

## Live Issue — Regional Caching Redirect (IOS Image Download)

**📊 Level:** CCNA + Beyond — `copy` with TFTP/FTP is CCNA (4.9); caching proxies and WCCP are beyond the CCNA.

***🧠 What CCNA already gave me:*** *The copy command (`copy <source> <destination>`) for moving IOS images and configs to/from flash, TFTP, or an HTTP server — already covered as a basic file-management operation, not tied to any specific exam ref.*

**🔧 What's actually happening:** Running `copy http://repo.example.internal/firmware/isr4300-universalk9.<version>.SPA.bin bootflash:` on an ISR4300 to pull down a new IOS image. The request hits the network core, and CACHE-SRV — a caching server sitting there — intercepts it, recognises a local copy of that exact file already exists, and redirects the router to fetch it from there instead of pulling it all the way from the central repository server. Net effect: the download comes from a local/regional source instead of crossing the WAN back to head office.

- `copy <url> bootflash:` is a straightforward file copy in IOS — grabs the file at the URL (HTTP/HTTPS/TFTP/FTP all work) and writes it into local flash storage on the router. Nothing unusual there.
- The interesting part is what happens in between: CACHE-SRV is acting as a transparent caching proxy on the path to the origin server. It's not visible to the router as a separate hop in the copy command — from the router's point of view it just issued one HTTP GET and got a response — but somewhere upstream that request was intercepted and served from a local cache instead of going all the way to origin.
- This is the same principle as a CDN edge node, WSUS/Windows Update peer caching, or WCCP-based web caching: don't fetch identical content from the origin server every time — check if a copy already exists closer to the requester and serve from there. The router doesn't need to know or care that this happened; the redirect/interception is invisible at the CLI.
- Why it matters operationally: IOS images are large (hundreds of MB) and identical across every device of the same model. If CACHE-SRV didn't exist, every router doing this same firmware upgrade across the organisation would pull the full image over the WAN from the central repository — multiplied by however many devices are being upgraded. With CACHE-SRV, only the first request in a region actually crosses the WAN; everything after that is served locally, saving WAN bandwidth and completing faster.

**Takeaway / next action**

Not CCNA exam content — closest concepts are WAN design (1.2) and QoS (4.7), but this is really a caching/content-delivery pattern layered on top of a plain HTTP file copy. When troubleshooting a slow or failed copy from an internal repository URL like this, worth remembering there may be an invisible caching layer (a caching server or similar) between the router and the stated origin server — if a download is unexpectedly fast, that's the cache working; if it's failing oddly (wrong file, stale version), the cache itself — not the origin server — is the first thing to check.

## Live Issue — Cache Server Unreachable When Sourced from Loopback0

**📊 Level:** CCNA — routing table, loopbacks and extended ping are all CCNA (3.1, 3.2); applying them to a real fault is experience.

***🧠 What CCNA already gave me:*** *Source address selection for outbound traffic (the routing table picks the egress interface/IP unless a source-interface is explicitly configured) and the VRF concept above — a subnet or interface only has reachability to what it actually has a route/permit to, isolation is never automatic-but-universal.*

**🔧 What's actually happening:** On the CACHE-SRV caching setup (previous entry), some ISRs fail the copy download entirely rather than getting redirected to a local cache — because those ISRs source the request from Loopback0, and Loopback0's address sits in VLAN X. VLAN X has no path to that ISR's local CACHE-SRV instance, so the request can't get there at all.

- Step 1 — source selection: when the copy command opens its HTTP connection, IOS puts a source IP in the packet. That's either explicitly set (`ip http client source-interface Loopback0`, or the TFTP/FTP equivalents) or picked implicitly by the routing table for that destination. On the affected ISRs, the source is Loopback0 — addressed inside VLAN X's subnet.
- Step 2 — how CACHE-SRV decides "local": a caching redirect like this almost certainly maps requesting subnets to a specific nearby cache node, the same way a CDN or GSLB setup does — it has to know which subnets it's meant to serve. That mapping (or the routing/ACLs that support it) is built from a known list of subnets, not "any source, anywhere."
- Step 3 — the actual failure: if VLAN X was never added to that mapping, or there's no route/ACL permit from VLAN X to wherever CACHE-SRV lives, the packet from Loopback0 has nowhere to go — not "redirected to origin as a fallback," just unreachable. That reads as the copy command failing/timing out, with nothing pointing at the real cause.
- Diagnosis: `ping <CACHE-SRV-IP> source Loopback0` on an affected router. If that fails while pinging the same target sourced from a working interface succeeds, the fault is isolated to VLAN X's reachability (routing table gap, ACL, or the cache-mapping not knowing about that subnet) — not the router, not the copy command, and not CACHE-SRV being down.

**Takeaway / next action**

The caching redirect entry above explains the caching mechanism; this is the failure mode when the requesting subnet isn't one the cache knows how to serve. Fix is either: point the download's source-interface at an interface/subnet that already has CACHE-SRV access, or get VLAN X added to whatever routing/ACL/cache-mapping controls reachability to that regional CACHE-SRV node. Worth checking source-interface config on any ISR before assuming a failed firmware download is a bad file or a dead CACHE-SRV node — a source-address/reachability mismatch looks identical from the CLI.
