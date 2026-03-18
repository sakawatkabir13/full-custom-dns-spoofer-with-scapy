#!/usr/bin/env python3
import subprocess
import optparse
import re

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--interface", dest="interface", help="Interface to change MAC address")
    parser.add_option("-m", "--mac", dest="new_mac", help="New MAC address")
    (options, arguments) = parser.parse_args()
    if not options.interface:
        parser.error("[-] Please specify an interface")
    elif not options.new_mac:
        parser.error("[-] Please specify a new MAC address")
    return options

def mac_changer(interface, new_mac):
    print("[+] Changing MAC Address for " + interface + " to " + new_mac)
    subprocess.call(["ifconfig", interface, "down"])
    subprocess.call(["ifconfig", interface, "hw", "ether", new_mac])
    subprocess.call(["ifconfig", interface, "up"])

def get_current_mac(interface):
    ifconfig_result = subprocess.check_output(["ifconfig", interface])
    mac_address_search_result = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", str(ifconfig_result))

    if mac_address_search_result:
        return mac_address_search_result.group(0)
    else:
        print("[-] Could not read MAC address.")

options = get_arguments()
current_mac = get_current_mac(options.interface)
print("Current MAC = " + current_mac)
mac_changer(options.interface, options.new_mac)

current_mac = get_current_mac(options.interface)
if current_mac == options.new_mac:
    print("[+] MAC address successfully changed to " + options.new_mac)
else:
    print("[-] MAC address did not get changed.")
