"""
mab_gym.py — Agente epsilon-greedy su ambiente Gymnasium TwtEnv
================================================================
Produce due grafici:

  grafico_live.png    — aggiornato dopo OGNI step (aprilo con Preview su Mac)
  grafico_mab_gym.png — copia finale identica all'ultimo live
"""

import os
import json
import shutil
import datetime
import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec

from twt_env import TwtEnv, ARMS, N_ARMS


# ==========================================
# CONFIGURAZIONE AGENTE
# ==========================================

N_STEPS          = 15
EPSILON_INIZIALE = 0.8
EPSILON_FINALE   = 0.1

ARM_COLORS = ['#5DCAA5', '#378ADD', '#EF9F27', '#D85A30', '#AFA9EC']
ARM_LABELS = {k: f"A{k}: {ARMS[k]}" for k in ARMS}


# ==========================================
# EPSILON
# ==========================================

def epsilon_at(step, n_steps):
    frac = step / max(n_steps - 1, 1)
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
# GRAFICO LIVE — aggiornato ad ogni step
# ==========================================

def aggiorna_grafico_live(storia, stime_reward, conteggi, cartella, n_steps):
    """
    4 pannelli aggiornati dopo ogni step:
      1. Reward per step
      2. Stima corrente per arm
      3. Idle energia per step
      4. Latenza per step — scala dinamica per mostrare outlier
    """
    if not storia:
        return

    step_ids    = [s["step"]   for s in storia]
    rewards     = [s["reward"] for s in storia]
    arms_scelti = [s["arm_id"] for s in storia]
    tipi        = [s["tipo"]   for s in storia]

    idle_es = [s["metriche_aggregate"]["idle_energy_perc"]
               if "metriche_aggregate" in s else 0 for s in storia]
    latenze = [s["metriche_aggregate"]["avg_lat_ms"]
               if "metriche_aggregate" in s else 0 for s in storia]

    fig = plt.figure(figsize=(16, 12))
    fig.suptitle(
        f'MAB Gym — Step {len(storia)}/{n_steps} | '
        f'Arm corrente: {storia[-1]["arm_id"]} ({storia[-1]["tipo"].upper()})',
        fontsize=13, fontweight='bold'
    )
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

    colori_step    = ['#378ADD' if t == 'exploit' else '#EF9F27' for t in tipi]
    colori_arm_step = [ARM_COLORS[a % len(ARM_COLORS)] for a in arms_scelti]

    # ── Pannello 1: Reward per step ────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.bar(step_ids, rewards, color=colori_step, edgecolor='white', width=0.7)
    ax1.set_xlim(0.5, n_steps + 0.5)
    ax1.set_ylim(0, 1.15)
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Reward')
    ax1.set_title('Reward per step')
    ax1.set_xticks(range(1, n_steps + 1))
    if rewards:
        ax1.axhline(y=max(rewards), color='#5DCAA5', linestyle='--',
                    linewidth=1, alpha=0.7)
    for s, r in zip(step_ids, rewards):
        ax1.text(s, r + 0.02, f'{r:.2f}', ha='center', fontsize=7)
    ax1.legend(handles=[
        mpatches.Patch(color='#378ADD', label='Exploit'),
        mpatches.Patch(color='#EF9F27', label='Explore'),
    ], fontsize=8)
    ax1.grid(axis='y', alpha=0.3)

    # ── Pannello 2: Stima corrente per arm ─────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    arm_ids = sorted(stime_reward.keys())
    valori  = [stime_reward[a] for a in arm_ids]
    bars = ax2.bar(range(len(arm_ids)), valori,
                   color=[ARM_COLORS[a % len(ARM_COLORS)] for a in arm_ids],
                   edgecolor='white', width=0.6)
    for i, (bar, val) in enumerate(zip(bars, valori)):
        ax2.text(bar.get_x() + bar.get_width() / 2, val + 0.015,
                 f'{val:.3f}', ha='center', fontsize=9)
        if val == max(valori):
            bar.set_edgecolor('#333333')
            bar.set_linewidth(2)
    ax2.set_xticks(range(len(arm_ids)))
    ax2.set_xticklabels([f'A{k}\n{ARMS[k]}' for k in arm_ids], fontsize=7)
    ax2.set_ylabel('Stima reward')
    ax2.set_title('Stima corrente per arm')
    ax2.set_ylim(0, 1.15)
    for i, k in enumerate(arm_ids):
        ax2.text(i, -0.12, f'n={conteggi[k]}', ha='center',
                 fontsize=8, color='gray',
                 transform=ax2.get_xaxis_transform())
    ax2.grid(axis='y', alpha=0.3)

    # ── Pannello 3: Idle energia per step ─────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.bar(step_ids, idle_es, color=colori_arm_step, edgecolor='white', width=0.7)
    ax3.axhline(y=70, color='#D85A30', linestyle='--',
                linewidth=1, alpha=0.6, label='ref max (70%)')
    ax3.set_xlim(0.5, n_steps + 0.5)
    ax3.set_ylim(0, 80)
    ax3.set_xlabel('Step')
    ax3.set_ylabel('Idle energia (%)')
    ax3.set_title('Idle energia per step (meno = meglio)')
    ax3.set_xticks(range(1, n_steps + 1))
    for s, v in zip(step_ids, idle_es):
        ax3.text(s, v + 0.5, f'{v:.0f}', ha='center', fontsize=7)
    ax3.legend(fontsize=8)
    ax3.grid(axis='y', alpha=0.3)

    # ── Pannello 4: Latenza per step — scala DINAMICA ──────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.bar(step_ids, latenze, color=colori_arm_step, edgecolor='white', width=0.7)

    # Scala dinamica: se ci sono outlier sopra 25ms li mostra tutti
    lat_max = max(latenze) if latenze else 25
    asse_max = max(lat_max * 1.2, 5)          # almeno 5ms di spazio
    ref_max  = 25.0                            # riferimento fisso

    ax4.axhline(y=ref_max, color='#D85A30', linestyle='--',
                linewidth=1, alpha=0.6, label=f'ref ({ref_max:.0f}ms)')
    ax4.set_xlim(0.5, n_steps + 0.5)
    ax4.set_ylim(0, asse_max)
    ax4.set_xlabel('Step')
    ax4.set_ylabel('Latenza MAC (ms)')
    ax4.set_title('Latenza per step (meno = meglio)')
    ax4.set_xticks(range(1, n_steps + 1))
    for s, v in zip(step_ids, latenze):
        # Etichetta in rosso se supera il riferimento
        colore_label = '#D85A30' if v > ref_max else 'black'
        ax4.text(s, v + asse_max * 0.01, f'{v:.1f}',
                 ha='center', fontsize=7, color=colore_label,
                 fontweight='bold' if v > ref_max else 'normal')
    ax4.legend(fontsize=8)
    ax4.grid(axis='y', alpha=0.3)

    # Legenda arm colori comune in fondo
    patches = [mpatches.Patch(color=ARM_COLORS[k % len(ARM_COLORS)],
                               label=ARM_LABELS[k]) for k in ARMS]
    fig.legend(handles=patches, fontsize=7, loc='lower center',
               ncol=N_ARMS, bbox_to_anchor=(0.5, -0.02))

    plt.savefig(os.path.join(cartella, "grafico_live.png"),
                bbox_inches='tight', dpi=130)
    plt.close(fig)


