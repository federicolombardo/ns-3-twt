# Summary — `run_20260419_170902`

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
| Latenza media (ms) | 123.65 |
| Loss medio (%) | 56.97 |
| Energia per beacon (mJ) | 9.3780 |
| TX totali | 1546 |
| RX totali | 1515 |

## Distribuzione azioni scelte
| Azione (ms) | Count | % |
|---|---|---|
| 2.0 | 401 | 33.4% |
| 5.0 | 405 | 33.8% |
| 10.0 | 394 | 32.8% |

## Per-STA
| STA | TX | RX | Loss% | Lat(ms) | E(mJ) | BestArm | UCB val | t |
|---|---|---|---|---|---|---|---|---|
| 1 | 41 | 41 | 33.33 | 76.96 | 9.3316 | 2.0 | 0.4831 | 69 |
| 2 | 41 | 41 | 33.33 | 76.97 | 9.3310 | 2.0 | 0.4832 | 69 |
| 3 | 120 | 117 | 55.83 | 99.30 | 9.3838 | 5.0 | 0.3219 | 69 |
| 4 | 120 | 119 | 66.67 | 123.41 | 9.3897 | 10.0 | 0.2829 | 69 |
| 5 | 120 | 118 | 62.50 | 103.65 | 9.3938 | 5.0 | 0.2886 | 69 |
| 6 | 120 | 117 | 55.83 | 99.32 | 9.3839 | 5.0 | 0.3219 | 69 |
| 7 | 246 | 240 | 65.56 | 164.66 | 9.3912 | 5.0 | 0.2804 | 69 |
| 8 | 246 | 240 | 63.33 | 155.58 | 9.3959 | 5.0 | 0.2841 | 69 |
| 9 | 246 | 240 | 67.50 | 174.56 | 9.3912 | 5.0 | 0.2752 | 69 |
| 10 | 246 | 242 | 65.83 | 162.07 | 9.3882 | 2.0 | 0.2866 | 69 |
