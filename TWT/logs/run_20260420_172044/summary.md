# Summary — `run_20260420_172044`

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
| Latenza media (ms) | 123.08 |
| Loss medio (%) | 57.41 |
| Energia per beacon (mJ) | 9.4260 |
| TX totali | 4638 |
| RX totali | 4615 |

## Distribuzione azioni scelte
| Azione (ms) | Count | % |
|---|---|---|
| 2.0 | 1200 | 33.3% |
| 5.0 | 1198 | 33.3% |
| 10.0 | 1202 | 33.4% |

## Per-STA
| STA | TX | RX | Loss% | Lat(ms) | E(mJ) | BestArm | UCB val | t |
|---|---|---|---|---|---|---|---|---|
| 1 | 123 | 123 | 33.06 | 70.35 | 9.3750 | 5.0 | 0.0164 | 118 |
| 2 | 123 | 123 | 33.06 | 70.34 | 9.3816 | 5.0 | 0.0164 | 118 |
| 3 | 360 | 358 | 60.56 | 105.58 | 9.4269 | 10.0 | 0.1238 | 214 |
| 4 | 360 | 360 | 64.72 | 115.14 | 9.4412 | 10.0 | 0.0820 | 213 |
| 5 | 360 | 359 | 64.17 | 112.85 | 9.4386 | 5.0 | 0.0805 | 213 |
| 6 | 360 | 360 | 58.89 | 101.20 | 9.4412 | 10.0 | 0.1179 | 216 |
| 7 | 738 | 730 | 63.52 | 156.44 | 9.4385 | 2.0 | 0.0734 | 214 |
| 8 | 738 | 734 | 65.83 | 170.16 | 9.4392 | 2.0 | 0.0696 | 215 |
| 9 | 738 | 736 | 64.72 | 162.52 | 9.4398 | 2.0 | 0.0660 | 213 |
| 10 | 738 | 732 | 65.56 | 166.24 | 9.4380 | 5.0 | 0.0747 | 213 |
