#!/usr/bin/env python3
"""Build the CML lab files from the device configs.

- ccna-lab.yaml                  full lab (16 nodes), configs in configs/
- free/<lab>/<lab>.yaml           3 small labs (5 nodes max, fits CML-Free),
                                  configs in free/<lab>/configs/

Edit a config, then run:  python3 build_topology.py
"""

from pathlib import Path

import yaml

HERE = Path(__file__).parent

IOSV_PORTS = [f"GigabitEthernet0/{i}" for i in range(4)]
IOSVL2_PORTS = [f"GigabitEthernet{s}/{p}" for s in range(2) for p in range(4)]


def host_config(name, static=None):
    """Alpine boot script: DHCP by default, or a static address."""
    lines = [
        "# this is a shell script which will be sourced at boot",
        f"hostname {name}",
        "USERNAME=cisco",
        "PASSWORD=cisco",
        "ip link set eth0 up",
    ]
    if static:
        addr, gw = static
        lines += [f"ip addr add {addr} dev eth0", f"ip route add default via {gw}"]
    else:
        lines += ["udhcpc -i eth0 -b -t 10 -T 3"]
    return "\n".join(lines) + "\n"


# label: (node_definition, x, y, config file or Alpine boot script)
NODES = {
    "ISP0": ("iosv", 0, -400, "isp0.txt"),
    "R1-EDGE": ("iosv", 0, -250, "r1-edge.txt"),
    "SW-DIST1": ("iosvl2", -200, -80, "sw-dist1.txt"),
    "SW-DIST2": ("iosvl2", 200, -80, "sw-dist2.txt"),
    "R2-BRANCH": ("iosv", 0, 60, "r2-branch.txt"),
    "SW-ACC1": ("iosvl2", -300, 150, "sw-acc1.txt"),
    "SW-ACC2": ("iosvl2", 300, 150, "sw-acc2.txt"),
    "SERVER1": ("iosv", 450, 320, "server1.txt"),
    "PC1": ("alpine", -500, 320, host_config("PC1")),
    "PC2": ("alpine", -380, 320, host_config("PC2")),
    "PC-ADMIN": ("alpine", -260, 320, host_config("PC-ADMIN")),
    "PC-WIFI": ("alpine", -140, 320, host_config("PC-WIFI")),
    "PC3": ("alpine", 90, 320, host_config("PC3")),
    "PC4": ("alpine", 210, 320, host_config("PC4")),
    "PC-VOICE": ("alpine", 330, 320, host_config("PC-VOICE")),
    "PC5": ("alpine", 0, 200, host_config("PC5")),
}

# (node A, port A, node B, port B)
LINKS = [
    ("ISP0", "GigabitEthernet0/0", "R1-EDGE", "GigabitEthernet0/0"),
    ("R1-EDGE", "GigabitEthernet0/1", "SW-DIST1", "GigabitEthernet0/0"),
    ("R1-EDGE", "GigabitEthernet0/2", "SW-DIST2", "GigabitEthernet0/0"),
    ("SW-DIST1", "GigabitEthernet0/1", "R2-BRANCH", "GigabitEthernet0/0"),
    ("SW-DIST2", "GigabitEthernet0/1", "R2-BRANCH", "GigabitEthernet0/1"),
    ("SW-DIST1", "GigabitEthernet0/2", "SW-DIST2", "GigabitEthernet0/2"),
    ("SW-DIST1", "GigabitEthernet0/3", "SW-DIST2", "GigabitEthernet0/3"),
    ("SW-DIST1", "GigabitEthernet1/0", "SW-ACC1", "GigabitEthernet0/0"),
    ("SW-DIST1", "GigabitEthernet1/1", "SW-ACC1", "GigabitEthernet0/1"),
    ("SW-DIST2", "GigabitEthernet1/0", "SW-ACC2", "GigabitEthernet0/0"),
    ("SW-DIST2", "GigabitEthernet1/1", "SW-ACC2", "GigabitEthernet0/1"),
    ("R2-BRANCH", "GigabitEthernet0/2", "PC5", "eth0"),
    ("SW-ACC1", "GigabitEthernet0/2", "PC1", "eth0"),
    ("SW-ACC1", "GigabitEthernet0/3", "PC2", "eth0"),
    ("SW-ACC1", "GigabitEthernet1/0", "PC-ADMIN", "eth0"),
    ("SW-ACC1", "GigabitEthernet1/1", "PC-WIFI", "eth0"),
    ("SW-ACC2", "GigabitEthernet0/2", "PC3", "eth0"),
    ("SW-ACC2", "GigabitEthernet0/3", "PC4", "eth0"),
    ("SW-ACC2", "GigabitEthernet1/0", "SERVER1", "GigabitEthernet0/0"),
    ("SW-ACC2", "GigabitEthernet1/1", "PC-VOICE", "eth0"),
]

