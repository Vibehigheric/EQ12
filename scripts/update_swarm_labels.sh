#!/bin/bash
# Apply Swarm Labels
docker node update --label-add tier=0 EQ12-Manager
docker node update --label-add capability=orchestration EQ12-Manager
docker node update --label-add capability=capital_allocation EQ12-Manager
docker node update --label-add capability=risk_engine EQ12-Manager
docker node update --label-add capability=parlay_engine EQ12-Manager
docker node update --label-add capability=cli_host EQ12-Manager
docker node update --label-add tier=1 Pi-Worker-01
docker node update --label-add capability=inference_tpu Pi-Worker-01
docker node update --label-add capability=prop_tensor Pi-Worker-01
docker node update --label-add capability=anomaly_detection Pi-Worker-01
docker node update --label-add tier=1 M70q-Worker-Ubuntu
docker node update --label-add capability=heavy_inference_cpu M70q-Worker-Ubuntu
docker node update --label-add capability=docker_swarm_manager_backup M70q-Worker-Ubuntu
docker node update --label-add capability=database_host M70q-Worker-Ubuntu
docker node update --label-add tier=2 VM-Worker-A
docker node update --label-add capability=heavy_scraping VM-Worker-A
docker node update --label-add capability=line_monitoring VM-Worker-A
docker node update --label-add tier=2 VM-Worker-B
docker node update --label-add capability=vpn_rotation VM-Worker-B
docker node update --label-add capability=geofenced_queries VM-Worker-B
docker node update --label-add tier=2 VM-Worker-C
docker node update --label-add capability=anti_book_spoofing VM-Worker-C
docker node update --label-add capability=rate_limit_evasion VM-Worker-C
docker node update --label-add tier=3 TCL-Display
docker node update --label-add capability=visualization TCL-Display
docker node update --label-add capability=dashboard_target TCL-Display
