# EQ12 Unified Availability Orchestrator Model

## Overview
This document defines the authoritative architecture for the EQ12 "GodStack". It merges the **Swarm/Cluster Availability Framework** (Runtime) with the **GitHub CLI Framework** (DevOps) into a single unified model.

## Core Philosophy
**"Availability is the primary constraint."**
A node's ability to perform work is determined not just by its hardware, but by its **Availability Tier**, **Network Reachability**, and **Exclusion Rules**.

## Node Topology & Roles

### Tier 0: The Core (Always On)
*   **Node**: `EQ12-Manager` (192.168.1.144)
*   **Role**: Swarm Manager, Orchestrator, Data Vault.
*   **Guarantee**: Must be 100% available. If this node is down, the cluster is dead.

### Tier 1: High-Performance Edge (Conditional)
*   **Node**: `Pi-Worker-01` (192.168.1.80 / 192.168.100.1)
*   **Role**: Inference, TPU Acceleration.
*   **Guarantee**: Available when `load < 70%` and network is stable.
*   **Fallback**: Tasks revert to EQ12-Manager if Pi is unavailable.

### Tier 2: Satellite Workers (Opportunistic)
*   **Nodes**: `VM-Worker-A` (.94), `VM-Worker-B` (.116), `VM-Worker-C` (.126)
*   **Role**: Scraping, VPN Routing, Shadow Traffic.
*   **Guarantee**: "Best Effort". The system expects these to go offline (e.g., VPN rotation, VM restarts) and handles it gracefully.

### Tier 3: Visualization (Read-Only)
*   **Node**: `TCL-Display` (192.168.1.249)
*   **Role**: Passive display for Grafana/Dashboards.
*   **Guarantee**: Non-critical.

### Tier 99: Excluded (Permanent)
*   **Node**: `LG-TV-Excluded` (192.168.1.246)
*   **Role**: None.
*   **Rule**: **HARD EXCLUSION**. This IP is blacklisted from all logic.

## Orchestration Logic (`src/core/orchestrator.py`)

The `AvailabilityOrchestrator` class is the brain. It:
1.  Reads `config/nodes.json` (Static Truth).
2.  Reads `logs/network_scan_report.json` (Dynamic Truth).
3.  Reconciles them to determine `live_status`.
4.  Assigns tasks based on `responsibilities` and `availability_tier`.

## Workflow

1.  **Scan**: `scripts/scan_network.ps1` runs periodically (cron/scheduler).
2.  **Update**: `logs/network_scan_report.json` is refreshed.
3.  **Orchestrate**: Engines (Parlay, Scraper, etc.) query `AvailabilityOrchestrator` to find where to run their workloads.
4.  **Execute**: Workload is dispatched to the assigned IP.

## Security & IP Management
*   **Scan First**: We never assume a node is up. We verify.
*   **Strict Config**: Only IPs listed in `nodes.json` are trusted.
*   **Exclusion**: The LG TV is explicitly blocked to prevent accidental casting or connection attempts.

## Future Expansion
To add a new node:
1.  Add entry to `config/nodes.json`.
2.  Assign Role and Tier.
3.  The Orchestrator automatically picks it up in the next cycle.
