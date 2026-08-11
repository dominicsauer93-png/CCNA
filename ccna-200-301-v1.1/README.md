# CCNA 200-301 v1.1 — Exam Blueprint Lab & Reference Notes

Hands-on configuration procedures and concept notes for every objective in
the official Cisco CCNA 200-301 v1.1 exam blueprint (120-minute exam:
network fundamentals, network access, IP connectivity, IP services,
security fundamentals, automation and programmability). Source blueprint:
`200301CCNAv1.1.pdf`.

Each file below covers one exam domain, numbered to match the blueprint
sections exactly, so you can study section-by-section and cross-reference
directly against Cisco's official guidelines.

| Domain | Weight | File |
|---|---|---|
| 1.0 Network Fundamentals | 20% | [`01-network-fundamentals.md`](01-network-fundamentals.md) |
| 2.0 Network Access | 20% | [`02-network-access.md`](02-network-access.md) |
| 3.0 IP Connectivity | 25% | [`03-ip-connectivity.md`](03-ip-connectivity.md) |
| 4.0 IP Services | 10% | [`04-ip-services.md`](04-ip-services.md) |
| 5.0 Security Fundamentals | 15% | [`05-security-fundamentals.md`](05-security-fundamentals.md) |
| 6.0 Automation and Programmability | 10% | [`06-automation-programmability.md`](06-automation-programmability.md) |

Every "Configure and verify" objective includes real IOS/IOS-XE CLI plus
the matching `show`/`debug` verification commands. "Describe/Explain/
Compare" objectives get concise reference tables and diagrams instead of
CLI, since they aren't hands-on configuration items on the exam.

## Related

- [`../configs/cisco-switch-day0-production-config.md`](../configs/cisco-switch-day0-production-config.md) —
  a complete, ordered Day-0 build for a new access switch in a live
  environment. Domains 2.0 and 5.0 above cross-reference it for the
  VLAN/trunk/STP/port-security/DHCP-snooping/DAI sections rather than
  repeating the full walkthrough.

## Suggested study/lab order

1. Build the fundamentals (1.0) and get comfortable with VLANs/trunking/STP
   on a real or simulated switch (2.0) — use Packet Tracer, GNS3, or EVE-NG
   if you don't have physical gear.
2. Layer in routing (3.0) — static routes first, then single-area OSPF.
3. Add IP services (4.0): NAT, NTP, DHCP relay, SSH access.
4. Harden it with security fundamentals (5.0): ACLs, port security, DHCP
   snooping/DAI, AAA.
5. Finish with automation concepts (6.0) — mostly recognition-level, review
   close to exam day.

For each domain, configure it in a lab, then run every verification command
listed and read the output until you can explain each field — that's the
level of understanding the exam expects.
