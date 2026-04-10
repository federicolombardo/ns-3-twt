"""
mab.py — Multi-Armed Bandit per ottimizzazione TWT dinamico
============================================================
Algoritmo: epsilon-greedy con epsilon decrescente nel tempo.

Struttura cartelle prodotta:
    Risultati/
    └── MAB_2026-xx-xx_xx-xx-xx/
        ├── mab_log.json
        ├── grafico_mab.png
        ├── Run_..._epoch01_arm2_explore/
        │   ├── risultato_raw.csv
        │   ├── metriche.json          <- dati completi per validazione
        │   ├── configurazioni.txt
        │   ├── terminal_log.txt
        │   └── grafico_overview.png   <- solo ogni GENERA_GRAFICI_OGNI epoch
        ├── Run_..._epoch02_arm0_exploit/
        └── ...

Reward = w_energy * (1 - idle_energy_norm) + w_latency * (1 - latency_norm)
"""

import os
import json
import datetime
import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from run_esperimento import run


# ==========================================
# CONFIGURAZIONE MAB
# ==========================================

PARAMS_FISSI = {
    "nStations":         5,
    "t0":                0.1,
    "t1":                0.1,
    "packetPeriodicity": [0.5, 1.0, 2.0, 2.0, 5.0],
    "mcs":               4,
    "frequency":         5,
    "simulationTime":    10240,
    "enableTWT":         "true",
    "twtTriggerBased":   "true",
    "STAtype":           3,
}

ARMS = {
    0: [10, 10, 10, 10, 10],   # naive uguale (Run C)
    1: [8,   6,  4,  4,  2],   # calibrato manuale (Run D)
    2: [5,   5,  5,  5,  5],   # omogeneo piccolo (Run B)
    3: [12,  8,  5,  3,  1],   # molto differenziato
    4: [6,   6,  6,  6,  6],   # omogeneo medio
}

N_ARMS           = len(ARMS)
N_EPOCH          = 15
EPSILON_INIZIALE = 0.8
EPSILON_FINALE   = 0.1
W_ENERGY         = 0.6
W_LATENCY        = 0.4
GENERA_GRAFICI_OGNI = 5


# ==========================================
# FUNZIONE REWARD
# ==========================================

def calcola_reward(metriche, storia_metriche):
    """
    Reward normalizzata online su idle_energy_perc e avg_lat_ms.
    Legge i valori dagli alias diretti del dict metriche.
    """
    tutte = storia_metriche + [metriche]

    max_idle_e = max(m["idle_energy_perc"] for m in tutte) or 1.0
    max_lat    = max(m["avg_lat_ms"]       for m in tutte) or 1.0

    idle_norm = metriche["idle_energy_perc"] / max_idle_e
    lat_norm  = metriche["avg_lat_ms"]       / max_lat

    return round(W_ENERGY * (1.0 - idle_norm) + W_LATENCY * (1.0 - lat_norm), 4)


# ==========================================
# EPSILON DECRESCENTE
# ==========================================

def epsilon_at(epoch, n_epoch):
    frac = epoch / max(n_epoch - 1, 1)
    return EPSILON_INIZIALE + frac * (EPSILON_FINALE - EPSILON_INIZIALE)


# ==========================================
# SCELTA ARM
# ==========================================

def scegli_arm(stime_reward, epsilon):
    if random.random() < epsilon:
        return random.randint(0, N_ARMS - 1), "explore"
    return max(stime_reward, key=stime_reward.get), "exploit"


# ==========================================
# AGGIORNAMENTO STIMA
# ==========================================

def aggiorna_stima(stime_reward, conteggi, arm_id, reward):
    conteggi[arm_id]     += 1
    n                     = conteggi[arm_id]
    stime_reward[arm_id] += (reward - stime_reward[arm_id]) / n


# ==========================================
# GRAFICO FINALE DEL MAB
# ==========================================

