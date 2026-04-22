"""
Genera un riepilogo compatto (summary.json + summary.md) da una cartella di log.

Uso:
    python riepilogo.py logs/run_YYYYMMDD_HHMMSS [altre_cartelle ...]

Output:
    <log_dir>/summary.json  — versione machine-readable (per confronti)
    <log_dir>/summary.md    — versione human-readable (per report/tesi)
"""

import re
import json
import sys
from pathlib import Path
from collections import defaultdict
import matplotlib

# ── Parsing mab.log ──────────────────────────────────────────────────
def parse_mab_log(path: Path) -> dict:
    text = path.read_text()

    # Header (seed, STA, beacon)
    m = re.search(
        r'MAB Controller avviato \| seed=(\d+) \| STA=(\d+) \| beacon=(\d+)',
        text,
    )
    cfg = {}
    if m:
        cfg = {
            'seed': int(m.group(1)),
            'n_stations': int(m.group(2)),
            'max_beacon': int(m.group(3)),
        }

    m = re.search(r'Azioni disponibili: \[([\d.,\s]+)\]', text)
    if m:
        cfg['actions_ms'] = [float(x.strip()) for x in m.group(1).split(',')]

    # Beacon (tutti i CHECK + le righe STA)
    beacons = []
    check_re = re.compile(
        r'\[CHECK\] beacon_count=(\d+) \| sim_time ricevuto=([\d.]+)ms'
    )
    sta_re = re.compile(
        r'STA(\d+): lat=([\d.]+)ms \| loss=([\d.]+)% \| '
        r'energy=([\d.]+)mJ \| twt_attivo=([\d.]+)ms \| → scelta=([\d.]+)ms'
    )

    # Splittiamo il testo in blocchi per beacon
    parts = re.split(r'\[MAB\] Aspetto beacon #\d+\.\.\.', text)
    for block in parts[1:]:
        # Stoppa al prossimo MAB.Aspetto (non c'è più, è già splittato) o al COMPLETATO
        block = block.split('MAB COMPLETATO')[0]
        cm = check_re.search(block)
        if not cm:
            continue
        stations = []
        for sm in sta_re.finditer(block):
            stations.append({
                'sta_id':        int(sm.group(1)),
                'lat_ms':        float(sm.group(2)),
                'loss_pct':      float(sm.group(3)),
                'energy_mJ':     float(sm.group(4)),
                'twt_active_ms': float(sm.group(5)),
                'choice_ms':     float(sm.group(6)),
            })
        beacons.append({
            'index':       int(cm.group(1)),
            'sim_time_ms': float(cm.group(2)),
            'stations':    stations,
        })

    # UCB finale: STA N | t=X \n  azione=Yms  count=Z  val=W
    final_ucb = {}
    ucb_re = re.compile(
    r'STA(\d+) \| t=(\d+)[ \t]*\n'
    r'((?:[ \t]+azione=[\d.]+ms[ \t]+count=\d+[ \t]+val=[-\d.]+[ \t]*\n)+)'
    )
    arm_re = re.compile(
        r'azione=([\d.]+)ms\s+count=(\d+)\s+val=([-\d.]+)'
    )
    for m in ucb_re.finditer(text):
        sta = int(m.group(1))
        t = int(m.group(2))
        arms = {}
        for am in arm_re.finditer(m.group(3)):
            arms[am.group(1)] = {
                'count': int(am.group(2)),
                'value': float(am.group(3)),
            }
        final_ucb[sta] = {'t': t, 'arms': arms}

    return {'config': cfg, 'beacons': beacons, 'final_ucb': final_ucb}


# ── Parsing ns3.log ──────────────────────────────────────────────────
def parse_ns3_log(path: Path) -> dict:
    text = path.read_text()

    anomalies = {
        'timeouts':  len(re.findall(r'\[ns-3\]\[TIMEOUT\]', text)),
        'errors':    len(re.findall(r'\[ns-3\]\[ERRORE\]',  text)),
        'warnings':  len(re.findall(r'warning generated',   text)),
    }

    # Ultimo valore cumulativo per STA
    per_sta = {}
    cum_re = re.compile(
        r'\[DEBUG\] STA(\d+) cumulative: tx=(\d+) rx=(\d+) avg_lat=([-\d.]+)'
    )
    for m in cum_re.finditer(text):
        sta = int(m.group(1))
        per_sta[sta] = {
            'tx':         int(m.group(2)),
            'rx':         int(m.group(3)),
            'avg_lat_ms': float(m.group(4)),
        }

    return {'anomalies': anomalies, 'per_sta': per_sta}


