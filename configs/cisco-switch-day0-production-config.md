# Cisco Catalyst Switch — Day-0 Production Configuration

A complete, ordered command set to take a brand-new Cisco IOS/IOS-XE switch
from factory default to a secured, functional device ready to join a live
network. Commands are grouped by stage and annotated with the reasoning
behind each block. Replace anything in `<angle brackets>` with your site's
actual values.

Tested against Catalyst 9300/3850/2960-X style IOS/IOS-XE syntax. Minor
platform differences (e.g. `switchport` availability on routed platforms,
license/`app-hosting` steps) may apply — check your platform's config guide.

---

## 0. Before you type anything

- Rack, ground, and power the switch; connect console cable (RJ45/USB) at
  9600 8N1.
- Confirm boot image / IOS version with `show version` and upgrade first if
  the shipped image is outdated (do this before production cutover, not
  after).
- Have ready: hostname, mgmt VLAN + IP/mask/gateway, NTP servers, syslog
  server, AAA/RADIUS or TACACS+ server (if used), local admin credentials,
  domain name, VLAN plan, uplink/trunk plan.

---

## 1. Global identity & basic hardening

```
enable
configure terminal

hostname <SW-HOSTNAME>
ip domain-name <yourdomain.com>

! Local admin account (used for SSH/console fallback — pair with AAA/TACACS below if available)
username <admin-user> privilege 15 algorithm-type scrypt secret <StrongPassword!>

! Enable secret (never use "enable password" — it's reversible)
enable secret <StrongEnableSecret!>

! Encrypt any remaining plaintext passwords in the config
service password-encryption

! Minimum password length enforced locally
security passwords min-length 10

! Legal/warning banners (required in most orgs for AUP enforcement)
banner motd ^C
***********************************************************************
* Authorized access only. All activity is logged and monitored.      *
* Disconnect immediately if you are not an authorized user.          *
***********************************************************************
^C
```

---

## 2. Disable insecure/unnecessary services

```
no ip http server
no ip http secure-server
no ip bootp server
no service pad
no cdp run
! ^ disable CDP globally only if not needed for phones/neighbor discovery;
!   otherwise leave enabled and disable per-port on untrusted/uplink ports:
!   interface <if> -> no cdp enable

no service dhcp
ip domain-lookup             ! use "no ip domain-lookup" if you don't want the switch resolving DNS (prevents delay on typos)
```

---

## 3. Time & logging (get this right before anything else — every other log depends on it)

```
clock timezone <TZ> <offset>
clock summer-time <TZ_DST> recurring

ntp server <ntp1-ip> prefer
ntp server <ntp2-ip>

service timestamps log datetime msec localtime show-timezone
service timestamps debug datetime msec localtime show-timezone

logging buffered 16384 informational
logging host <syslog-server-ip>
logging trap informational
logging source-interface <mgmt-interface>
```

---

## 4. Remote access — SSH only, no Telnet

```
! SSH requires domain-name (set above) + RSA keys
crypto key generate rsa modulus 2048
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3

line vty 0 15
 transport input ssh
 login local
 exec-timeout 10 0
 logging synchronous

line con 0
 login local
 exec-timeout 10 0
 logging synchronous

! Restrict VTY access to a management subnet only
ip access-list standard MGMT-ACCESS
 permit <mgmt-subnet> <wildcard-mask>
 deny   any log
line vty 0 15
 access-class MGMT-ACCESS in
```

If you have TACACS+/RADIUS (recommended for a live environment over
local-only accounts):

```
aaa new-model
tacacs server TACACS1
 address ipv4 <tacacs-ip>
 key <shared-secret>
aaa group server tacacs+ TACACS-GROUP
 server name TACACS1
aaa authentication login default group TACACS-GROUP local
aaa authorization exec default group TACACS-GROUP local
aaa authorization console
aaa accounting exec default start-stop group TACACS-GROUP
aaa accounting commands 15 default start-stop group TACACS-GROUP
```

---

## 5. Management interface

Best practice: don't manage the switch over VLAN 1. Create a dedicated
management VLAN.

```
vlan <mgmt-vlan-id>
 name MGMT

interface vlan <mgmt-vlan-id>
 description Switch Management
 ip address <mgmt-ip> <mgmt-mask>
 no shutdown

ip default-gateway <gateway-ip>       ! Layer 2 switch only
! --- OR, if this is a Layer 3 switch/multilayer switch ---
ip routing
ip route 0.0.0.0 0.0.0.0 <gateway-ip>
```

