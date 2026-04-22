# Summary — `run_20260422_093228`

**Config**: seed=42 · STA=5 · MAX_BEACON=361 · azioni=[2.0, 5.0, 10.0]  
**Beacon processati**: 361

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
| Latenza media (ms) | 59.85 |
| Loss medio (%) | 4.71 |
| Energia per beacon (mJ) | 5.7211 |
| TX totali | 440 |
| RX totali | 440 |

## Distribuzione azioni scelte
| Azione (ms) | Count | % |
|---|---|---|
| 2.0 | 650 | 36.0% |
| 5.0 | 551 | 30.5% |
| 10.0 | 604 | 33.5% |

## Per-STA
| STA | TX | RX | Loss% | Lat(ms) | E(mJ) | BestArm | UCB val | t |
|---|---|---|---|---|---|---|---|---|
| 1 | 19 | 19 | 5.26 | 55.59 | 5.7589 | 2.0 | 0.0000 | 18 |
| 2 | 10 | 10 | 2.77 | 74.54 | 5.7561 | 2.0 | 0.0000 | 9 |
| 3 | 361 | 361 | 1.94 | 5.53 | 5.5607 | 10.0 | 0.9523 | 214 |
| 4 | 37 | 37 | 9.97 | 53.68 | 5.7673 | 2.0 | 0.0734 | 36 |
| 5 | 13 | 13 | 3.60 | 109.91 | 5.7625 | 2.0 | 0.0000 | 12 |
