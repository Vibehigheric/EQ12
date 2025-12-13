#!/bin/bash
echo "=== DNS CHECK: ALL NODES ==="

for ip in 192.168.1.144 192.168.1.80 192.168.1.130 192.168.1.94; do
  echo "Checking node: $ip"
  ssh ricoj100@$ip "cat /etc/resolv.conf | grep nameserver"
done