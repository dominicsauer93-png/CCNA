# 5.0 Security Fundamentals (15%)

Reference and hands-on lab procedures mapped to CCNA 200-301 v1.1 blueprint
section 5.0. Layer 2 hardening items cross-reference
`../configs/cisco-switch-day0-production-config.md`.

---

## 5.1 Key security concepts

| Term | Definition |
|---|---|
| **Threat** | A potential danger to an asset (e.g. an attacker, malware). |
| **Vulnerability** | A weakness that could be exploited (unpatched software, misconfiguration, weak password). |
| **Exploit** | The specific mechanism/code used to take advantage of a vulnerability. |
| **Mitigation technique** | The control applied to reduce risk — patching, ACLs, segmentation, port security, DHCP snooping/DAI, AAA, encryption, monitoring. |

---

## 5.2 Security program elements

- **User awareness/training** — phishing simulations, security policy acknowledgment, ongoing education; humans are consistently the weakest link.
- **Physical access control** — locked server rooms/racks, badge access, camera coverage, visitor logs, cable locks — no amount of logical (CLI) security matters if someone can walk up to the device console.

---

## 5.3 Configure and verify device access control using local passwords

```
enable secret <StrongEnableSecret!>
service password-encryption

username netadmin privilege 15 algorithm-type scrypt secret <StrongPassword!>

line console 0
 login local
 exec-timeout 10 0
 logging synchronous

line vty 0 15
 login local
 transport input ssh
 exec-timeout 10 0
```

Verify:
```
show running-config | section username
show running-config | section line
show privilege
```

---

## 5.4 Security password policy elements

- **Management** — centralize via AAA/TACACS+/RADIUS rather than shared local passwords wherever possible; rotate credentials; unique accounts per admin (no shared "admin" login) for accountability/audit trail.
- **Complexity** — minimum length (`security passwords min-length 10`), mixed character classes, no dictionary words, no default/vendor passwords left in place.
- **Alternatives to passwords alone:**
  - **MFA** — something you know (password) + something you have (OTP token/app) or are (biometric).
  - **Certificates** — public-key based device/user identity (e.g. 802.1X EAP-TLS), stronger than shared secrets.
  - **Biometrics** — fingerprint/facial recognition, typically for endpoint or physical access, not device CLI.

---

## 5.5 IPsec remote access and site-to-site VPNs

- **Site-to-site VPN** — encrypts traffic between two fixed gateways (e.g. HQ router ↔ branch router) transparently to the hosts behind them. Built from **IKEv2** (key exchange/negotiation) + **IPsec** (ESP for encryption/integrity of the actual data).
- **Remote access VPN** — an individual client (AnyConnect, native OS IPsec/IKEv2 client) connects inbound to a VPN headend/firewall, gets a virtual internal address, and reaches internal resources as if local.

Example site-to-site IKEv2/IPsec skeleton (conceptual — not exam-CLI-tested in depth, but know the building blocks):
```
crypto ikev2 keyring KEYRING
 peer BRANCH
  address 203.0.113.2
  pre-shared-key <secret>

crypto ikev2 profile IKEV2-PROFILE
 match identity remote address 203.0.113.2 255.255.255.255
 authentication local pre-share
 authentication remote pre-share
 keyring local KEYRING

crypto ipsec transform-set TSET esp-aes esp-sha-hmac
 mode tunnel

crypto map VPN-MAP 10 ipsec-isakmp
 set peer 203.0.113.2
 set transform-set TSET
 set ikev2-profile IKEV2-PROFILE
 match address VPN-TRAFFIC-ACL

interface GigabitEthernet0/1
 crypto map VPN-MAP
```

---

## 5.6 Configure and verify access control lists

**Standard ACL (source only, filters as close to the destination as possible):**
```
access-list 10 permit 192.168.10.0 0.0.0.255
access-list 10 deny any log

interface GigabitEthernet0/1
 ip access-group 10 out
```

**Extended ACL (source, destination, protocol, port — filter as close to the source as possible):**
```
ip access-list extended BLOCK-TELNET
 deny tcp any any eq 23
 permit tcp any any eq 22
 permit ip any any

interface GigabitEthernet0/1
 ip access-group BLOCK-TELNET in
```

**Named ACL with sequence numbers (easier to edit in place):**
```
ip access-list extended WEB-ONLY
 10 permit tcp 192.168.10.0 0.0.0.255 any eq 443
 20 permit tcp 192.168.10.0 0.0.0.255 any eq 80
 30 deny ip any any log
```

