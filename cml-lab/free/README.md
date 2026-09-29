# CCNA Lab — CML-Free version (3 small labs)

CML-Free runs at most **5 nodes**, so the full [16-node lab](../README.md) is
split into 3 labs. Each one runs on its own. Addressing, VLANs, passwords
and configs are the same as the full lab; only what's needed to work without
the missing devices has changed.

| Lab | File | Nodes | Topics |
|---|---|---|---|
| 1 | [`lab1-switching/lab1-switching.yaml`](lab1-switching/) | SW-DIST1, SW-DIST2, SW-ACC1, SW-ACC2, PC1 | VLANs, trunks, EtherChannel, STP, HSRP, inter-VLAN routing, DHCP snooping, DAI, port security |
| 2 | [`lab2-routing/lab2-routing.yaml`](lab2-routing/) | ISP0, R1-EDGE, SW-DIST1, SW-DIST2, R2-BRANCH | OSPF, static + floating static routes, NAT/PAT, NTP, HSRP |
| 3 | [`lab3-services/lab3-services.yaml`](lab3-services/) | R1-EDGE, SW-DIST1, SW-ACC1, PC1, SERVER1 | DHCP relay, DNS, NTP, SSH + VTY ACL, SNMPv3, HTTP/TFTP, DHCP snooping, DAI |

Run **one lab at a time**: stop (and wipe) the current lab before starting
the next, or CML-Free will refuse to start more nodes.

**Import:** CML web UI → **Import** → pick the lab's `.yaml` → **Start lab**.
Or in Claude Code on your PC: *"import cml-lab/free/lab1-switching/lab1-switching.yaml
into CML and start it"*. Allow ~5 minutes to boot.

**Logins:** `admin` / `Lab-Admin1!` (enable `Lab-Enable1!`); `cisco` / `cisco`
on every device.

---

## Lab 1 — Switching

**Changes vs full lab:** no routers or server, so
- SW-DIST1 is the **DHCP server** (pools for VLAN 10/20/50/99) instead of SERVER1 + `ip helper-address`.
- SW-DIST1 is the **NTP master**; OSPF, routed ports, syslog/SNMP hosts removed.
- Only PC1 is connected (SW-ACC1 Gi0/2, VLAN 10). The other access ports keep their config.

**Verify:**
- `show vlan brief`, `show interfaces trunk` — native VLAN 999 on every trunk.
- `show etherchannel summary` — Po1 / Po10 in `SU`.
- `show spanning-tree vlan 10` on SW-DIST1 (root) and `vlan 20` on SW-DIST2 (root).
- `show standby brief` — D1 active for 10/30/99, D2 active for 20/50.
- PC1: `ip addr` shows a 192.168.10.x lease; `ping 192.168.10.1`, `ping 192.168.99.11` (SW-ACC2, via inter-VLAN routing).
- `show ip dhcp snooping binding`, `show ip arp inspection`, `show port-security interface Gi0/2` on SW-ACC1.
- **HSRP failover:** SW-DIST1 `interface vlan 10` → `shutdown`; PC1 keeps pinging `192.168.10.1`.
  (DHCP stays on SW-DIST1, so existing leases keep working.)

## Lab 2 — Routing & edge

**Changes vs full lab:** no access switches, hosts or server, so
- The **branch LAN** on R2-BRANCH is `Loopback1 192.168.40.1/24` (replaces Gi0/2 + PC5).
- The SW-DIST SVIs stay up because VLANs run over the Po1 peer link.
- DHCP relay, DHCP snooping/DAI, Po10 and syslog/SNMP hosts removed.

**Verify:**
- R1-EDGE: `show ip ospf neighbor` — FULL to 2.2.2.2 and 3.3.3.3 (no DR/BDR, point-to-point).
- SW-DIST1: `show ip ospf interface vlan 10` — DR; `show ip route` — `O*E2` default from R1.
- **Static / floating:** R2-BRANCH `show ip route static`, then `shutdown` Gi0/0 — the AD 200
  route via 172.16.13.1 appears. SW-DIST1 `ping 192.168.40.1` (static route to the branch).
- **NAT/PAT:** SW-DIST1 `ping 8.8.8.8 source vlan 10`, then R1-EDGE `show ip nat translations`.
- **NTP:** `show ntp associations` on R1-EDGE, SW-DIST1/2, R2-BRANCH.
- `show standby brief` on SW-DIST1/2.

## Lab 3 — Services

**Changes vs full lab:** no ISP0, SW-DIST2 or SW-ACC2, so
- R1-EDGE is the **NTP master**, has the "Internet" host `Loopback1 8.8.8.8`, and sends a
  default route into OSPF (`default-information originate always`). NAT removed.
- SW-DIST1 is the only distribution switch, so it is **HSRP active for every VLAN**.
- SERVER1 moves to **SW-ACC1 Gi1/2** (VLAN 30).

**Verify:**
- **DHCP relay:** PC1 `ip addr` — lease from SERVER1 (192.168.10.11+); SERVER1 `show ip dhcp binding`.
- **DNS:** PC1 `nslookup server1.lab.local` → 192.168.30.10.
- **Routing:** PC1 `ping 8.8.8.8` (R1's loopback via the OSPF default).
- **NTP:** `show ntp associations` on SW-DIST1, SW-ACC1, SERVER1.
- **SSH + VTY ACL:** SW-ACC1 `ssh -l admin 192.168.99.2` → works (source is VLAN 99).
  PC1 `nc -w 3 192.168.99.2 22` → no SSH banner (VLAN 10 blocked by `MGMT-ACCESS`).
- **SNMPv3:** `show snmp user` on R1-EDGE / SW-DIST1.
- **Syslog:** `show logging` (SERVER1 can't receive syslog).
- **L2 security:** SW-ACC1 `show ip dhcp snooping binding`, `show ip arp inspection`.
