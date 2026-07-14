# Server1 — GUI configuration

Server1 sits on ACC2 Gi0/5 in VLAN 30 (SERVERS). Set it up first — most
other devices' logging/NTP/DHCP config points at it.

## IP configuration

Desktop → IP Configuration (or the Config tab → interface, depending on
your PT version):

```
IP Address:      192.168.30.10
Subnet Mask:      255.255.255.0
Default Gateway:  192.168.30.1        (the HSRP VIP for VLAN 30)
DNS Server:       192.168.30.10       (itself)
```

## Services tab

### DHCP

Add three pools/scopes (name them anything memorable — `DATA`, `VOICE`,
`WIRELESS`):

| Pool | Network | Mask | Default Gateway | DNS | Start / range |
|---|---|---|---|---|---|
| DATA | 192.168.10.0 | 255.255.255.0 | 192.168.10.1 | 192.168.30.10 | .11–.254 |
| VOICE | 192.168.20.0 | 255.255.255.0 | 192.168.20.1 | 192.168.30.10 | .11–.254 |
| WIRELESS | 192.168.50.0 | 255.255.255.0 | 192.168.50.1 | 192.168.30.10 | .11–.254 |

Turn the DHCP service **On**. These are reached across VLANs via the
`ip helper-address 192.168.30.10` relay configured on D1's and D2's SVIs —
that's the objective-4.6 lab in action, so if leases aren't working, check
the relay config before touching the server.

### DNS

Add at least one A record so name resolution has something to test, e.g.:

```
Name: server1.lab.local    Type: A    Address: 192.168.30.10
Name: r1.lab.local         Type: A    Address: 203.0.113.5
```

Turn the DNS service **On**.

### Syslog

Turn the Syslog service **On** (no further config needed) — it listens on
UDP 514 and every infra device's `logging host 192.168.30.10` sends here.
Open the syslog viewer after making a config change on any switch/router
(e.g. `shutdown`/`no shutdown` an interface) to confirm messages arrive.

### NTP

Optional — you don't need a second NTP source since ISP0 is already acting
as `ntp master`. If your PT version's server NTP service is easy to enable,
turning it on doesn't hurt, but nothing in this lab is configured to use it
(the hierarchy is ISP0 → R1 → D1/D2 → ACC1/ACC2/R2).

### TFTP

Turn the TFTP service **On** — used to practice objective 4.9
(`copy running-config tftp://192.168.30.10/...`) and IOS backup/restore
from any device.

### HTTP (optional)

If you want to exercise the `permit tcp any host 203.0.113.5 eq 80` line in
R1's `OUTSIDE-IN` ACL, enable the server's HTTP service too, otherwise that
ACL line is just inert (harmless either way).

## Verify

From any PC: `ipconfig /all` should show a 192.168.10/20/50.x address, GW,
and DNS server 192.168.30.10 depending on which VLAN it's in.
`nslookup server1.lab.local` should resolve.
