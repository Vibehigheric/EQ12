# 🥧 Pi SSH Operations Handbook

**Role**: Edge Inference Node (TPU)
**IP**: `192.168.1.80`
**User**: `ricoj100`

---

## 🔑 1. Connection & Access

**Connect via SSH:**
```bash
ssh ricoj100@192.168.1.80
```

**Verify Identity:**
```bash
hostname  # Should be 'raspberrypi' or similar
uname -m  # Should be 'aarch64'
```

---

## 🧠 2. TPU Management (Coral)

The Pi's primary job is running the Google Coral TPU.

**Check TPU Visibility:**
```bash
lsusb
# Look for: "Global Unichip Corp." or "Google Inc."
```

**Test TPU Driver:**
```bash
# If installed correctly, this python import should work:
python3 -c "import tflite_runtime.interpreter as tflite; print('TPU Driver OK')"
```

**Restart TPU Subsystem (if stuck):**
```bash
sudo systemctl restart udev
# Unplug and replug USB stick if necessary
```

---

## 🐳 3. Docker & Swarm Operations

**Check Swarm Status:**
```bash
docker node ls
# Note: You might only see 'Self' if it's a worker.
# To see full list, run on Manager (EQ12).
```

**Check Running Containers:**
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
```

**View Container Logs:**
```bash
docker service logs -f eq12_prop-tensor
```

**Prune Unused Images (Save SD Card Space):**
```bash
docker system prune -a -f
```

---

## ⚡ 4. Performance Monitoring

**Check Temperature:**
```bash
vcgencmd measure_temp
# Keep below 80°C. Throttling starts at 80°C.
```

**Check RAM Usage:**
```bash
free -h
# Pi has 8GB. If 'used' > 6GB, consider restarting services.
```

**Check Load:**
```bash
htop
```

---

## 🛑 5. "Do Not Do" List

1.  **DO NOT** run `docker swarm init`. The Pi is a **Worker**, not a Manager.
2.  **DO NOT** pull `amd64` images. Always look for `arm64` or `multiarch` tags.
3.  **DO NOT** run heavy databases (Postgres/MySQL) on the SD card. Use the M70q for that.
4.  **DO NOT** change the hostname. The Swarm relies on it.
5.  **DO NOT** unplug the TPU while a container is using it.

---

## 🛠️ 6. Emergency Recovery

**If Pi drops from Swarm:**
1.  **Leave Swarm:**
    ```bash
    docker swarm leave --force
    ```
2.  **Get New Token (from EQ12):**
    ```powershell
    # On EQ12
    docker swarm join-token worker
    ```
3.  **Re-Join:**
    ```bash
    # On Pi
    docker swarm join --token <TOKEN> 192.168.100.1:2377 --advertise-addr 192.168.1.80
    ```
