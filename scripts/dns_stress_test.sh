#!/bin/bash
DOMAINS=("api.the-odds-api.com" "api.sportsdata.io" "google.com")
RESOLVERS=("192.168.100.1" "1.1.1.1" "8.8.8.8")

for d in "${DOMAINS[@]}"; do
  echo "--- Testing $d ---"
  for r in "${RESOLVERS[@]}"; do
    echo -n "Resolver $r: "
    (time nslookup $d $r > /dev/null) 2>&1 | grep real
  done
  echo ""
done