# ==========================================
# LOOP PRINCIPALE
# ==========================================

def main():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    cartella  = os.path.join("Risultati", f"MAB_GYM_{timestamp}")
    os.makedirs(cartella, exist_ok=True)

    stime_reward = {k: 0.0 for k in ARMS}
    conteggi     = {k: 0   for k in ARMS}
    storia       = []

    print("\n" + "=" * 60)
    print(f"  MAB GYM AVVIATO — {N_STEPS} step | {N_ARMS} arm")
    print(f"  Epsilon: {EPSILON_INIZIALE} -> {EPSILON_FINALE}")
    print(f"  Output: {cartella}/")
    print(f"  Grafico live: {cartella}/grafico_live.png")
    print("=" * 60)

    env = TwtEnv(cartella_padre=cartella, max_steps=N_STEPS)

    print("\n[AGENTE] Reset ambiente...")
    obs, info = env.reset()
    print(f"[AGENTE] Osservazione iniziale: {[round(x, 3) for x in obs.tolist()]}")

    for step in range(N_STEPS):
        epsilon      = epsilon_at(step, N_STEPS)
        arm_id, tipo = scegli_arm(stime_reward, epsilon)

        print(f"\n{'='*55}")
        print(f"  STEP {step+1}/{N_STEPS} | epsilon={epsilon:.2f} | {tipo.upper()}")
        print(f"  Arm scelto: {arm_id} -> twtDuration={ARMS[arm_id]}")
        print(f"{'='*55}")

        obs, reward, terminated, truncated, info = env.step(arm_id)

        aggiorna_stima(stime_reward, conteggi, arm_id, reward)

        record = {
            "step":         step + 1,
            "arm_id":       arm_id,
            "tipo":         tipo,
            "epsilon":      round(epsilon, 3),
            "twtDuration":  ARMS[arm_id],
            "obs":          obs.tolist(),
            "reward":       reward,
            "stime_reward": dict(stime_reward),
            "conteggi":     dict(conteggi),
        }
        if "metriche" in info:
            record["metriche_aggregate"] = info["metriche"]["aggregate"]
        storia.append(record)

        print(f"\n  -> obs:      {[round(x, 3) for x in obs.tolist()]}")
        print(f"  -> reward:   {reward:.4f}")
        print(f"  -> stime:   { {k: round(v,3) for k,v in stime_reward.items()} }")

        # Aggiorna grafico live dopo ogni step
        aggiorna_grafico_live(storia, stime_reward, conteggi, cartella, N_STEPS)
        print(f"  📊 grafico_live.png aggiornato")

        if terminated or truncated:
            break

    env.close()

    arm_migliore = max(stime_reward, key=stime_reward.get)

    print("\n" + "=" * 60)
    print("  EPISODIO COMPLETATO")
    print(f"  Arm migliore: {arm_migliore} -> {ARMS[arm_migliore]}")
    print(f"  Stima reward: {stime_reward[arm_migliore]:.4f}")
    print("=" * 60 + "\n")

    # Salvataggio log JSON
    log_path = os.path.join(cartella, "mab_gym_log.json")
    with open(log_path, "w") as f:
        json.dump({
            "timestamp":     timestamp,
            "n_steps":       N_STEPS,
            "n_arms":        N_ARMS,
            "arms":          ARMS,
            "epsilon_init":  EPSILON_INIZIALE,
            "epsilon_final": EPSILON_FINALE,
            "arm_migliore":  arm_migliore,
            "stime_finali":  stime_reward,
            "conteggi":      conteggi,
            "storia":        storia,
        }, f, indent=2)
    print(f"📄 Log salvato: {log_path}")

    # Copia del grafico live come grafico finale con nome originale
    src = os.path.join(cartella, "grafico_live.png")
    dst = os.path.join(cartella, "grafico_mab_gym.png")
    shutil.copy(src, dst)
    print(f"📊 Grafico finale salvato: {dst}")

    return arm_migliore, stime_reward


if __name__ == "__main__":
    main()