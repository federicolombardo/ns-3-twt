import numpy as np

AZIONI = [2.0, 5.0, 10.0]  # ms, spazio delle azioni

# parametri fissi da mettere in cima al file insieme agli altri
ENERGY_MIN_J = 0.005   # ~5mJ, minimo osservato nei log
ENERGY_MAX_J = 0.013   # ~13mJ, massimo osservato nei log
LAT_MAX_MS   = 200   # latenza di riferimento per normalizzazione
W_ENERGY     = 0.6    # peso energia
W_LAT        = 0.4    # peso latenza
W_LOSS       = 0.4    # peso loss

MIN_HOLD = 3  # campioni minimi per braccio prima di cambiare azione (per stabilizzare reward)

class UCBAgent:
    """Un agente UCB1 per una singola STA."""

    def __init__(self, sta_id: int, seed: int = 42):
        self.sta_id   = sta_id
        self.n_arms   = len(AZIONI)
        self.counts   = np.zeros(self.n_arms)   # quante volte ho scelto ogni braccio
        self.valori   = np.zeros(self.n_arms)   # reward media per braccio
        self.t        = 0                        # numero totale di round validi
        self.rng      = np.random.default_rng(seed + sta_id)
        self.current_arm_idx  = None
        self.current_arm_hold = 0  # quante volte ho aggiornato il braccio corrente

        # normalizzazione dinamica energia
        self.energy_max = None

    # ------------------------------------------------------------------
    """"
    def scegli(self) -> float:
        Restituisce la durata TWT scelta (in ms).
        # Fase di inizializzazione: esplora ogni braccio almeno una volta
        bracci_non_esplorati = np.where(self.counts == 0)[0]
        if len(bracci_non_esplorati) > 0:
            idx = bracci_non_esplorati[0]
        else:
            # UCB1
            ucb = self.valori + np.sqrt(2 * np.log(self.t) / self.counts)
            idx = int(np.argmax(ucb))

        return AZIONI[idx]"""
    def scegli(self) -> float:
        bracci_non_esplorati = np.where(self.counts == 0)[0]
        if len(bracci_non_esplorati) > 0:
            # esplorazione iniziale: esplora ogni braccio almeno una volta
            idx = int(bracci_non_esplorati[0])
        elif self.current_arm_hold is not None and self.current_arm_hold < MIN_HOLD:
            # rimani sul braccio corrente finché non hai abbastanza campioni
            idx = self.current_arm_idx
        else:
            # UCB1
            ucb = self.valori + np.sqrt(2 * np.log(self.t) / self.counts)
            idx = int(np.argmax(ucb))

        if idx != self.current_arm_idx:
            self.current_arm_idx  = idx
            self.current_arm_hold = 0
        return AZIONI[idx]

    # ------------------------------------------------------------------
    def aggiorna(self, azione_ms: float, stato: dict):
        """
        Aggiorna il braccio corrispondente ad azione_ms con la reward
        calcolata dallo stato del beacon corrente.

        stato: dict con chiavi avg_lat_ms, pktloss_perc, beacon_energy_J,
               twt_duration_ms (durata attiva sull'aria)
        """
        # Beacon di transizione: la durata attiva non corrisponde all'azione
        # scelta — reward non affidabile, saltiamo l'aggiornamento
        if abs(stato["twt_duration_ms"] - azione_ms) > 0.01:
            return

        # Beacon vuoto: nessun pacchetto trasmesso in questo intervallo.
        # lat=0 e loss=0 sono artefatti, non metriche reali — nessuna informazione utile.
        if stato.get("tx_count", 0) == 0:
            return

        # Trova l'indice del braccio
        distanze = [abs(a - azione_ms) for a in AZIONI]
        idx = int(np.argmin(distanze))

        # Calcola reward
        reward = self._calcola_reward(stato)

        # Aggiornamento media incrementale
        self.current_arm_hold += 1
        self.counts[idx] += 1
        self.t            += 1
        self.valori[idx]  += (reward - self.valori[idx]) / self.counts[idx]

    # ------------------------------------------------------------------
    """def _calcola_reward(self, stato: dict) -> float:
        Reward in [0, 1] — più alta è meglio.

        # --- energia ---
        energy_j = stato["beacon_energy_J"]
        if self.energy_max is None or energy_j > self.energy_max:
            self.energy_max = energy_j
        if self.energy_max > 0:
            r_energy = 1.0 - energy_j / self.energy_max
        else:
            r_energy = 0.0

        # --- latenza ---
        lat = stato["avg_lat_ms"]
        r_lat = 1.0 - min(lat / LAT_MAX_MS, 1.0)

        # --- loss ---
        loss = stato["pktloss_perc"] / 100.0   # da % a [0,1]
        r_loss = 1.0 - loss

        return W_ENERGY * r_energy + W_LAT * r_lat + W_LOSS * r_loss
        
    def _calcola_reward(self, stato: dict) -> float:
        # --- energia ---
        energy_j = stato["beacon_energy_J"]
        r_energy = 1.0 - (energy_j - ENERGY_MIN_J) / (ENERGY_MAX_J - ENERGY_MIN_J)
        r_energy = float(np.clip(r_energy, 0.0, 1.0))

        # --- latenza ---
        lat = stato["avg_lat_ms"]
        r_lat = 1.0 - min(lat / LAT_MAX_MS, 1.0)  # normalizzazione con saturazione a 1.0

        # --- loss ---
        loss = stato["pktloss_perc"] / 100.0
        r_loss = 1.0 - loss

        return W_ENERGY * r_energy + W_LAT * r_lat + W_LOSS * r_loss

    # ------------------------------------------------------------------"""
    def _calcola_reward(self, stato: dict) -> float:
        loss = stato["pktloss_perc"] / 100.0
        delivery_rate = 1.0 - loss  # 0.0 = tutto perso, 1.0 = tutto consegnato

        # energia
        energy_j = stato["beacon_energy_J"]
        r_energy = 1.0 - (energy_j - ENERGY_MIN_J) / (ENERGY_MAX_J - ENERGY_MIN_J)
        r_energy = float(np.clip(r_energy, 0.0, 1.0))

        # latenza (lat=0 quando delta_rx=0 è già escluso dal controllo tx_count in aggiorna)
        lat = stato["avg_lat_ms"]
        r_lat = 1.0 - min(lat / LAT_MAX_MS, 1.0)

        # delivery_rate come moltiplicatore globale:
        # energia e latenza contano solo nella misura in cui i pacchetti arrivano.
        # loss=100% → reward=0 sempre; loss=0% → reward piena.
       
        return delivery_rate * (W_ENERGY * r_energy + W_LAT * r_lat)
        #return 1.0 - min(lat / LAT_MAX_MS, 1.0)
    
    def stato_str(self) -> str:
        """Stringa di debug leggibile."""
        righe = [f"STA{self.sta_id} | t={self.t}"]
        for i, a in enumerate(AZIONI):
            righe.append(
                f"  azione={a}ms  count={int(self.counts[i])}  "
                f"val={self.valori[i]:.4f}"
            )
        return "\n".join(righe)