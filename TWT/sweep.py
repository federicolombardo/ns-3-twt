"""
sweep_completo.py
=================
Riesegue lo sweep periodicità × twtDuration con le stesse impostazioni
delle 3 run baseline, salvando effective_latency invece di avg_lat_ms.

Modifiche rispetto alla versione precedente:
  - latenza_ms      → effective_latency  (include attesa beacon successivo)
  - feasible        → basato su effective_latency, non avg_lat_ms
  - simulationTime  → 102400ms (stesso delle run baseline, non 256000)
  - twtTriggerBased → true (stesso delle run baseline, era false)
  - Aggiunta colonna avg_lat_ms salvata separatamente per confronto
  - Aggiunta colonna pktloss per completezza
"""

import subprocess
import datetime
import time
import pandas as pd
import os

# ══════════════════════════════════════════════════════════════════════════════
# PARAMETRI — allineati alle 3 run baseline
# ══════════════════════════════════════════════════════════════════════════════

LATENZA_SOGLIA_MS = 50.0     # vincolo QoS

periodicita_test = [0.1, 0.5, 1.0, 2.0, 5.0]   # stesse delle run baseline
durations_test   = [2, 5, 10, 20, 30, 50]        # arms del MAB (include 3ms → aggiunto)

# Impostazioni fisse — identiche alle run baseline
SIM_TIME_MS      = 102400    # era 256000 nello sweep vecchio — allineato alle run
MCS              = 4
FREQUENCY        = 5
TWTTriggerBased  = "true"    # era false nello sweep vecchio — allineato alle run
STAtype          = 3
T0               = 0.1
T1               = 0.1

OUTPUT_DIR = "sweep_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# SWEEP
# ══════════════════════════════════════════════════════════════════════════════
risultati  = []
n_tot      = len(periodicita_test) * len(durations_test)
n_done     = 0
n_failed   = 0

print(f"Avvio sweep: {len(periodicita_test)} periodicità × {len(durations_test)} duration = {n_tot} simulazioni")
print(f"Parametri: simTime={SIM_TIME_MS}ms | MCS={MCS} | TriggerBased={TWTTriggerBased}")
print("=" * 65)

for periodicity in periodicita_test:
    for duration in durations_test:

        # Piccola pausa per evitare collision sui simId basati su timestamp
        time.sleep(1)
        sim_id   = int(datetime.datetime.now().timestamp())
        out_path = f"{OUTPUT_DIR}/p{periodicity}_d{duration}"
        os.makedirs(out_path, exist_ok=True)

        cmd = (
            f'./ns3 --run "twtUDP '
            f'--simId={sim_id} '
            f'--nStations=1 '
            f'--t0={T0} --t1={T1} '
            f'--twtDuration={duration} '
            f'--packetPeriodicity={periodicity} '
            f'--enableTWT=true '
            f'--mcs={MCS} '
            f'--STAtype={STAtype} '
            f'--frequency={FREQUENCY} '
            f'--twtTriggerBased={TWTTriggerBased} '
            f'--simulationTime={SIM_TIME_MS} '
            f'--csv-output-file={out_path}/raw"'
        )

        print(f"[{n_done+1:2d}/{n_tot}] periodicity={periodicity}s  duration={duration}ms ... ", end="", flush=True)
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        csv_path = f"{out_path}/raw.csv"
        if os.path.exists(csv_path):
            df  = pd.read_csv(csv_path)
            row = df.iloc[0]

            # ── Latenza: usa effective_latency se disponibile ──────────────
            # effective_latency include l'attesa del beacon successivo
            # quando la SP è troppo corta per il pacchetto in arrivo.
            # avg_lat_ms misura solo la latenza MAC (~1ms sempre) ed è
            # inutilizzabile come metrica QoS per il MAB.
            eff_lat = row.get("effective_latency", None)
            avg_lat = row.get("avg_lat_ms", None)

            if eff_lat is None or (isinstance(eff_lat, float) and pd.isna(eff_lat)):
                # Fallback a avg_lat solo se effective_latency non esiste
                lat_usata = avg_lat if avg_lat is not None else 999.0
                fonte_lat = "avg_lat_ms (fallback)"
            else:
                lat_usata = float(eff_lat)
                fonte_lat = "effective_latency"

            risultati.append({
                "periodicity_s":    periodicity,
                "duration_ms":      duration,
                "idle_energy_pct":  row.get("IDLE_energy_percentage", 0),
                "sleep_time_pct":   row.get("SLEEP_time_percentage", 0),
                "energy_J":         row.get("energymodel_total_energy_J", 0),
                # Latenza corretta per il MAB
                "latenza_ms":       lat_usata,
                "fonte_latenza":    fonte_lat,
                # Latenza MAC separata per riferimento
                "avg_lat_ms":       avg_lat if avg_lat is not None else 0,
                "pktloss_pct":      row.get("pktloss_perc", 0),
                # feasible basato su effective_latency, non avg_lat_ms
                "feasible":         lat_usata < LATENZA_SOGLIA_MS,
            })
            print(f"✅  lat={lat_usata:.1f}ms  energy={row.get('energymodel_total_energy_J',0)*1000:.0f}mJ  feasible={lat_usata < LATENZA_SOGLIA_MS}")
            n_done += 1
        else:
            print(f"❌ CSV non trovato")
            n_failed += 1

# ══════════════════════════════════════════════════════════════════════════════
# SALVATAGGIO
# ══════════════════════════════════════════════════════════════════════════════
df_sweep = pd.DataFrame(risultati)
out_csv  = f"{OUTPUT_DIR}/sweep_completo.csv"
df_sweep.to_csv(out_csv, index=False)

print("\n" + "=" * 65)
print(f"Sweep completato: {n_done} ok, {n_failed} falliti")
print(f"Salvato: {out_csv}")
print("\nAnteprima risultati:")
print(df_sweep[["periodicity_s","duration_ms","latenza_ms","feasible","energy_J"]].to_string())

# Sanity check: verifica che effective_latency e avg_lat_ms differiscano
# nei casi critici (periodicità alta + duration bassa)
print("\n── Sanity check: casi con latenza > 10ms (dovrebbero esserci) ──")
critici = df_sweep[df_sweep["latenza_ms"] > 10]
if len(critici) > 0:
    print(critici[["periodicity_s","duration_ms","latenza_ms","avg_lat_ms","feasible"]].to_string())
else:
    print("⚠️  Nessun caso critico trovato — verifica che effective_latency")
    print("    sia la colonna giusta nel CSV delle run (controlla con prova.py)")