# WLC1 — GUI configuration (WPA2-PSK WLAN)

WLC1 connects to ACC1's trunk, carrying VLAN 99 (management/AP-manager)
and VLAN 50 (wireless client traffic). Exact menu wording varies between
Packet Tracer releases (AireOS-style vs. Catalyst 9800-style GUI) — the
steps below are the general workflow common to both.

## 1. Management IP

On first boot / Config tab → Controller → General (or the initial setup
wizard):

```
Management IP:      192.168.99.20
Subnet Mask:         255.255.255.0
Default Gateway:     192.168.99.1     (the HSRP VIP for VLAN 99)
```

## 2. Dynamic interface for the wireless VLAN

Controller → Interfaces → New:

```
Interface Name:   wireless-vlan50
VLAN ID:           50
IP Address:        192.168.50.5
Subnet Mask:        255.255.255.0
Gateway:            192.168.50.1     (the HSRP VIP for VLAN 50)
```

This is the interface client traffic gets bridged onto after leaving the
CAPWAP tunnel from AP1.

## 3. AP join

Once AP1 is cabled to ACC1 Gi0/5 (access port, VLAN 99) and powered on, it
should discover WLC1 automatically via CAPWAP (both are in VLAN 99/same
broadcast domain in this lab, which is the simplest discovery method). If
it doesn't join within a minute or two:
- Confirm AP1 has an IP in 192.168.99.0/24 (DHCP or static `192.168.99.30`,
  mask `255.255.255.0`, gateway `192.168.99.1`).
- Check Wireless → Access Points on the WLC — AP1 should appear once
  joined.

## 4. Create the WLAN (objective 5.10 — WPA2-PSK)

WLANs → Create New (or the `+` icon):

1. **General**
   - Profile Name: `CCNA-LAB-WIFI`
   - SSID: `CCNA-LAB-WIFI`
   - Status: Enabled
   - Interface/Interface Group: `wireless-vlan50`
2. **Security → Layer 2**
   - Layer 2 Security: `WPA2`
   - WPA2 Policy: `AES`
   - Auth Key Management: `PSK`
   - PSK: `Lab-WiFi123!` (ASCII)
3. **Security → Layer 3 / AAA**
   - Leave as None — no RADIUS needed for PSK-only.
4. **QoS** (if present in your version)
   - Leave default (Silver/Best Effort) — this lab doesn't have real voice
     traffic riding the wireless SSID.
5. **Advanced**
   - Leave defaults unless your PT version requires explicitly enabling
     "Allow AAA Override" or similar for the WLAN to broadcast — check
     Wireless → AP Groups / the AP's radio config if the SSID doesn't show
     up on Laptop0's scan list.
6. **Apply / Save.**

## 5. Connect the wireless client

On **Laptop0** → Desktop → PC Wireless (or the wireless NIC's config):

```
SSID:        CCNA-LAB-WIFI
Auth:        WPA2-PSK
Passphrase:  Lab-WiFi123!
```

It should associate, pull a DHCP lease from Server1 in the
`192.168.50.0/24` range (relayed via D1/D2's `ip helper-address` on the
VLAN 50 SVI), and be able to ping `192.168.50.1` (its HSRP gateway).

## Verify

```
show wlan summary
show ap summary
show client summary
```
(Run on the WLC CLI if your PT version exposes one; otherwise the
equivalent GUI pages under Monitor/Wireless show the same state.)
