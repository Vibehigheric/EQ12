#!/bin/bash
# EQ12 Cluster Control Center (WSL Edition)
# Expert management for the Distributed Betting System

INVENTORY=~/eq12_cluster/inventory.ini

function show_header() {
    clear
    echo "=================================================="
    echo "   EQ12 CLUSTER CONTROL CENTER (WSL)"
    echo "=================================================="
}

function check_status() {
    show_header
    echo "[*] Pinging Cluster Nodes..."
    ansible -i $INVENTORY all -m ping
    
    echo ""
    echo "[*] Edge Node (Pi) Docker Status:"
    docker --context eq12-edge ps --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"
    
    echo ""
    echo "[*] TPU Availability:"
    ssh eq12-pi "lsusb | grep -i 'Global\|Google'" || echo "TPU NOT FOUND"
    
    read -p "Press Enter to continue..."
}

function deploy_templates() {
    show_header
    echo "[*] Syncing Templates to Edge Node..."
    # We assume we are running from repo root or scripts dir
    # Find the templates dir
    if [ -d "coral_templates" ]; then
        SRC="coral_templates/"
    elif [ -d "../scripts/coral_templates" ]; then
        SRC="../scripts/coral_templates/"
    elif [ -d "/mnt/c/EQ12_BROKEN_20251122_210342/scripts/coral_templates" ]; then
        SRC="/mnt/c/EQ12_BROKEN_20251122_210342/scripts/coral_templates/"
    else
        echo "Error: Could not find coral_templates directory."
        read -p "Press Enter..."
        return
    fi
    
    rsync -avz -e ssh $SRC eq12-pi:~/coral_templates/
    ssh eq12-pi "chmod +x ~/coral_templates/*.sh"
    
    echo "[+] Deployment Complete."
    read -p "Press Enter..."
}

function run_demo() {
    show_header
    echo "[*] Triggering Sports Demo on Edge Node..."
    ssh eq12-pi "cd ~/coral_templates && ./run_sports_demo.sh"
    read -p "Press Enter..."
}

function view_logs() {
    show_header
    echo "[*] Tailing Logs on Edge Node..."
    # Assuming the container logs to stdout, we can attach or view logs
    # But our script runs interactively. Let's just check the last run output if saved, 
    # or run a quick check.
    ssh eq12-pi "dmesg | grep -i tpu | tail -n 10"
    read -p "Press Enter..."
}

while true; do
    show_header
    echo "1. Check Cluster Status (Ansible + Docker)"
    echo "2. Deploy Templates (Rsync)"
    echo "3. Run Sports Demo (Remote Exec)"
    echo "4. View TPU Logs"
    echo "5. Exit"
    echo "=================================================="
    read -p "Select Option: " opt
    
    case $opt in
        1) check_status ;;
        2) deploy_templates ;;
        3) run_demo ;;
        4) view_logs ;;
        5) exit 0 ;;
        *) echo "Invalid option" ;;
    esac
done
