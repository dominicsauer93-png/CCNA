# CCNA Packet Tracer Lab — "CCNA-LAB"

A single, cohesive Packet Tracer topology built to exercise essentially
every **configure-and-verify** objective in
[`../ccna-200-301-v1.1/`](../ccna-200-301-v1.1/), end to end, with real
traffic paths you can test. Redundant distribution pair with HSRP + OSPF
DR/BDR election, a branch office demonstrating pure static/floating-static
routing, a NAT'd Internet edge, wireless, and full Layer 2 security on the
access layer.

> Credentials/keys used throughout are intentionally simple and consistent
> for lab pastability (e.g. `Lab-Enable1!`). Never reuse lab credentials on
> a real device.

---

## 1. Device list

| Device | Role | Suggested PT model | Notes |
|---|---|---|---|
| **ISP0** | Simulated Internet edge | Router — 1941 (or any 2-port router) | Only needs 1 interface; also acts as NTP stratum-1 master |
| **R1-EDGE** | Internet edge / NAT router | Router — 2911 | 3 onboard GigabitEthernet ports — no modules needed |
| **R2-BRANCH** | Branch-office router | Router — 2911 | 3 onboard GigabitEthernet ports — no modules needed |
| **D1 (SW-DIST1)** | Distribution/core L3 switch #1 | Multilayer switch — 3560-24PS or 3650-24PS (any model supporting `ip routing`) | Needs 6+ usable ports |
| **D2 (SW-DIST2)** | Distribution/core L3 switch #2 | Same as D1 | Redundant peer of D1 |
| **ACC1 (SW-ACC1)** | Access switch #1 | 2960-24TT or similar L2-only switch | |
| **ACC2 (SW-ACC2)** | Access switch #2 | Same as ACC1 | |
| **WLC1** | Wireless LAN Controller | 2504 WLC (or whatever WLC model your PT version ships) | GUI-configured, see `configs/wlc1-gui-steps.md` |
| **AP1** | Lightweight AP | AP-PT-N (lightweight mode) | Joins WLC1 via CAPWAP |
| **Server1** | DHCP/DNS/Syslog/NTP/TFTP server | Generic Server | GUI-configured, see `configs/server1-services.md` |
| **PC1–PC4** | End-user hosts | PC | DHCP clients |
| **IP Phone** | Voice endpoint (optional) | IP Phone | Behind PC2's port, voice VLAN |
| **PC-ADMIN** | Management workstation | PC | Static or DHCP in VLAN 99, used to SSH into everything |
| **PC5** | Branch LAN host | PC | Behind R2, DHCP client |
| **Laptop0** | Wireless client | Laptop w/ wireless NIC | Associates to AP1 via WPA2-PSK |

Exact model numbers vary between Packet Tracer releases — pick any router
with ≥3 routable interfaces, any switch capable of `ip routing` for D1/D2,
and any standard L2 switch for the access layer. All configs below assume
`GigabitEthernet` interface names; substitute `FastEthernet`/
`TenGigabitEthernet` to match your actual hardware without changing any
logic.

---

## 2. Topology

See [`topology.svg`](topology.svg) for the full diagram. Summary of link
types:

- **ISP0 ↔ R1**: routed, simulates the Internet handoff.
- **R1 ↔ D1** and **R1 ↔ D2**: routed, OSPF **point-to-point** network type.
- **D1 ↔ D2**: Layer 2 **EtherChannel (LACP) trunk**, `Po1` — carries every
  VLAN and is where OSPF forms a **broadcast/DR-BDR** adjacency over each
  VLAN SVI, and where HSRP heartbeats travel.
- **D1 ↔ ACC1**, **D2 ↔ ACC2**: Layer 2 **EtherChannel (LACP) trunk**
  uplinks.
- **R2-BRANCH**: primary WAN link to **D1**, backup WAN link to **D2** —
  deliberately kept **outside OSPF**, pure static + floating static routing.
- **ACC1 ↔ WLC1 ↔ AP1**: wireless infrastructure.
- **Server1** hangs off ACC2 in the SERVERS VLAN.

---

## 3. Addressing plan

### VLANs / SVIs (on D1 + D2, HSRP pair)

| VLAN | Name | Subnet | Gateway (HSRP VIP) | D1 real IP | D2 real IP | HSRP active | STP root | OSPF DR |
|---|---|---|---|---|---|---|---|---|
| 10 | DATA | 192.168.10.0/24 | .1 | .2 | .3 | **D1** (110/90) | D1 | D1 |
| 20 | VOICE | 192.168.20.0/24 | .1 | .2 | .3 | **D2** (110/90) | D2 | D2 |
| 30 | SERVERS | 192.168.30.0/24 | .1 | .2 | .3 | **D1** (110/90) | D1 | D1 |
| 50 | WIRELESS | 192.168.50.0/24 | .1 | .2 | .3 | **D2** (110/90) | D2 | D2 |
| 99 | MGMT | 192.168.99.0/24 | .1 | .2 | .3 | **D1** (110/90) | D1 | D1 |
| 999 | NATIVE_UNUSED | — (no SVI) | — | — | — | — | — | — |

