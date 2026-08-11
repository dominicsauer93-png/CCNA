# 3.0 IP Connectivity (25%)

Reference and hands-on lab procedures mapped to CCNA 200-301 v1.1 blueprint
section 3.0 — the highest-weighted domain on the exam.

---

## 3.1 Interpret the components of a routing table

```
show ip route
```
Example line:
```
O    10.1.2.0/24 [110/20] via 10.1.1.2, 00:14:22, GigabitEthernet0/1
```

| Field | Meaning |
|---|---|
| **3.1.a Routing protocol code** | Letter prefix: `C` connected, `S` static, `O` OSPF, `D` EIGRP, `B` BGP, `R` RIP, `L` local. |
| **3.1.b Prefix** | Destination network, `10.1.2.0`. |
| **3.1.c Network mask** | `/24` (or shown as a dotted mask depending on platform/output style). |
| **3.1.d Next hop** | `via 10.1.1.2` — the next router to forward toward. |
| **3.1.e Administrative distance** | First number in brackets, `110` — trustworthiness of the source (lower = preferred). |
| **3.1.f Metric** | Second number in brackets, `20` — protocol-specific cost (OSPF cost, EIGRP composite metric, hop count for RIP). |
| **3.1.g Gateway of last resort** | The default route, shown at the top of `show ip route`: `Gateway of last resort is 10.1.1.1 to network 0.0.0.0`. |

Common default administrative distances (memorize these):

| Source | AD |
|---|---|
| Connected | 0 |
| Static | 1 |
| eBGP | 20 |
| EIGRP (internal) | 90 |
| OSPF | 110 |
| RIP | 120 |
| iBGP | 200 |

---

## 3.2 How a router makes a forwarding decision by default

1. **3.2.a Longest prefix match** — always wins first, regardless of protocol/AD/metric. A `/32` route beats a `/24` beats a `/0` for a matching destination.
2. **3.2.b Administrative distance** — if multiple *different sources* offer the *same* prefix length for the destination, the route with the lowest AD is installed.
3. **3.2.c Routing protocol metric** — if multiple routes from the *same* protocol exist to the same prefix, the lowest metric is preferred (and, if equal, load-balanced across equal-cost paths up to `maximum-paths`).

---

## 3.3 Configure and verify IPv4 and IPv6 static routing

**3.3.a Default route:**
```
ip route 0.0.0.0 0.0.0.0 203.0.113.1
ipv6 route ::/0 2001:db8:0:1::1
```

**3.3.b Network route:**
```
ip route 192.168.30.0 255.255.255.0 10.1.1.2
ipv6 route 2001:db8:30::/64 2001:db8:0:1::1
```

**3.3.c Host route:**
```
ip route 192.168.30.55 255.255.255.255 10.1.1.2
ipv6 route 2001:db8:30::55/128 2001:db8:0:1::1
```

**3.3.d Floating static** — a backup route with a higher AD than the primary dynamic/static route, only installed in the RIB if the primary disappears:
```
ip route 192.168.30.0 255.255.255.0 10.1.1.2          ! primary, default AD 1
ip route 192.168.30.0 255.255.255.0 10.9.9.2 200        ! floating backup, AD 200 — only used if primary route withdrawn
```

Verify:
```
show ip route static
show ip route 192.168.30.0
show ipv6 route static
ping / traceroute
```

---

## 3.4 Configure and verify single-area OSPFv2

Basic config:
```
router ospf 1
 router-id 1.1.1.1
 network 10.1.1.0 0.0.0.255 area 0
 network 192.168.10.0 0.0.0.255 area 0
```

Per-interface alternative (preferred in modern designs — avoids wildcard-mask mistakes):
```
interface GigabitEthernet0/1
 ip ospf 1 area 0
```

**3.4.a Neighbor adjacencies** require: same area number, matching subnet/mask, same OSPF hello/dead timers, matching authentication (if configured), and — for broadcast/NBMA networks — reachability of the DR.

**3.4.b Point-to-point network type** (e.g. on a /30 serial or a routed link configured as p2p) — no DR/BDR election, adjacency forms directly:
```
interface Serial0/0/0
 ip ospf network point-to-point
```

**3.4.c Broadcast network (DR/BDR selection)** — on multi-access segments (Ethernet), OSPF elects a **DR** (Designated Router) and **BDR** to reduce the number of adjacencies (n×(n-1)/2 → all routers form full adjacency only with DR/BDR, 2-way with everyone else). Election is based on highest OSPF interface priority, tiebreak by highest router ID:
```
interface GigabitEthernet0/1
 ip ospf priority 255      ! higher = more preferred; 0 = never becomes DR/BDR
```

**3.4.d Router ID** — selected in this order: manually configured `router-id` (highest priority) → highest IP on a **Loopback** interface → highest IP on any active physical interface. Best practice: always set it manually.

Verify:
```
show ip ospf neighbor
show ip ospf interface brief
show ip ospf interface GigabitEthernet0/1
show ip protocols
show ip route ospf
```

---

## 3.5 First Hop Redundancy Protocols (FHRP)

Purpose: give hosts a single, highly-available default gateway IP backed by multiple physical routers, so a router failure doesn't require reconfiguring every endpoint.

| Protocol | Type | Notes |
|---|---|---|
| **HSRP** | Cisco proprietary | Active/Standby; virtual IP + virtual MAC `0000.0c07.acXX`; multicast hellos to 224.0.0.102. |
| **VRRP** | Open standard | Master/Backup; virtual MAC `0000.5e00.01XX`; can use a real interface IP as the virtual IP (unlike HSRP). |
| **GLBP** | Cisco proprietary | Active/active load balancing — multiple routers can forward simultaneously via AVG/AVF roles, unlike HSRP/VRRP's single active forwarder. |

Example HSRP config:
```
interface GigabitEthernet0/1
 ip address 192.168.10.2 255.255.255.0
 standby 1 ip 192.168.10.1
 standby 1 priority 110
 standby 1 preempt
 standby 1 authentication md5 key-string <secret>
```

Verify:
```
show standby brief
show standby
show vrrp brief
show glbp brief
```
