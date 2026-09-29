# CCNA Lab — CML version

A port of [`../packet-tracer-lab/`](../packet-tracer-lab/) to Cisco Modeling
Labs (CML). Same design, addressing, VLANs, OSPF, HSRP, EtherChannel, NAT,
static/floating routes, ACLs and L2 security — running on real IOS images.

| File | What it is |
|---|---|
| `ccna-lab.yaml` | The CML lab file — import this. |
| `configs/*.txt` | Startup config of each device (already inside the YAML). |
| `build_topology.py` | Rebuilds `ccna-lab.yaml` after you edit a config. |

## 1. Import and start

**Option A — CML web UI:** Dashboard → **Import** → pick `ccna-lab.yaml` →
**Start lab**.

**Option B — Claude Code with cml-mcp:** from the repo folder, ask
*"import cml-lab/ccna-lab.yaml into CML and start it"*.

Give it ~5 minutes to boot and converge (OSPF, HSRP, LACP, DHCP).

**Needs:** 16 nodes (CML-Free is capped at 5 nodes — use Personal or higher)
and roughly 10 GB of free RAM on the CML VM. Node images used: `iosv`,
`iosvl2`, `alpine`.

**Logins:** `admin` / `Lab-Admin1!` (enable: `Lab-Enable1!`) on all IOS
devices; `cisco` / `cisco` on all devices (used by CML automation/cml-mcp).

## 2. What changed from Packet Tracer

| Packet Tracer | CML | Why |
|---|---|---|
| 2911 / 1941 routers | `iosv` | Same interface names (Gi0/0–0/2). |
| 3560/3650 multilayer (D1/D2) | `iosvl2` | Ports renamed, see §3. |
| 2960 access switches | `iosvl2` | Ports renamed, see §3. |
| Generic Server (GUI) | `SERVER1` — an `iosv` router acting as server | DHCP, DNS, NTP, HTTP, TFTP (serve only). No syslog receiver — use `show logging`. |
| WLC1 + AP1 + Laptop0 | `PC-WIFI` — wired host in VLAN 50 | CML has no wireless. VLAN 50 DHCP/HSRP/routing still tested. |
| IP Phone | `PC-VOICE` — host in VLAN 20 on SW-ACC2 | Used to test the `VOICE-RESTRICT` ACL. PC2's port keeps its voice VLAN config. |
| PCs | `alpine` Linux hosts | DHCP via `udhcpc`. |
| PC-ADMIN static IP | PC-ADMIN uses DHCP (new `MGMT` pool on SERVER1, helper on the VLAN 99 SVIs) | DAI on VLAN 99 would drop a static host with no binding. |

Config fixes needed for real IOS (PT didn't enforce these):

- `switchport trunk encapsulation dot1q` added to every trunk (IOSvL2 needs it before `mode trunk`).
- DHCP snooping / DAI **trust moved to the Port-channel** interfaces, and the
  D1–D2 peer link (`Po1`) is now trusted — otherwise relayed DHCP offers and
  HSRP/SVI ARPs crossing the peer link get dropped.
- R1 `OUTSIDE-IN` ACL now permits NTP replies from ISP0 — the original ACL
  blocked them, breaking the NTP chain.
- Banners use `#` as delimiter; `copy run start` lines removed (startup configs).

## 3. Port map

| Device | Port | Connects to |
|---|---|---|
| ISP0 | Gi0/0 | R1-EDGE Gi0/0 |
| R1-EDGE | Gi0/1 / Gi0/2 | SW-DIST1 Gi0/0 / SW-DIST2 Gi0/0 |
| R2-BRANCH | Gi0/0 / Gi0/1 / Gi0/2 | SW-DIST1 Gi0/1 (primary) / SW-DIST2 Gi0/1 (backup) / PC5 |
| SW-DIST1/2 | Gi0/0 | R1-EDGE (routed, OSPF p2p) |
| SW-DIST1/2 | Gi0/1 | R2-BRANCH (routed, static only) |
| SW-DIST1/2 | Gi0/2–3 | each other — `Po1` (LACP trunk) |
| SW-DIST1/2 | Gi1/0–1 | SW-ACC1 / SW-ACC2 — `Po10` (LACP trunk) |
| SW-ACC1 | Gi0/0–1 | SW-DIST1 — `Po1` |
| SW-ACC1 | Gi0/2 / Gi0/3 / Gi1/0 / Gi1/1 | PC1 (V10) / PC2 (V10 + voice V20) / PC-ADMIN (V99) / PC-WIFI (V50) |
| SW-ACC2 | Gi0/0–1 | SW-DIST2 — `Po1` |
| SW-ACC2 | Gi0/2 / Gi0/3 / Gi1/0 / Gi1/1 | PC3 (V10) / PC4 (V10) / SERVER1 (V30) / PC-VOICE (V20) |

Addressing is unchanged — see §3 of the
[Packet Tracer README](../packet-tracer-lab/README.md#3-addressing-plan).

## 4. Verify

Use the checklist in §6 of the
[Packet Tracer README](../packet-tracer-lab/README.md#6-verification-checklist-mapped-to-the-exam-blueprint),
with these CML substitutions:

- PC commands: `ip addr` (instead of `ipconfig /all`), `ping`, `nslookup server1.lab.local`.
- **FHRP test:** on SW-DIST1 `interface vlan 10` → `shutdown`; PC1 keeps pinging `192.168.10.1`.
- **ACL test (5.6):** from PC-VOICE `nc -w 3 192.168.30.10 22` → no reply (blocked); from PC-ADMIN → shows the SSH banner.
- **NAT test (4.1):** from PC1 `ping 8.8.8.8`, then `show ip nat translations` on R1-EDGE.
- **Wireless (5.10):** not possible in CML — do this part in Packet Tracer.
- **Syslog (4.5):** use `show logging` on the device instead of a server viewer.

## 5. Editing

Change a file in `configs/` (or the node/link list in `build_topology.py`),
then run `python3 build_topology.py` (needs PyYAML) to regenerate
`ccna-lab.yaml`.
