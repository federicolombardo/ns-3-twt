# Summary — `run_20260420_181843`

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
| Latenza media (ms) | 100.69 |
| Loss medio (%) | 26.44 |
| Energia per beacon (mJ) | 6.6000 |
| TX totali | 3690 |
| RX totali | 3654 |

## Distribuzione azioni scelte
| Azione (ms) | Count | % |
|---|---|---|
| 2.0 | 577 | 32.1% |
| 10.0 | 623 | 34.6% |
| 50.0 | 600 | 33.3% |

## Per-STA
| STA | TX | RX | Loss% | Lat(ms) | E(mJ) | BestArm | UCB val | t |
|---|---|---|---|---|---|---|---|---|
| 1 | 738 | 718 | 31.39 | 106.24 | 6.5947 | 2.0 | 0.7768 | 226 |
| 2 | 738 | 734 | 26.30 | 94.30 | 6.6027 | 2.0 | 0.7539 | 220 |
| 3 | 738 | 736 | 23.89 | 88.34 | 6.5890 | 10.0 | 0.7654 | 217 |
| 4 | 738 | 732 | 25.83 | 101.25 | 6.6301 | 10.0 | 0.7659 | 219 |
| 5 | 738 | 734 | 24.81 | 113.32 | 6.5837 | 50.0 | 0.7780 | 217 |