# ── Aggregazione ─────────────────────────────────────────────────────
def build_summary(log_dir: Path) -> dict:
    mab = parse_mab_log(log_dir / 'mab.log')
    ns3 = parse_ns3_log(log_dir / 'ns3.log')

    beacons = mab['beacons']
    n_sta = mab['config'].get('n_stations', 10)

    # Monotonia sim_time (indicatore di concorrenza o file residui)
    non_mon = 0
    last = -1.0
    for b in beacons:
        if b['sim_time_ms'] < last:
            non_mon += 1
        last = b['sim_time_ms']

    # Aggregati per STA: media sui beacon dei valori istantanei
    per_sta_mab = defaultdict(lambda: {'lat': [], 'loss': [], 'energy': [], 'choice': []})
    for b in beacons:
        for s in b['stations']:
            p = per_sta_mab[s['sta_id']]
            p['lat'].append(s['lat_ms'])
            p['loss'].append(s['loss_pct'])
            p['energy'].append(s['energy_mJ'])
            p['choice'].append(s['choice_ms'])

    def mean(xs): return sum(xs) / len(xs) if xs else 0.0

    per_sta = []
    for i in range(1, n_sta + 1):
        p = per_sta_mab.get(i, {'lat': [], 'loss': [], 'energy': [], 'choice': []})
        ucb = mab['final_ucb'].get(i, {})
        best_arm = None
        best_val = None
        if ucb.get('arms'):
            ba = max(ucb['arms'].items(), key=lambda kv: kv[1]['value'])
            best_arm = float(ba[0])
            best_val = ba[1]['value']

        per_sta.append({
            'sta_id':                i,
            'tx':                    ns3['per_sta'].get(i, {}).get('tx', 0),
            'rx':                    ns3['per_sta'].get(i, {}).get('rx', 0),
            'lat_ms_cum':            ns3['per_sta'].get(i, {}).get('avg_lat_ms', 0.0),
            'lat_ms_beacon_avg':     mean(p['lat']),
            'loss_pct_beacon_avg':   mean(p['loss']),
            'energy_mJ_beacon_avg':  mean(p['energy']),
            'best_action_ms':        best_arm,
            'best_action_value':     best_val,
            't_valid_updates':       ucb.get('t'),
            'ucb_arms':              ucb.get('arms', {}),
        })

    # Distribuzione globale delle azioni scelte
    action_totals = defaultdict(int)
    for p in per_sta_mab.values():
        for c in p['choice']:
            action_totals[str(c)] += 1

    # Metriche globali (media sulle STA)
    def avg(key): return mean([s[key] for s in per_sta])

    return {
        'run_id':              log_dir.name,
        'config':              mab['config'],
        'beacons_processed':   len(beacons),
        'anomalies': {
            'ns3_timeouts':           ns3['anomalies']['timeouts'],
            'ns3_errors':             ns3['anomalies']['errors'],
            'ns3_warnings':           ns3['anomalies']['warnings'],
            'non_monotonic_sim_time': non_mon,
        },
        'global': {
            'avg_lat_ms':    avg('lat_ms_cum'),
            'avg_loss_pct':  avg('loss_pct_beacon_avg'),
            'real_loss_pct': (1 - sum(s['rx'] for s in per_sta) / 
                          max(sum(s['tx'] for s in per_sta), 1)) * 100,
            'avg_energy_mJ': avg('energy_mJ_beacon_avg'),
            'total_tx':      sum(s['tx'] for s in per_sta),
            'total_rx':      sum(s['rx'] for s in per_sta),
        },
        'action_distribution': dict(action_totals),
        'per_sta':             per_sta,
    }

