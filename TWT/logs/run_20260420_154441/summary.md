# Summary — `run_20260420_154441`

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
| Latenza media (ms) | 127.87 |
| Loss medio (%) | 57.44 |
| Energia per beacon (mJ) | 9.4248 |
| TX totali | 4638 |
| RX totali | 4601 |

## Distribuzione azioni scelte
| Azione (ms) | Count | % |
|---|---|---|
| 2.0 | 1214 | 33.7% |
| 5.0 | 1193 | 33.1% |
| 10.0 | 1193 | 33.1% |

## Per-STA
| STA | TX | RX | Loss% | Lat(ms) | E(mJ) | BestArm | UCB val | t |
|---|---|---|---|---|---|---|---|---|
| 1 | 123 | 123 | 33.06 | 75.19 | 9.3815 | 5.0 | 0.4656 | 215 |
| 2 | 123 | 123 | 33.06 | 75.20 | 9.3809 | 5.0 | 0.4657 | 215 |
| 3 | 360 | 360 | 59.17 | 108.34 | 9.4269 | 10.0 | 0.3601 | 221 |
| 4 | 360 | 360 | 63.89 | 118.55 | 9.4331 | 2.0 | 0.3202 | 219 |
| 5 | 360 | 357 | 63.33 | 116.97 | 9.4322 | 10.0 | 0.3565 | 219 |
| 6 | 360 | 360 | 58.61 | 103.99 | 9.4301 | 2.0 | 0.3363 | 219 |
| 7 | 738 | 734 | 63.98 | 162.82 | 9.4429 | 10.0 | 0.2781 | 213 |
| 8 | 738 | 732 | 66.39 | 174.69 | 9.4431 | 5.0 | 0.2831 | 213 |
| 9 | 738 | 722 | 66.20 | 168.05 | 9.4385 | 10.0 | 0.2799 | 213 |
| 10 | 738 | 730 | 66.67 | 174.86 | 9.4387 | 2.0 | 0.2850 | 213 |
