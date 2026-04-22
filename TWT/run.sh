#!/bin/bash
set -uo pipefail

# ── Configurazione ───────────────────────────────────────────────────
TWT_DIR="/Users/federicolombardo/Documents/GitHub/ns-3-twt/TWT"
BEACON_BASE="${TWT_DIR}/output_beacon"
VENV="/Users/federicolombardo/Documents/GitHub/ns-3-twt/.venv/bin/activate"

cd "${TWT_DIR}"

# ── 1. Kill di eventuali istanze residue (fix concorrenza) ───────────
# Il timeout ns-3 (30s per beacon) può lasciare vivo il binario molti
# minuti dopo che il MAB è terminato. Se partiamo una nuova run mentre
# una vecchia è ancora attiva, le due scrivono sullo stesso set di file
# di sincronizzazione causando sim_time non monotoni e action con 0 durate.
echo "[run.sh] Pulizia istanze residue..."
pkill -f "ns3-dev-twtUDP" 2>/dev/null || true
pkill -f "mab_controller.py" 2>/dev/null || true
sleep 1
pkill -9 -f "ns3-dev-twtUDP" 2>/dev/null || true
pkill -9 -f "mab_controller.py" 2>/dev/null || true

# ── 2. Pulizia file di sincronizzazione residui ──────────────────────
rm -f "${BEACON_BASE}_state.json" \
      "${BEACON_BASE}_action.json" \
      "${BEACON_BASE}_ack.json" \
      "${BEACON_BASE}_done.json" \
      "${BEACON_BASE}_action.json.tmp" \
      "${BEACON_BASE}_done.json.tmp"

# ── 3. Cartella log ──────────────────────────────────────────────────
mkdir -p logs
TS=$(date +%Y%m%d_%H%M%S)
LOG_DIR="logs/run_${TS}"
mkdir -p "${LOG_DIR}"

echo "=== Run ${TS} ==="
echo "Log in: ${LOG_DIR}"

# ── 4. Parametri simulazione (condivisi tra ns-3 e MAB) ──────────────
# Se cambi simulationTime o la schedulazione dei beacon in ns-3, aggiorna qui
# così il MAB sa esattamente quanti beacon aspettare e non finisce prima.
SIM_TIME_MS=40038.4
BEACON_INTERVAL_MS=102.4
FIRST_BEACON_MS=3174.4
N_STATIONS=5
SEED=42

# ── 5. Lancia ns-3 ─────────────────────────────────────

./ns3 --run "twtUDP \
  --simId=1 \
  --globalSeed=${SEED} \
  --nStations=${N_STATIONS} \
  --frequency=5 \
  --mcs=4#4#6#6#8#8#10#10#11#11 \
  --packetPeriodicity=2#4#0.1024#1#3#0.1024#0.05#0.05#0.05#0.05 \
  --payloadSize=200#200#700#700#700#700#1400#1400#1400#1400 \
  --simulationTime=${SIM_TIME_MS} \
  --t0=0.10#0.11#0.12#0.13#0.14#0.15#0.16#0.17#0.18#0.19
  --t1=1#1#1#1#1#1#1#1#1#1 \
  --STAtype=3#3#3#3#3#3#3#3#3#3 \
  --trafficType=0#0#0#0#0#0#0#0#0#0" 2>&1 | tee "${LOG_DIR}/ns3.log" &


NS3_PID=$!

# Cleanup su CTRL+C / SIGTERM
cleanup() {
  echo ""
  echo "[run.sh] Interruzione, chiudo i processi..."
  kill "${NS3_PID}" 2>/dev/null || true
  pkill -f "mab_controller.py" 2>/dev/null || true
  exit 130
}
trap cleanup INT TERM

# ── 6. Lancia MAB ───────────────────────────────────────
# shellcheck disable=SC1090
source "${VENV}"
python3 mab_controller.py \
  --sim-time-ms "${SIM_TIME_MS}" \
  --beacon-interval-ms "${BEACON_INTERVAL_MS}" \
  --first-beacon-ms "${FIRST_BEACON_MS}" \
  --n-stations "${N_STATIONS}" \
  --seed "${SEED}" \
  --beacon-base "${BEACON_BASE}" \
  2>&1 | tee "${LOG_DIR}/mab.log"

# ── 7. Aspetta la fine di ns-3 ───────────────────────────────────────
wait "${NS3_PID}"

# ── 8. Genera riepilogo compatto ─────────────────────────────────────
python3 riepilogo.py "${LOG_DIR}" || true

echo ""
echo "=== Fine run ${TS} ==="
echo "Log salvati in: ${LOG_DIR}"
echo "Summary:       ${LOG_DIR}/summary.md"
