# srsRAN ZMQ Unblock Guide — Step-by-Step (2026-02-27)

Status: Action Required (User)
Priority: **HIGH — blocks all empirical scheduler validation**

This guide fixes the "Frozen Clock" deadlock identified on Jan 30. Follow these steps **on Ubuntu (dual boot)** to get gNB + UE + Open5GS running over ZMQ.

---

## Quick Context: What's Broken

| Symptom | Root Cause | Fix |
|---|---|---|
| gNB hangs indefinitely | No I/Q samples from UE → clock frozen at t=0 | Launch UE before or simultaneously with gNB |
| UE fails: `Neither Tx nor Rx port specified` | srsRAN_4G ZMQ defaults to 2-channel MIMO | Set `nof_antennas = 1` in `ue_zmq.conf` |
| UE conf parsing error | `ue_zmq.conf` corrupted with shell `cat <<EOF` syntax | Re-create a clean file (below) |

---

## Step 1: Prepare the Working Directory

```bash
cd ~
rm -rf srsRAN-docker-zmq   # Clean slate
mkdir srsRAN-docker-zmq && cd srsRAN-docker-zmq
```

## Step 2: Create Clean Configuration Files

### A. Open5GS 5GC Config (`open5gs-5gc.yml`)

Only needed if the default `srsran/open5gs` image doesn't bind AMF to `0.0.0.0`. Check by running:
```bash
docker run --rm srsran/open5gs cat /etc/open5gs/amf.yaml | grep -A2 ngap
```
If it shows `127.0.0.5`, you need to override. Otherwise, skip this file.

```yaml
# open5gs-5gc.yml — NGAP bind override
# Only create this file if the default AMF binds to 127.0.0.5
amf:
  ngap:
    server:
      - address: 0.0.0.0    # Listen on ALL interfaces (critical for Docker bridge)
```

### B. gNB Config (`gnb_zmq.yaml`)

```yaml
# gnb_zmq.yaml — srsRAN Project gNB with ZMQ virtual radio

amf:
  addr: 10.53.1.2                   # Open5GS container IP
  bind_addr: 10.53.1.5              # gNB container IP

ru_sdr:
  device_driver: zmq
  device_args: tx_port=tcp://0.0.0.0:2000,rx_port=tcp://srsue:2001,base_srate=23.04e6,id=zmq
  srate: 23.04
  otw_format: sc12
  tx_gain: 75
  rx_gain: 75

cell_cfg:
  dl_arfcn: 632628                   # Band n78 (3.5 GHz)
  band: 78
  channel_bandwidth_MHz: 20          # 20 MHz → 51 PRBs at 30 kHz SCS
  common_scs: 30                     # µ=1
  plmn: "00101"
  tac: 7
  pdcch:
    common:
      ss0_index: 0
      coreset0_index: 12
    dedicated:
      ss2_type: common
      dci_format_0_1_and_1_1: false
  prach:
    prach_config_index: 1

log:
  filename: /tmp/gnb.log
  all_level: info
  phy_level: warning
  hex_max_size: 32

pcap:
  mac_enable: true                   # Enable MAC PCAP for scheduler analysis
  mac_filename: /tmp/gnb_mac.pcap
```

> **Note:** Start with 20 MHz (51 PRBs) to confirm the stack works. Once validated, change to `channel_bandwidth_MHz: 100` for the full 273-PRB demonstration. Make sure to also update `base_srate` to `61.44e6` and `srate` to `61.44` for 100 MHz.

### C. UE Config (`ue_zmq.conf`) — THE CRITICAL FIX

```ini
# ue_zmq.conf — srsRAN 4G UE in 5G SA mode via ZMQ
# IMPORTANT: This file must contain ONLY ini-format lines.
#            No shell syntax (cat, EOF, heredoc) allowed.

[rf]
device_name = zmq
device_args = tx_port=tcp://0.0.0.0:2001,rx_port=tcp://gnb:2000,base_srate=23.04e6
freq_offset = 0
rx_gain = 40
tx_gain = 50
srate = 23.04e6
nof_antennas = 1

[rat.nr]
bands = 78
nof_carriers = 1

[pcap]
enable = none
mac_filename = /tmp/ue_mac.pcap
mac_nr_filename = /tmp/ue_mac_nr.pcap

[gw]
netns =
ip_devname = tun_srsue
ip_netmask = 255.255.255.0

[usim]
mode = soft
algo = milenage
opc  = 63BFA50EE6523365FF14C1F45F88737D
k    = 00112233445566778899aabbccddeeff
imsi = 001010123456780
imei = 353490069873319

[log]
all_level = info
phy_lib_level = none
all_hex_limit = 32
filename = /tmp/ue.log
file_max_size = -1

[general]
```

**Key fix:** `nof_antennas = 1` forces SISO mode, preventing the 2-channel ZMQ panic.

### D. Dockerfile for UE (`Dockerfile.ue`)

```dockerfile
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y software-properties-common curl iproute2 iputils-ping iperf3 net-tools libzmq3-dev && \
    add-apt-repository ppa:softwareradiosystems/srsran && \
    apt-get update && \
    apt-get install -y srsran && \
    rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["srsue"]
CMD ["/config/ue_zmq.conf"]
```

### E. Docker Compose (`docker-compose.yml`)

