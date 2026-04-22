# Summary — `run_20260419_171200`

**Config**: seed=42 · STA=10 · MAX_BEACON=120 · azioni=[2.0, 5.0, 10.0]  
**Beacon processati**: 120

## Salute della run
| Metrica | Valore |
|---|---|
| ns-3 TIMEOUT | **0** |
| ns-3 ERRORE  | **0** |
| ns-3 warning di compilazione | 0 |
| sim_time non monotoni (concorrenza) | **0** |

Una run sana ha **0** su tutte e 4 le righe.

## Metriche globali
| Metrica | Valore |
|---|---|
| Latenza media (ms) | 117.60 |
| Loss medio (%) | 53.97 |
| Energia per beacon (mJ) | 9.3706 |
| TX totali | 1546 |
| RX totali | 1529 |

## Distribuzione azioni scelte
| Azione (ms) | Count | % |
|---|---|---|
| 2.0 | 418 | 34.8% |
| 5.0 | 391 | 32.6% |
| 10.0 | 391 | 32.6% |

## Per-STA
| STA | TX | RX | Loss% | Lat(ms) | E(mJ) | BestArm | UCB val | t |
|---|---|---|---|---|---|---|---|---|
| 1 | 41 | 41 | 33.33 | 71.66 | 9.2677 | 2.0 | 0.5137 | 69 |
| 2 | 41 | 41 | 33.33 | 71.66 | 9.2780 | 2.0 | 0.5137 | 69 |
| 3 | 120 | 120 | 48.33 | 87.03 | 9.3904 | 2.0 | 0.3670 | 69 |
| 4 | 120 | 119 | 64.17 | 114.94 | 9.3979 | 5.0 | 0.2371 | 71 |
| 5 | 120 | 118 | 61.67 | 103.90 | 9.3958 | 10.0 | 0.2652 | 69 |
| 6 | 120 | 120 | 48.33 | 87.04 | 9.3907 | 2.0 | 0.3670 | 69 |
| 7 | 246 | 244 | 61.39 | 160.88 | 9.3954 | 5.0 | 0.1951 | 69 |
| 8 | 246 | 240 | 62.50 | 154.94 | 9.3982 | 2.0 | 0.2634 | 69 |
| 9 | 246 | 242 | 64.17 | 162.18 | 9.3962 | 2.0 | 0.2181 | 70 |
| 10 | 246 | 244 | 62.50 | 161.75 | 9.3957 | 2.0 | 0.2021 | 69 |
