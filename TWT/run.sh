#!/bin/bash

cd /Users/federicolombardo/Documents/GitHub/ns-3-twt/TWT

# Crea cartella logs se non esiste
mkdir -p logs

# Timestamp per questa run
TS=$(date +%Y%m%d_%H%M%S)
LOG_DIR="logs/run_${TS}"
mkdir -p "$LOG_DIR"

echo "=== Run $TS ===" 
echo "Log in: $LOG_DIR"

# Lancia ns-3 in background loggando l'output
./ns3 --run "twtUDP \
  --simId=1 \
  --globalSeed=42 \
  --nStations=10 \
  --frequency=5 \
  --mcs=4#4#6#6#8#8#10#10#11#11 \
  --packetPeriodicity=0.1024#0.2048#0.1024#0.3072#0.1024#0.2048#0.1024#0.3072#0.1024#0.2048 \
  --payloadSize=700#700#1000#1000#500#500#1400#1400#700#700 \
  --twtDuration=5#5#5#5#5#5#5#5#5#5 \
  --simulationTime=15360 \
  --t0=0.1#0.1#0.1#0.1#0.1#0.1#0.1#0.1#0.1#0.1 \
  --t1=1#1#1#1#1#1#1#1#1#1 \
  --STAtype=3#3#3#3#3#3#3#3#3#3 \
  --trafficType=0#0#0#0#0#0#0#0#0#0" 2>&1 | tee "$LOG_DIR/ns3.log" &

NS3_PID=$!

# Lancia Python
source /Users/federicolombardo/Documents/GitHub/ns-3-twt/.venv/bin/activate
python3 test_canale.py 2>&1 | tee "$LOG_DIR/python.log"

# Aspetta ns-3
wait $NS3_PID

echo ""
echo "=== Fine run $TS ==="
echo "Log salvati in: $LOG_DIR"