```yaml
version: "3.8"
services:
  open5gs:
    image: srsran/open5gs
    container_name: open5gs
    privileged: true
    networks:
      5g_network:
        ipv4_address: 10.53.1.2
    environment:
      - IP_ADDR=10.53.1.2

  gnb:
    image: srsran/gnb:latest
    container_name: gnb
    privileged: true
    depends_on:
      - open5gs
    networks:
      5g_network:
        ipv4_address: 10.53.1.5
    volumes:
      - ./gnb_zmq.yaml:/etc/srsran/gnb.yaml
    command: /usr/bin/gnb -c /etc/srsran/gnb.yaml
    # NOTE: gnb will "hang" until UE sends I/Q samples — this is NORMAL

  srsue:
    build:
      context: .
      dockerfile: Dockerfile.ue
    container_name: srsue
    privileged: true
    depends_on:
      - gnb
    networks:
      5g_network:
    volumes:
      - ./ue_zmq.conf:/config/ue_zmq.conf
    restart: on-failure

networks:
  5g_network:
    driver: bridge
    ipam:
      config:
        - subnet: 10.53.1.0/24
```

---

## Step 3: Load SCTP Kernel Modules (Host)

```bash
sudo modprobe sctp
sudo modprobe nf_conntrack_sctp
# Verify:
lsmod | grep sctp
```

## Step 4: Build and Launch

```bash
cd ~/srsRAN-docker-zmq
docker compose up --build -d
```

Wait ~15 seconds for the containers to start.

## Step 5: Monitor the Logs

Open **3 terminals** (or use tmux splits):

```bash
# Terminal 1: Core
docker logs -f open5gs

# Terminal 2: gNB
docker logs -f gnb

# Terminal 3: UE
docker logs -f srsue
```

### What You Should See (In Order)

| Component | Expected Log | Meaning |
|---|---|---|
| **open5gs** | `AMF initialize...done` | Core is ready |
| **srsue** | `Searching for cell...` | UE is streaming I/Q noise to gNB |
| **gnb** | `==== gNB started ===` | gNB clock ticking from UE samples |
| **gnb** | `NG connection established` | gNB ↔ Core connected (N2/SCTP) |
| **srsue** | `PDU Session Establishment successful. IP: 10.45.1.x` | **✅ SUCCESS** |

### If Something Goes Wrong

| Symptom | Likely Cause | Fix |
|---|---|---|
| gNB never prints `started` | UE not streaming → check UE logs | Verify `ue_zmq.conf` has no syntax errors; check `nof_antennas = 1` |
| gNB says `SCTP connect failed` | AMF not listening on container IP | Verify `open5gs` logs show AMF on `0.0.0.0`; check SCTP modules loaded |
| UE says `zmq: Neither Tx nor Rx` | 2-channel MIMO panic | Confirm `nof_antennas = 1` in `ue_zmq.conf` |
| UE in infinite `Searching for cell` | gNB not yet booted OR frequency mismatch | Check `dl_arfcn` and `bands` match between gNB and UE |
| `PDU Session` never appears | USIM credentials mismatch | Verify IMSI/K/OPC match between `ue_zmq.conf` and Open5GS subscriber DB |

## Step 6: Run Traffic Through the 5G Stack

Once you see `PDU Session Establishment successful`:

```bash
# Start iperf3 server inside the Core (acts as "internet")
docker exec -d open5gs iperf3 -s

# Run DL traffic through the 5G tunnel (from UE)
docker exec srsue iperf3 -c 10.45.1.1 -b 50M -t 60

# For UL traffic:
docker exec srsue iperf3 -c 10.45.1.1 -b 50M -t 60 -R
```

## Step 7: (Optional) Start Scaphandre Power Logging

If you want to capture power during the experiment:

```bash
# On the HOST (not in Docker):
# Start Scaphandre Prometheus exporter
sudo scaphandre prometheus --port 8080 &

# In another terminal, log power:
while true; do
  curl -s http://localhost:8080/metrics | grep scaph_host_power_microwatts | grep -v "^#" >> power_uw.txt
  sleep 1
done
```

## Step 8: Extract MAC PCAP for Scheduler Analysis

```bash
# Copy the MAC PCAP out of the gNB container
docker cp gnb:/tmp/gnb_mac.pcap ./gnb_mac.pcap

# Open in Wireshark with MAC-NR dissector
wireshark gnb_mac.pcap &
```

In Wireshark, filter for `mac-nr` to see:
- DCI grants showing `rbSize` (PRBs allocated)
- Per-slot scheduling decisions
- HARQ ACK/NACK patterns

---

## Results to Report Back

After running these steps, please report:

1. ✅ or ❌ — Did `PDU Session Establishment successful` appear?
2. The **IP address** assigned to the UE (e.g., `10.45.1.2`)
3. The **iperf3 throughput** achieved (Mbps)
4. Any **error messages** from the gNB or UE logs
5. If you extracted the MAC PCAP: the `rbSize` values visible in Wireshark

---

## References

- srsRAN Project ZMQ guide: https://docs.srsran.com/projects/project/en/latest/tutorials/source/srsUE/source/index.html
- Our previous attempt: `docs/StudyNotes/2026-01-30_Current-Progres-srsRAN.md`
- Our original setup guide: `docs/StudyNotes/2026-01-29_Guide-srsRAN-ZMQ-Setup.md`
