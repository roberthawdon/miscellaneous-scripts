#!/usr/bin/env python3
import sys
import ipaddress

def check_ip_in_range(file_path, ip_to_check):
    try:
        ip = ipaddress.ip_address(ip_to_check)
    except ValueError:
        return f"Invalid IP address: {ip_to_check}"

    try:
        with open(file_path, 'r') as file:
            ranges = file.readlines()
    except FileNotFoundError:
        return f"File not found: {file_path}"

    for line in ranges:
        line = line.strip()
        try:
            if ip in ipaddress.ip_network(line, strict=False):
                return f"The IP {ip_to_check} is within the range: {line}"
        except ValueError:
            continue  # Skip lines that are not valid CIDR notation

    return "No matching range found for the IP."

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <file_path> <ip_to_check>")
        sys.exit(1)

    file_path = sys.argv[1]
    ip_to_check = sys.argv[2]

    result = check_ip_in_range(file_path, ip_to_check)
    print(result)

