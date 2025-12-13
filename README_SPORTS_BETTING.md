# EQ12 Expert Sports Betting Architecture

This system uses a distributed architecture to gain an edge in sports betting by combining **Edge AI (Computer Vision)** with **Cluster Processing (Strategy)**.

## Architecture

1.  **The Eyes (Edge Node)**: Raspberry Pi 5 + Google Coral TPU
    *   **Role**: Watches live video feeds (HDMI capture or stream).
    *   **Tech**: Docker container `eq12-coral` running `eq12_sports_edge.py`.
    *   **Function**: Detects game state (e.g., "Ball in Play", "Goal Scored", "Timeout") in milliseconds using the TPU.
    *   **Latency**: ~5-10ms inference time.

2.  **The Brain (Cluster)**: EQ12 Windows/Linux Node
    *   **Role**: Receives signals and executes bets.
    *   **Tech**: Python `eq12_betting_cluster.py`.
    *   **Function**: Applies betting strategy, manages bankroll, and places orders via API.

## How to Run

### 1. Start the Edge Node (Raspberry Pi)

SSH into your Pi (`192.168.1.80`) and run the Sports Vision module:

```bash
cd ~/coral_templates
# Download the Sports Models (First time only)
./run_sports_demo.sh

# The script will:
# 1. Download SSD MobileNet V2 (if missing)
# 2. Run the Docker container with TPU access
# 3. Analyze the sample image (or your custom input)
# 4. Output a JSON signal
```

To run on a custom image or stream:
```bash
./run_sports_demo.sh /path/to/your/image.jpg <CLUSTER_IP>
```

### 2. Start the Cluster Engine (Windows/Server)

On your main machine:

```powershell
python src/eq12_betting_cluster.py
```

(Currently runs in simulation mode. To make it live, implement a Flask/FastAPI receiver in `eq12_betting_cluster.py`).

## Expert Tips

*   **Latency is King**: The Coral TPU processes frames faster than a human can blink. Use this to detect events (like a goal) *before* the odds update on public streams.
*   **Custom Models**: Train a custom TFLite model to read the specific scoreboard font of your target league.
*   **Data Pipeline**: Pipe the JSON output from the Pi into a time-series DB (InfluxDB) to backtest your strategies.
