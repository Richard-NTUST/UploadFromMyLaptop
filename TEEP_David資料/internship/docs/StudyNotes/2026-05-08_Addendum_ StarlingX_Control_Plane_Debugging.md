---
title: 'Addendum: QA Review & Obstacles - StarlingX Control Plane Debugging'

---

# Addendum: QA Review & Obstacles - StarlingX Control Plane Debugging

**Phase:** Post-Ansible Bootstrap / Service Initialization
**Focus:** Service Manager (SM) "Enabling" Loops, HAProxy Routing, and API Endpoint Failures.

![WhatsApp Image 2026-05-05 at 8.39.48 PM](https://hackmd.io/_uploads/SJaLX1j0be.jpg)

### Executive Summary of Additions

Following the successful (or bypassed) Ansible bootstrap, the control plane immediately enters a deadlock state. The `sysinv-inv` service becomes trapped in an infinite `enabling` loop. Investigation reveals a cascade of architectural mismatches: port binding collisions between HAProxy and system APIs, HTTP/HTTPS protocol mismatches, and circular routing definitions within HAProxy's backend configurations.

---

### Additional Steps Executed (Control Plane Debugging)

#### a. Identifying the Port Conflict

The `sysinv-api` manual execution revealed an `OSError: [Errno 98] Address already in use`. We checked the port ownership.

```bash
sudo lsof -i :6385

```

**Output:**

```text
COMMAND      PID    USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
haproxy   168176 haproxy   15u  IPv4 504820      0t0  TCP oamcontroller:6385 (LISTEN)
sysinv-ap 246593  sysinv    7u  IPv4 767770      0t0  TCP controller-0:6385 (LISTEN)
sysinv-ap 246593  sysinv   10u  IPv4 767772      0t0  TCP pxecontroller:6385 (LISTEN)
...

```

*Note: HAProxy acts as a greedy gatekeeper on the floating IP, blocking the native services from successfully starting.*

#### b. Testing Keystone Routing (The "Empty Reply")

Testing the path through HAProxy to Keystone via HTTP revealed the connection was being dropped.

```bash
curl -v http://controller.internal:5000/v3

```

**Output:**

```text
* Trying 10.10.10.2:5000...
* Connected to controller.internal (10.10.10.2) port 5000 (#0)
> GET /v3 HTTP/1.1
> Host: controller.internal:5000
> User-Agent: curl/7.74.0
> Accept: */*
> 
* Empty reply from server
* Connection #0 to host controller.internal left intact
curl: (52) Empty reply from server

```

#### c. Uncovering the Protocol Mismatch & HAProxy Loop

Checking HAProxy logs revealed `SSL handshake failure`. Services were attempting plain HTTP against an HTTPS-enforced HAProxy port. Testing with HTTPS bypasses the handshake error but reveals a `502 Bad Gateway` because HAProxy was routing requests back to its own front door.

```bash
curl -vk https://controller.internal:5000/v3

```

**Output:**

```text
...
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384
* ALPN, server did not agree to a protocol
* Server certificate:
* subject: L=b7c0896b367e49eb98409d8b9d8f460e; O=starlingx; CN=system-restapi-gui
* SSL certificate verify ok.
> GET /v3 HTTP/1.1
...
< HTTP/1.1 502 Bad Gateway
< content-length: 107
< cache-control: no-cache
< content-type: text/html
< 
<html><body><h1>502 Bad Gateway</h1>
The server returned an invalid or incomplete response.
</body></html>

```

#### d. Validating the Keystone Backend directly

We bypassed HAProxy and verified the backend process was alive on the internal OAM IP.

```bash
curl -v http://192.168.204.1:5000/v3

```

**Output:**

```text
* Connected to 192.168.204.1 (192.168.204.1) port 5000 (#0)
> GET /v3 HTTP/1.1
...
< HTTP/1.1 200 OK
< Server: gunicorn
{"version": {"id": "v3.14", "status": "stable", "updated": "2020-04-07T00:00:00Z", "links": [{"rel": "self", "href": "http://192.168.204.1:5000/v3/"}], "media-types": [{"base": "application/json", "type": "application/vnd.openstack.identity-v3+json"}]}}

```

#### e. CLI "None" Output Debugging

After fixing the Keystone routing, `system host-list` started returning a literal `None`. Running it in debug mode revealed the CLI client was attempting to parse an HTML 503 error as JSON due to a dead backend.

```bash
system --debug host-list

```

**Output:**

```text
DEBUG (session:520) REQ: curl -g -i -X GET https://10.10.10.2:6385/v1/ihosts -H "Accept: application/json" -H "Content-Type: application/json" -H "User-Agent: cgtsclient" -H "X-Auth-Token: {SHA256}c8551245a6d08512a5c8f0ff6829ffda153ee0da08a481df41744d30c7454842"
DEBUG (connectionpool:973) Starting new HTTPS connection (1): 10.10.10.2:6385
DEBUG (connectionpool:452) https://10.10.10.2:6385 "GET /v1/ihosts HTTP/1.1" 503 107
DEBUG (session:551) RESP: [503] cache-control: no-cache content-length: 107 content-type: text/html
DEBUG (session:583) RESP BODY: Omitted, Content-Type is set to text/html. Only application/json responses have their bodies logged.
None

```

### Part II: Maintenance State Machine & Kubernetes Deadlocks

**Phase:** Post-API Recovery / Node Unlock
**Focus:** Maintenance Agent (MTC) RPC Timeouts, Kubernetes Taint Deadlocks, and Node "Intest" Recovery.

### Additional Steps Executed (Maintenance & K8s Debugging)

#### f. Bypassing HAProxy & The JSON Parser Panic

After restoring basic connectivity, the CLI returned a literal `'errors'` string. Debugging revealed the API was responding, but the CLI's weak parser failed to handle the error JSON.

```bash
system --debug host-list

```

**Output:**

```text
DEBUG (session:583) RESP BODY: {"message": "The server is currently unavailable. Please try again at a later time.<br /><br />
The Keystone service is temporarily unavailable.\n\n", "code": "503 Service Unavailable", "title": "Service Unavailable"}
'errors'

```

*Note: This proved the API was alive but unable to reach Keystone to validate the token.*

#### g. Identifying the Internal Identity Deadlock

We found that while the CLI could talk to the API, the **API could not talk to Keystone**. The `/etc/hosts` file had mapped `controller.internal` to the node IP (`.2`) instead of the Floating VIP (`.1`) where Keystone was listening.

**The Fix:**

```bash
sudo sed -i 's/192.168.204.2 controller.internal/192.168.204.1 controller.internal/g' /etc/hosts
sudo pkill -f sysinv-api

```

#### h. The Semantic Check Timeout

Once the API was healthy, attempting to `lock` or `unlock` the host resulted in a 60-second RPC timeout.

```bash
system host-unlock controller-0

```

**Output:**

```text
Timeout while waiting on RPC response - topic: "sysinv.conductor_manager", 
RPC method: "mtc_action_apps_semantic_checks" info: "<unknown>"

```

*Note: The Sysinv Conductor was hanging because it was waiting for Kubernetes to report that all platform applications (FluxCD) were healthy.*

#### i. Uncovering the Kubernetes Scheduling Deadlock

Investigation into the Kubernetes layer revealed that all pods were stuck in `Pending` because the node was both **Cordoned** and **Tainted**.

```bash
kubectl get pods -A | grep -v Running

```

**Output:**

```text
NAMESPACE      NAME                                        READY   STATUS    RESTARTS   AGE
cert-manager   cm-cert-manager-5d7fdf9b4-qv2cz             0/1     Pending   0          103m
flux-helm      helm-controller-76795d9bfc-tmf25            0/1     Pending   0          103m
...

```

**The Node Taint:**

```bash
kubectl describe node controller-0 | grep -i Taint
# Output: Taints: services=disabled:NoExecute

```

#### j. Breaking the Deadlock

To allow the pods to run (and thus satisfy the StarlingX semantic check), we had to manually override the node's scheduling state.

```bash
kubectl uncordon controller-0
kubectl taint nodes controller-0 services=disabled:NoExecute-

```

#### l. Service Manager (SM) Loopback Audit Mismatch

**The Issue:** `registry-token-server` and `haproxy` became trapped in an `enabling-throttle` loop. Due to the `/etc/hosts` bypass, the token server bound strictly to the management IP (`192.168.204.1`). However, the StarlingX Service Manager's hardcoded `/etc/init.d/` health-check scripts attempt to audit the service via the loopback address (`127.0.0.1`). The audit receives a `Connection refused`, assumes the service is dead, and violently kills the process.
**The Fix:** Implemented `iptables` NAT rules to intercept local loopback checks and route them to the bound management IP.

**Commands & Output:**

```bash
sudo sm-dump | grep -E "failed|throttle"

```

```text
haproxy                          enabled-active       enabling-throttle               
registry-token-server            enabled-active       enabling-throttle 

```

```bash
curl -k -v https://127.0.0.1:9002/

```

```text
* Trying 127.0.0.1:9002...
* connect to 127.0.0.1 port 9002 failed: Connection refused
* Failed to connect to 127.0.0.1 port 9002: Connection refused
* Closing connection 0
curl: (7) Failed to connect to 127.0.0.1 port 9002: Connection refused

```

```bash
# The Fix:
sudo iptables -t nat -I OUTPUT -d 127.0.0.1 -p tcp --dport 9002 -j DNAT --to-destination 192.168.204.1:9002
sudo iptables -t nat -I OUTPUT -d 127.0.0.1 -p tcp --dport 5000 -j DNAT --to-destination 192.168.204.1:5000

```

#### m. The Ceph Duplex Peer Deadlock (60-Second RPC Timeout)

**The Issue:** The `sysinv-conductor` consistently failed the `mtc_action_apps_semantic_checks` with a 60-second RPC timeout when attempting to unlock the node. Network socket analysis revealed that Ceph (the storage engine) was attempting to synchronize with `controller-1` (`192.168.204.3`) because the cluster was configured as `duplex`. Since `controller-1` was offline, the packets fell into a void, hanging in a `SYN-SENT` state until the Linux kernel's default 60-second TCP timeout expired, triggering the Conductor's own timeout limit.
**The Fix:** Added an `unreachable` route for the offline peer to force Ceph into an immediate "No route to host" fast-fail, allowing the semantic checks to bypass the storage deadlock.

**Commands & Output:**

```bash
sudo ss -tapn | grep SYN-SENT

```

```text
SYN-SENT   0      1               192.168.204.2:38618           192.168.204.3:6789  users:(("ceph",pid=702686,fd=14))                                                                                                                                                                                                                                                                                                                       
SYN-SENT   0      1               192.168.204.2:48908           192.168.204.3:6789  users:(("ceph",pid=686325,fd=14))                                                                                                                                                                                                                                                                                                                       
SYN-SENT   0      1               192.168.204.2:55456           192.168.204.3:3300  users:(("ceph",pid=654053,fd=12))
...
```

```bash
# The Fix:
sudo ip route add unreachable 192.168.204.3
sudo pkill -9 ceph
sudo pkill -9 -f sysinv-conductor

```
---

### Issues Found

### 1. Control Plane Block: HTTP/HTTPS Protocol Mismatch

**Location:** `/etc/sysinv/sysinv.conf` and HAProxy Config
**The Issue:** The default configuration writes internal authentication URLs (`auth_url` and `www_authenticate_uri`) as plain `http://controller.internal:5000`. However, HAProxy is configured to strictly enforce SSL (`https`) on these floating IPs. This causes an immediate `SSL handshake failure`, severing the Identity path and causing services like `sysinv` to hang indefinitely in an `enabling` state.
**The Fix:** Manually patch `sysinv.conf` via `sed` to replace `http://` with `https://` for all Keystone authentication URLs.

### 2. Routing Block: HAProxy Circular Backend Definitions

**Location:** `/etc/haproxy/haproxy.cfg`
**The Issue:** HAProxy is configured to listen on the floating IP (`10.10.10.2:5000`). However, its backend server definitions point to `controller.internal:5000`, which resolves *back* to the floating IP. This creates a routing loop where HAProxy forwards traffic to itself, resulting in a `502 Bad Gateway` error.
**The Fix:** Modify the `haproxy.cfg` backend configurations to point to the actual interface IPs where the underlying Python/Gunicorn processes are listening (e.g., `192.168.204.1` for Keystone).

### 3. Current Fatal Block: Sysinv-API Binding Failure & "None" Responses

**Location:** Node API Interface (`10.10.10.3:6385`)
**The Issue:** Despite the Service Manager (`sm-dump`) reporting `sysinv-inv` as `enabled-active`, the actual backend API process is dead or failing to bind to the expected management IP.

* A direct `curl` to the node IP (`http://10.10.10.3:6385`) returns **Connection refused**.
* Consequently, when the `system host-list` command queries the HAProxy front-door, HAProxy returns a `503 Service Unavailable` HTML page.
* The StarlingX Python CLI (`cgtsclient`) fails to parse this HTML body, throwing a silent error and printing a literal `None` to the console.
**The Fix:** Pending investigation. The `sysinv-api` process is currently unable to bind to `10.10.10.3`, likely due to a persistent ghost process or race condition during startup.

This session was a deep dive into the **Maintenance (MTC) State Machine** and the circular dependency between the **StarlingX Control Plane** and **Kubernetes Pod Scheduling**.

Here are the additions for your Markdown document, capturing the specific logs and architectural blocks we cleared today.

### 4. Circular Dependency: Unlock vs. Pod Health

**The Issue:** StarlingX refuses to `unlock` a node until all platform applications are healthy. However, Kubernetes refuses to start those applications because the node is `locked` (which applies a `NoExecute` taint).
**The Symptom:** `mtc_action_apps_semantic_checks` timeouts in `sysinv.log`.
**The Fix:** Manually `uncordon` and remove the `services=disabled` taint via `kubectl` to allow pods to reach a `Running` state, satisfying the Sysinv Conductor.

### 5. Service-to-Service Authentication Failure

**The Issue:** The `sysinv-api` requires a connection to Keystone to validate every CLI request. By mapping `controller.internal` to the physical Node IP (`.2`) to solve an earlier DNS issue, we accidentally broke the API's ability to find the Keystone process, which was strictly bound to the Floating VIP (`.1`).
**The Fix:** Update `/etc/hosts` to point `controller.internal` to the Floating VIP (`192.168.204.1`).

### 6. Persistent RPC Jamming

**The Issue:** When an RPC call (like a semantic check) times out, the `sysinv-conductor` process can sometimes retain a "zombie" thread, causing subsequent commands to fail immediately.
**The Fix:** Use `sudo sm-restart service sysinv-conductor` to clear the process queue before re-attempting a host action.
