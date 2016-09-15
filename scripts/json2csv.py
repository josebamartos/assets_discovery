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
        asset_list.append(asset)
    
    return asset_list


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
    processor    = data["ansible_facts"]["ansible_processor"][0] + data["ansible_facts"]["ansible_processor"][1]
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


if data["ansible_facts"]["ansible_system"] == "Win32NT":

    # Netorking
    hostname     = data["win_hostname"]
    domain       = data["win_domain"]
    ipv4         = data["win_all_ipv4_addresses"]
    netmask      = data["win_netmask"]
    ipv6         = data["win_all_ipv6_addresses"]

    # Processor
    architecture = data["win_architecture"]
    processor    = data["win_processor"]
    processors   = str(data["win_processor_count"])
    cores        = str(data["win_processor_cores"])
    vcpus        = str(data["win_processor_vcpus"])

    # Memory
    swap_total   = str(data["win_swap_total"])
    swap_used    = str(data["win_swap_used"])
    swap_free    = str(data["win_swap_free"])
    mem_total    = str(data["win_mem_total"])
    mem_used     = str(data["win_mem_used"])
    mem_free     = str(data["win_mem_free"])

    # Storage
    drives       = data["win_devices"]

    # Virtualization
    virt_type    = data["win_virtualization_type"]
    virt_role    = data["win_virtualization_role"]

    # Operating system"
    system       = data["ansible_facts"]["ansible_system"]
    os_family    = data["ansible_facts"]["ansible_os_family"]
    distribution = data["ansible_facts"]["ansible_distribution"]
    release      = ""
    version = data["ansible_facts"]["ansible_distribution_version"]

    # Assets
    appservers   = get_assets(data["appservers"])
    databases    = get_assets(data["databases"])


# CSV
if len(appservers) > len(databases) or len(appservers) == len(databases):
    asset_num = len(appservers)
elif len(appservers) < len(databases):
    asset_num = len(databases)

csv_buffer = StringIO.StringIO()
writer = csv.writer(csv_buffer, delimiter=',')

for i in range(0, asset_num - 1):
    as_vendor  = ""
    as_name    = ""
    as_version = ""
    as_path    = ""

    db_vendor  = ""
    db_name    = ""
    db_version = ""
    db_path    = ""

    try:
        as_vendor = appservers[i]["vendor"]
        as_name = appservers[i]["name"]
        as_version = appservers[i]["version"]
        as_path = appservers[i]["path"]
    except:
        pass

    try:
        db_vendor = databases[i]["vendor"]
        db_name = databases[i]["name"]
        db_version = databases[i]["version"]
        db_path = databases[i]["path"]
    except:
        pass

    if i == 0:
        row     = [hostname, domain, ipv4, netmask, ipv6, architecture, processor, processors, cores, vcpus, swap_total, swap_used, swap_free, mem_total, mem_used, mem_free, drives, virt_type, virt_role, system, os_family, distribution, release, version, as_vendor, as_name, as_version, as_path, db_vendor, db_name, db_version, db_path]
    elif i > 0:
       row     = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", as_vendor, as_name, as_version, as_path, db_vendor, db_name, db_version, db_path]

    writer.writerow(row)

csv_content = csv_buffer.getvalue()
csv_buffer.close()

print csv_content
