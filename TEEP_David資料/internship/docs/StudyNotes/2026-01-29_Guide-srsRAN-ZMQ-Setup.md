# Guide: Running srsRAN 5G (ZMQ) on Docker

This guide explains how to set up a fully virtualized 5G Network (Core + gNB + UE) on your Ubuntu machine using Docker. This setup simulates a **Real 5G Software Loads** (PHY/MAC processing) rather than just simple network traffic.

## Objective
Use this setup to measure the "Compute Power" of a 5G stack.
- **Scenario:** Run full 5G stack (Core/gNB/UE).
- **Load:** Use `iperf3` *through* the 5G tunnel.
- **Measurement:** Capture Laptop Power. This value is your "5G Compute" baseline.

## 1. Prerequisites
- Ubuntu OS (Native or VM, but RAPL requires Native for power).
- Docker & Docker Compose installed:
  ```bash
  sudo apt update
  sudo apt install docker.io docker-compose -y
  sudo usermod -aG docker $USER
  # (Log out and log back in for group changes to take effect)
  ```

## 2. Directory Setup
Create a dedicated folder for this experiment:
```bash
mkdir ~/srsRAN-docker-zmq
cd ~/srsRAN-docker-zmq
```

## 3. Configuration Files

### A. gNB Configuration (`gnb_zmq.yaml`)
Create this file for the Base Station. It points to the Core (AMF) and the ZMQ radio driver.
```yaml
amf:
  addr: 10.53.1.2                  # Fixed IP of Open5GS container
  bind_addr: 10.53.1.5             # Fixed IP of gNB container
  
ru_sdr:
  device_driver: zmq
  # tx_port: listen on 2000, rx_port: connect to UE on 2001
  device_args: tx_port=tcp://0.0.0.0:2000,rx_port=tcp://srsue:2001,base_srate=23.04e6,id=zmq
  srate: 23.04
  xf_saturation: 0

cell_cfg:
  dl_arfcn: 632620                 # N78 Band center
  band: 78
  channel_bandwidth_MHz: 20
  common_scs: 30
  plmn: "00101"
  tac: 7
```

### B. UE Configuration (`ue_zmq.conf`)
Create this file for the User Device. It connects to the gNB via ZMQ.
```ini
[rf]
device_name = zmq
# tx_port: listen on 2001, rx_port: connect to gNB on 2000
device_args = tx_port=tcp://0.0.0.0:2001,rx_port=tcp://gnb:2000,base_srate=23.04e6
freq_offset = 0
rx_gain = 40
tx_gain = 50
srate = 23.04e6

[rat.nr]
bands = 78
nof_carriers = 1
nof_prb = 52 # Matches 20MHz @ 30kHz SCS

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
```

### C. Dockerfile for UE (`Dockerfile.ue`)
Since `srsue` (4G/5G NSA client) is not in the standard image list yet for pure ZMQ 5G SA ease, we verify a custom build or reuse the 4G/5G NSA client. For 1-week speed, we actually recommend using the **srsRAN_Project gNB** + **srsRAN 4G UE** combination which supports 5G SA ZMQ.
```dockerfile
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && \
    apt-get install -y software-properties-common curl iproute2 iputils-ping iperf3 net-tools libzmq3-dev && \
    add-apt-repository ppa:softwareradiosystems/srsran && \
    apt-get update && \
    apt-get install -y srsran && \
    rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["srsue"]
CMD ["/config/ue_zmq.conf"]
```

### D. Docker Compose (`docker-compose.yml`)
Wire everything together.
```yaml
version: "3.8"
services:
  # 1. CORE NETWORK (Open5GS)
  open5gs:
    image: srsran/open5gs
    container_name: open5gs
    privileged: true
    networks:
      5g_network:
        ipv4_address: 10.53.1.2
    environment:
      - IP_ADDR=10.53.1.2

  # 2. BASE STATION (srsRAN Project gNB)
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

  # 3. USER EQUIPMENT (srsUE)
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

## 4. Execution Steps

### Step A: Build and Launch
```bash
docker-compose up --build -d
# Wait 10-20 seconds for services to sync
```

### Step B: Verify Connection
Check logs of the UE:
```bash
docker logs -f srsue
```
**Success Indicator:** You should see `PDU Session Establishment successful` and `IP: 10.45.1.x`.

### Step C: Run Traffic (The Experiment)
Now you generate load **through the 5G stack**.
1.  **Start Scaphandre Logging** on your host (Linux).
2.  **Start iperf Server** inside the Core (Internet):
    ```bash
    docker exec -d open5gs iperf3 -s
    ```
3.  **Start iperf Client** inside the UE:
    ```bash
    # Run 100Mbps traffic for 300 seconds
    docker exec srsue iperf3 -c 10.45.1.1 -b 100M -t 300
    ```

## 5. What to expect
- **Power:** Your laptop fans will spin up. `gnb` will use significant CPU to compute PHY (FFTs, LDPC).
- **Result:** This power measurement is your **"Compute Baseline"**. It will be higher than pure `iperf` (25W) but lower than "Radio" (200W).
