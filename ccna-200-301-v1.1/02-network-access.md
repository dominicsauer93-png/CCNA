# 2.0 Network Access (20%)

Reference and hands-on lab procedures mapped to CCNA 200-301 v1.1 blueprint
section 2.0. Builds on the working config in
`../configs/cisco-switch-day0-production-config.md`.

---

## 2.1 Configure and verify VLANs (normal range) spanning multiple switches

```
vlan 10
 name DATA
vlan 20
 name VOICE
exit
```

**2.1.a Access ports (data and voice):**
```
interface GigabitEthernet1/0/5
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 20
```

**2.1.b Default VLAN:** VLAN 1 is the factory-default VLAN for all switch ports and carries CDP/DTP/PAgP/VTP traffic by default. Best practice: don't use VLAN 1 for user or management traffic — move it off as native/unused (see 2.2.c).

**2.1.c InterVLAN connectivity** — two methods:

Router-on-a-stick (single router, sub-interfaces):
```
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
```

Multilayer switch (SVI — preferred in campus designs):
```
ip routing
interface vlan 10
 ip address 192.168.10.1 255.255.255.0
 no shutdown
interface vlan 20
 ip address 192.168.20.1 255.255.255.0
 no shutdown
```

Verify:
```
show vlan brief
show interfaces switchport
show interfaces vlan 10
```

---

## 2.2 Configure and verify interswitch connectivity

**2.2.a Trunk ports / 2.2.b 802.1Q:**
```
interface GigabitEthernet1/0/24
 switchport trunk encapsulation dot1q     ! required on platforms supporting both ISL and dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 switchport nonegotiate                    ! disable DTP — don't auto-negotiate trunk state
```

**2.2.c Native VLAN** — the one VLAN on a trunk that is sent untagged (802.1Q default is VLAN 1). Mismatched native VLANs between the two ends of a trunk cause VLAN leakage and generate a native VLAN mismatch error — both ends must match.
```
interface GigabitEthernet1/0/24
 switchport trunk native vlan 999          ! move off VLAN 1 for security
```

Verify:
```
show interfaces trunk
show interfaces GigabitEthernet1/0/24 switchport
```

---

## 2.3 Configure and verify Layer 2 discovery protocols (CDP and LLDP)

**CDP (Cisco proprietary):**
```
cdp run                          ! global enable (on by default)
interface GigabitEthernet1/0/1
 cdp enable                      ! per-interface (on by default)
```
```
show cdp neighbors
show cdp neighbors detail
show cdp interface
no cdp enable                    ! disable per-interface facing untrusted/external devices
```

**LLDP (open standard — use for multivendor neighbors, e.g. Cisco-to-non-Cisco or IP phones):**
```
lldp run
interface GigabitEthernet1/0/1
 lldp transmit
 lldp receive
```
```
show lldp neighbors
show lldp neighbors detail
```

---

## 2.4 Configure and verify (Layer 2/Layer 3) EtherChannel (LACP)

**Layer 2 EtherChannel:**
```
interface range GigabitEthernet1/0/23 - 24
 channel-group 1 mode active        ! active = LACP initiator; passive = responds only (need at least one active side)
!
interface Port-channel1
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
```

**Layer 3 EtherChannel:**
```
interface range GigabitEthernet1/0/23 - 24
 no switchport
 channel-group 2 mode active
!
interface Port-channel2
 no switchport
 ip address 10.0.0.1 255.255.255.252
```

Requirements for bundling: matching speed/duplex, matching mode (access/trunk, same VLANs), same channel-group mode on both sides (active/active or active/passive — never passive/passive).

Verify:
```
show etherchannel summary
show etherchannel port-channel
show interfaces port-channel 1
show lacp neighbor
```

---

## 2.5 Interpret basic operations of Rapid PVST+ STP

**2.5.a Root port / root bridge / other port names:**
- **Root bridge** — the switch with the lowest Bridge ID (priority + MAC) for a VLAN; elected automatically, or forced:
```
spanning-tree vlan 10 root primary          ! sets priority to 24576 (or lower than current root)
spanning-tree vlan 10 root secondary        ! sets priority to 28672
! or manually:
spanning-tree vlan 10 priority 4096
```
- **Root port** — the one port on a non-root switch with the lowest-cost path back to the root bridge.
- **Designated port** — the forwarding port on each segment responsible for forwarding traffic toward the root.
- **Non-designated/blocking port** — receives BPDUs but does not forward, to prevent a loop.

**2.5.b Port states and roles (Rapid PVST+ / 802.1w):**

| State | Forwards data | Learns MACs |
|---|---|---|
| Discarding (blocking/listening merged) | No | No |
| Learning | No | Yes |
| Forwarding | Yes | Yes |

Roles: Root, Designated, Alternate (backup to root port), Backup (backup to designated port).

**2.5.c PortFast** — skips listening/learning and goes straight to forwarding; use only on ports connected to end hosts, never to another switch:
```
interface GigabitEthernet1/0/5
 spanning-tree portfast edge
```

