# Summary — `run_20260420_172854`

**Config**: seed=42 · STA=10 · MAX_BEACON=360 · azioni=[2.0, 5.0, 10.0]  
**Beacon processati**: 360

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
| Latenza media (ms) | 2407.29 |
| Loss medio (%) | 65.55 |
| Energia per beacon (mJ) | 6.4064 |
| TX totali | 4638 |
| RX totali | 3791 |

## Distribuzione azioni scelte
| Azione (ms) | Count | % |
|---|---|---|
| 2.0 | 1215 | 33.8% |
| 5.0 | 1257 | 34.9% |
| 10.0 | 1128 | 31.3% |

## Per-STA
| STA | TX | RX | Loss% | Lat(ms) | E(mJ) | BestArm | UCB val | t |
|---|---|---|---|---|---|---|---|---|
| 1 | 123 | 122 | 32.78 | 1103.06 | 6.2676 | 10.0 | 0.0142 | 118 |
| 2 | 123 | 122 | 33.06 | 1103.89 | 6.2692 | 10.0 | 0.0142 | 118 |
| 3 | 360 | 358 | 66.67 | 1256.43 | 6.7282 | 5.0 | 0.1558 | 229 |
| 4 | 360 | 355 | 67.50 | 1365.98 | 6.5310 | 2.0 | 0.1491 | 227 |
| 5 | 360 | 355 | 73.61 | 1912.73 | 6.6107 | 5.0 | 0.1460 | 233 |
| 6 | 360 | 360 | 64.44 | 2067.79 | 6.5219 | 2.0 | 0.1888 | 234 |
| 7 | 738 | 724 | 76.11 | 3166.19 | 6.4485 | 10.0 | 0.0802 | 219 |
| 8 | 738 | 715 | 75.00 | 4918.29 | 6.5367 | 2.0 | 0.0972 | 223 |
| 9 | 738 | 680 | 66.30 | 7178.58 | 6.5282 | 5.0 | 0.2184 | 252 |
| 10 | 738 | 0 | 100.00 | 0.00 | 5.6225 | 2.0 | 0.0000 | 213 |
