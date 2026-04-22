import json
import os
import time
import sys
import argparse
import numpy as np
from mab import UCBAgent, AZIONI


# ── Parser argomenti ─────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(
        description="MAB Controller online per TWT ns-3"
    )
    p.add_argument("--sim-time-ms", type=float, default=15360.0,
                   help="Durata totale della simulazione ns-3 in ms.")
    p.add_argument("--beacon-interval-ms", type=float, default=102.4,
                   help="Intervallo tra due beacon TWT consecutivi in ms.")
    p.add_argument("--first-beacon-ms", type=float, default=3174.4,
                   help="Timestamp (ms) del primo beacon TWT sincronizzato.")
    p.add_argument("--n-stations", type=int, default=10,
                   help="Numero di STA nella simulazione.")
    p.add_argument("--seed", type=int, default=42,
                   help="Seed globale per la riproducibilità.")
    p.add_argument("--beacon-base", type=str,
                   default="/Users/federicolombardo/Documents/GitHub/ns-3-twt/TWT/output_beacon",
                   help="Prefisso dei file di sincronizzazione (_state/_action/_ack/_done).")
    p.add_argument("--timeout-s", type=float, default=60.0,
                   help="Timeout (s) per l'attesa dei file da ns-3.")
    return p.parse_args()


def aspetta_file(percorso, timeout_s):
    atteso = 0.0
    while not os.path.exists(percorso) and atteso < timeout_s:
        time.sleep(0.05)
        atteso += 0.05
    return os.path.exists(percorso)


def main():
    args = parse_args()

    BEACON_BASE     = args.beacon_base
    STATE_FILE      = BEACON_BASE + "_state.json"
    ACTION_FILE     = BEACON_BASE + "_action.json"
    ACK_FILE        = BEACON_BASE + "_ack.json"
    DONE_FILE       = BEACON_BASE + "_done.json"

    GLOBAL_SEED     = args.seed
    NUMBER_OF_STA   = args.n_stations
    TIMEOUT_SECONDI = args.timeout_s

    # MAX_BEACON = numero di beacon che ns-3 genererà durante l'intera
    # simulazione. ns-3 schedula la callback a partire da first_beacon_ms
    # e ogni beacon_interval_ms finché sim_time < sim_time_ms.
    # Calcolarlo dinamicamente evita che il MAB finisca prima di ns-3
    # (causava ~20 TIMEOUT a 30s ciascuno, ~10 minuti wall clock sprecati).
    MAX_BEACON = int(
        (args.sim_time_ms - args.first_beacon_ms) / args.beacon_interval_ms
    ) + 1

    np.random.seed(GLOBAL_SEED)

    # Pulizia file residui (run.sh li ha già puliti, ma ridondanza protettiva)
    for f in [STATE_FILE, ACTION_FILE, ACK_FILE, DONE_FILE,
              ACTION_FILE + ".tmp", DONE_FILE + ".tmp"]:
        try: os.remove(f)
        except OSError: pass

    # Inizializza un agente UCB per ogni STA
    agenti = [UCBAgent(sta_id=i+1, seed=GLOBAL_SEED) for i in range(NUMBER_OF_STA)]

    # Tiene traccia dell'ultima azione scelta per ogni STA
    ultime_azioni = [AZIONI[0]] * NUMBER_OF_STA

    print(f"MAB Controller avviato | seed={GLOBAL_SEED} | "
          f"STA={NUMBER_OF_STA} | beacon={MAX_BEACON}")
    print(f"Simulazione: {args.sim_time_ms:.0f}ms | "
          f"primo beacon @{args.first_beacon_ms:.1f}ms | "
          f"intervallo {args.beacon_interval_ms:.1f}ms")
    print(f"Azioni disponibili: {AZIONI} ms")
    print(f"Pesi reward: energia={0.5} latenza={0.3} loss={0.2}\n")

    beacon_count = 0

    while beacon_count < MAX_BEACON:
        print(f"[MAB] Aspetto beacon #{beacon_count + 1}...")

        # ── 1. Aspetta stato da ns-3 ─────────────────────────────────
        if not aspetta_file(STATE_FILE, TIMEOUT_SECONDI):
            print(f"[ERRORE] Timeout stato al beacon #{beacon_count + 1}")
            sys.exit(1)

        time.sleep(0.05)

        with open(STATE_FILE, 'r') as f:
            stato = json.load(f)
        try: os.remove(STATE_FILE)
        except OSError: pass

        sim_time = stato['sim_time_ms']

        # ── Check di monotonia: se sim_time va indietro, è un file
        # residuo (race condition con una vecchia istanza ns-3).
        # run.sh fa pkill all'avvio, ma per sicurezza logghiamo l'anomalia.
        print(f"  [CHECK] beacon_count={beacon_count} | "
              f"sim_time ricevuto={sim_time:.1f}ms")

        print(f"  Beacon #{beacon_count+1} @ {sim_time:.1f} ms")

        # ── 2. Aggiorna ogni agente con le metriche ricevute ─────────
        # (solo dal secondo beacon in poi — al primo non abbiamo ancora
        #  un'azione da valutare)
        if beacon_count > 0:
            for sta in stato['stations']:
                idx     = sta['sta_id'] - 1
                azione  = ultime_azioni[idx]
                agenti[idx].aggiorna(azione, sta)

        # ── 3. Ogni agente sceglie la nuova azione ───────────────────
        nuove_durate = []
        for i, agente in enumerate(agenti):
            scelta = agente.scegli()
            ultime_azioni[i] = scelta
            nuove_durate.append(scelta)

        # ── 4. Stampa stato attuale ──────────────────────────────────
        for sta in stato['stations']:
            idx = sta['sta_id'] - 1
            print(f"  STA{sta['sta_id']}: "
                  f"lat={sta['avg_lat_ms']:.3f}ms | "
                  f"loss={sta['pktloss_perc']:.2f}% | "
                  f"energy={sta['beacon_energy_J']*1000:.4f}mJ | "
                  f"twt_attivo={sta['twt_duration_ms']}ms | "
                  f"→ scelta={nuove_durate[idx]}ms")

        # ── 5. Scrivi azione (atomica via rename) ────────────────────
        tmp_path = ACTION_FILE + ".tmp"
        with open(tmp_path, 'w') as f:
            json.dump({"twt_durations": nuove_durate}, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, ACTION_FILE)

        # ── 6. Aspetta ACK ───────────────────────────────────────────
        if not aspetta_file(ACK_FILE, TIMEOUT_SECONDI):
            print(f"[ERRORE] Timeout ACK al beacon #{beacon_count + 1}")
            sys.exit(1)

        try:
            with open(ACK_FILE, 'r') as f:
                ack = json.load(f)
            print(f"  ACK @ sim_time={ack.get('sim_time_ms','?')}ms")
        except (OSError, json.JSONDecodeError): pass
        try: os.remove(ACK_FILE)
        except OSError: pass

        # ── 7. Scrivi done (atomica via rename) ──────────────────────
        tmp_done = DONE_FILE + ".tmp"
        with open(tmp_done, 'w') as f:
            json.dump({"done": True}, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_done, DONE_FILE)

        beacon_count += 1

    # ── Fine run: stampa stato finale di ogni agente ─────────────────
    print("\n" + "="*60)
    print(f"MAB COMPLETATO: {MAX_BEACON} beacon | seed={GLOBAL_SEED}")
    print("="*60)
    for agente in agenti:
        print(agente.stato_str())
    print("="*60)


if __name__ == "__main__":
    main()