# ── Plot (opzionale, richiede matplotlib) ────────────────────────────
def generate_plots(s: dict, log_dir: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")          # no GUI, salva solo su file
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("[WARN] matplotlib non installato, plot saltati")
        return

    CREAM   = "#F5F0E8"
    DARK    = "#1C2B1E"
    GREEN   = "#4A7C59"
    ORANGE  = "#C8622A"
    BLUE    = "#2E5B8A"
    GRAY    = "#9A9A8A"

    per_sta   = s["per_sta"]
    sta_ids   = [p["sta_id"] for p in per_sta]
    x         = np.arange(len(sta_ids))
    labels    = [f"STA {i}" for i in sta_ids]

    # ── Plot 1: Loss% e Latenza per STA ──────────────────────────────
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7),
                                   facecolor=CREAM, tight_layout=True)
    fig.suptitle(f"Per-STA · {s['run_id']}", fontsize=13,
                 color=DARK, fontweight="bold", y=1.01)

    losses   = [p["loss_pct_beacon_avg"]  for p in per_sta]
    latencies = [p["lat_ms_cum"]          for p in per_sta]

    bars1 = ax1.bar(x, losses, color=ORANGE, edgecolor=DARK, linewidth=0.6)
    ax1.set_ylabel("Loss medio (%)", color=DARK)
    ax1.set_xticks(x); ax1.set_xticklabels(labels, rotation=30, ha="right")
    ax1.set_facecolor(CREAM)
    ax1.tick_params(colors=DARK)
    ax1.spines[:].set_color(GRAY)
    ax1.axhline(s["global"]["avg_loss_pct"], color=DARK, ls="--",
                lw=1.2, label=f"media {s['global']['avg_loss_pct']:.1f}%")
    ax1.legend(fontsize=9)
    for bar, v in zip(bars1, losses):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
                 f"{v:.1f}", ha="center", va="bottom", fontsize=8, color=DARK)

    bars2 = ax2.bar(x, latencies, color=BLUE, edgecolor=DARK, linewidth=0.6)
    ax2.set_ylabel("Latenza cumulativa (ms)", color=DARK)
    ax2.set_xticks(x); ax2.set_xticklabels(labels, rotation=30, ha="right")
    ax2.set_facecolor(CREAM)
    ax2.tick_params(colors=DARK)
    ax2.spines[:].set_color(GRAY)
    ax2.axhline(s["global"]["avg_lat_ms"], color=DARK, ls="--",
                lw=1.2, label=f"media {s['global']['avg_lat_ms']:.1f} ms")
    ax2.legend(fontsize=9)
    for bar, v in zip(bars2, latencies):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
                 f"{v:.0f}", ha="center", va="bottom", fontsize=8, color=DARK)

    out1 = log_dir / "plot_per_sta.png"
    fig.savefig(out1, dpi=150, bbox_inches="tight", facecolor=CREAM)
    plt.close(fig)
    print(f"  → {out1}")

    # ── Plot 2: UCB arm values per STA ───────────────────────────────
    actions = sorted({a for p in per_sta for a in p["ucb_arms"].keys()},
                     key=float)
    n_arms  = len(actions)
    colors_arms = [GREEN, ORANGE, BLUE, GRAY][:n_arms]
    width   = 0.25

    fig, ax = plt.subplots(figsize=(11, 5), facecolor=CREAM)
    ax.set_facecolor(CREAM)
    ax.set_title(f"UCB arm values per STA · {s['run_id']}",
                 color=DARK, fontweight="bold")

    for i, (arm, col) in enumerate(zip(actions, colors_arms)):
        vals = [p["ucb_arms"].get(arm, {}).get("value", 0) for p in per_sta]
        offset = (i - n_arms / 2 + 0.5) * width
        rects = ax.bar(x + offset, vals, width, label=f"{arm} ms",
                       color=col, edgecolor=DARK, linewidth=0.5)
        for r, v in zip(rects, vals):
            if v > 0:
                ax.text(r.get_x() + r.get_width()/2, r.get_height() + 0.003,
                        f"{v:.3f}", ha="center", va="bottom",
                        fontsize=7, color=DARK)

    # evidenzia best arm con ★
    for j, p in enumerate(per_sta):
        ba = str(p["best_action_ms"])
        if ba in p["ucb_arms"]:
            bv = p["ucb_arms"][ba]["value"]
            ax.text(x[j], bv + 0.015, "★", ha="center",
                    fontsize=10, color=DARK)

    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylabel("Valore UCB stimato", color=DARK)
    ax.tick_params(colors=DARK); ax.spines[:].set_color(GRAY)
    ax.legend(title="twtDuration", fontsize=9)

    out2 = log_dir / "plot_ucb_arms.png"
    fig.savefig(out2, dpi=150, bbox_inches="tight", facecolor=CREAM)
    plt.close(fig)
    print(f"  → {out2}")

    # ── Plot 3: distribuzione azioni (pie) ───────────────────────────
    dist   = s["action_distribution"]
    keys   = sorted(dist.keys(), key=float)
    values = [dist[k] for k in keys]
    pie_colors = [GREEN, ORANGE, BLUE, GRAY][:len(keys)]

    fig, ax = plt.subplots(figsize=(5, 5), facecolor=CREAM)
    ax.set_facecolor(CREAM)
    ax.set_title(f"Distribuzione azioni · {s['run_id']}",
                 color=DARK, fontweight="bold")
    wedges, texts, autotexts = ax.pie(
        values,
        labels=[f"{k} ms" for k in keys],
        autopct="%1.1f%%",
        colors=pie_colors,
        startangle=90,
        wedgeprops={"edgecolor": DARK, "linewidth": 0.8},
    )
    for t in texts + autotexts:
        t.set_color(DARK)
        t.set_fontsize(11)

    out3 = log_dir / "plot_action_dist.png"
    fig.savefig(out3, dpi=150, bbox_inches="tight", facecolor=CREAM)
    plt.close(fig)
    print(f"  → {out3}")

