import csv
import json
import os
import sys

def get_drives(facts):
    devices = facts["ansible_facts"]["ansible_devices"]
    drive_list = []

    for device in devices:
        drive = device + "(" + data["ansible_facts"]["ansible_devices"][device]["size"] + ")"
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


output = open(sys.argv[1], "r").read()
data = json.loads(output)

# Netorking
hostname = data["ansible_facts"]["ansible_hostname"]
domain   = data["ansible_facts"]["ansible_domain"]
ipv4     = ", ".join(data["ansible_facts"]["ansible_all_ipv4_addresses"])
netmask  = data["ansible_facts"]["ansible_default_ipv4"]["netmask"]
ipv6     = ", ".join(data["ansible_facts"]["ansible_all_ipv6_addresses"])

# Processor
architecture = data["ansible_facts"]["ansible_architecture"]
processors   = str(data["ansible_facts"]["ansible_processor_count"])
cores        = str(data["ansible_facts"]["ansible_processor_cores"])
processor    = " ".join(data["ansible_facts"]["ansible_processor"])

# Memory
swap_total = str(data["ansible_facts"]["ansible_memory_mb"]["swap"]["total"])
swap_used  = str(data["ansible_facts"]["ansible_memory_mb"]["swap"]["used"])
swap_free  = str(data["ansible_facts"]["ansible_memory_mb"]["swap"]["free"])
mem_total  = str(data["ansible_facts"]["ansible_memory_mb"]["real"]["total"])
mem_used   = str(data["ansible_facts"]["ansible_memory_mb"]["real"]["used"])
mem_free   = str(data["ansible_facts"]["ansible_memory_mb"]["real"]["free"])

# Storage
drives = get_drives(data)

# Virtualization
virt_type = data["ansible_facts"]["ansible_virtualization_type"]
virt_role = data["ansible_facts"]["ansible_virtualization_role"]

# Operating system"
system       = data["ansible_facts"]["ansible_system"]
os_family    = data["ansible_facts"]["ansible_os_family"]
distribution = data["ansible_facts"]["ansible_distribution"]
release      = data["ansible_facts"]["ansible_distribution_release"]
version      = data["ansible_facts"]["ansible_distribution_version"]

# Assets
appservers = get_assets(data["appservers"])
databases = get_assets(data["databases"])

# Writing process
csv_dir = os.path.join(os.environ.get('HOME'), "files")
csv_file = os.path.join(csv_dir, hostname + ".csv")

if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)

with open(csv_file, "wb") as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(["Hostname", "Domain", "IPv4", "Netmask", "IPv6", "Architecture", "Processors", "Processor", "Cores", "Swap", "Used swap", "Free swap", "Mem", "Used mem", "Free mem", "Drives", "Virt type", "Virt role", "System", "OS Family", "Distribution", "Release", "Version", "Appservers", "Databases"])
    writer.writerow([hostname, domain, ipv4, netmask, ipv6, architecture, processors, processor, cores, swap_total, swap_used, swap_free, mem_total, mem_used, mem_free, drives, virt_type, virt_role, system, os_family, distribution, release, version, appservers, databases])
