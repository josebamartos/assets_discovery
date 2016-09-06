###########
# Modules #
###########

import csv
import json
import StringIO
import sys


#############
# Functions #
#############

def get_drives(devices):
    drive_list = []

    for device in devices:
        drive = device + "(" + devices[device]["size"] + ")"
        drive_list.append(drive)

    drives = ", ".join(drive_list)
    return drives

def get_assets(assets):
    asset_list = []

    for asset in assets:
        product = asset["vendor"] + " " + asset["name"] + " " + asset["version"] + ": " + asset["path"]
        asset_list.append(product)
    
    products = ", ".join(asset_list)
    return products


################
# Main program #
################

data = json.loads(sys.argv[1])

if data["ansible_facts"]["ansible_system"] == "Linux":
    # Netorking
    hostname     = data["ansible_facts"]["ansible_hostname"]
    domain       = data["ansible_facts"]["ansible_domain"]
    ipv4         = ", ".join(data["ansible_facts"]["ansible_all_ipv4_addresses"])
    netmask      = data["ansible_facts"]["ansible_default_ipv4"]["netmask"]
    ipv6         = ", ".join(data["ansible_facts"]["ansible_all_ipv6_addresses"])

    # Processor
    architecture = data["ansible_facts"]["ansible_architecture"]
    processor    = " ".join(data["ansible_facts"]["ansible_processor"])
    processors   = str(data["ansible_facts"]["ansible_processor_count"])
    cores        = str(data["ansible_facts"]["ansible_processor_cores"] * int(processors))
    vcpus        = str(data["ansible_facts"]["ansible_processor_vcpus"])

    # Memory
    swap_total   = str(data["ansible_facts"]["ansible_memory_mb"]["swap"]["total"])
    swap_used    = str(data["ansible_facts"]["ansible_memory_mb"]["swap"]["used"])
    swap_free    = str(data["ansible_facts"]["ansible_memory_mb"]["swap"]["free"])
    mem_total    = str(data["ansible_facts"]["ansible_memory_mb"]["real"]["total"])
    mem_used     = str(data["ansible_facts"]["ansible_memory_mb"]["real"]["used"])
    mem_free     = str(data["ansible_facts"]["ansible_memory_mb"]["real"]["free"])

    # Storage
    drives       = get_drives(data["ansible_facts"]["ansible_devices"])

    # Virtualization
    virt_type    = data["ansible_facts"]["ansible_virtualization_type"]
    virt_role    = data["ansible_facts"]["ansible_virtualization_role"]

    # Operating system"
    system       = data["ansible_facts"]["ansible_system"]
    os_family    = data["ansible_facts"]["ansible_os_family"]
    distribution = data["ansible_facts"]["ansible_distribution"]
    release      = data["ansible_facts"]["ansible_distribution_release"]
    version      = data["ansible_facts"]["ansible_distribution_version"]

    # Assets
    appservers   = get_assets(data["appservers"])
    databases    = get_assets(data["databases"])

    # CSV
    headers = ["Hostname", "Domain", "IPv4", "Netmask", "IPv6", "Architecture", "Processor", "Processors", "Cores", "VCPUs""Swap", "Used swap", "Free swap", "Mem", "Used mem", "Free mem", "Drives", "Virt type", "Virt role", "System", "OS Family", "Distribution", "Release", "Version", "Appservers", "Databases"]
    row     = [hostname, domain, ipv4, netmask, ipv6, architecture, processor, processors, cores, vcpus, swap_total, swap_used, swap_free, mem_total, mem_used, mem_free, drives, virt_type, virt_role, system, os_family, distribution, release, version, appservers, databases]


if data["ansible_facts"]["ansible_system"] == "Win32NT":
    # Netorking
    hostname = data["ansible_facts"]["ansible_hostname"]
    domain   = data["ansible_facts"]["ansible_env"]["USERDOMAIN"]
    ips     = ", ".join(data["ansible_facts"]["ansible_ip_addresses"])

    # Processor
    architecture = data["ansible_facts"]["ansible_env"]["PROCESSOR_IDENTIFIER"]
    processor    = data["ansible_facts"]["ansible_env"]["PROCESSOR_IDENTIFIER"]
    processors   = data["processors"]
    cores        = data["cores"]
    vcpus        = data["vcpus"]

    # Memory
    mem_total  = str(data["ansible_facts"]["ansible_totalmem"])

    # Operating system"
    system       = data["ansible_facts"]["ansible_system"]
    os_family    = data["ansible_facts"]["ansible_os_family"]
    distribution = data["ansible_facts"]["ansible_distribution"]
    version      = data["ansible_facts"]["ansible_distribution_version"]

    # Assets
    appservers = get_assets(data["appservers"])
    databases = get_assets(data["databases"])

    # CSV
    headers = ["Hostname", "Domain", "IPs", "Architecture", "Processor", "Processors", "Cores", "VCPUs", "Mem", "System", "OS Family", "Distribution", "Version", "Appservers", "Databases"]
    row     = [hostname, domain, ips, architecture, processor, processors, cores, vcpus, mem_total, system, os_family, distribution, version, appservers, databases]


csv_buffer = StringIO.StringIO()
writer = csv.writer(csv_buffer, delimiter=',')
writer.writerow(headers)
writer.writerow(row)
csv_content = csv_buffer.getvalue()
csv_buffer.close()

print csv_content
