<div align="center">

# 🛰️ DNS Spoofer Lab Toolkit

### A chained, educational red-team lab for network interception using Scapy + NetfilterQueue

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Scapy](https://img.shields.io/badge/Scapy-Packet%20Crafting-1f9d55?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Educational-orange?style=for-the-badge)

**An end-to-end, MITM-positioned DNS spoofing workflow — from MAC randomization to NFQUEUE packet modification.**

[Overview](#-overview) • [Features](#-features) • [Architecture](#-workflow-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Troubleshooting](#-troubleshooting) • [Roadmap](#-roadmap) • [Contributing](#-contributing) • [License](#-license)

</div>

---

## ⚠️ Disclaimer

> **This project is for education and authorized security testing only.**
> You are solely responsible for the legal and ethical use of these tools.
> Unauthorized interception and spoofing of network traffic may violate laws and policies in your jurisdiction.

---

## 📌 Overview

This repository is **not** a collection of isolated scripts — it is a **full chained workflow** that mirrors how a real on-path adversary operates, broken into ordered phases:

1. **MAC randomization** → Prepare attacker identity.
2. **ARP discovery** → Map the LAN and choose victim + gateway.
3. **ARP spoofing** → Become the MITM (man-in-the-middle).
4. **HTTP sniffing** → Observe victim destinations to pick realistic targets.
5. **DNS spoofing** → Rewrite selected DNS answers via NFQUEUE.

Each phase feeds the next. DNS spoofing is most effective **after** traffic observation, because you can pick realistic target domains the victim actually queries.

---

## ✨ Features

- 🧱 **Ordered red-team style lab workflow** — each step is a discrete, runnable script.
- 🛠️ **CLI-driven** — every script uses `optparse` with clean `-h` help.
- 🎯 **Targeted DNS spoofing** — only chosen domains are rewritten; everything else passes through.
- 📡 **Live HTTP request sniffing** with optional credential keyword detection.
- 🔁 **Auto ARP-table restoration** on `CTRL+C`.
- 🐧 **Practical Linux packet-queue integration** — `iptables` + `NFQUEUE`.

---

## 🗺️ Workflow Architecture

```text
         ┌──────────────────────────┐
         │     Attacker Machine     │
         └──────────────────────────┘
                     │
   ┌─────────────────┼─────────────────┐
   │ Step 1          │                 │
   ▼                 │                 │
┌────────────────┐   │                 │
│  mac_changer   │   │                 │
└────────────────┘   │                 │
   │                 │                 │
   ▼                 │                 │
┌────────────────┐   │   ┌─────────┐   │
│network_scanner │──▶│──▶│ Victim  │   │
└────────────────┘   │   └─────────┘   │
   │                 │                 │
   ▼                 │                 │
┌────────────────┐   │                 │
│  arp_spoofer   │──▶│─── MITM ───┐   │
└────────────────┘   │            │   │
   │                 │            ▼   │
   ▼                 │   ┌─────────────┐
┌────────────────┐   │   │  Gateway    │
│ packet_sniffer │   │   └─────────────┘
└────────────────┘   │
   │                 │
   ▼                 │
┌────────────────┐   │
│  dns_spoofer   │───┘   (NFQUEUE → packet rewrite)
└────────────────┘
```

---

## 📂 Repository Structure

```text
dns_spoofer_with_scapy/
├── arp_spoofer.py        # ARP poison victim + gateway (MITM)
├── dns_spoofer.py        # Rewrite DNS answers via NFQUEUE
├── mac_changer.py        # MAC address randomization
├── network_scanner.py    # ARP-based host discovery
├── packet_sniffer.py     # HTTP request sniffer
├── requirements.txt      # Python dependencies
├── LICENSE               # MIT License
└── README.md             # This file
```

---

## 🧰 Requirements

### System

| Component       | Version / Notes                  |
| --------------- | -------------------------------- |
| OS              | Linux (Kali / Debian / Ubuntu)   |
| Python          | 3.8+                             |
| Privileges      | `root`                           |

### Python Packages

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:

- `scapy`
- `NetfilterQueue`

### Linux Dependencies

```bash
sudo apt update
sudo apt install -y python3-pip python3-dev libnetfilter-queue-dev net-tools iptables
```

---

## 🚀 Installation

```bash
git clone https://github.com/sakawatkabir13/full-custom-dns-spoofer-with-scapy.git
cd full-custom-dns-spoofer-with-scapy

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📖 Usage

> 💡 **Recommended:** Use **three terminals** for stable operation —
> Terminal A: `arp_spoofer.py` · Terminal B: `packet_sniffer.py` · Terminal C: `dns_spoofer.py`

### Step 1 — Change Attacker MAC Address

```bash
sudo python3 mac_changer.py -i eth0 -m 00:11:22:33:44:55
```

| Flag                 | Description      |
| -------------------- | ---------------- |
| `-i`, `--interface`  | Network interface |
| `-m`, `--mac`        | New MAC address   |

### Step 2 — Scan Network

```bash
sudo python3 network_scanner.py -t 192.168.1.1/24
```

| Flag           | Description                       |
| -------------- | --------------------------------- |
| `-t`, `--target` | Host/range (single IP or CIDR)   |

Output: IP ↔ MAC mapping table. Choose your **victim** and **gateway**.

### Step 3 — ARP Spoof (MITM)

```bash
sudo python3 arp_spoofer.py -t 192.168.1.10 -g 192.168.1.1
```

| Flag             | Description |
| ---------------- | ----------- |
| `-t`, `--target` | Victim IP   |
| `-g`, `--gateway` | Gateway IP |

Behavior:

- Continuously sends ARP poison packets to both victim and gateway.
- On `CTRL+C`, attempts to **restore ARP tables** before exit.

### Step 4 — Sniff Victim Traffic

Run in a second terminal while ARP spoofing is active:

```bash
sudo python3 packet_sniffer.py -i eth0
```

| Flag                 | Description      |
| -------------------- | ---------------- |
| `-i`, `--interface`  | Sniffing interface |

Look for:

- HTTP host + path requests
- Recurring domains relevant to your test scenario

### Step 5 — DNS Spoof

#### 5.1 — Add NFQUEUE Rule

```bash
sudo iptables -I FORWARD -j NFQUEUE --queue-num 0
```

> Depending on lab topology, you may need `INPUT` or `OUTPUT` chains instead of `FORWARD`.

#### 5.2 — Run DNS Spoofer

```bash
sudo python3 dns_spoofer.py -d www.stackoverflow.com -s 10.80.246.83 -q 0
```

| Flag               | Description                  |
| ------------------ | ---------------------------- |
| `-d`, `--domain`   | Domain to spoof              |
| `-s`, `--spoof-ip` | Fake IP in DNS answer        |
| `-q`, `--queue-num` | NFQUEUE number (default `0`) |

> 🎯 **How to choose a domain:** Use domains you observed in Step 4 — realistic targets based on victim behavior.

---

## 🧹 Stop & Cleanup

1. Stop DNS spoofer (`CTRL+C`).
2. Stop ARP spoofer (`CTRL+C`) — wait for restore packets to complete.
3. Remove queue / firewall rules:

```bash
sudo iptables --flush
```

> ⚠️ In real environments, remove only the inserted rules instead of flushing the full chain.

---

## 🛠️ Troubleshooting

<details>
<summary><b>ImportError: netfilterqueue</b></summary>

```bash
sudo apt install -y python3-dev libnetfilter-queue-dev
pip install NetfilterQueue
```

</details>

<details>
<summary><b>DNS spoof not triggering</b></summary>

- Verify the `iptables` rule is active and matches the traffic path.
- Verify queue number in `iptables` matches `-q` value.
- Ensure target uses plain DNS (not DoH/DoT).
- Ensure domain in `-d` matches observed queries.

</details>

<details>
<summary><b>No sniff output</b></summary>

- Verify ARP spoofing is running.
- Verify correct interface in sniffer.
- HTTPS limits payload visibility — use host-level indicators only.

</details>

<details>
<summary><b>MAC address not changing</b></summary>

- Check interface name.
- Ensure `ifconfig` exists (`net-tools` installed).
- Run with `sudo`.

</details>

<details>
<summary><b>Permission denied</b></summary>

Most raw-packet operations require `root`. Always use `sudo` for sniffing, ARP, and NFQUEUE scripts.

</details>

---

## 🧭 Roadmap

- [ ] Add **IPv6 support** (NDP spoofing)
- [ ] Add **HTTPS SNI filtering** to detect DoH-resistant domains
- [ ] Add **unit tests** for CLI argument parsing
- [ ] Add **Docker lab environment** for safe testing
- [ ] Add **logging** option (file output)
- [ ] Add **JSON output** for `network_scanner.py`
- [ ] Migrate CLI from `optparse` → `argparse` (future maintenance)

---

## 🤝 Contributing

Contributions, ideas, and improvements are welcome!

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/improvement`).
3. Commit your changes (`git commit -m "Add improvement"`).
4. Push to the branch (`git push origin feature/improvement`).
5. Open a Pull Request.

Please ensure changes are focused, documented, and tested in an isolated lab.

---

## 🔒 Legal & Ethical Notice

Use this project **only** on networks and devices you own or have explicit written authorization to test.

Unauthorized interception, spoofing, and modification of network traffic may violate:

- Local computer-misuse laws
- Wiretap / telecommunications regulations
- Organizational security policies
- Terms of service of your ISP

You are solely responsible for your actions.

---

## 👤 Author

**Sakawat Kabir Tanveer**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/s-kbr13)
[![X](https://img.shields.io/badge/X-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/tanveer_sakawat)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/sakawatkabir13)

---

## 🙏 Acknowledgements

- [Scapy](https://scapy.net/) — the Swiss Army knife of packet crafting.
- [NetfilterQueue](https://pypi.org/project/NetfilterQueue/) — Python binding for `libnetfilter-queue`.
- The offensive-security community for foundational research and teaching material.

---

## 📜 License

This project is licensed under the **MIT License** — see the [`LICENSE`](LICENSE) file for details.

---

<div align="center">
⭐ If you found this project helpful for learning network security fundamentals, consider giving it a star!
</div>