def genera_grafico_mab(storia, cartella_mab):
    epoch_ids   = [s["epoch"]  for s in storia]
    rewards     = [s["reward"] for s in storia]
    arms_scelti = [s["arm_id"] for s in storia]
    tipi        = [s["tipo"]   for s in storia]

    arm_colors = ['#5DCAA5', '#378ADD', '#EF9F27', '#D85A30', '#AFA9EC']

    fig, axes = plt.subplots(3, 1, figsize=(12, 14))
    fig.suptitle('MAB — Risultati del loop di ottimizzazione TWT',
                 fontsize=13, fontweight='bold')

    # Pannello 1: Reward per epoch
    ax = axes[0]
    colori_barra = ['#378ADD' if t == 'exploit' else '#EF9F27' for t in tipi]
    ax.bar(epoch_ids, rewards, color=colori_barra, edgecolor='white', width=0.7)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Reward')
    ax.set_title('Reward per epoch')
    ax.set_xticks(epoch_ids)
    ax.set_ylim(0, 1.15)
    if rewards:
        ax.axhline(y=max(rewards), color='#5DCAA5', linestyle='--', linewidth=1, alpha=0.7)
        ax.text(epoch_ids[-1], max(rewards) + 0.02,
                f'max={max(rewards):.3f}', ha='right', fontsize=8, color='#5DCAA5')
    for e, r in zip(epoch_ids, rewards):
        ax.text(e, r + 0.02, f'{r:.2f}', ha='center', fontsize=7)
    ax.legend(handles=[
        mpatches.Patch(color='#378ADD', label='Exploit (sfrutta)'),
        mpatches.Patch(color='#EF9F27', label='Explore (esplora)'),
    ], fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    # Pannello 2: Arm scelto per epoch
    ax = axes[1]
    bar_colors_arm = [arm_colors[a % len(arm_colors)] for a in arms_scelti]
    ax.bar(epoch_ids, [1] * len(epoch_ids), color=bar_colors_arm, edgecolor='white', width=0.7)
    ax.set_xlabel('Epoch')
    ax.set_title('Arm scelto per epoch')
    ax.set_xticks(epoch_ids)
    ax.set_yticks([])
    for e, a in zip(epoch_ids, arms_scelti):
        ax.text(e, 0.5, f'A{a}', ha='center', va='center',
                fontsize=9, fontweight='bold', color='white')
    ax.legend(
        handles=[mpatches.Patch(color=arm_colors[k % len(arm_colors)],
                                label=f'Arm {k}: {ARMS[k]}') for k in ARMS],
        fontsize=7, loc='upper right', bbox_to_anchor=(1.0, 1.4), ncol=3
    )

    # Pannello 3: Stima finale reward per arm
    ax = axes[2]
    stima_finale = storia[-1]["stime_reward"]
    arm_ids_list = sorted(stima_finale.keys())
    valori       = [stima_finale[a] for a in arm_ids_list]
    colors_f     = [arm_colors[a % len(arm_colors)] for a in arm_ids_list]
    bars = ax.bar(range(len(arm_ids_list)), valori, color=colors_f, edgecolor='white', width=0.5)
    for bar, val in zip(bars, valori):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.015,
                f'{val:.3f}', ha='center', fontsize=9)
    ax.set_xlabel('Arm')
    ax.set_ylabel('Stima reward')
    ax.set_title("Stima finale della reward per arm (piu' alto = migliore)")
    ax.set_xticks(range(len(arm_ids_list)))
    ax.set_xticklabels([f'Arm {k}\n{ARMS[k]}' for k in arm_ids_list], fontsize=7)
    ax.set_ylim(0, 1.15)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    path_grafico = os.path.join(cartella_mab, "grafico_mab.png")
    plt.savefig(path_grafico, bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f"📊 Grafico MAB salvato: {path_grafico}")


# ==========================================
# LOOP PRINCIPALE MAB
# ==========================================