---

## 6. SNMP (v3 — avoid v2c community strings in a live environment)

```
snmp-server group SNMP-ADMINS v3 priv
snmp-server user snmpadmin SNMP-ADMINS v3 auth sha <auth-pass> priv aes 128 <priv-pass>
snmp-server contact <noc-contact>
snmp-server location <site/rack-id>
snmp-server host <nms-ip> version 3 priv snmpadmin
```

---

## 7. VLAN plan

```
vlan 10
 name DATA
vlan 20
 name VOICE
vlan 30
 name SERVERS
vlan 999
 name UNUSED-PARKING
vlan 666
 name NATIVE-UNUSED       ! dedicated, unused native VLAN for trunk security
```

---

## 8. Access ports (end-user/device-facing)

Apply per port or via an interface range. Example: a standard user port with
voice VLAN:

```
interface range GigabitEthernet1/0/1 - 24
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 20
 switchport nonegotiate
 spanning-tree portfast edge
 spanning-tree bpduguard enable
 storm-control broadcast level 1.00
 storm-control action shutdown
 no cdp enable                        ! optional: disable on untrusted user ports
 no snmp trap link-status              ! optional: reduce trap noise on user ports

! Port security — lock ports to expected device counts, shut down on violation
 switchport port-security
 switchport port-security maximum 3
 switchport port-security violation restrict
 switchport port-security aging time 2
 switchport port-security aging type inactivity
 switchport port-security mac-address sticky
```

---

## 9. Trunk ports (uplinks/interswitch links)

```
interface range TenGigabitEthernet1/0/1 - 2
 description UPLINK-TO-CORE
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 666
 switchport trunk allowed vlan 10,20,30,<mgmt-vlan-id>
 switchport nonegotiate
 spanning-tree guard root                 ! on access-layer uplinks facing the core
 no shutdown
```

---

## 10. Spanning Tree

```
spanning-tree mode rapid-pvst
spanning-tree vlan 10,20,30 priority 32768     ! adjust per your root-bridge design; lower = more preferred
spanning-tree portfast bpduguard default
spanning-tree loopguard default
spanning-tree extend system-id
```

If this switch is meant to be the root bridge for these VLANs, use
`spanning-tree vlan <ids> root primary` instead of setting priority manually.

---

## 11. Layer 2 threat mitigation (recommended for any live network)

```
! DHCP Snooping — trust only the uplink toward the real DHCP server
ip dhcp snooping
ip dhcp snooping vlan 10,20,30
no ip dhcp snooping information option
interface range TenGigabitEthernet1/0/1 - 2
 ip dhcp snooping trust

! Dynamic ARP Inspection — relies on DHCP snooping database
ip arp inspection vlan 10,20,30
interface range TenGigabitEthernet1/0/1 - 2
 ip arp inspection trust

! IP Source Guard on access ports (optional, tighter security)
interface range GigabitEthernet1/0/1 - 24
 ip verify source
```

---

## 12. Unused ports — don't leave them live

```
interface range GigabitEthernet1/0/25 - 48
 switchport mode access
 switchport access vlan 999
 shutdown
```

---

## 13. Interface housekeeping

```
interface range GigabitEthernet1/0/1 - 48
 description <update per port — end device / uplink / etc>
```

---

## 14. Save and verify

```
copy running-config startup-config
```

Verification checklist:

```
show version
show ip interface brief
show vlan brief
show interfaces trunk
show spanning-tree summary
show port-security
show ip dhcp snooping
show logging
show ntp status
show ssh
show running-config | include aaa|logging|ntp|snmp
```

Confirm:
- SSH access works from a management host; Telnet is refused.
- `show clock detail` reflects correct time/timezone (NTP synced).
- Syslog entries are arriving at the syslog server.
- Trunk ports show the correct allowed VLANs and native VLAN mismatch
  warnings are absent (`show interfaces trunk` + check both ends match).
- No console/VTY sessions are left without `exec-timeout` set.

---

## Notes on scope

This gets a switch to a secured, functional baseline for production. Not
included (add as your environment requires): 802.1X/dot1x port
authentication, QoS/auto-QoS for voice, HSRP/VRRP if this is a first-hop
router, stacking/StackWise config, license registration (smart licensing),
and change-control/backup automation (e.g., RANCID, Oxidized, or a
config-backup TACACS+ accounting trail).
