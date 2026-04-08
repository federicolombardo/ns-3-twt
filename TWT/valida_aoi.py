import subprocess
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os

# ══════════════════════════════════════════════════════════════
# VALIDAZIONE AoI — verifica che last_AOI vari correttamente
# con packetPeriodicity, a parità di tutti gli altri parametri
# ══════════════════════════════════════════════════════════════

PERIODICITA_TEST = [0.1, 0.5, 1.0, 2.0, 5.0]
DURATION_FISSA   = 20      # teniamo fissa la duration
SIM_TIME         = 102400  # lungo abbastanza per statistiche stabili

os.makedirs("validazione_aoi", exist_ok=True)
risultati = []

for periodicity in PERIODICITA_TEST:
    sim_id   = int(datetime.datetime.now().timestamp())
    out_path = f"validazione_aoi/p{periodicity}"
    os.makedirs(out_path, exist_ok=True)

    cmd = (
        f'./ns3 --run "twtUDP '
        f'--simId={sim_id} '
        f'--nStations=1 '
        f'--t0=0.1 '
        f'--t1=0.1 '
        f'--twtDuration={DURATION_FISSA} '
        f'--packetPeriodicity={periodicity} '
        f'--enableTWT=true '
        f'--mcs=4 '
        f'--STAtype=3 '
        f'--frequency=5 '
        f'--twtTriggerBased=false '
        f'--simulationTime={SIM_TIME} '
        f'--csv-output-file={out_path}/raw"'
    )

    print(f"▶ Lancio run: packetPeriodicity={periodicity}s")
    with open(f"{out_path}/terminal_log.txt", "w") as f_log:
     subprocess.run(cmd, shell=True, stdout=f_log, stderr=subprocess.STDOUT)
    csv_path = f"{out_path}/raw.csv"
    if os.path.exists(csv_path):
        df  = pd.read_csv(csv_path)
        row = df.iloc[0]

        aoi_ms        = row.get("last_AOI", -1)
        latenza_ms    = row.get("avg_lat_ms", -1)
        energia_j     = row.get("energymodel_total_energy_J", -1)
        sleep_t_pct   = row.get("SLEEP_time_percentage", -1)
        idle_e_pct    = row.get("IDLE_energy_percentage", -1)
        aoi_teorica   = (periodicity * 1000) / 2  # ms

        risultati.append({
            "periodicity_s":  periodicity,
            "aoi_misurata_ms": aoi_ms,
            "aoi_teorica_ms":  aoi_teorica,
            "errore_pct":      abs(aoi_ms - aoi_teorica) / aoi_teorica * 100 if aoi_teorica > 0 else -1,
            "latenza_ms":      latenza_ms,
            "energia_J":       energia_j,
            "sleep_time_pct":  sleep_t_pct,
            "idle_energy_pct": idle_e_pct,
        })

        print(f"   AoI misurata: {aoi_ms:.1f}ms | AoI teorica: {aoi_teorica:.1f}ms | "
              f"Errore: {abs(aoi_ms - aoi_teorica)/aoi_teorica*100:.1f}%")
    else:
        print(f"   ❌ CSV non trovato")

# ── Stampa tabella ─────────────────────────────────────────────
print("\n" + "="*75)
print(f"{'Periodicità':>12} {'AoI misurata':>14} {'AoI teorica':>12} "
      f"{'Errore%':>9} {'Latenza':>9} {'Energia(mJ)':>12}")
print("-"*75)
for r in risultati:
    print(f"{str(r['periodicity_s'])+'s':>12} "
          f"{r['aoi_misurata_ms']:>13.1f}ms "
          f"{r['aoi_teorica_ms']:>11.1f}ms "
          f"{r['errore_pct']:>8.1f}% "
          f"{r['latenza_ms']:>8.2f}ms "
          f"{r['energia_J']*1000:>11.1f}mJ")

# ── Grafici ────────────────────────────────────────────────────
if risultati:
    df_val = pd.DataFrame(risultati)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle(f'Validazione AoI — TWT Duration={DURATION_FISSA}ms',
                 fontsize=13, fontweight='bold')

    # G1: AoI misurata vs teorica
    ax = axes[0]
    ax.plot(df_val['periodicity_s'], df_val['aoi_teorica_ms'],
            'o--', color='#5DCAA5', label='AoI teorica (T/2)', linewidth=1.5)
    ax.plot(df_val['periodicity_s'], df_val['aoi_misurata_ms'],
            's-', color='#378ADD', label='AoI misurata', linewidth=1.5)
    ax.set_xlabel('Packet Periodicity (s)')
    ax.set_ylabel('AoI (ms)')
    ax.set_title('AoI misurata vs teorica')
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    # G2: Errore percentuale
    ax = axes[1]
    bars = ax.bar(range(len(risultati)),
                  df_val['errore_pct'],
                  color=['#D85A30' if e > 20 else '#5DCAA5'
                         for e in df_val['errore_pct']],
                  edgecolor='white')
    ax.set_xticks(range(len(risultati)))
    ax.set_xticklabels([f"{r['periodicity_s']}s" for r in risultati])
    ax.set_ylabel('Errore %')
    ax.set_title('Discrepanza AoI misurata vs teorica')
    ax.axhline(y=20, color='#D85A30', linestyle='--',
               alpha=0.7, linewidth=1, label='soglia 20%')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)
    for bar, val in zip(bars, df_val['errore_pct']):
        ax.text(bar.get_x() + bar.get_width()/2,
                val + 0.3, f'{val:.1f}%',
                ha='center', va='bottom', fontsize=9)

    # G3: Energia vs periodicità (dovrebbe essere piatta — conferma il modello)
    ax = axes[2]
    ax.plot(df_val['periodicity_s'],
            df_val['energia_J'] * 1000,
            's-', color='#D85A30', linewidth=1.5)
    ax.set_xlabel('Packet Periodicity (s)')
    ax.set_ylabel('Energia (mJ)')
    ax.set_title('Energia vs Periodicità\n(attesa piatta — conferma modello)')
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("validazione_aoi/validazione_aoi.png",
                dpi=150, bbox_inches='tight')
    print(f"\n📊 Grafico salvato: validazione_aoi/validazione_aoi.png")
    
df = pd.read_csv("validazione_aoi/p0.1/raw.csv")
print(df.columns.tolist())
print(df.iloc[0].to_string())

rx_bytes    = row.get("rx_bytes_per_class", 0)
tx_bytes    = row.get("tx_bytes_per_class", 0)
payload     = 700  # bytes per pacchetto
pkt_rx      = rx_bytes / payload
pkt_tx      = tx_bytes / payload
pkt_attesi  = (SIM_TIME/1000 - 3.072) / periodicity

print(f"   Pacchetti TX: {pkt_tx:.0f} | RX: {pkt_rx:.0f} | "
      f"Attesi: {pkt_attesi:.0f}")