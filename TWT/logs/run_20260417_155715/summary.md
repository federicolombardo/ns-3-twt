# Summary — `run_20260417_155715`

**Config**: seed=42 · STA=10 · MAX_BEACON=100 · azioni=[2.0, 5.0, 10.0]  
**Beacon processati**: 100

## Salute della run
| Metrica | Valore |
|---|---|
| ns-3 TIMEOUT | **34** |
| ns-3 ERRORE  | **1** |
| ns-3 warning di compilazione | 1 |
| sim_time non monotoni (concorrenza) | **3** |

Una run sana ha **0** su tutte e 4 le righe.

## Metriche globali
| Metrica | Valore |
|---|---|
| Latenza media (ms) | 48.07 |
| Loss medio (%) | 33.30 |
| Energia per beacon (mJ) | 9.2248 |
| TX totali | 860 |
| RX totali | 860 |

## Distribuzione azioni scelte
| Azione (ms) | Count | % |
|---|---|---|
| 2.0 | 332 | 33.2% |
| 5.0 | 332 | 33.2% |
| 10.0 | 336 | 33.6% |

## Per-STA
| STA | TX | RX | Loss% | Lat(ms) | E(mJ) | BestArm | UCB val | t |
|---|---|---|---|---|---|---|---|---|
| 1 | 120 | 120 | 46.00 | 55.37 | 9.2687 | 2.0 | 0.4080 | 32 |
| 2 | 60 | 60 | 17.00 | 26.51 | 9.1899 | 2.0 | 0.4471 | 31 |
| 3 | 120 | 120 | 48.00 | 54.66 | 9.2728 | 2.0 | 0.4080 | 32 |
| 4 | 40 | 40 | 27.00 | 72.72 | 9.1718 | 2.0 | 0.4324 | 32 |
| 5 | 120 | 120 | 45.00 | 49.41 | 9.2703 | 2.0 | 0.4080 | 32 |
| 6 | 60 | 60 | 17.00 | 26.55 | 9.1895 | 2.0 | 0.4471 | 31 |
| 7 | 120 | 120 | 54.00 | 64.24 | 9.2472 | 2.0 | 0.4080 | 32 |
| 8 | 40 | 40 | 28.00 | 75.23 | 9.1736 | 2.0 | 0.4324 | 32 |
| 9 | 120 | 120 | 33.00 | 27.08 | 9.2594 | 2.0 | 0.4080 | 32 |
| 10 | 60 | 60 | 18.00 | 28.89 | 9.2051 | 2.0 | 0.4471 | 31 |
