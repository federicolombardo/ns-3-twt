# Summary — `run_20260420_170638`

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
| Latenza media (ms) | 105.05 |
| Loss medio (%) | 53.37 |
| Energia per beacon (mJ) | 9.4232 |
| TX totali | 4638 |
| RX totali | 4616 |

## Distribuzione azioni scelte
| Azione (ms) | Count | % |
|---|---|---|
| 2.0 | 1222 | 33.9% |
| 5.0 | 1189 | 33.0% |
| 10.0 | 1189 | 33.0% |

## Per-STA
| STA | TX | RX | Loss% | Lat(ms) | E(mJ) | BestArm | UCB val | t |
|---|---|---|---|---|---|---|---|---|
| 1 | 123 | 123 | 33.33 | 59.20 | 9.3295 | 2.0 | 0.5638 | 215 |
| 2 | 123 | 123 | 33.33 | 59.20 | 9.3293 | 2.0 | 0.5638 | 215 |
| 3 | 360 | 358 | 54.44 | 83.20 | 9.4443 | 10.0 | 0.4014 | 215 |
| 4 | 360 | 360 | 58.61 | 92.23 | 9.4488 | 2.0 | 0.4101 | 226 |
| 5 | 360 | 358 | 59.44 | 94.50 | 9.4479 | 2.0 | 0.3805 | 219 |
| 6 | 360 | 360 | 53.33 | 83.38 | 9.4455 | 5.0 | 0.4615 | 217 |
| 7 | 738 | 736 | 60.28 | 143.18 | 9.4485 | 5.0 | 0.3498 | 213 |
| 8 | 738 | 734 | 59.72 | 146.13 | 9.4487 | 2.0 | 0.3916 | 217 |
| 9 | 738 | 730 | 60.83 | 143.99 | 9.4462 | 2.0 | 0.3507 | 215 |
| 10 | 738 | 734 | 60.37 | 145.45 | 9.4437 | 2.0 | 0.3308 | 215 |
