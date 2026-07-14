# 1.0 Network Fundamentals (20%)

Reference and hands-on lab procedures mapped to CCNA 200-301 v1.1 blueprint
section 1.0.

---

## 1.1 Role and function of network components

| Component | Function |
|---|---|
| **Router** | Layer 3 forwarding between different networks/subnets; runs routing protocols; policy enforcement (ACL/NAT) at the WAN/LAN edge. |
| **Layer 2 switch** | Forwards frames within a broadcast domain based on the MAC address table; no routing. |
| **Layer 3 switch** | Combines L2 switching with inter-VLAN routing (SVIs) at wire speed; typical distribution/core device. |
| **Next-gen firewall (NGFW) / IPS** | Stateful inspection + application awareness, user identity, TLS inspection (NGFW); signature/anomaly-based inline threat blocking (IPS). |
| **Access point (AP)** | Layer 2 bridge between wired Ethernet and 802.11 wireless clients. Autonomous (standalone) or lightweight (managed by a WLC via CAPWAP). |
| **Controller (WLC)** | Centralizes AP configuration, RF management, roaming, and security policy for lightweight APs. |
| **Endpoints** | End-user/IoT devices — PCs, phones, printers, cameras. |
| **Servers** | Provide services (DNS, DHCP, AAA, file, application) consumed by endpoints. |
| **PoE** | Delivers DC power over the same Ethernet cable as data (802.3af 15.4W, 802.3at/PoE+ 30W, 802.3bt/PoE++ 60-100W). Powers APs, phones, cameras. |

Verify PoE on a switch port:
```
show power inline
show power inline <interface>
```

---

## 1.2 Network topology architectures

- **Two-tier (collapsed core):** Access + Distribution/Core collapsed into one layer. Common in smaller campuses.
- **Three-tier:** Access → Distribution → Core. Core does high-speed backbone forwarding only; Distribution aggregates/routes between access blocks; Access connects endpoints.
- **Spine-leaf:** Every leaf switch connects to every spine switch (full mesh), no leaf-to-leaf or spine-to-spine links. Predictable low latency, common in data centers; typically routed (L3) links using ECMP.
- **WAN:** Connects geographically separate sites — MPLS, Internet VPN, SD-WAN, leased line.
- **SOHO:** Single integrated device (router+switch+AP+firewall) for a home/small office.
- **On-premises and cloud:** On-prem = infrastructure owned/operated in your own facility. Cloud = infrastructure/services consumed from a provider (IaaS/PaaS/SaaS); hybrid designs connect the two via VPN/Direct Connect/ExpressRoute-style links.

---

## 1.3 Physical interface and cabling types

| Type | Notes |
|---|---|
| **Single-mode fiber (SMF)** | Small core, laser source, long distance (10s of km), used for long backbone/WAN links. |
| **Multimode fiber (MMF)** | Larger core, LED/VCSEL source, shorter distance (up to ~550m/OM4), used inside a building/data center. |
| **Copper (UTP)** | Cat5e/6/6a twisted pair, distance limited to 100m, used for access-layer connections. |

**Connections:**
- **Ethernet shared media** — legacy hub/coax segment, half-duplex, CSMA/CD collision domain shared by all stations.
- **Point-to-point** — modern switched Ethernet link between exactly two devices, typically full-duplex, no collisions.

---

## 1.4 Identify interface and cable issues

```
show interfaces <interface>
show interfaces <interface> counters errors
show controllers <interface>
```

What to look for in `show interfaces`:

| Symptom | Counter | Typical cause |
|---|---|---|
| Late collisions | `late collision` | Duplex mismatch or cable too long |
| Runts/giants | `runts`, `giants` | Bad NIC, duplex mismatch, jabbering device |
| CRC errors | `CRC` | Bad cable/connector, EMI, duplex mismatch |
| Input errors | `input errors` | Physical layer noise, bad cable |
| Collisions (half-duplex only) | `collisions` | Normal on hubs/half-duplex; abnormal on full-duplex link |
| Duplex/speed mismatch | Compare both ends | One side `full 1000`, other `half 100` — always set both ends the same, or both to `auto` |

Force/verify speed and duplex:
```
interface GigabitEthernet1/0/1
 speed auto
 duplex auto
! or force explicitly on both ends if auto-negotiation fails:
 speed 1000
 duplex full
```

---

## 1.5 TCP vs UDP

| | TCP | UDP |
|---|---|---|
| Connection | Connection-oriented (3-way handshake: SYN, SYN-ACK, ACK) | Connectionless |
| Reliability | Acknowledged, retransmits lost segments | Best-effort, no acknowledgment |
| Ordering | Guaranteed in-order delivery | No ordering guarantee |
| Flow/congestion control | Yes (windowing) | No |
| Overhead | Higher (20-byte header + handshake/teardown) | Lower (8-byte header) |
| Use cases | HTTP/HTTPS, SSH, FTP, SMTP — data integrity matters | DNS, DHCP, SNMP, TFTP, VoIP/video (RTP) — speed matters more than retransmission |

---

## 1.6 Configure and verify IPv4 addressing and subnetting

Interface addressing:
```
interface GigabitEthernet0/1
 ip address 192.168.10.1 255.255.255.0
 no shutdown
```

Secondary address on the same interface:
```
interface GigabitEthernet0/1
 ip address 192.168.20.1 255.255.255.0 secondary
```

Verification:
```
show ip interface brief
show ip interface GigabitEthernet0/1
show running-config interface GigabitEthernet0/1
```

