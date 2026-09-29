#!/usr/bin/env python3
"""Build ccna-lab.yaml (CML topology) from the device configs in configs/.

Edit a config in configs/, then run:  python3 build_topology.py
"""

from pathlib import Path

import yaml

HERE = Path(__file__).parent
CONFIGS = HERE / "configs"

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


# label: (node_definition, x, y, config source)
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


class _Literal(str):
    pass


yaml.add_representer(
    _Literal, lambda d, s: d.represent_scalar("tag:yaml.org,2002:str", s, style="|")
)


def build():
    nodes, iface_ids = [], {}
    for n, (label, (ndef, x, y, cfg)) in enumerate(NODES.items()):
        node_id = f"n{n}"
        if ndef == "alpine":
            ports, config = ["eth0"], cfg
        else:
            ports = IOSV_PORTS if ndef == "iosv" else IOSVL2_PORTS
            config = (CONFIGS / cfg).read_text()
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
    for n, (a, pa, b, pb) in enumerate(LINKS):
        n1, i1 = iface_ids[(a, pa)]
        n2, i2 = iface_ids[(b, pb)]
        links.append({"id": f"l{n}", "n1": n1, "i1": i1, "n2": n2, "i2": i2,
                      "label": f"{a} {pa} <-> {b} {pb}"})

    return {
        "lab": {
            "title": "CCNA-LAB (CML)",
            "description": "CML port of the CCNA Packet Tracer lab: OSPF, HSRP, "
                           "EtherChannel, STP, NAT, static/floating routes, DHCP relay, "
                           "ACLs and L2 security.",
            "notes": "See cml-lab/README.md in the CCNA repo.",
            "version": "0.2.2",
        },
        "nodes": nodes,
        "links": links,
        "annotations": [],
    }


if __name__ == "__main__":
    out = HERE / "ccna-lab.yaml"
    out.write_text(yaml.dump(build(), sort_keys=False, width=1000))
    print(f"wrote {out}")