DHCP_PC1 = host_config("PC1")

# Small labs for CML-Free (5 nodes max). Same addressing as the full lab.
FREE_LABS = {
    "lab1-switching": {
        "title": "CCNA-LAB 1 - Switching (CML-Free)",
        "description": "VLANs, trunks, EtherChannel (LACP), Rapid PVST+, HSRP, "
                       "inter-VLAN routing, DHCP snooping, DAI and port security.",
        "nodes": {
            "SW-DIST1": ("iosvl2", -200, -80, "sw-dist1.txt"),
            "SW-DIST2": ("iosvl2", 200, -80, "sw-dist2.txt"),
            "SW-ACC1": ("iosvl2", -200, 150, "sw-acc1.txt"),
            "SW-ACC2": ("iosvl2", 200, 150, "sw-acc2.txt"),
            "PC1": ("alpine", -200, 320, DHCP_PC1),
        },
        "links": [
            ("SW-DIST1", "GigabitEthernet0/2", "SW-DIST2", "GigabitEthernet0/2"),
            ("SW-DIST1", "GigabitEthernet0/3", "SW-DIST2", "GigabitEthernet0/3"),
            ("SW-DIST1", "GigabitEthernet1/0", "SW-ACC1", "GigabitEthernet0/0"),
            ("SW-DIST1", "GigabitEthernet1/1", "SW-ACC1", "GigabitEthernet0/1"),
            ("SW-DIST2", "GigabitEthernet1/0", "SW-ACC2", "GigabitEthernet0/0"),
            ("SW-DIST2", "GigabitEthernet1/1", "SW-ACC2", "GigabitEthernet0/1"),
            ("SW-ACC1", "GigabitEthernet0/2", "PC1", "eth0"),
        ],
    },
    "lab2-routing": {
        "title": "CCNA-LAB 2 - Routing & edge (CML-Free)",
        "description": "OSPF (p2p + DR/BDR), static and floating static routes, "
                       "NAT/PAT, NTP, extended ACL, HSRP.",
        "nodes": {
            "ISP0": ("iosv", 0, -400, "isp0.txt"),
            "R1-EDGE": ("iosv", 0, -250, "r1-edge.txt"),
            "SW-DIST1": ("iosvl2", -200, -80, "sw-dist1.txt"),
            "SW-DIST2": ("iosvl2", 200, -80, "sw-dist2.txt"),
            "R2-BRANCH": ("iosv", 0, 100, "r2-branch.txt"),
        },
        "links": [
            ("ISP0", "GigabitEthernet0/0", "R1-EDGE", "GigabitEthernet0/0"),
            ("R1-EDGE", "GigabitEthernet0/1", "SW-DIST1", "GigabitEthernet0/0"),
            ("R1-EDGE", "GigabitEthernet0/2", "SW-DIST2", "GigabitEthernet0/0"),
            ("SW-DIST1", "GigabitEthernet0/1", "R2-BRANCH", "GigabitEthernet0/0"),
            ("SW-DIST2", "GigabitEthernet0/1", "R2-BRANCH", "GigabitEthernet0/1"),
            ("SW-DIST1", "GigabitEthernet0/2", "SW-DIST2", "GigabitEthernet0/2"),
            ("SW-DIST1", "GigabitEthernet0/3", "SW-DIST2", "GigabitEthernet0/3"),
        ],
    },
    "lab3-services": {
        "title": "CCNA-LAB 3 - Services (CML-Free)",
        "description": "DHCP relay, DNS, NTP, SSH + VTY ACL, SNMPv3, syslog "
                       "config, HTTP/TFTP, DHCP snooping and DAI.",
        "nodes": {
            "R1-EDGE": ("iosv", 0, -250, "r1-edge.txt"),
            "SW-DIST1": ("iosvl2", 0, -80, "sw-dist1.txt"),
            "SW-ACC1": ("iosvl2", 0, 100, "sw-acc1.txt"),
            "PC1": ("alpine", -150, 260, DHCP_PC1),
            "SERVER1": ("iosv", 150, 260, "server1.txt"),
        },
        "links": [
            ("R1-EDGE", "GigabitEthernet0/1", "SW-DIST1", "GigabitEthernet0/0"),
            ("SW-DIST1", "GigabitEthernet1/0", "SW-ACC1", "GigabitEthernet0/0"),
            ("SW-DIST1", "GigabitEthernet1/1", "SW-ACC1", "GigabitEthernet0/1"),
            ("SW-ACC1", "GigabitEthernet0/2", "PC1", "eth0"),
            ("SW-ACC1", "GigabitEthernet1/2", "SERVER1", "GigabitEthernet0/0"),
        ],
    },
}


