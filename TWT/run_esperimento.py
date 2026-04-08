import os
import subprocess
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import shutil

# ==========================================
# 1. IMPOSTA QUI I TUOI PARAMETRI PER LA RUN
# ==========================================

# Profili IoT realistici — uno per STA, fissi e deliberati
# STA1=sensore veloce, STA2=medio, STA3-5=lenti (tipico IoT)
"""""
IOT_PERIODICITY = [0.1, 0.5, 1.0, 2.0, 5.0]
params = {
    "nStations": 5, # Quanti dispositivi IoT ci sono nella rete          # fisso — parametro MAB futuro
    "twtDuration": [20, 10, 5, 3, 2],   # La durata della finestra TWT in ms - parametro principale del MAB
    "packetPeriodicity": IOT_PERIODICITY,  # eterogeneo — rappresenta diversi device
    "mcs": 4,            # fisso — non è una scelta del MAB
    "frequency": 5,
    "simulationTime": 102400,
    "enableTWT": "true",
    "twtTriggerBased": "true",
    "STAtype": 3,
}"""


IOT_PERIODICITY = [1.0, 1.0, 1.0, 1.0, 1.0]

params = {
    "nStations": 5,
    "t0": 0.1,
    "t1": 0.1,
    "twtDuration": [5, 5, 5, 5, 5],
    "packetPeriodicity": IOT_PERIODICITY,
    "mcs": 4,
    "frequency": 5,
    "simulationTime": 10240,
    "enableTWT": "true",
    "twtTriggerBased": "true",
    "STAtype": 3,
}

# Generiamo simId e Cartella
sim_id_univoco = int(datetime.datetime.now().timestamp())
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
twt_label = params['twtDuration']
if isinstance(twt_label, list):
    twt_label = "-".join(str(v) for v in twt_label)
folder_name = f"Risultati/Run_{timestamp}_STA-{params['nStations']}_TWT-{twt_label}ms"
os.makedirs(folder_name, exist_ok=True)

# Assicuriamoci che la cartella temporanea di ns-3 esista
if not os.path.exists("outputTWT"):
    os.makedirs("outputTWT")

# ==========================================
# 2. PREPARAZIONE E LANCIO NS-3
# ==========================================
n = params["nStations"]

def rep(val):
    if isinstance(val, list):
        return "#".join([str(v) for v in val])
    else:
        return "#".join([str(val)] * n)
csv_path_ns3 = f"{folder_name}/risultato_raw"

comando_ns3 = (
    f'./ns3 --run "twtUDP '
    f'--simId={sim_id_univoco} '
    f'--nStations={n} '
    f'--t0={rep(params["t0"])} '
    f'--t1={rep(params["t1"])} '
    f'--twtDuration={rep(params["twtDuration"])} '
    f'--packetPeriodicity={rep(params["packetPeriodicity"])} '
    f'--enableTWT={params["enableTWT"]} '
    f'--mcs={rep(params["mcs"])} '
    f'--STAtype={rep(params["STAtype"])} '
    f'--frequency={params["frequency"]} '
    f'--twtTriggerBased={params["twtTriggerBased"]} '
    f'--simulationTime={params["simulationTime"]} '
    f'--csv-output-file={csv_path_ns3}"'
)

print("-" * 50)
print(f"🚀 AVVIO RUN: {timestamp}")
print(f"🛠 COMANDO: {comando_ns3}")
print("-" * 50)

