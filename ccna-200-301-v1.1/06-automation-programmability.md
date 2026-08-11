# 6.0 Automation and Programmability (10%)

Reference material mapped to CCNA 200-301 v1.1 blueprint section 6.0. This
domain is conceptual/comparative rather than CLI-configuration heavy — the
exam tests recognition and understanding, not hands-on scripting depth.

---

## 6.1 How automation impacts network management

Traditional CLI, box-by-box management doesn't scale: config drift between devices, slow/manual/error-prone changes, no single source of truth. Automation (scripts, Ansible, controllers, APIs) enables:
- Consistent, repeatable configuration pushed from a single source of truth (often version-controlled).
- Faster provisioning (minutes instead of hours per device).
- Reduced human error from manual CLI typos.
- Easier compliance/audit — config state can be validated and drift detected automatically.

---

## 6.2 Traditional networks vs. controller-based networking

| | Traditional | Controller-based (SDN) |
|---|---|---|
| Configuration | Per-device CLI, distributed | Centralized on a controller, pushed to devices |
| Control plane | Distributed — every device runs its own routing/switching logic | Often centralized/abstracted — controller has network-wide visibility |
| Management | Manual or per-device scripts | API-driven (RESTCONF/NETCONF/REST) from one management point |
| Example | Manually configuring VLANs on 50 switches | Cisco DNA Center/Catalyst Center pushing an intent-based policy to the whole fabric |

---

## 6.3 Controller-based, software-defined architecture

- **Underlay** — the physical network (routers/switches and their real links) providing basic IP reachability between devices.
- **Overlay** — a logical network built on top of the underlay using tunneling/encapsulation (e.g. VXLAN in Cisco SD-Access), carrying the actual user traffic and policy independent of the physical topology.
- **Fabric** — the combination of underlay + overlay + a controller managing them as one cohesive, policy-driven system (e.g. Cisco SD-Access, ACI).

**6.3.a Separation of control plane and data plane:**
- **Control plane** — decides *how* traffic should be forwarded (routing/reachability information); in SDN this logic is centralized on the controller.
- **Data plane** — actually forwards the traffic based on decisions handed down from the control plane; stays distributed on the switches/routers (fast-path hardware forwarding).
- This separation lets the controller have a global view and push consistent policy, while forwarding still happens locally and fast.

**6.3.b Northbound and Southbound APIs:**
- **Northbound API** — between the controller and applications/orchestration/GUI *above* it (e.g. a REST API a provisioning app calls to request a new VLAN). Human/application-facing.
- **Southbound API** — between the controller and the physical devices *below* it (e.g. NETCONF, OpenFlow, CLI/SSH, SNMP) used to actually push configuration/collect state to/from the network gear.

```
      [ Applications / GUI / Orchestration ]
                    ↑  Northbound API (REST)
              [ Controller / SDN Fabric ]
                    ↓  Southbound API (NETCONF, OpenFlow, CLI)
      [ Routers / Switches / APs — data plane ]
```

---

## 6.4 AI (generative and predictive) and machine learning in network operations

- **Predictive AI/ML** — analyzes historical telemetry (interface errors, utilization trends, client roaming patterns) to forecast issues before they cause an outage — e.g. predicting AP RF degradation or link saturation.
- **Generative AI** — used in tools like Cisco AI Assistant/Catalyst Center copilots to translate natural-language intent into device configuration, summarize logs/incidents, or answer "why is this happening" style troubleshooting questions.
- Both feed into **AIOps**: automated anomaly detection, root-cause analysis, and remediation suggestions layered on top of the automation/controller stack described in 6.1-6.3.

---

## 6.5 Characteristics of REST-based APIs

| Aspect | Details |
|---|---|
| **Authentication types** | Basic auth (username/password, base64-encoded — weak alone), API key/token, OAuth2 (bearer token, most common for modern APIs), certificate-based. |
| **CRUD** | Create, Read, Update, Delete — the four basic data operations a REST API exposes. |
| **HTTP verbs** | `POST` = Create, `GET` = Read, `PUT`/`PATCH` = Update (PUT replaces the whole resource, PATCH partially updates), `DELETE` = Delete. |
| **Data encoding** | **JSON** is the overwhelming default for modern network APIs (RESTCONF, Meraki, DNA Center); XML is used by older/legacy APIs (NETCONF uses XML natively). |

Example REST call (conceptual):
```
POST https://controller.example.com/api/v1/vlans
Authorization: Bearer <token>
Content-Type: application/json

{
  "vlanId": 30,
  "name": "SERVERS"
}
```
Expected response: HTTP `201 Created` on success, `4xx` for client error (e.g. `401` unauthorized, `404` not found), `5xx` for server error.

---

## 6.6 Configuration management mechanisms — Ansible and Terraform

| Tool | Model | Typical use in networking |
|---|---|---|
| **Ansible** | Agentless, push-based, procedural-ish YAML "playbooks" run over SSH/API | Pushing configuration changes to existing network devices (VLANs, ACLs, interface config) in a repeatable, idempotent way. |
| **Terraform** | Agentless, declarative, state-file based ("desired end state") | Provisioning infrastructure (cloud resources, and increasingly network constructs via provider plugins) — you declare *what* should exist, Terraform figures out *how* to get there and tracks state. |

Example Ansible playbook snippet (network module, conceptual):
```yaml
- name: Configure access VLAN on switch port
  hosts: switches
  tasks:
    - name: Set VLAN 10 on Gi1/0/5
      cisco.ios.ios_config:
        lines:
          - switchport mode access
          - switchport access vlan 10
        parents: interface GigabitEthernet1/0/5
```

Example Terraform snippet (conceptual):
```hcl
resource "some_network_vlan" "servers" {
  vlan_id = 30
  name    = "SERVERS"
}
```

Key exam distinction: Ansible = *push config to existing devices, procedural, no persistent state file*; Terraform = *declare desired infrastructure state, tracks it in a state file, reconciles differences*.

---

## 6.7 Components of JSON-encoded data

```json
{
  "hostname": "SW-ACCESS-01",
  "managementIp": "192.168.10.5",
  "vlans": [10, 20, 30],
  "poeEnabled": true,
  "uplink": {
    "interface": "GigabitEthernet1/0/24",
    "mode": "trunk"
  }
}
```

| JSON element | Analogy |
|---|---|
| **Object** `{ }` | A set of key/value pairs (like a dictionary). |
| **Array** `[ ]` | An ordered list of values, e.g. `"vlans": [10, 20, 30]`. |
| **Key/value pair** | `"hostname": "SW-ACCESS-01"` — string keys always in double quotes. |
| **Data types** | String (`"..."`), Number (`10`), Boolean (`true`/`false`), Null (`null`), Object, Array. |

JSON is used pervasively in REST API request/response bodies (RESTCONF, DNA Center, Meraki Dashboard API, webhook payloads) — being able to read a JSON blob and identify the field you need is a practical exam and real-world skill.
