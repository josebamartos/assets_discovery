import csv
import json
import os
import sys

#def get_drives(facts):
#    devices = facts["ansible_facts"]["ansible_devices"]
#    drive_list = []
#
#    for device in devices:
#        drive = device + "(" + data["ansible_facts"]["ansible_devices"][device]["size"] + ")"
#        drive_list.append(drive)
#
#    drives = ", ".join(drive_list)
#    return drives

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
domain   = data["ansible_facts"]["ansible_env"]["USERDOMAIN"]
ips     = ", ".join(data["ansible_facts"]["ansible_ip_addresses"])

# Processor
architecture = data["ansible_facts"]["ansible_env"]["PROCESSOR_IDENTIFIER"]
processors   = data["ansible_facts"]["ansible_env"]["NUMBER_OF_PROCESSORS"]
processor    = data["ansible_facts"]["ansible_env"]["PROCESSOR_IDENTIFIER"]

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

# Writing process
csv_dir = os.path.join(os.environ.get('HOME'), "files")
csv_file = os.path.join(csv_dir, hostname + ".csv")

if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)

with open(csv_file, "wb") as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(["Hostname", "Domain", "IPs", "Architecture", "Processors", "Processor", "Mem", "System", "OS Family", "Distribution", "Version", "Appservers", "Databases"])
    writer.writerow([hostname, domain, ips, architecture, processors, processor, mem_total, system, os_family, distribution, version, appservers, databases])