# Esecuzione e cattura log su file
with open(f"{folder_name}/terminal_log.txt", "w") as f_log:
    process = subprocess.Popen(comando_ns3, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        print(line, end="")
        f_log.write(line)
    process.wait()

# ==========================================
# 3. ARCHIVIAZIONE FILE PCAP / STATELOG
# ==========================================
print("\n📦 Spostamento file originali (PCAP e Statelog)...")
if os.path.exists("outputTWT"):
    for file in os.listdir("outputTWT"):
        # Spostiamo i file generati da ns-3 nella cartella della Run
        shutil.move(os.path.join("outputTWT", file), os.path.join(folder_name, file))

# Salviamo la configurazione finale
with open(f"{folder_name}/configurazioni.txt", "w") as f:
    f.write(f"Timestamp: {timestamp}\nID: {sim_id_univoco}\n")
    for key, value in params.items():
        f.write(f"{key}: {value}\n")

# ==========================================
# 4. GENERAZIONE GRAFICI
# ==========================================
csv_file_generato = f"{csv_path_ns3}.csv"

if os.path.exists(csv_file_generato):
    df = pd.read_csv(csv_file_generato)

    # Colonna STA_id: se non esiste la creiamo noi (indice 1-based)
    if 'STA_id' not in df.columns:
        df['STA_id'] = [f'STA {i+1}' for i in range(len(df))]
    else:
        df['STA_id'] = df['STA_id'].astype(str)

    sta_labels = df['STA_id'].tolist()
    df_mean    = df.mean(numeric_only=True)
    n_sta      = len(df)

    COLORS = {
        'Sleep': '#5DCAA5',
        'Idle':  '#378ADD',
        'RX':    '#EF9F27',
        'TX':    '#D85A30',
        'CCA':   '#AFA9EC',
    }

    # ── Helper: estrai colonna con fallback a 0 ────────────────────────────
    def col(name):
        return df[name].tolist() if name in df.columns else [0] * n_sta

    def col_mean(name):
        return df_mean.get(name, 0)

    # ── Valori per-STA ─────────────────────────────────────────────────────
    sleep_e_sta = col('SLEEP_energy_percentage')
    idle_e_sta  = col('IDLE_energy_percentage')
    rx_e_sta    = col('RX_energy_percentage')
    tx_e_sta    = col('TX_energy_percentage')
    cca_e_sta   = col('CCA_BUSY_energy_percentage')

    sleep_t_sta = col('SLEEP_time_percentage')
    idle_t_sta  = col('IDLE_time_percentage')
    rx_t_sta    = col('RX_time_percentage')
    tx_t_sta    = col('TX_time_percentage')
    cca_t_sta   = col('CCA_BUSY_time_percentage')

    lat_sta     = col('avg_lat_ms')
    lat_eff_sta = col('avg_effective_lat_ms') if 'avg_effective_lat_ms' in df.columns else lat_sta
    tput_sta    = col('throughput_Mbps')

    energy_j_sta = col('energymodel_total_energy_J')

    # ── Medie globali (per le torte aggregate) ─────────────────────────────
    sleep_e = col_mean('SLEEP_energy_percentage')
    idle_e  = col_mean('IDLE_energy_percentage')
    rx_e    = col_mean('RX_energy_percentage')
    tx_e    = col_mean('TX_energy_percentage')
    cca_e   = col_mean('CCA_BUSY_energy_percentage')
    sleep_t = col_mean('SLEEP_time_percentage')
    idle_t  = col_mean('IDLE_time_percentage')
    rx_t    = col_mean('RX_time_percentage')
    tx_t    = col_mean('TX_time_percentage')
    cca_t   = col_mean('CCA_BUSY_time_percentage')
    latenza = col_mean('avg_lat_ms')
    lat_eff = col_mean('avg_effective_lat_ms') if 'avg_effective_lat_ms' in df.columns else latenza
    throughput = col_mean('throughput_Mbps')

    x_sta = range(n_sta)
    bar_w = max(0.12, min(0.35, 0.8 / n_sta))  # larghezza barre adattiva

    twt_display = params['twtDuration']
    if isinstance(twt_display, list):
        twt_display = "-".join(str(v) for v in twt_display)
    suptitle = (
        f'Report Simulazione — {n_sta} STA | TWT={twt_display}ms | '
        f'MCS={params["mcs"]} | t={params["simulationTime"]}ms'
    )

    

    # ══════════════════════════════════════════════════════════════════════
    # FIGURA 1 — Overview aggregato (torte medie + paradosso + latenza)
    # Identica alla versione precedente, valida sempre
    # ══════════════════════════════════════════════════════════════════════
    fig1, axes1 = plt.subplots(2, 2, figsize=(14, 10))
    fig1.suptitle(suptitle + ' — Overview', fontsize=13, fontweight='bold', y=1.01)

    # Torta tempo medio
    ax = axes1[0, 0]
    td = [sleep_t, idle_t, rx_t, tx_t, cca_t]
    tl = ['Sleep', 'Idle', 'RX', 'TX', 'CCA']
    tc = [COLORS[l] for l in tl]
    f  = [(s,l,c) for s,l,c in zip(td,tl,tc) if s > 0]
    if f:
        s,l,c = zip(*f)
        _, _, ats = ax.pie(s, labels=l, autopct='%1.1f%%', startangle=90, colors=c,
                           wedgeprops={'edgecolor':'white','linewidth':1.2})
        [at.set_fontsize(9) for at in ats]
    ax.set_title('Distribuzione Tempo — media STA', fontsize=11, pad=12)

    # Torta energia media
    ax = axes1[0, 1]
    ed = [sleep_e, idle_e, rx_e, tx_e, cca_e]
    el = ['Sleep', 'Idle', 'RX', 'TX', 'CCA']
    ec = [COLORS[l] for l in el]
    f  = [(s,l,c) for s,l,c in zip(ed,el,ec) if s > 0]
    if f:
        s,l,c = zip(*f)
        _, _, ats = ax.pie(s, labels=l, autopct='%1.1f%%', startangle=90, colors=c,
                           wedgeprops={'edgecolor':'white','linewidth':1.2})
        [at.set_fontsize(9) for at in ats]
    ax.set_title('Distribuzione Energia — media STA', fontsize=11, pad=12)

    # Paradosso tempo vs energia (medie)
    ax = axes1[1, 0]
    stati     = ['Sleep', 'Idle', 'RX', 'TX', 'CCA']
    t_vals    = [sleep_t, idle_t, rx_t, tx_t, cca_t]
    e_vals    = [sleep_e, idle_e, rx_e, tx_e, cca_e]
    xr        = range(len(stati))
    b1 = ax.bar([i - 0.175 for i in xr], t_vals, 0.35, label='Tempo (%)',   color='#5DCAA5', edgecolor='white')
    b2 = ax.bar([i + 0.175 for i in xr], e_vals, 0.35, label='Energia (%)', color='#378ADD', edgecolor='white')
    for bar in list(b1) + list(b2):
        h = bar.get_height()
        if h > 0.5:
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.4, f'{h:.1f}%',
                    ha='center', va='bottom', fontsize=8)
    ax.set_xticks(list(xr))
    ax.set_xticklabels(stati)
    ax.set_ylabel('%')
    ax.set_title('Paradosso Tempo vs Energia — media', fontsize=11)
    ax.legend(fontsize=9)
    ax.set_ylim(0, max(max(t_vals), max(e_vals)) * 1.18)
    ax.grid(axis='y', alpha=0.3)
    if idle_e > 50 and idle_t < 20:
        ax.annotate(
            f'Idle: {idle_t:.1f}% tempo\nma {idle_e:.1f}% energia!',
            xy=(1 + 0.175, idle_e), xytext=(2.5, idle_e * 0.82),
            arrowprops=dict(arrowstyle='->', color='#D85A30'),
            fontsize=8, color='#D85A30', fontweight='bold'
        )

    # Latenza e throughput medi
    ax  = axes1[1, 1]
    ax.set_title('Prestazioni di Rete — media STA', fontsize=11)
    bl  = ax.bar([0.3, 0.7], [latenza, lat_eff], width=0.25,
                 color=['#EF9F27','#D85A30'], edgecolor='white')
    ax.set_ylabel('ms')
    ax.set_xticks([0.3, 0.7])
    ax.set_xticklabels(['Latenza MAC\n(ms)', 'Latenza Effettiva\n(ms)'], fontsize=9)
    for bar in bl:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h * 1.02, f'{h:.1f} ms',
                ha='center', va='bottom', fontsize=9)
    ax2r = ax.twinx()
    ax2r.bar([1.2], [throughput * n_sta], width=0.25, color='#378ADD', edgecolor='white')
    ax2r.set_ylabel('Mbps', color='#378ADD')
    ax2r.tick_params(axis='y', labelcolor='#378ADD')
    ax2r.set_xlim(0, 1.5)
    ax2r.text(1.2, throughput * n_sta * 1.02, f'{throughput * n_sta:.3f} Mbps',
              ha='center', va='bottom', fontsize=9, color='#378ADD')
    ax.set_xlim(0, 1.5)
    ax.grid(axis='y', alpha=0.3)

    fig1.tight_layout()
    fig1.savefig(f"{folder_name}/grafico_overview.png", bbox_inches='tight', dpi=150)
    plt.close(fig1)

    # ══════════════════════════════════════════════════════════════════════
    # FIGURA 2 — Per-STA (solo se n_sta > 1)
    # ══════════════════════════════════════════════════════════════════════
    if n_sta > 1:
        fig2, axes2 = plt.subplots(3, 2, figsize=(max(14, n_sta * 2.2), 16))
        fig2.suptitle(suptitle + ' — Dettaglio per STA', fontsize=13, fontweight='bold', y=1.01)

        # ── G1: Sleep% vs Idle% energia per STA (barre affiancate) ───────
        ax = axes2[0, 0]
        b1 = ax.bar([i - bar_w/2 for i in x_sta], sleep_t_sta, bar_w,
                    label='Sleep% (tempo)', color='#5DCAA5', edgecolor='white')
        b2 = ax.bar([i + bar_w/2 for i in x_sta], idle_e_sta,  bar_w,
                    label='Idle% (energia)', color='#378ADD', edgecolor='white')
        for bar in list(b1) + list(b2):
            h = bar.get_height()
            if h > 1:
                ax.text(bar.get_x() + bar.get_width()/2, h + 0.4, f'{h:.1f}%',
                        ha='center', va='bottom', fontsize=8)
        ax.set_xticks(list(x_sta))
        ax.set_xticklabels(sta_labels, rotation=0 if n_sta <= 6 else 45)
        ax.set_ylabel('%')
        ax.set_title('Sleep% tempo vs Idle% energia per STA', fontsize=11)
        ax.legend(fontsize=9)
        ax.set_ylim(0, 110)
        ax.axhline(y=sum(sleep_t_sta)/n_sta, color='#5DCAA5', linestyle='--',
                   alpha=0.5, linewidth=1, label='_media')
        ax.axhline(y=sum(idle_e_sta)/n_sta,  color='#378ADD', linestyle='--',
                   alpha=0.5, linewidth=1, label='_media')
        ax.grid(axis='y', alpha=0.3)

        # ── G2: Energia totale per STA (Joule) ────────────────────────────
        ax = axes2[0, 1]
        colors_energy = ['#D85A30' if e == max(energy_j_sta) else
                         '#5DCAA5' if e == min(energy_j_sta) else
                         '#AFA9EC' for e in energy_j_sta]
        bars = ax.bar(list(x_sta), energy_j_sta, bar_w * 1.8,
                      color=colors_energy, edgecolor='white')
        for bar, val in zip(bars, energy_j_sta):
            ax.text(bar.get_x() + bar.get_width()/2, val * 1.01,
                    f'{val*1000:.1f} mJ', ha='center', va='bottom', fontsize=8)
        ax.set_xticks(list(x_sta))
        ax.set_xticklabels(sta_labels, rotation=0 if n_sta <= 6 else 45)
        ax.set_ylabel('Joule')
        ax.set_title('Energia totale per STA', fontsize=11)
        media_e = sum(energy_j_sta) / n_sta
        ax.axhline(y=media_e, color='gray', linestyle='--', alpha=0.6, linewidth=1)
        ax.text(n_sta - 0.5, media_e * 1.01, f'media: {media_e*1000:.1f} mJ',
                fontsize=8, color='gray', ha='right')
        ax.grid(axis='y', alpha=0.3)
        # Legenda colori
        from matplotlib.patches import Patch
        ax.legend(handles=[
            Patch(color='#D85A30', label='STA più energivora'),
            Patch(color='#5DCAA5', label='STA più efficiente'),
            Patch(color='#AFA9EC', label='Altre STA'),
        ], fontsize=8, loc='upper right')

        # ── G3: Latenza MAC per STA ────────────────────────────────────────
        ax = axes2[1, 0]
        b1 = ax.bar([i - bar_w/2 for i in x_sta], lat_sta,     bar_w,
                    label='Latenza MAC (ms)',      color='#EF9F27', edgecolor='white')
        b2 = ax.bar([i + bar_w/2 for i in x_sta], lat_eff_sta, bar_w,
                    label='Latenza Effettiva (ms)', color='#D85A30', edgecolor='white')
        for bar in list(b1) + list(b2):
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h * 1.02,
                        f'{h:.1f}', ha='center', va='bottom', fontsize=7)
        ax.set_xticks(list(x_sta))
        ax.set_xticklabels(sta_labels, rotation=0 if n_sta <= 6 else 45)
        ax.set_ylabel('ms')
        ax.set_title('Latenza per STA', fontsize=11)
        ax.legend(fontsize=9)
        ax.grid(axis='y', alpha=0.3)

        # ── G4: Stacked bar composizione energetica per STA ───────────────
        ax = axes2[1, 1]
        bottom = [0.0] * n_sta
        for stato, valori, colore in [
            ('Sleep', sleep_e_sta, '#5DCAA5'),
            ('Idle',  idle_e_sta,  '#378ADD'),
            ('RX',    rx_e_sta,    '#EF9F27'),
            ('TX',    tx_e_sta,    '#D85A30'),
            ('CCA',   cca_e_sta,   '#AFA9EC'),
        ]:
            ax.bar(list(x_sta), valori, bar_w * 1.8,
                   bottom=bottom, label=stato, color=colore, edgecolor='white')
            # Etichetta dentro la barra solo se la fetta è visibile
            for i, (v, b) in enumerate(zip(valori, bottom)):
                if v > 3:
                    ax.text(i, b + v / 2, f'{v:.0f}%',
                            ha='center', va='center', fontsize=7,
                            color='white', fontweight='bold')
            bottom = [b + v for b, v in zip(bottom, valori)]

        ax.set_xticks(list(x_sta))
        ax.set_xticklabels(sta_labels, rotation=0 if n_sta <= 6 else 45)
        ax.set_ylabel('%')
        ax.set_ylim(0, 105)
        ax.set_title('Composizione energetica per STA (%)', fontsize=11)
        ax.legend(fontsize=8, loc='lower right', ncol=2)
        ax.grid(axis='y', alpha=0.3)

        fig2.tight_layout()
        ax.grid(axis='y', alpha=0.3)

        # ── G5: Packet loss per STA ───────────────────────────────────────
        pktloss_sta = col('pktloss_perc')
        ax = axes2[2, 0]
        colors_loss = ['#D85A30' if p > 5 else
                       '#EF9F27' if p > 1 else
                       '#5DCAA5' for p in pktloss_sta]
        bars = ax.bar(list(x_sta), pktloss_sta, bar_w * 1.8,
                      color=colors_loss, edgecolor='white')
        for bar, val in zip(bars, pktloss_sta):
            if val > 0.01:
                ax.text(bar.get_x() + bar.get_width()/2, val * 1.02,
                        f'{val:.1f}%', ha='center', va='bottom', fontsize=8)
        ax.set_xticks(list(x_sta))
        ax.set_xticklabels(sta_labels, rotation=0 if n_sta <= 6 else 45)
        ax.set_ylabel('%')
        ax.set_title('Packet loss per STA', fontsize=11)
        ax.axhline(y=1, color='#EF9F27', linestyle='--', alpha=0.7, linewidth=1)
        ax.axhline(y=5, color='#D85A30', linestyle='--', alpha=0.7, linewidth=1)
        ax.legend(handles=[
            Patch(color='#D85A30', label='critico > 5%'),
            Patch(color='#EF9F27', label='attenzione > 1%'),
            Patch(color='#5DCAA5', label='ok ≤ 1%'),
        ], fontsize=8)
        ax.grid(axis='y', alpha=0.3)

        # ── G6: Trade-off energia vs packet loss ──────────────────────────
        ax = axes2[2, 1]
        ax.scatter(pktloss_sta, energy_j_sta,
                   c=['#378ADD'] * n_sta, s=120, zorder=5)
        for i, label in enumerate(sta_labels):
            ax.annotate(label,
                        (pktloss_sta[i], energy_j_sta[i]),
                        textcoords="offset points",
                        xytext=(6, 4), fontsize=9)
        ax.set_xlabel('Packet loss (%)')
        ax.set_ylabel('Energia totale (J)')
        ax.set_title('Trade-off: energia vs packet loss', fontsize=11)
        ax.grid(alpha=0.3)

        fig2.tight_layout()
        fig2.savefig(f"{folder_name}/grafico_per_sta.png", bbox_inches='tight', dpi=150)
        plt.close(fig2)

        print(f"📊 Grafici salvati: grafico_overview.png + grafico_per_sta.png")
    else:
        print(f"📊 Grafico salvato: grafico_overview.png")

    print(f"✅ COMPLETATO! Controlla la cartella: {folder_name}")
    print(f"📊 Media -> SLEEP: {sleep_t:.1f}% tempo | IDLE energia: {idle_e:.1f}% | Latenza: {latenza:.2f} ms")

    # Stampa tabella riassuntiva per-STA a terminale
    if n_sta > 1:
        print("\n📋 Riepilogo per STA:")
        print(f"{'STA':<8} {'Sleep%t':>8} {'Idle%e':>8} {'Energia(mJ)':>12} {'Lat(ms)':>9}")
        print("-" * 50)
        for i, sta in enumerate(sta_labels):
            print(f"{sta:<8} {sleep_t_sta[i]:>7.1f}% {idle_e_sta[i]:>7.1f}% "
                  f"{energy_j_sta[i]*1000:>11.1f} {lat_sta[i]:>8.1f}")

        pktloss_sta = col('pktloss_perc')
        print("\n📋 Packet Loss per STA:")
        print(f"{'STA':<8} {'Periodicità':>12} {'Duration':>10} {'PktLoss%':>10} {'Latenza':>9}")
        print("-" * 55)
        for i, sta in enumerate(sta_labels):
            per = params['packetPeriodicity'][i] if isinstance(params['packetPeriodicity'], list) else params['packetPeriodicity']
            dur = params['twtDuration'][i] if isinstance(params['twtDuration'], list) else params['twtDuration']
            loss = pktloss_sta[i]
            flag = " ⚠️" if loss > 1 else ""
            print(f"{sta:<8} {str(per)+'s':>12} {str(dur)+'ms':>10} {loss:>9.2f}%{flag}")


else:
    print("❌ Errore: Il CSV non è stato trovato. La simulazione potrebbe essere fallita.")