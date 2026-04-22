# Summary — `run_20260420_191953`

**Config**: seed=42 · STA=5 · MAX_BEACON=361 · azioni=[2.0, 10.0, 50.0]  
**Beacon processati**: 361

## Salute della run
| Metrica | Valore |
|---|---|
| ns-3 TIMEOUT | **0** |
| ns-3 ERRORE  | **0** |
| ns-3 warning di compilazione | 1 |
| sim_time non monotoni (concorrenza) | **0** |

Una run sana ha **0** su tutte e 4 le righe.

## Metriche globali
| Metrica | Valore |
|---|---|
| Latenza media (ms) | 44.97 |
| Loss medio (%) | 16.62 |
| Energia per beacon (mJ) | 6.0876 |
| TX totali | 1331 |
| RX totali | 1329 |

## Distribuzione azioni scelte
| Azione (ms) | Count | % |
|---|---|---|
| 2.0 | 626 | 34.7% |
| 10.0 | 587 | 32.5% |
| 50.0 | 592 | 32.8% |

## Per-STA
| STA | TX | RX | Loss% | Lat(ms) | E(mJ) | BestArm | UCB val | t |
|---|---|---|---|---|---|---|---|---|
| 1 | 124 | 123 | 33.24 | 71.47 | 5.7731 | 2.0 | 0.0434 | 118 |
| 2 | 124 | 123 | 33.24 | 71.47 | 5.7744 | 2.0 | 0.0434 | 118 |
| 3 | 361 | 361 | 8.31 | 25.58 | 6.7701 | 50.0 | 0.8203 | 220 |
| 4 | 361 | 361 | 3.88 | 20.97 | 6.0650 | 2.0 | 0.8640 | 217 |
| 5 | 361 | 361 | 4.43 | 35.36 | 6.0555 | 10.0 | 0.9173 | 220 |