**Subnetting cheat sheet (VLSM):**

| CIDR | Mask | Hosts/subnet |
|---|---|---|
| /24 | 255.255.255.0 | 254 |
| /25 | 255.255.255.128 | 126 |
| /26 | 255.255.255.192 | 62 |
| /27 | 255.255.255.224 | 30 |
| /28 | 255.255.255.240 | 14 |
| /29 | 255.255.255.248 | 6 |
| /30 | 255.255.255.252 | 2 (point-to-point links) |

Fast method: block size = 256 − (last octet of mask). E.g. /27 → mask `.224` → block size 32 → subnets at .0, .32, .64, .96 ... First/last usable host = network+1 / broadcast−1.

---

## 1.7 Private IPv4 addressing (RFC 1918)

| Range | CIDR | Typical use |
|---|---|---|
| 10.0.0.0 – 10.255.255.255 | 10.0.0.0/8 | Large enterprise |
| 172.16.0.0 – 172.31.255.255 | 172.16.0.0/12 | Medium networks |
| 192.168.0.0 – 192.168.255.255 | 192.168.0.0/16 | Small office/home |

Not routable on the public Internet — requires NAT/PAT at the edge (see 4.1). Also know **APIPA** `169.254.0.0/16` (auto-assigned when DHCP fails) and loopback `127.0.0.0/8`.

---

## 1.8 Configure and verify IPv6 addressing and prefix

```
ipv6 unicast-routing

interface GigabitEthernet0/1
 ipv6 address 2001:db8:10::1/64
 ipv6 enable                      ! forces a link-local even without a global address
```

EUI-64 auto-generated interface ID:
```
interface GigabitEthernet0/1
 ipv6 address 2001:db8:10::/64 eui-64
```

Verification:
```
show ipv6 interface brief
show ipv6 interface GigabitEthernet0/1
show ipv6 route
```

---

## 1.9 IPv6 address types

| Type | Range/notes |
|---|---|
| **Global unicast** | `2000::/3` — globally routable, equivalent to a public IPv4 address |
| **Unique local (ULA)** | `fc00::/7` (in practice `fd00::/8`) — private, not internet-routable, like RFC 1918 |
| **Link-local** | `fe80::/10` — auto-configured on every IPv6 interface, non-routable off the local link, used for neighbor discovery/next-hop |
| **Anycast** | Same address assigned to multiple devices; packet delivered to the *nearest* one (routing-distance-wise) |
| **Multicast** | `ff00::/8` — delivered to a group of interfaces (replaces IPv4 broadcast entirely — IPv6 has no broadcast) |
| **Modified EUI-64** | Derives the 64-bit interface ID from the 48-bit MAC: split MAC in half, insert `FFFE` in the middle, flip the 7th bit of the first byte (U/L bit) |

---

## 1.10 Verify IP parameters for client OS

**Windows:**
```
ipconfig /all
ipconfig /release
ipconfig /renew
ipconfig /displaydns
nslookup <host>
```

**macOS:**
```
ifconfig en0
ipconfig getifaddr en0
scutil --dns
```

**Linux:**
```
ip addr show
ip route show
resolvectl status      ! or: cat /etc/resolv.conf
```

Check: assigned IP/mask, default gateway, DNS server(s), and whether the address is DHCP-assigned vs static/APIPA.

---

## 1.11 Wireless principles

- **Nonoverlapping Wi-Fi channels:** 2.4 GHz has only channels **1, 6, 11** as non-overlapping (20 MHz each) in most regulatory domains; 5 GHz/6 GHz offer many more nonoverlapping channels and support wider channels (40/80/160 MHz).
- **SSID:** The advertised (or hidden) name of a WLAN; maps to a specific VLAN/security policy on the WLC.
- **RF principles:** Frequency, power (dBm), gain (dBi), attenuation, and interference (co-channel/adjacent-channel) all affect coverage and capacity — design for cell overlap (~15-20%) without co-channel interference.
- **Encryption:** WEP (broken, don't use) → WPA (TKIP, deprecated) → WPA2 (AES-CCMP, standard) → WPA3 (SAE, current best). See section 5.9.

---

## 1.12 Virtualization fundamentals

- **Server virtualization:** A hypervisor (Type 1 bare-metal — ESXi, Hyper-V; or Type 2 hosted) runs multiple isolated VMs, each with its own OS kernel, on shared physical hardware.
- **Containers:** Share the host OS kernel (Docker, containerd); package an app + its dependencies without a full guest OS — lighter weight and faster to start than VMs.
- **VRF (Virtual Routing and Forwarding):** Creates multiple independent routing tables on one physical router/switch, isolating traffic between tenants/departments even though they share the same hardware.
```
ip vrf CUSTOMER_A
interface GigabitEthernet0/1
 ip vrf forwarding CUSTOMER_A
 ip address 10.1.1.1 255.255.255.0
```

---

## 1.13 Switching concepts

- **MAC learning and aging:** A switch inspects the source MAC of every incoming frame and records it against the ingress port in the MAC address table. Entries age out (default 300s) if no traffic is seen — `mac address-table aging-time <seconds>`.
- **Frame switching:** Once a destination MAC is known, the switch forwards the frame out only the matching port (unicast).
- **Frame flooding:** If the destination MAC is unknown (or is broadcast/multicast), the switch floods the frame out all ports in the VLAN except the one it arrived on.
- **MAC address table:**
```
show mac address-table
show mac address-table dynamic
show mac address-table interface GigabitEthernet1/0/1
clear mac address-table dynamic
```