Key rules to remember for the exam: implicit `deny any` at the end of every ACL; processed top-down, first match wins; standard ACLs should be placed close to the destination, extended close to the source; one ACL per interface, per direction, per protocol.

Verify:
```
show access-lists
show ip interface GigabitEthernet0/1 | include access list
show access-lists WEB-ONLY
```

---

## 5.7 Configure and verify Layer 2 security features

**DHCP snooping** — builds a trusted binding table from a trusted (uplink) port; blocks rogue DHCP servers on untrusted (access) ports:
```
ip dhcp snooping
ip dhcp snooping vlan 10,20
interface GigabitEthernet1/0/24
 ip dhcp snooping trust
```

**Dynamic ARP Inspection (DAI)** — validates ARP packets against the DHCP snooping binding table to stop ARP spoofing/MITM; requires DHCP snooping to be running first:
```
ip arp inspection vlan 10,20
interface GigabitEthernet1/0/24
 ip arp inspection trust
```

**Port security** — restricts which/how many MAC addresses may use an access port:
```
interface GigabitEthernet1/0/5
 switchport mode access
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict     ! options: protect, restrict, shutdown
```

Verify:
```
show ip dhcp snooping
show ip dhcp snooping binding
show ip arp inspection
show port-security
show port-security interface GigabitEthernet1/0/5
show port-security address
```

(Full production baseline combining all three at once is in
`../configs/cisco-switch-day0-production-config.md` §8 and §11.)

---

## 5.8 Authentication, authorization, and accounting (AAA)

| Concept | Question it answers |
|---|---|
| **Authentication** | Who are you? (username/password, certificate, MFA) |
| **Authorization** | What are you allowed to do? (privilege level, command sets, VLAN assignment) |
| **Accounting** | What did you actually do? (command logging, session start/stop, for audit) |

```
aaa new-model
tacacs server TACACS1
 address ipv4 192.0.2.50
 key <shared-secret>
aaa group server tacacs+ TACACS-GROUP
 server name TACACS1

aaa authentication login default group TACACS-GROUP local
aaa authorization exec default group TACACS-GROUP local
aaa authorization console
aaa accounting exec default start-stop group TACACS-GROUP
aaa accounting commands 15 default start-stop group TACACS-GROUP
```
`local` as a fallback method ensures you're not locked out if the TACACS+ server is unreachable.

Verify:
```
show aaa servers
test aaa group TACACS-GROUP <user> <password> legacy
debug aaa authentication      ! lab only
```

---

## 5.9 Wireless security protocols

| Protocol | Encryption | Notes |
|---|---|---|
| **WEP** | RC4, static key | Broken — do not use. |
| **WPA** | TKIP (RC4-based, per-packet keying) | Legacy stopgap for WEP hardware; deprecated. |
| **WPA2** | AES-CCMP | Current baseline standard; PSK (pre-shared key) for small networks, 802.1X/Enterprise (RADIUS) for larger ones. |
| **WPA3** | AES-GCMP + **SAE** (Simultaneous Authentication of Equals, replaces PSK's 4-way handshake) | Resistant to offline dictionary attacks; WPA3-Personal and WPA3-Enterprise (with optional 192-bit mode). |

---

## 5.10 Configure and verify WLAN within the GUI using WPA2 PSK

Typical WLC GUI steps (Catalyst 9800 / AireOS-style):

1. **Configuration → Wireless → WLANs → Add New WLAN.**
2. **General:** set Profile Name and SSID, enable the WLAN, assign it to the correct Interface/VLAN.
3. **Security → Layer 2:**
   - Layer 2 Security = **WPA + WPA2**.
   - WPA2 Policy = **AES**.
   - Auth Key Mgmt = **PSK**.
   - Enter the pre-shared key (ASCII or hex).
4. **Security → Layer 3 / AAA:** leave as none/open for PSK-only designs (no RADIUS needed).
5. **QoS:** assign an appropriate profile if voice/video will share the SSID.
6. **Advanced:** confirm client band-select/DHCP-required settings as needed for the design.
7. **Apply**, then push/associate the WLAN to the correct **AP Group** so it broadcasts from the intended APs.
8. **Verify:** connect a test client, confirm WPA2-PSK negotiation succeeds, client receives a DHCP address in the mapped VLAN, and traffic passes.

CLI-equivalent verification on the WLC (where CLI access exists):
```
show wlan summary
show wlan id <id>
show ap summary
show client summary
```
