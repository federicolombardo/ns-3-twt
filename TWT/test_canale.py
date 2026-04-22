import json
import os
import time
import sys
import random
import numpy as np

GLOBAL_SEED = 42
random.seed(GLOBAL_SEED)
np.random.seed(GLOBAL_SEED)

BEACON_BASE = "/Users/federicolombardo/Documents/GitHub/ns-3-twt/TWT/output_beacon"
STATE_FILE  = BEACON_BASE + "_state.json"
ACTION_FILE = BEACON_BASE + "_action.json"
ACK_FILE    = BEACON_BASE + "_ack.json"
DONE_FILE   = BEACON_BASE + "_done.json"

TIMEOUT_SECONDI = 60
MAX_BEACON = 119
NUMBER_OF_STA = 10


def aspetta_file(percorso, timeout_s):
    atteso = 0.0
    while not os.path.exists(percorso) and atteso < timeout_s:
        time.sleep(0.05)
        atteso += 0.05
    return os.path.exists(percorso)


def main():
    for f in [STATE_FILE, ACTION_FILE, ACK_FILE, DONE_FILE]:
        try: os.remove(f)
        except: pass

    print(f"Seed globale: {GLOBAL_SEED}")
    print(f"Aspetto {MAX_BEACON} beacon da ns-3...\n")

    beacon_count = 0
    storia = []  # per verificare che le metriche cambino beacon per beacon

    while beacon_count < MAX_BEACON:
        print(f"[Python] Aspetto beacon #{beacon_count + 1}...")

        if not aspetta_file(STATE_FILE, TIMEOUT_SECONDI):
            print("[ERRORE] Timeout stato")
            sys.exit(1)

        time.sleep(0.05)

        with open(STATE_FILE, 'r') as f:
            stato = json.load(f)
        try: os.remove(STATE_FILE)
        except: pass

        print(f"  Beacon #{beacon_count+1} @ {stato['sim_time_ms']:.1f} ms")

        snapshot_beacon = []
        for sta in stato['stations']:
            print(f"  STA{sta['sta_id']}: "
                  f"lat={sta['avg_lat_ms']:.3f}ms | "
                  f"loss={sta['pktloss_perc']:.2f}% | "
                  f"rx={sta['rx_count']} pkt | "
                  f"tx={sta['tx_count']} pkt | "
                  f"twt={sta['twt_duration_ms']}ms | "
                  f"energy={sta['beacon_energy_J']*1000:.4f}mJ")
            
            snapshot_beacon.append(sta['avg_lat_ms'])

        storia.append(snapshot_beacon)

        # Verifica che le metriche stiano cambiando (dal secondo beacon in poi)
        if beacon_count >= 1:
            delta = [abs(storia[-1][i] - storia[-2][i]) for i in range(len(storia[-1]))]
            if all(d < 1e-9 for d in delta):
                print("  [ATTENZIONE] Latenze identiche al beacon precedente: "
                      "le metriche sono ancora cumulative?")
            else:
                print(f"  [OK] Metriche cambiate rispetto al beacon precedente "
                      f"(delta max lat: {max(delta):.4f} ms)")

        # Alterna durate per forzare rinegoziazione e vedere l'effetto sulle latenze
        #durate = [10.0] * NUMBER_OF_STA if beacon_count % 2 == 0 else [2.0] * NUMBER_OF_STA
        #durate = [5.0] * NUMBER_OF_STA  TEST 1: durate fisse
        
        #if beacon_count < 4:
        #    durate = [5.0] * NUMBER_OF_STA
        #else:
        #    durate = [10.0] * NUMBER_OF_STA TEST 2: durate che cambiano dopo 4 beacon

        #durate = [10.0] * NUMBER_OF_STA if (beacon_count // 3) % 2 == 0 else [5.0] * NUMBER_OF_STA # TEST 3: durate che cambiano ogni 3 beacon

        durate = [10.0] * NUMBER_OF_STA if beacon_count % 2 == 0 else [5.0] * NUMBER_OF_STA  # TEST 4: durate che cambiano ogni beacon


        with open(ACTION_FILE, 'w') as f:
            json.dump({"twt_durations": durate}, f)
        print(f"  Azione inviata: {durate}\n")

        if not aspetta_file(ACK_FILE, TIMEOUT_SECONDI):
            print("[ERRORE] Timeout ACK")
            sys.exit(1)

        try:
            with open(ACK_FILE, 'r') as f:
                ack = json.load(f)
            print(f"  ACK @ sim_time={ack.get('sim_time_ms','?')}ms")
        except: pass
        try: os.remove(ACK_FILE)
        except: pass

        with open(DONE_FILE, 'w') as f:
            json.dump({"done": True}, f)

        beacon_count += 1

    print("\n" + "="*50)
    print(f"TEST COMPLETATO: {MAX_BEACON} beacon scambiati con seed={GLOBAL_SEED}")
    print("Metriche per-beacon registrate:")
    for i, snap in enumerate(storia):
        print(f"  Beacon {i+1}: {[f'{v:.3f}ms' for v in snap]}")
    print("="*50)


if __name__ == "__main__":
    main()