def main():
    timestamp_mab = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    cartella_mab  = os.path.join("Risultati", f"MAB_{timestamp_mab}")
    os.makedirs(cartella_mab, exist_ok=True)

    stime_reward    = {k: 0.0 for k in ARMS}
    conteggi        = {k: 0   for k in ARMS}
    storia          = []
    storia_metriche = []

    print("\n" + "=" * 60)
    print(f"  MAB AVVIATO — {N_EPOCH} epoch | {N_ARMS} arm")
    print(f"  Reward: energia {W_ENERGY*100:.0f}% | latenza {W_LATENCY*100:.0f}%")
    print(f"  Epsilon: {EPSILON_INIZIALE} -> {EPSILON_FINALE} (lineare)")
    print(f"  Output: {cartella_mab}/")
    print("=" * 60 + "\n")

    for epoch in range(N_EPOCH):
        epsilon      = epsilon_at(epoch, N_EPOCH)
        arm_id, tipo = scegli_arm(stime_reward, epsilon)
        twt_scelto   = ARMS[arm_id]

        print(f"\n{'='*55}")
        print(f"  EPOCH {epoch+1}/{N_EPOCH}  |  epsilon={epsilon:.2f}  |  {tipo.upper()}")
        print(f"  Arm scelto: {arm_id} -> twtDuration={twt_scelto}")
        print(f"{'='*55}")

        params_epoch   = {**PARAMS_FISSI, "twtDuration": twt_scelto}
        genera_grafici = ((epoch + 1) % GENERA_GRAFICI_OGNI == 0) or (epoch == N_EPOCH - 1)
        label          = f"epoch{epoch+1:02d}_arm{arm_id}_{tipo}"

        metriche = run(
            params_epoch,
            genera_grafici=genera_grafici,
            epoch_label=label,
            cartella_padre=cartella_mab,
        )

        if metriche is None:
            print(f"⚠️  Epoch {epoch+1} fallita — salto e continuo")
            continue

        reward = calcola_reward(metriche, storia_metriche)
        storia_metriche.append(metriche)
        aggiorna_stima(stime_reward, conteggi, arm_id, reward)

        record = {
            "epoch":        epoch + 1,
            "arm_id":       arm_id,
            "tipo":         tipo,
            "epsilon":      round(epsilon, 3),
            "twtDuration":  twt_scelto,
            "reward":       reward,
            "stime_reward": dict(stime_reward),
            "conteggi":     dict(conteggi),
            # metriche aggregate compatte per il log (il JSON completo sta nella cartella epoch)
            "metriche_aggregate": metriche["aggregate"],
        }
        storia.append(record)

        print(f"\n  -> Reward:        {reward:.4f}")
        print(f"  -> Idle energia:  {metriche['idle_energy_perc']:.1f}%")
        print(f"  -> Latenza MAC:   {metriche['avg_lat_ms']:.2f} ms")
        print(f"  -> PktLoss:       {metriche['pktloss_perc']:.2f}%")
        print(f"  -> Stime arm:    { {k: round(v, 3) for k, v in stime_reward.items()} }")
        print(f"  -> Conteggi arm:  {conteggi}")

    if not storia:
        print("Nessuna epoch completata correttamente.")
        return None, {}

    arm_migliore = max(stime_reward, key=stime_reward.get)

    print("\n" + "=" * 60)
    print("  LOOP MAB COMPLETATO")
    print(f"  Arm migliore:  {arm_migliore} -> twtDuration={ARMS[arm_migliore]}")
    print(f"  Stima reward:  {stime_reward[arm_migliore]:.4f}")
    print(f"  Volte scelto:  {conteggi[arm_migliore]}/{N_EPOCH}")
    print(f"  Output:        {cartella_mab}/")
    print("=" * 60 + "\n")

    # Log JSON MAB (storia compatta — i dati completi stanno nei metriche.json per-epoch)
    log_path = os.path.join(cartella_mab, "mab_log.json")
    with open(log_path, "w") as f:
        json.dump({
            "timestamp":      timestamp_mab,
            "n_epoch":        N_EPOCH,
            "n_arms":         N_ARMS,
            "arms":           ARMS,
            "w_energy":       W_ENERGY,
            "w_latency":      W_LATENCY,
            "epsilon_init":   EPSILON_INIZIALE,
            "epsilon_final":  EPSILON_FINALE,
            "arm_migliore":   arm_migliore,
            "stime_finali":   stime_reward,
            "conteggi":       conteggi,
            "storia":         storia,
        }, f, indent=2)
    print(f"📄 Log MAB salvato: {log_path}")

    genera_grafico_mab(storia, cartella_mab)

    return arm_migliore, stime_reward


if __name__ == "__main__":
    main()