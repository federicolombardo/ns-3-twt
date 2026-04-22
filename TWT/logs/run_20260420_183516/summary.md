# Summary — `run_20260420_183516`

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
| Latenza media (ms) | 111.77 |
| Loss medio (%) | 11.35 |
| Energia per beacon (mJ) | 5.8632 |
| TX totali | 3690 |
| RX totali | 3674 |

## Distribuzione azioni scelte
| Azione (ms) | Count | % |
|---|---|---|
| 2.0 | 653 | 36.3% |
| 10.0 | 548 | 30.4% |
| 50.0 | 599 | 33.3% |

## Per-STA
| STA | TX | RX | Loss% | Lat(ms) | E(mJ) | BestArm | UCB val | t |
|---|---|---|---|---|---|---|---|---|
| 1 | 738 | 736 | 10.56 | 106.73 | 5.8208 | 2.0 | 0.7986 | 217 |
| 2 | 738 | 734 | 8.89 | 101.43 | 5.8454 | 2.0 | 0.7784 | 217 |
| 3 | 738 | 734 | 10.00 | 103.00 | 6.0893 | 2.0 | 0.7919 | 215 |
| 4 | 738 | 736 | 17.59 | 124.43 | 5.7135 | 50.0 | 0.7689 | 215 |
| 5 | 738 | 734 | 9.72 | 123.24 | 5.8468 | 50.0 | 0.7773 | 215 |
