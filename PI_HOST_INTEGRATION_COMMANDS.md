
# EQ12 Host Integration Commands
# Run these commands on Windows host after Pi is configured

# 1. Test Pi connectivity
ping -n 4 192.168.1.200

# 2. Test SSH connectivity  
ssh pi@192.168.1.200 "echo 'SSH connection successful'"

# 3. Generate SSH key for automated access
ssh-keygen -t rsa -b 4096 -f C:\EQ12\ssh_keys\eq12_pi_key -N ""

# 4. Copy SSH key to Pi
scp C:\EQ12\ssh_keys\eq12_pi_key.pub pi@192.168.1.200:~/.ssh/authorized_keys

# 5. Test key-based SSH
ssh -i C:\EQ12\ssh_keys\eq12_pi_key pi@192.168.1.200 "echo 'Key-based SSH working'"

# 6. Add Pi to EQ12 cluster
cd C:\EQ12\scripts
python eq12_raspberry_pi_cluster_manager.py --action add-node --ip 192.168.1.200 --username pi --ssh-key "C:\EQ12\ssh_keys\eq12_pi_key"

# 7. Start cluster
python eq12_raspberry_pi_cluster_manager.py --action start

# 8. Monitor cluster status
python eq12_raspberry_pi_cluster_manager.py --action status

# 9. Generate dashboard
python eq12_raspberry_pi_cluster_manager.py --action dashboard

# 10. Test with sample tasks
python eq12_raspberry_pi_cluster_manager.py --action test-task