Splitting active HSRP/STP-root/OSPF-DR roles between D1 and D2 by VLAN
(instead of one switch owning everything) is deliberate — it mirrors real
distribution-pair design and gives you both directions to test failover.

### Static management IPs (VLAN 99)

| Device | IP |
|---|---|
| ACC1 | 192.168.99.10/24 |
| ACC2 | 192.168.99.11/24 |
| WLC1 | 192.168.99.20/24 |
| AP1 | 192.168.99.30/24 |

### Routed point-to-point links

| Link | Subnet | Side A | Side B | In OSPF? |
|---|---|---|---|---|
| ISP0 ↔ R1 | 203.0.113.0/29 | ISP0 Gi0/0 = .1 | R1 Gi0/0 = .2 | No |
| R1 ↔ D1 | 10.0.12.0/30 | R1 Gi0/1 = .1 | D1 Gi1/0/1 = .2 | **Yes — point-to-point** |
| R1 ↔ D2 | 10.0.13.0/30 | R1 Gi0/2 = .1 | D2 Gi1/0/1 = .2 | **Yes — point-to-point** |
| D1 ↔ R2 (primary) | 172.16.12.0/30 | D1 Gi1/0/2 = .1 | R2 Gi0/0 = .2 | **No — static only, by design** |
| D2 ↔ R2 (backup) | 172.16.13.0/30 | D2 Gi1/0/2 = .1 | R2 Gi0/1 = .2 | **No — static only, by design** |
| R2 ↔ branch LAN | 192.168.40.0/24 | R2 Gi0/2 = .1 | PC5 (DHCP) | No |

Loopbacks for stable OSPF router IDs: R1 `Lo0 1.1.1.1/32`, D1 `Lo0
2.2.2.2/32`, D2 `Lo0 3.3.3.3/32`.

### Static NAT

Server1 (192.168.30.10) is published outbound as **203.0.113.5** on R1.

---

## 4. Physical port assignments

| Device | Port(s) | Connects to |
|---|---|---|
| R1 | Gi0/0 | ISP0 |
| R1 | Gi0/1 | D1 Gi1/0/1 |
| R1 | Gi0/2 | D2 Gi1/0/1 |
| R2 | Gi0/0 | D1 Gi1/0/2 (primary) |
| R2 | Gi0/1 | D2 Gi1/0/2 (backup) |
| R2 | Gi0/2 | PC5 (branch LAN) |
| D1 | Gi1/0/1 | R1 Gi0/1 (routed) |
| D1 | Gi1/0/2 | R2 Gi0/0 (routed) |
| D1 | Gi1/0/3–4 | D2 Gi1/0/3–4 — `Po1` (LACP) |
| D1 | Gi1/0/5–6 | ACC1 Gi0/1–2 — `Po10` (LACP) |
| D2 | Gi1/0/1 | R1 Gi0/2 (routed) |
| D2 | Gi1/0/2 | R2 Gi0/1 (routed) |
| D2 | Gi1/0/3–4 | D1 Gi1/0/3–4 — `Po1` (LACP) |
| D2 | Gi1/0/5–6 | ACC2 Gi0/1–2 — `Po10` (LACP) |
| ACC1 | Gi0/1–2 | D1 Gi1/0/5–6 — `Po1` (LACP) |
| ACC1 | Gi0/3 | PC1 (VLAN 10) |
| ACC1 | Gi0/4 | PC2 + IP Phone (VLAN 10 data / VLAN 20 voice) |
| ACC1 | Gi0/5 | AP1 (VLAN 99 access) |
| ACC1 | Gi0/6 | PC-ADMIN (VLAN 99) |
| ACC2 | Gi0/1–2 | D2 Gi1/0/5–6 — `Po1` (LACP) |
| ACC2 | Gi0/3 | PC3 (VLAN 10) |
| ACC2 | Gi0/4 | PC4 (VLAN 10) |
| ACC2 | Gi0/5 | Server1 (VLAN 30) |
| WLC1 | uplink | ACC1 (trunk carrying VLAN 99 + VLAN 50) |

Adjust port numbers to whatever your actual PT device models expose — what
matters is which logical link goes where.

---

## 5. Build order

1. Drop all devices onto the canvas per the device list above; rename them
   immediately (matches hostnames in the configs) so cabling is unambiguous.
2. Cable per §4 — use copper straight-through everywhere (PT auto-detects
   crossover needs, but if your version doesn't, use the "Automatic" cable
   type).
3. Power on and paste each device's config file from `configs/` into its
   CLI (`enable` → `configure terminal` → paste → `end` → `copy running-config startup-config`).

   **Paste in smaller chunks, not the whole file at once.** Packet Tracer's
   simulated console can drop a character on the first line after a paste
   (commonly the leading letter of a command right after a blank line —
   e.g. `ip access-list ...` becomes `p access-list ...` and PT rejects it
   as an ambiguous command). Paste one logical block at a time (hostname/
   passwords, then banner, then ACLs, then lines, then interfaces, etc.),
   and run `show running-config` afterward to confirm nothing got
   truncated. If a line does get mangled, just retype it manually at the
   prompt — it's a paste artifact, not a problem with the config itself.