# ── Rendering Markdown ───────────────────────────────────────────────
def render_md(s: dict) -> str:
    L = []
    cfg = s['config']
    a = s['anomalies']
    g = s['global']

    L.append(f"# Summary — `{s['run_id']}`")
    L.append("")
    L.append(f"**Config**: seed={cfg.get('seed')} · STA={cfg.get('n_stations')} · "
             f"MAX_BEACON={cfg.get('max_beacon')} · azioni={cfg.get('actions_ms')}  ")
    L.append(f"**Beacon processati**: {s['beacons_processed']}")
    L.append("")
    L.append("## Salute della run")
    L.append(f"| Metrica | Valore |")
    L.append(f"|---|---|")
    L.append(f"| ns-3 TIMEOUT | **{a['ns3_timeouts']}** |")
    L.append(f"| ns-3 ERRORE  | **{a['ns3_errors']}** |")
    L.append(f"| ns-3 warning di compilazione | {a['ns3_warnings']} |")
    L.append(f"| sim_time non monotoni (concorrenza) | **{a['non_monotonic_sim_time']}** |")
    L.append("")
    L.append("Una run sana ha **0** su tutte e 4 le righe.")
    L.append("")
    L.append("## Metriche globali")
    L.append(f"| Metrica | Valore |")
    L.append(f"|---|---|")
    L.append(f"| Latenza media (ms) | {g['avg_lat_ms']:.2f} |")
    L.append(f"| Loss medio (%) | {g['avg_loss_pct']:.2f} |")
    L.append(f"| Energia per beacon (mJ) | {g['avg_energy_mJ']:.4f} |")
    L.append(f"| TX totali | {g['total_tx']} |")
    L.append(f"| RX totali | {g['total_rx']} |")
    L.append("")
    L.append("## Distribuzione azioni scelte")
    tot = sum(s['action_distribution'].values()) or 1
    L.append("| Azione (ms) | Count | % |")
    L.append("|---|---|---|")
    for act in sorted(s['action_distribution'].keys(), key=float):
        n = s['action_distribution'][act]
        L.append(f"| {act} | {n} | {100*n/tot:.1f}% |")
    L.append("")
    L.append("## Per-STA")
    L.append("| STA | TX | RX | Loss% | Lat(ms) | E(mJ) | BestArm | UCB val | t |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for p in s['per_sta']:
        ba = p['best_action_ms']
        bv = p['best_action_value']
        L.append(
            f"| {p['sta_id']} | {p['tx']} | {p['rx']} | "
            f"{p['loss_pct_beacon_avg']:.2f} | {p['lat_ms_cum']:.2f} | "
            f"{p['energy_mJ_beacon_avg']:.4f} | "
            f"{ba if ba is not None else '—'} | "
            f"{bv:.4f}" if bv is not None else f"| {p['sta_id']} | ... | —"
        ) if bv is not None else L.append(
            f"| {p['sta_id']} | {p['tx']} | {p['rx']} | "
            f"{p['loss_pct_beacon_avg']:.2f} | {p['lat_ms_cum']:.2f} | "
            f"{p['energy_mJ_beacon_avg']:.4f} | — | — | — |"
        )
        if bv is not None:
            # la riga prima è incompleta perché la f-string è stata spezzata — la completiamo
            L[-1] = (
                f"| {p['sta_id']} | {p['tx']} | {p['rx']} | "
                f"{p['loss_pct_beacon_avg']:.2f} | {p['lat_ms_cum']:.2f} | "
                f"{p['energy_mJ_beacon_avg']:.4f} | "
                f"{ba} | {bv:.4f} | {p['t_valid_updates']} |"
            )

    return "\n".join(L) + "\n"


# ── Main ─────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    for arg in sys.argv[1:]:
        log_dir = Path(arg)
        if not (log_dir / 'mab.log').exists() or not (log_dir / 'ns3.log').exists():
            print(f"[SKIP] {log_dir}: manca mab.log o ns3.log")
            continue
        s = build_summary(log_dir)
        (log_dir / 'summary.json').write_text(json.dumps(s, indent=2))
        (log_dir / 'summary.md').write_text(render_md(s))
        # Print veloce sul terminale
        print(f"\n=== {s['run_id']} ===")
        print(f"Beacon: {s['beacons_processed']}/{s['config'].get('max_beacon')}  "
              f"| TIMEOUT: {s['anomalies']['ns3_timeouts']}  "
              f"| ERRORE: {s['anomalies']['ns3_errors']}  "
              f"| sim_time anomali: {s['anomalies']['non_monotonic_sim_time']}")
        print(f"Lat={s['global']['avg_lat_ms']:.2f}ms  "
              f"Loss={s['global']['avg_loss_pct']:.2f}%  "
              f"E={s['global']['avg_energy_mJ']:.4f}mJ/beacon")
        print(f"Summary → {log_dir}/summary.md")

        # ── Plot ──────────────────────────────────────────────────────
        print("Plot:")
        generate_plots(s, log_dir)


if __name__ == "__main__":
    main()
