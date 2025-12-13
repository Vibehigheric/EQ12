#!/bin/bash
# Check USB Ethernet connectivity on Raspberry Pi

echo "=========================================="
echo "Raspberry Pi USB/Ethernet Diagnostics"
echo "=========================================="
echo ""

echo "USB Devices List:"
lsusb
echo ""

echo "Network Interfaces:"
ip link show
echo ""

echo "IP Configuration:"
ip addr show
echo ""

echo "Routing Table:"
ip route show
echo ""

echo "Ethernet Adapter Details:"
ethtool -i eth0 2>/dev/null || ethtool -i en0 2>/dev/null || echo "No standard Ethernet interface found"
echo ""

echo "Checking USB Network Devices:"
ls -la /sys/class/net/ 2>/dev/null | grep -v "^d"
echo ""

echo "Status: Verify if any interface has 192.168.100.x address for cluster network"