class _Literal(str):
    pass


yaml.add_representer(
    _Literal, lambda d, s: d.represent_scalar("tag:yaml.org,2002:str", s, style="|")
)


def build(title, description, node_defs, link_defs, config_dir, notes):
    nodes, iface_ids = [], {}
    for n, (label, (ndef, x, y, cfg)) in enumerate(node_defs.items()):
        node_id = f"n{n}"
        if ndef == "alpine":
            ports, config = ["eth0"], cfg
        else:
            ports = IOSV_PORTS if ndef == "iosv" else IOSVL2_PORTS
            config = (config_dir / cfg).read_text()
        interfaces = []
        if ndef != "alpine":
            interfaces.append({"id": "i0", "label": "Loopback0", "type": "loopback"})
        for slot, port in enumerate(ports):
            iid = f"i{len(interfaces)}"
            interfaces.append({"id": iid, "label": port, "slot": slot, "type": "physical"})
            iface_ids[(label, port)] = (node_id, iid)
        nodes.append({
            "id": node_id,
            "label": label,
            "node_definition": ndef,
            "x": x,
            "y": y,
            "configuration": _Literal(config),
            "tags": [],
            "interfaces": interfaces,
        })

    links = []
    for n, (a, pa, b, pb) in enumerate(link_defs):
        n1, i1 = iface_ids[(a, pa)]
        n2, i2 = iface_ids[(b, pb)]
        links.append({"id": f"l{n}", "n1": n1, "i1": i1, "n2": n2, "i2": i2,
                      "label": f"{a} {pa} <-> {b} {pb}"})

    return {
        "lab": {
            "title": title,
            "description": description,
            "notes": notes,
            "version": "0.2.2",
        },
        "nodes": nodes,
        "links": links,
        "annotations": [],
    }


def write(path, topology):
    path.write_text(yaml.dump(topology, sort_keys=False, width=1000))
    print(f"wrote {path.relative_to(HERE)}")


if __name__ == "__main__":
    write(HERE / "ccna-lab.yaml", build(
        "CCNA-LAB (CML)",
        "CML port of the CCNA Packet Tracer lab: OSPF, HSRP, EtherChannel, STP, "
        "NAT, static/floating routes, DHCP relay, ACLs and L2 security.",
        NODES, LINKS, HERE / "configs", "See cml-lab/README.md in the CCNA repo."))
    for name, lab in FREE_LABS.items():
        lab_dir = HERE / "free" / name
        assert len(lab["nodes"]) <= 5, f"{name} exceeds the CML-Free node limit"
        write(lab_dir / f"{name}.yaml", build(
            lab["title"], lab["description"], lab["nodes"], lab["links"],
            lab_dir / "configs", "See cml-lab/free/README.md in the CCNA repo."))