**2.5.d Root guard, loop guard, BPDU filter, BPDU guard:**
```
! Root guard — prevents a downstream/access-layer switch from becoming root; place on ports facing away from the core
interface GigabitEthernet1/0/24
 spanning-tree guard root

! Loop guard — prevents an alternate/root port from becoming designated (looping) when BPDUs stop arriving unidirectionally; typically enabled globally on point-to-point links
spanning-tree loopguard default

! BPDU guard — err-disables a PortFast port if it receives a BPDU (someone plugged in a switch/hub where only a host should be)
interface GigabitEthernet1/0/5
 spanning-tree bpduguard enable
! or globally, applies only to portfast ports:
spanning-tree portfast bpduguard default

! BPDU filter — suppresses sending/processing BPDUs on a port entirely (use sparingly — can create loops if misapplied)
interface GigabitEthernet1/0/5
 spanning-tree bpdufilter enable
```

Verify:
```
show spanning-tree summary
show spanning-tree vlan 10
show spanning-tree interface GigabitEthernet1/0/24 detail
```

---

## 2.6 Cisco Wireless Architectures and AP modes

| Architecture | Description |
|---|---|
| **Autonomous** | Each AP is independently configured/managed; no controller. Simple, doesn't scale. |
| **Lightweight + WLC** | APs (LAPs) tunnel control and (usually) data traffic to a Wireless LAN Controller via **CAPWAP**. Centralized RF, security, and roaming management. |
| **Cloud-based (Meraki-style)** | APs managed from a cloud dashboard; no on-prem controller hardware. |
| **Embedded/Mobility Express** | Controller function runs on one of the APs itself — no separate WLC appliance. |

**AP modes:** Local (normal client-serving), FlexConnect (can switch traffic locally at a remote site if WAN to WLC drops), Monitor (RF/IDS scanning only, no client service), Sniffer, Rogue Detector, Bridge/Mesh, SE-Connect.

---

## 2.7 Physical infrastructure connections of WLAN components

- **AP ↔ Access switch port:** typically an access port (single-SSID/VLAN designs) or trunk port (multiple SSIDs mapped to multiple VLANs), often PoE-powered.
- **WLC ↔ Distribution/Core switch:** usually a trunk carrying the AP-management VLAN + all WLAN client VLANs; on physical WLC appliances the uplink ports are commonly bundled into a **LAG (LACP)** to the switch for redundancy/throughput — configure LACP identically on the switch side (see 2.4).
- **CAPWAP tunnel:** logical control+data tunnel between AP and WLC, riding over the regular IP network (UDP 5246 control / 5247 data).

---

## 2.8 Network device management access

| Method | Port | Security notes |
|---|---|---|
| **Console** | Physical, out-of-band | Set `login local` + `exec-timeout`; physically secure the device. |
| **Telnet** | TCP 23 | Cleartext — disable it (`transport input ssh` only). |
| **SSH** | TCP 22 | Encrypted — standard for CLI remote access (see 4.8). |
| **HTTP** | TCP 80 | Cleartext GUI — disable (`no ip http server`). |
| **HTTPS** | TCP 443 | Encrypted GUI — use if a web UI is required (`ip http secure-server`). |
| **TACACS+** | TCP 49 | Cisco-preferred for device-administration AAA; encrypts the entire payload; separates authentication/authorization/accounting. |
| **RADIUS** | UDP 1812/1813 | Common for network-access AAA (802.1X, VPN); encrypts only the password in the packet. |
| **Cloud-managed** | HTTPS to vendor cloud (e.g. Meraki, Catalyst Center/DNA cloud) | Device phones home to a cloud controller/dashboard instead of being managed box-by-box. |

---

## 2.9 Interpret the wireless LAN GUI configuration for client connectivity

Typical WLC GUI workflow (Catalyst 9800 / AireOS-style):

1. **WLANs → Create New** — set Profile Name, SSID, WLAN ID.
2. **General tab** — enable the WLAN, assign to an Interface/Interface Group (maps to a VLAN).
3. **Security tab:**
   - Layer 2: select WPA2/WPA3, AES, and either PSK (enter the pre-shared key) or 802.1X (point to a configured RADIUS server for enterprise auth).
   - Layer 3 (if used): web auth, etc.
   - AAA servers: attach the RADIUS server(s) defined under Security → AAA.
4. **QoS tab** — assign a QoS profile (Platinum/Gold/Silver/Bronze) to prioritize voice/video traffic over best-effort data.
5. **Advanced tab** — settings like session timeout, client band-select, DHCP address assignment requirement, AP groups the WLAN is broadcast on.
6. **Apply/Save**, then confirm the SSID is broadcasting on the intended AP group and a test client can associate, authenticate, and pull a DHCP address in the correct VLAN.

See 5.10 for the WPA2-PSK-specific walkthrough.
