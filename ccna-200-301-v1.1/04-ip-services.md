# 4.0 IP Services (10%)

Reference and hands-on lab procedures mapped to CCNA 200-301 v1.1 blueprint
section 4.0.

---

## 4.1 Configure and verify inside source NAT using static and pools

**Static NAT (1:1, permanent mapping — e.g. a published server):**
```
ip nat inside source static 192.168.10.50 203.0.113.50

interface GigabitEthernet0/0
 ip address 192.168.10.1 255.255.255.0
 ip nat inside
interface GigabitEthernet0/1
 ip address 203.0.113.1 255.255.255.252
 ip nat outside
```

**Dynamic NAT with a pool:**
```
ip nat pool PUBLIC-POOL 203.0.113.10 203.0.113.20 netmask 255.255.255.0
access-list 1 permit 192.168.10.0 0.0.0.255
ip nat inside source list 1 pool PUBLIC-POOL
```

**PAT (overload — pool or single outside IP shared by many inside hosts, most common in production):**
```
access-list 1 permit 192.168.10.0 0.0.0.255
ip nat inside source list 1 interface GigabitEthernet0/1 overload
```

Verify:
```
show ip nat translations
show ip nat statistics
clear ip nat translation *
debug ip nat            ! lab/testing only, not in production
```

---

## 4.2 Configure and verify NTP operating in client and server mode

**Client (points at an external/upstream time source):**
```
ntp server 192.0.2.1 prefer
ntp server 192.0.2.2
clock timezone EST -5
clock summer-time EDT recurring
```

**Server mode (device serves time to downstream devices, e.g. a core router acting as the internal time source):**
```
ntp master 3            ! stratum 3; use only if no external source is reachable
! more commonly, be a client to an external source AND serve internal clients:
ntp server 192.0.2.1
! (a device with a synced clock automatically answers NTP requests from
!   clients unless restricted)
ntp access-group peer NTP-PEERS
```

Verify:
```
show ntp status
show ntp associations
show clock detail
```

---

## 4.3 Role of DHCP and DNS within the network

- **DHCP** dynamically assigns IP address, subnet mask, default gateway, DNS servers, and lease time to clients — eliminates manual IP configuration and prevents address conflicts. Process: **DORA** (Discover → Offer → Request → Acknowledge).
- **DNS** resolves human-readable names to IP addresses (and vice versa) — hierarchical, distributed database (root → TLD → authoritative). Without it, every service would need to be reached by raw IP.

---

## 4.4 Function of SNMP in network operations

SNMP lets a Network Management System (NMS) **poll** devices for statistics (GET) and **receive unsolicited alerts** (traps/informs) — used for monitoring, capacity planning, and alerting without manually logging into every device.

```
! v2c (community-string based — avoid on production networks, cleartext)
snmp-server community <ro-string> RO
snmp-server community <rw-string> RW

! v3 (preferred — authentication + encryption)
snmp-server group SNMP-ADMINS v3 priv
snmp-server user snmpadmin SNMP-ADMINS v3 auth sha <auth-pass> priv aes 128 <priv-pass>
snmp-server host <nms-ip> version 3 priv snmpadmin
snmp-server enable traps
```

Verify:
```
show snmp
show snmp community
show snmp user
show snmp group
```

---

## 4.5 Syslog features — facilities and severity levels

```
logging host 192.0.2.100
logging trap informational
logging source-interface Vlan10
logging buffered 16384 informational
service timestamps log datetime msec localtime show-timezone
```

**Severity levels (0 = most severe, lower number = higher severity; a configured level includes everything numerically below it too):**

| Level | Keyword | Meaning |
|---|---|---|
| 0 | emergencies | System unusable |
| 1 | alerts | Immediate action needed |
| 2 | critical | Critical conditions |
| 3 | errors | Error conditions |
| 4 | warnings | Warning conditions |
| 5 | notifications | Normal but significant |
| 6 | informational | Informational messages |
| 7 | debugging | Debug-level messages |

**Facility** identifies the *source* subsystem of a message (e.g. `local7`, `auth`, `kern`) — used by the receiving syslog server to filter/route messages; set with `logging facility <facility>` if the default (`local7`) needs to change to match the collector's expectations.

Verify:
```
show logging
show logging | include %LINK|%SYS
```

---

## 4.6 Configure and verify DHCP client and relay

**DHCP client (interface pulls its own address):**
```
interface GigabitEthernet0/1
 ip address dhcp
```

**DHCP relay (agent forwards broadcast DHCP requests to a remote DHCP server across a router boundary):**
```
interface GigabitEthernet0/0
 description Client-facing VLAN, DHCP server is remote
 ip helper-address 192.0.2.53
```

(For reference — configuring the router itself as the DHCP server, a related but separate skill:)
```
ip dhcp excluded-address 192.168.10.1 192.168.10.10
ip dhcp pool DATA-VLAN
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
 dns-server 192.0.2.53
 lease 8
```

Verify:
```
show ip interface GigabitEthernet0/0 | include helper
show ip dhcp binding
show ip dhcp conflict
show ip dhcp server statistics
```

---

## 4.7 QoS forwarding per-hop behavior (PHB)

| Stage | Purpose |
|---|---|
| **Classification** | Identify traffic type (ACL match, NBAR, DSCP/CoS already set) so different policies can be applied. |
| **Marking** | Stamp a value (DSCP in IP header, CoS in 802.1Q tag) so downstream devices can classify quickly without re-inspecting the packet. |
| **Queuing** | Place classified/marked traffic into separate queues (e.g. priority queue for voice) so it's serviced according to policy during contention. |
| **Congestion (management/avoidance)** | Techniques like WRED to drop lower-priority traffic proactively before a queue fills and tail-drops everything indiscriminately. |
| **Policing** | Enforces a rate limit by *dropping* (or re-marking) traffic that exceeds it — no buffering, used mostly on ingress/edge. |
| **Shaping** | Enforces a rate limit by *buffering/delaying* excess traffic to smooth it out rather than dropping — used mostly on egress toward a slower WAN link. |

Example MQC (Modular QoS CLI) skeleton:
```
class-map match-all VOICE
 match dscp ef

policy-map WAN-EDGE
 class VOICE
  priority percent 10
 class class-default
  fair-queue

interface Serial0/0/0
 service-policy output WAN-EDGE
```

---

## 4.8 Configure network devices for remote access using SSH

```
ip domain-name example.com
crypto key generate rsa modulus 2048
ip ssh version 2

username admin privilege 15 algorithm-type scrypt secret <StrongPassword!>

line vty 0 15
 transport input ssh
 login local
 exec-timeout 10 0
```

Verify:
```
show ip ssh
show ssh
```
(Full hardened remote-access baseline, including ACL-restricted VTY lines and TACACS+, is in `05-security-fundamentals.md` §5.3 and the switch Day-0 config.)

---

## 4.9 Capabilities and functions of TFTP/FTP in the network

| | TFTP | FTP |
|---|---|---|
| Transport | UDP 69 | TCP 20/21 |
| Authentication | None | Username/password |
| Reliability | No built-in reliability (simple lockstep ack per block) | Reliable (TCP) |
| Typical use | IOS image and config backup/restore on network gear — simple, no-login | General file transfer, larger transfers, needs auth |

```
! Backup running config to a TFTP server
copy running-config tftp:
! Restore/upgrade an IOS image from TFTP
copy tftp: flash:
! FTP example (username/password required)
ip ftp username admin
ip ftp password <secret>
copy running-config ftp://192.0.2.10/backup-config.txt
```
