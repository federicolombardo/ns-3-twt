# Summary — `run_20260420_170157`

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
| Latenza media (ms) | 101.16 |
| Loss medio (%) | 49.05 |
| Energia per beacon (mJ) | 9.4056 |
| TX totali | 4638 |
| RX totali | 4628 |

## Distribuzione azioni scelte
| Azione (ms) | Count | % |
|---|---|---|
| 2.0 | 1173 | 32.6% |
| 5.0 | 1177 | 32.7% |
| 10.0 | 1250 | 34.7% |

## Per-STA
| STA | TX | RX | Loss% | Lat(ms) | E(mJ) | BestArm | UCB val | t |
|---|---|---|---|---|---|---|---|---|
| 1 | 123 | 123 | 33.06 | 63.88 | 9.3091 | 2.0 | 0.4986 | 215 |
| 2 | 123 | 123 | 33.06 | 63.88 | 9.3084 | 2.0 | 0.4987 | 215 |
| 3 | 360 | 360 | 47.22 | 77.90 | 9.4062 | 10.0 | 0.5338 | 237 |
| 4 | 360 | 360 | 52.22 | 83.09 | 9.4201 | 10.0 | 0.5156 | 241 |
| 5 | 360 | 360 | 51.67 | 85.54 | 9.4197 | 2.0 | 0.5200 | 243 |
| 6 | 360 | 360 | 45.28 | 73.35 | 9.4029 | 5.0 | 0.5528 | 239 |
| 7 | 738 | 734 | 56.85 | 140.61 | 9.4451 | 10.0 | 0.3872 | 215 |
| 8 | 738 | 736 | 57.78 | 143.75 | 9.4479 | 2.0 | 0.3330 | 219 |
| 9 | 738 | 736 | 56.39 | 138.23 | 9.4474 | 10.0 | 0.3225 | 217 |
| 10 | 738 | 736 | 56.94 | 141.34 | 9.4493 | 2.0 | 0.3543 | 221 |
