

"""
grafici_comparativi.py
======================
Genera 4 figure comparative per la presentazione della tesi TWT-MAB.

USO:
    Modifica la sezione CONFIG qui sotto con i path corretti, poi:
    python grafici_comparativi.py

OUTPUT (nella cartella OUTPUT_DIR):
    fig1_energy_comparison.png      — Energia media per run (barre + saving%)
    fig2_scatter_pareto.png         — Scatter latenza vs energia (Pareto front)
    fig3_sweep_energy_duration.png  — Energia vs twtDuration × periodicità (sweep)
    fig4_safe_duration_table.png    — Tabella regione ammissibile per STA (motiva MAB)
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG — modifica questi path
# ══════════════════════════════════════════════════════════════════════════════

CSV_RUN1 = "Risultati/Run_2026-04-07_16-17-29_STA-5_TWT-20ms/risultato_raw.csv"           # No TWT
CSV_RUN2 = "Risultati/Run_2026-04-07_16-16-06_STA-5_TWT-20ms/risultato_raw.csv"  # TWT omogeneo 20ms
CSV_RUN3 = "Risultati/Run_2026-04-07_16-25-06_STA-5_TWT-20-10-5-3-2ms/risultato_raw.csv"   # TWT eterogeneo 20-10-5-3-2ms
CSV_SWEEP = "sweep_results/sweep_completo.csv"

OUTPUT_DIR = "Risultati/grafici_comparativi"

STA_LABELS      = ["STA 1", "STA 2", "STA 3", "STA 4", "STA 5"]
STA_PERIODICITY = [0.1, 0.5, 1.0, 2.0, 5.0]   # secondi
RUN3_DURATIONS  = [20, 10, 5, 3, 2]            # ms, ordine STA

RUN_LABELS = ["Run 1 — No TWT", "Run 2 — TWT 20ms omog.", "Run 3 — TWT eterogeneo"]
RUN_COLORS = ["#D85A30", "#378ADD", "#5DCAA5"]

LATENCY_THRESHOLD_MS = 50.0

# ── Nomi colonne run CSV ──────────────────────────────────────────────────────
COL_ENERGY  = "energymodel_total_energy_J"
COL_LAT     = "avg_lat_ms"
COL_LAT_EFF = "effective_latency"   # usata se presente
COL_PKTLOSS = "pktloss_perc"

# ── Nomi colonne sweep CSV ────────────────────────────────────────────────────
SW_DUR = "duration_ms"
SW_PER = "periodicity_s"
SW_EN  = "energy_J"
SW_LAT = "latenza_ms"

# ══════════════════════════════════════════════════════════════════════════════
# STILE
# ══════════════════════════════════════════════════════════════════════════════
plt.rcParams.update({
    "font.family": "sans-serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# CARICAMENTO DATI
# ══════════════════════════════════════════════════════════════════════════════
def load_run(path, label):
    df = pd.read_csv(path)
    df["_run"] = label
    return df

def lat_col(df):
    return COL_LAT_EFF if COL_LAT_EFF in df.columns else COL_LAT

df1 = load_run(CSV_RUN1, RUN_LABELS[0])
df2 = load_run(CSV_RUN2, RUN_LABELS[1])
df3 = load_run(CSV_RUN3, RUN_LABELS[2])
df_sweep = pd.read_csv(CSV_SWEEP)

n_sta = len(df1)
x_sta = np.arange(n_sta)

print(f"✔  Run1: {len(df1)} STA | Run2: {len(df2)} STA | Run3: {len(df3)} STA")
print(f"✔  Sweep: {len(df_sweep)} righe")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 1 — Energia media per run + per-STA affiancate
# ══════════════════════════════════════════════════════════════════════════════
def fig1_energy_comparison():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Confronto Energia — 3 Run Baseline", fontsize=14, fontweight="bold")

    # Sinistra: 1 barra per run
    ax = axes[0]
    means = [df[COL_ENERGY].mean() for df in [df1, df2, df3]]
    ref   = means[0]
    bars  = ax.bar(range(3), means, color=RUN_COLORS, edgecolor="white", width=0.5)

    for bar, val in zip(bars, means):
        saving = (1 - val / ref) * 100
        txt = f"{val*1000:.0f} mJ"
        if saving > 0:
            txt += f"\n(−{saving:.0f}% vs No TWT)"
        ax.text(bar.get_x() + bar.get_width() / 2,
                val + ref * 0.01, txt,
                ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xticks(range(3))
    ax.set_xticklabels(RUN_LABELS, rotation=10, ha="right")
    ax.set_ylabel("Energia media per STA (J)")
    ax.set_title("Risparmio energetico per configurazione")
    ax.set_ylim(0, ref * 1.3)

    # Destra: barre per-STA affiancate
    ax = axes[1]
    bar_w = 0.25
    for k, (df, color, label) in enumerate(zip([df1, df2, df3], RUN_COLORS, RUN_LABELS)):
        vals = df[COL_ENERGY].tolist()
        ax.bar(x_sta + (k - 1) * bar_w, vals, bar_w,
               label=label, color=color, edgecolor="white", alpha=0.9)

    ax.set_xticks(x_sta)
    ax.set_xticklabels(STA_LABELS)
    ax.set_ylabel("Energia (J)")
    ax.set_title("Energia per STA — confronto run")
    ax.legend(fontsize=9)

    mid_y = df2[COL_ENERGY].mean()
    ax.annotate(
        "Energia identica per tutte le STA\n→ dipende da twtDuration, non dal traffico",
        xy=(2, mid_y),
        xytext=(2.5, mid_y * 2.5),
        arrowprops=dict(arrowstyle="->", color="#378ADD", lw=1.5),
        fontsize=8, color="#378ADD", fontstyle="italic",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  edgecolor="#378ADD", alpha=0.8)
    )

    fig.tight_layout()
    out = f"{OUTPUT_DIR}/fig1_energy_comparison.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✅  Salvato: {out}")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 2 — Scatter Pareto: latenza vs energia per STA × run
# ══════════════════════════════════════════════════════════════════════════════
def fig2_scatter_pareto():
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.suptitle("Trade-off Latenza vs Energia — Pareto Front (per STA × Run)",
                 fontsize=13, fontweight="bold")

    markers = ["o", "s", "^"]

    all_lats = []
    all_ens  = []

    for k, (df, color, label, marker) in enumerate(
            zip([df1, df2, df3], RUN_COLORS, RUN_LABELS, markers)):

        lc        = lat_col(df)
        energies  = df[COL_ENERGY].tolist()
        latencies = df[lc].tolist()
        all_lats += latencies
        all_ens  += energies

        ax.scatter(latencies, energies,
                   c=color, s=140, marker=marker, zorder=5,
                   edgecolors="white", linewidths=0.8, label=label)

        for i, (lat, en) in enumerate(zip(latencies, energies)):
            ax.annotate(STA_LABELS[i], (lat, en),
                        textcoords="offset points", xytext=(7, 4),
                        fontsize=8, color=color)

    ymin = min(all_ens) * 0.8
    ymax = max(all_ens) * 1.2
    ax.set_ylim(ymin, ymax)

    ax.axvline(x=LATENCY_THRESHOLD_MS, color="#D85A30",
               linestyle="--", linewidth=1.5, alpha=0.7)
    ax.text(LATENCY_THRESHOLD_MS + 0.5, ymax * 0.97,
            f"Soglia {LATENCY_THRESHOLD_MS:.0f} ms",
            color="#D85A30", fontsize=8, va="top")

    ax.set_xlabel("Latenza (ms)", fontsize=11)
    ax.set_ylabel("Energia totale (J)", fontsize=11)
    ax.legend(fontsize=10, loc="upper left")

    fig.tight_layout()
    out = f"{OUTPUT_DIR}/fig2_scatter_pareto.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✅  Salvato: {out}")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 3 — Sweep: energia vs twtDuration × periodicità
# ══════════════════════════════════════════════════════════════════════════════
def fig3_sweep_energy():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        "Sweep: Energia vs twtDuration × Periodicità\n"
        "Scoperta chiave: l'energia dipende SOLO da twtDuration, non dalla periodicità",
        fontsize=13, fontweight="bold"
    )

    periodicities = sorted(df_sweep[SW_PER].unique())
    durations     = sorted(df_sweep[SW_DUR].unique())
    cmap_colors   = plt.cm.viridis(np.linspace(0.15, 0.85, len(periodicities)))

    # Sinistra: linee sovrapposte
    ax = axes[0]
    for per, color in zip(periodicities, cmap_colors):
        subset = df_sweep[df_sweep[SW_PER] == per].sort_values(SW_DUR)
        ax.plot(subset[SW_DUR], subset[SW_EN] * 1000,
                marker="o", color=color, linewidth=2, markersize=6,
                label=f"T={per}s")

    ax.set_xlabel("twtDuration (ms)", fontsize=11)
    ax.set_ylabel("Energia per STA (mJ)", fontsize=11)
    ax.set_title("Energia vs twtDuration (per periodicità)")
    ax.legend(title="Periodicità", fontsize=9)
    ax.set_xticks(durations)
    ax.text(0.5, 0.93,
            "Le curve si sovrappongono → la periodicità\nnon influenza l'energia!",
            transform=ax.transAxes, fontsize=9, ha="center", color="#D85A30",
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="#D85A30", alpha=0.85))

    # Destra: heatmap
    ax = axes[1]
    pivot = df_sweep.pivot_table(
        index=SW_PER, columns=SW_DUR, values=SW_EN, aggfunc="mean"
    ) * 1000

    im = ax.imshow(pivot.values, aspect="auto", cmap="YlOrRd_r",
                   interpolation="nearest")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([f"{d}ms" for d in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([f"{p}s" for p in pivot.index])
    ax.set_xlabel("twtDuration (ms)")
    ax.set_ylabel("Periodicità pacchetti (s)")
    ax.set_title("Heatmap energia (mJ)\nRighe quasi uguali → indipendenza dalla periodicità")

    mean_val = pivot.values.mean()
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.values[i, j]
            ax.text(j, i, f"{val:.0f}", ha="center", va="center",
                    fontsize=9, color="white" if val < mean_val else "black")

    plt.colorbar(im, ax=ax, label="Energia (mJ)")
    fig.tight_layout()
    out = f"{OUTPUT_DIR}/fig3_sweep_energy_duration.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✅  Salvato: {out}")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 4 — Heatmap latenza + tabella regione ammissibile
# ══════════════════════════════════════════════════════════════════════════════
def fig4_safe_duration_table():
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle(
        f"Regione Ammissibile per STA — soglia latenza ≤ {LATENCY_THRESHOLD_MS:.0f} ms\n"
        "Perché il MAB è necessario: la duration ottimale dipende dal profilo di traffico",
        fontsize=12, fontweight="bold"
    )

    pivot_lat = df_sweep.pivot_table(
        index=SW_PER, columns=SW_DUR, values=SW_LAT, aggfunc="mean"
    )
    pivot_en = df_sweep.pivot_table(
        index=SW_PER, columns=SW_DUR, values=SW_EN, aggfunc="mean"
    ) * 1000

    cols_sorted = sorted(pivot_lat.columns.tolist())
    rows_sorted = sorted(pivot_lat.index.tolist())
    pivot_lat   = pivot_lat.reindex(index=rows_sorted, columns=cols_sorted)
    pivot_en    = pivot_en.reindex(index=rows_sorted, columns=cols_sorted)
    lat_vals    = pivot_lat.values
    en_vals     = pivot_en.values

    # Sinistra: heatmap latenza
    ax = axes[0]
    im = ax.imshow(lat_vals, aspect="auto", cmap=plt.cm.RdYlGn_r,
                   vmin=0, vmax=LATENCY_THRESHOLD_MS * 2, interpolation="nearest")

    ax.set_xticks(range(len(cols_sorted)))
    ax.set_xticklabels([f"{d}ms" for d in cols_sorted])
    ax.set_yticks(range(len(rows_sorted)))
    ax.set_yticklabels([f"T={p}s" for p in rows_sorted])
    ax.set_xlabel("twtDuration (ms)", fontsize=11)
    ax.set_ylabel("Periodicità pacchetti (s)", fontsize=11)
    ax.set_title(f"Latenza media (ms)\nverde = OK (< {LATENCY_THRESHOLD_MS:.0f} ms)  |  rosso = violazione")

    for i in range(lat_vals.shape[0]):
        for j in range(lat_vals.shape[1]):
            val = lat_vals[i, j]
            ok  = val <= LATENCY_THRESHOLD_MS
            ax.text(j, i, f"{val:.1f}\n{'✓' if ok else '✗'}",
                    ha="center", va="center", fontsize=9,
                    color="black" if ok else "white",
                    fontweight="normal" if ok else "bold")

    plt.colorbar(im, ax=ax, label="Latenza (ms)")

    # Destra: tabella per STA
    ax = axes[1]
    ax.axis("off")

    header = ["STA", "Periodicità", "Duration\nmin sicura", "Energia\nmin (mJ)", "Complessità MAB"]
    table_data = []

    for sta, per in zip(STA_LABELS, STA_PERIODICITY):
        safe = []
        if per in rows_sorted:
            ri = rows_sorted.index(per)
            for ci, dur in enumerate(cols_sorted):
                if lat_vals[ri, ci] <= LATENCY_THRESHOLD_MS:
                    safe.append((dur, en_vals[ri, ci]))

        if safe:
            opt_dur, opt_en = min(safe, key=lambda x: x[0])
            complexity = "Bassa" if opt_dur <= 5 else "Alta"
            en_str  = f"{opt_en:.0f}"
            dur_str = f"{opt_dur}ms"
        else:
            complexity = "Critica"
            en_str  = "n/d"
            dur_str = "n/d"

        table_data.append([sta, f"{per}s", dur_str, en_str, complexity])

    tbl = ax.table(
        cellText=table_data,
        colLabels=header,
        cellLoc="center",
        loc="center",
        bbox=[0, 0.1, 1, 0.85]
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)

    for j in range(len(header)):
        tbl[0, j].set_facecolor("#2C3E50")
        tbl[0, j].set_text_props(color="white", fontweight="bold")

    for i, row in enumerate(table_data):
        bg = "#F7F9FC" if i % 2 == 0 else "#EAF0FB"
        for j in range(len(header)):
            tbl[i+1, j].set_facecolor(bg)
        if row[4] == "Alta":
            tbl[i+1, 4].set_facecolor("#FFF3CD")
            tbl[i+1, 4].set_text_props(color="#856404")
        elif row[4] == "Critica":
            tbl[i+1, 4].set_facecolor("#FDECEA")
            tbl[i+1, 4].set_text_props(color="#C0392B", fontweight="bold")

    ax.set_title(
        "Duration ottimale per STA\n"
        "Il MAB deve scoprire questa colonna online, senza conoscere la periodicità",
        fontsize=10, pad=16
    )

    fig.tight_layout()
    out = f"{OUTPUT_DIR}/fig4_safe_duration_table.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✅  Salvato: {out}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  Generazione grafici comparativi TWT-MAB")
    print("=" * 60)

    print("\n[1/4] Fig1 — Confronto energia per run...")
    fig1_energy_comparison()

    print("\n[2/4] Fig2 — Scatter Pareto latenza vs energia...")
    fig2_scatter_pareto()

    print("\n[3/4] Fig3 — Sweep energia vs twtDuration...")
    fig3_sweep_energy()

    print("\n[4/4] Fig4 — Tabella regione ammissibile...")
    fig4_safe_duration_table()

    print(f"\n🎉 Tutti i grafici salvati in: {OUTPUT_DIR}/")