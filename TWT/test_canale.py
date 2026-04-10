"""
test_canale.py - Fase 1 con handshake corretto.
Sequenza per ogni beacon:
  1. ns-3 scrive _state.json
  2. Python legge e CANCELLA _state.json, poi scrive _action.json
  3. ns-3 legge e cancella _action.json, poi scrive _ack.json
  4. Python legge e CANCELLA _ack.json, poi scrive _done.json
  5. ns-3 legge e cancella _done.json, passa al beacon successivo
"""

import json
import os
import time
import sys

BEACON_BASE = "/Users/federicolombardo/Documents/GitHub/ns-3-twt/TWT/output_beacon"

STATE_FILE  = BEACON_BASE + "_state.json"
ACTION_FILE = BEACON_BASE + "_action.json"
ACK_FILE    = BEACON_BASE + "_ack.json"
DONE_FILE   = BEACON_BASE + "_done.json"

TIMEOUT_SECONDI = 60
MAX_BEACON      = 5


def aspetta_file(percorso, timeout_s):
    atteso = 0.0
    while not os.path.exists(percorso) and atteso < timeout_s:
        time.sleep(0.05)
        atteso += 0.05
    return os.path.exists(percorso)


def main():
    # Pulizia file residui prima di iniziare
    for f in [STATE_FILE, ACTION_FILE, ACK_FILE, DONE_FILE]:
        try:
            os.remove(f)
        except:
            pass

    print("=" * 55)
    print("  test_canale.py - Fase 1")
    print(f"  Aspetto {MAX_BEACON} beacon da ns-3...")
    print("=" * 55)
    print()

    beacon_count = 0

    while beacon_count < MAX_BEACON:
        print(f"[Python] Aspetto beacon #{beacon_count + 1}...")

        # ── PASSO 1: aspetta _state.json ────────────────────────────
        trovato = aspetta_file(STATE_FILE, TIMEOUT_SECONDI)
        if not trovato:
            print(f"[Python][ERRORE] Timeout aspettando stato. ns-3 si e' bloccato?")
            sys.exit(1)

        # Piccola pausa per assicurarsi che ns-3 abbia finito di scrivere
        time.sleep(0.05)

        # Leggi lo stato
        try:
            with open(STATE_FILE, 'r') as f:
                stato = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[Python][ERRORE] JSON malformato: {e}")
            sys.exit(1)

        # CANCELLA subito _state.json cosi' ns-3 non lo ri-scrive
        # e Python non lo ri-legge per errore
        try:
            os.remove(STATE_FILE)
        except:
            pass

        print(f"[Python] Beacon #{beacon_count + 1} ricevuto @ {stato['sim_time_ms']:.1f}ms")
        for sta in stato['stations']:
            print(f"         STA{sta['sta_id']}: "
                  f"lat={sta['avg_lat_ms']:.3f}ms  "
                  f"loss={sta['pktloss_perc']:.2f}%  "
                  f"twt={sta['twt_duration_ms']}ms")

        # ── PASSO 2: scrivi _action.json ────────────────────────────
        durate = [sta['twt_duration_ms'] for sta in stato['stations']]
        with open(ACTION_FILE, 'w') as f:
            json.dump({"twt_durations": durate}, f)
        print(f"[Python] Risposta inviata: {durate}")

        # ── PASSO 3: aspetta _ack.json da ns-3 ──────────────────────
        trovato_ack = aspetta_file(ACK_FILE, TIMEOUT_SECONDI)
        if not trovato_ack:
            print(f"[Python][ERRORE] Timeout aspettando ACK")
            sys.exit(1)

        # Leggi l'ACK
        try:
            with open(ACK_FILE, 'r') as f:
                ack = json.load(f)
            print(f"[Python] ACK ricevuto (sim_time={ack.get('sim_time_ms','?')}ms)")
        except:
            print("[Python] ACK ricevuto")

        # CANCELLA _ack.json
        try:
            os.remove(ACK_FILE)
        except:
            pass

        # ── PASSO 4: scrivi _done.json per segnalare a ns-3 ─────────
        with open(DONE_FILE, 'w') as f:
            json.dump({"done": True}, f)

        print(f"[Python] Done scritto. Beacon #{beacon_count + 1} completato.")
        print()

        beacon_count += 1

    print("=" * 55)
    print(f"  TEST SUPERATO: {MAX_BEACON} beacon scambiati!")
    print("  Il canale ns-3 <-> Python funziona correttamente.")
    print("  Puoi procedere alla Fase 2.")
    print("=" * 55)


if __name__ == "__main__":
    main()