#!/usr/bin/env python3
import scapy.all as scapy
import optparse

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-t", "--target", dest="ip_address", help="IP address to scan")
    (options, arguments) = parser.parse_args()

    if not options.ip_address:
        parser.error("[-] Please specify an IP range")
    return options

def scan(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    clients_list = []
    for element in answered_list:
        client_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
        clients_list.append(client_dict)
    return clients_list

def print_results(clients_list):
    print("IP\t\t\t\tMAC Address\n------------------------------------------")
    for client in clients_list:
        print(client["ip"] + "\t\t" + client["mac"])

options = get_arguments()
scan_result = scan(options.ip_address)
print_results(scan_result)