4. Configure Server1 and WLC1 via GUI per `configs/server1-services.md` and
   `configs/wlc1-gui-steps.md`.
5. Set PCs/laptop/PC5 to DHCP (`ip dhcp` / "DHCP" radio button under
   Desktop → IP Configuration). Set Laptop0's wireless profile to the SSID/
   PSK from the WLC steps.

---

## 6. Verification checklist, mapped to the exam blueprint

**1.0/1.13 — switching fundamentals:** `show mac address-table` on ACC1/ACC2
after PCs ping each other; confirm entries and aging.

**2.1/2.2 — VLANs & trunking:** `show vlan brief`, `show interfaces trunk`
on all four switches; confirm native VLAN 999 matches on both ends of every
trunk (no mismatch warning).

**2.3 — CDP/LLDP:** `show cdp neighbors detail` and `show lldp neighbors
detail` from D1 — you should see R1, D2, and ACC1.

**2.4 — EtherChannel:** `show etherchannel summary` on D1/D2/ACC1/ACC2 —
all bundles should show `SU` (Layer 2, up) or `RU` (Layer 3, up) status,
never individual/suspended ports.

**2.5 — STP:** `show spanning-tree summary` and `show spanning-tree vlan
10` on D1 (should show D1 as root for VLAN 10) and `... vlan 20` on D2
(should show D2 as root for VLAN 20). Plug a rogue switch/hub into an
access port to confirm BPDU guard err-disables it (`show interfaces status
err-disabled`).

**3.1–3.2 — routing table:** `show ip route` on D1 — confirm you can name
every field of an `O` line and the `Gateway of last resort` line (should be
an `O*E2` default learned from R1).

**3.3 — static routing:** on R2, `show ip route static` — only the primary
default (AD 1) should be installed. `shutdown` R2 Gi0/0, re-check — the
floating default (AD 200) via Gi0/1 should now appear, and `ping
172.16.13.1` should still succeed. `no shutdown` Gi0/0 to restore. On D1,
`show ip route 192.168.40.0` confirms the static network route to the
branch LAN.

**3.4 — OSPF:** `show ip ospf neighbor` on R1 (full adjacencies to D1 and
D2, no DR/BDR since these are point-to-point). `show ip ospf interface
vlan 10` on D1/D2 (D1 should be DR, D2 should be BDR or DROTHER). `show ip
protocols` to confirm router IDs 1.1.1.1/2.2.2.2/3.3.3.3.

**3.5 — FHRP:** `show standby brief` on D1 and D2 — confirm the
active/standby split matches the table in §3. Shut D1's VLAN 10 SVI,
confirm D2 takes over as active within a few seconds and PC1 doesn't lose
its default gateway reachability.

**4.1 — NAT:** from PC1, ping `8.8.8.8` (ISP0's loopback); on R1, `show ip
nat translations` should show the PAT overload entry. From ISP0, `telnet
203.0.113.5 80` or similar should reach the static-NAT'd Server1 mapping
(subject to the OUTSIDE-IN ACL permitting it).

**4.2 — NTP:** `show ntp associations` at each hop — confirm the client/
server chain ISP0 → R1 → D1/D2 → ACC1/ACC2/R2 all show synced (`*`).

**4.5 — syslog:** trigger an event (e.g. `shutdown`/`no shutdown` an
interface) and confirm the message shows up wherever Server1's syslog
viewer is in your PT version.

**4.6 — DHCP relay:** confirm PC1/PC2/PC3/PC4/Laptop0 all pull leases from
Server1 (a different subnet) via `ipconfig /all` at the PC, and `show ip
dhcp snooping binding` on the access switches.

**5.6 — ACLs:** from PC2 (VOICE VLAN via its phone, or test from any VLAN
20 host), attempt `ssh 192.168.30.10` — should be blocked by
`VOICE-RESTRICT` on D2's VLAN 20 SVI; ordinary traffic (e.g. DNS lookups)
should still work.

**5.7 — L2 security:** `show port-security interface Gi0/3` on ACC1;
`show ip dhcp snooping binding`; `show ip arp inspection` — all populated.
Try connecting a second, unauthorized device to PC1's access port (or clone
its MAC) to trigger a port-security violation.

**5.10 — WLAN/WPA2-PSK:** Laptop0 associates to the SSID, gets a VLAN 50
DHCP lease, and can ping its HSRP gateway `192.168.50.1`.

---

## 7. Bonus / stretch goals (beyond the CCNA blueprint, optional)

- **Full branch Internet access:** right now PC5 (branch LAN) can reach the
  whole campus but *not* the Internet, because `192.168.40.0/24` is
  deliberately kept out of OSPF to isolate the static-routing exercise. Fix
  it by adding `redistribute static subnets` under D1's `router ospf 1` —
  this is redistribution, which is outside the single-area-OSPF blueprint
  scope, so treat it as a preview of what comes after CCNA.
- Add a second AP and test client roaming between them.
- Add 802.1X/dot1x with a RADIUS server on Server1 for the DATA VLAN
  instead of open PSK-less access (not required for CCNA but a natural
  next step toward CCNP-level ISE integration).
