"""
Confronta affiancando 2+ run, leggendo i summary.json generati da riepilogo.py.

Uso:
    python confronta.py logs/run_A logs/run_B [logs/run_C ...]
    python confronta.py --last N            # confronta le ultime N run

Stampa una tabella con tutte le metriche affiancate, e evidenzia con ▲/▼/=
il miglioramento/peggioramento rispetto alla PRIMA run passata (baseline).
"""

import json
import sys
from pathlib import Path


LOGS_DIR = Path(__file__).parent / "logs"


def carica(log_dir: Path) -> dict | None:
    p = log_dir / "summary.json"
    if not p.exists():
        print(f"[ERRORE] {p} non esiste. Lancia `python riepilogo.py {log_dir}` prima.")
        return None
    return json.loads(p.read_text())


def risolvi_args(argv: list[str]) -> list[Path]:
    if "--last" in argv:
        i = argv.index("--last")
        n = int(argv[i + 1])
        runs = sorted([d for d in LOGS_DIR.iterdir() if d.is_dir() and d.name.startswith("run_")])
        return runs[-n:]
    return [Path(a) for a in argv]


def diff_symbol(new_v: float, base_v: float, lower_is_better: bool = True) -> str:
    """Ritorna un simbolo ▲ (migliorato) / ▼ (peggiorato) / = (uguale)."""
    if new_v is None or base_v is None:
        return " "
    if abs(new_v - base_v) < 1e-6:
        return "="
    improved = (new_v < base_v) if lower_is_better else (new_v > base_v)
    return "▲" if improved else "▼"


def fmt_num(v, width, prec=2):
    if v is None:
        return " " * width
    if isinstance(v, int):
        return f"{v:>{width}d}"
    return f"{v:>{width}.{prec}f}"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    dirs = risolvi_args(sys.argv[1:])
    if len(dirs) < 2:
        print("[ERRORE] Servono almeno 2 run da confrontare.")
        sys.exit(1)

    summaries = []
    for d in dirs:
        s = carica(d)
        if s:
            summaries.append(s)
    if len(summaries) < 2:
        sys.exit(1)

    # Tronchiamo i run_id a una lunghezza stampabile
    ids = [s["run_id"].replace("run_", "") for s in summaries]
    col_w = max(16, max(len(i) for i in ids) + 2)

    base = summaries[0]

    def header(title):
        print()
        print(f"── {title} " + "─" * max(0, 78 - len(title) - 4))

    def riga(nome, fn, lower_is_better=True, prec=2):
        vals = [fn(s) for s in summaries]
        pieces = [f"{nome:<32}"]
        for i, v in enumerate(vals):
            sym = " " if i == 0 else diff_symbol(v, vals[0], lower_is_better)
            if v is None:
                pieces.append(f"{'—':>{col_w-2}} {sym}")
            elif isinstance(v, int):
                pieces.append(f"{v:>{col_w-2}d} {sym}")
            else:
                pieces.append(f"{v:>{col_w-2}.{prec}f} {sym}")
        print("".join(pieces))

    # ── Intestazione ──
    print("\n" + "=" * 80)
    print("CONFRONTO RUN")
    print("=" * 80)
    print(f"{'Run':<32}" + "".join(f"{i:>{col_w}}" for i in ids))
    print("-" * (32 + col_w * len(ids)))

    # ── Config ──
    header("Config")
    riga("seed", lambda s: s["config"].get("seed"), lower_is_better=False)
    riga("n_stations", lambda s: s["config"].get("n_stations"), lower_is_better=False)
    riga("max_beacon", lambda s: s["config"].get("max_beacon"), lower_is_better=False)

    # ── Salute ──
    header("Salute (lower is better)")
    riga("Beacon processati",         lambda s: s["beacons_processed"], lower_is_better=False)
    riga("ns-3 TIMEOUT",              lambda s: s["anomalies"]["ns3_timeouts"])
    riga("ns-3 ERRORE",               lambda s: s["anomalies"]["ns3_errors"])
    riga("sim_time non monotoni",     lambda s: s["anomalies"]["non_monotonic_sim_time"])

    # ── Metriche globali ──
    header("Metriche globali (media su STA)")
    riga("Latenza media (ms)",        lambda s: s["global"]["avg_lat_ms"])
    riga("Loss medio (%)",            lambda s: s["global"]["avg_loss_pct"])
    riga("Energia/beacon (mJ)",       lambda s: s["global"]["avg_energy_mJ"], prec=4)
    riga("TX totali",                 lambda s: s["global"]["total_tx"], lower_is_better=False)
    riga("RX totali",                 lambda s: s["global"]["total_rx"], lower_is_better=False)

    # ── Distribuzione azioni ──
    header("Distribuzione azioni scelte (%)")
    all_actions = sorted(
        {a for s in summaries for a in s["action_distribution"]},
        key=float,
    )
    for act in all_actions:
        def frac(s, act=act):
            d = s["action_distribution"]
            tot = sum(d.values()) or 1
            return 100.0 * d.get(act, 0) / tot
        riga(f"Azione {act}ms", frac, lower_is_better=False)

    # ── Best action per STA ──
    header("Best action per STA (dal UCB finale)")
    n = max(len(s["per_sta"]) for s in summaries)
    for i in range(n):
        riga(f"STA{i+1} best arm",
             lambda s, i=i: s["per_sta"][i]["best_action_ms"] if i < len(s["per_sta"]) else None,
             lower_is_better=False)

    # ── Per-STA latenza ──
    header("Latenza cumulativa per STA (ms)")
    for i in range(n):
        riga(f"STA{i+1}",
             lambda s, i=i: s["per_sta"][i]["lat_ms_cum"] if i < len(s["per_sta"]) else None)

    print()
    print("Legenda: ▲ = migliorato rispetto alla baseline (prima colonna)")
    print("         ▼ = peggiorato · = = invariato")


if __name__ == "__main__":
    main()
