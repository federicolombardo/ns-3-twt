# Summary — `run_20260420_180525`

**Config**: seed=42 · STA=5 · MAX_BEACON=360 · azioni=[2.0, 10.0, 50.0]  
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
| Latenza media (ms) | 110.13 |
| Loss medio (%) | 23.78 |
| Energia per beacon (mJ) | 6.6292 |
| TX totali | 3690 |
| RX totali | 3668 |

## Distribuzione azioni scelte
| Azione (ms) | Count | % |
|---|---|---|
| 2.0 | 548 | 30.4% |
| 10.0 | 622 | 34.6% |
| 50.0 | 630 | 35.0% |

## Per-STA
| STA | TX | RX | Loss% | Lat(ms) | E(mJ) | BestArm | UCB val | t |
|---|---|---|---|---|---|---|---|---|
| 1 | 738 | 734 | 22.96 | 76.96 | 6.5549 | 50.0 | 0.5697 | 215 |
| 2 | 738 | 736 | 21.76 | 73.72 | 6.6043 | 50.0 | 0.4847 | 217 |
| 3 | 738 | 732 | 22.31 | 75.10 | 6.8040 | 50.0 | 0.4806 | 216 |
| 4 | 738 | 732 | 23.15 | 85.51 | 6.5845 | 10.0 | 0.4727 | 215 |
| 5 | 738 | 734 | 28.70 | 239.37 | 6.5982 | 10.0 | 0.4909 | 223 |
