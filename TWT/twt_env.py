"""
twt_env.py — Ambiente Gymnasium per ottimizzazione TWT
=======================================================
Segue l'interfaccia standard gymnasium.Env:

    env = TwtEnv()
    obs, info = env.reset()
    obs, reward, terminated, truncated, info = env.step(action)

Struttura:
  - action:      intero in [0, N_ARMS-1], corrisponde a un arm (twtDuration)
  - observation: vettore numpy con le metriche dello step precedente
  - reward:      float calcolato da energia idle e latenza

L'ambiente chiama run_esperimento.run() ad ogni step,
che lancia ns-3 e restituisce le metriche reali.
"""

import numpy as np
import gymnasium as gym
from gymnasium import spaces

from run_esperimento import run


# ==========================================
# CONFIGURAZIONE AMBIENTE
# ==========================================

# Parametri fissi — non toccati dall'agente
PARAMS_FISSI = {
    "nStations":         5,
    "t0":                0.1,
    "t1":                0.1,
    "packetPeriodicity": [0.5, 1.0, 2.0, 2.0, 5.0],
    "mcs":               4,
    "frequency":         5,
    "simulationTime":    10240,
    "enableTWT":         "true",
    "twtTriggerBased":   "true",
    "STAtype":           3,
}

# Arm: ogni arm è una configurazione di twtDuration per le 5 STA
ARMS = {
    0: [10, 10, 10, 10, 10],
    1: [8,   6,  4,  4,  2],
    2: [5,   5,  5,  5,  5],
    3: [12,  8,  5,  3,  1],
    4: [6,   6,  6,  6,  6],
}

N_ARMS = len(ARMS)

# Range di riferimento per normalizzazione della reward
# Stimati dai run precedenti — aggiornare se i range cambiano
MAX_IDLE_E_REF = 70.0   # % — peggiore caso osservato (arm 0)
MAX_LAT_REF    = 25.0   # ms — peggiore caso osservato (arm 1)


# ==========================================
# AMBIENTE
# ==========================================

class TwtEnv(gym.Env):
    """
    Ambiente Gymnasium per ottimizzazione dinamica della twtDuration.

    Action space:  Discrete(N_ARMS) — scelta dell'arm
    Observation space: Box con 3 valori normalizzati in [0, 1]:
        [idle_energy_norm, latency_norm, pktloss_norm]

    Ogni step corrisponde a una epoch di simulazione ns-3.
    """

    metadata = {"render_modes": []}

    def __init__(self, cartella_padre=None, max_steps=15):
        super().__init__()

        # Spazio delle azioni: uno dei N_ARMS arm disponibili
        self.action_space = spaces.Discrete(N_ARMS)

        # Spazio delle osservazioni: 3 metriche normalizzate
        # [idle_energy_norm, latency_norm, pktloss_norm]
        self.observation_space = spaces.Box(
            low=np.zeros(3, dtype=np.float32),
            high=np.ones(3, dtype=np.float32),
            dtype=np.float32,
        )

        self.cartella_padre = cartella_padre
        self.max_steps      = max_steps
        self.step_count     = 0
        self.last_metriche  = None

    # ── Helpers ───────────────────────────────────────────────────────────

    def _metriche_to_obs(self, metriche):
        """Converte il dict metriche in un vettore numpy normalizzato."""
        idle_norm = min(metriche["idle_energy_perc"] / MAX_IDLE_E_REF, 1.0)
        lat_norm  = min(metriche["avg_lat_ms"]       / MAX_LAT_REF,    1.0)
        loss_norm = min(metriche["pktloss_perc"]     / 100.0,          1.0)
        return np.array([idle_norm, lat_norm, loss_norm], dtype=np.float32)

    def _calcola_reward(self, metriche):
        """
        Reward con range fissi — confrontabile tra tutti gli step.
        Alta reward = bassa energia idle + bassa latenza.
        """
        idle_norm = min(metriche["idle_energy_perc"] / MAX_IDLE_E_REF, 1.0)
        lat_norm  = min(metriche["avg_lat_ms"]       / MAX_LAT_REF,    1.0)
        return round(0.6 * (1.0 - idle_norm) + 0.4 * (1.0 - lat_norm), 4)

    # ── Interfaccia Gymnasium ─────────────────────────────────────────────

    def reset(self, seed=None, options=None):
        """
        Resetta l'ambiente. Esegue uno step con arm 0 come stato iniziale.
        Obbligatorio prima di chiamare step().
        """
        super().reset(seed=seed)
        self.step_count = 0

        # Stato iniziale: eseguiamo arm 0 per avere un'osservazione reale
        params = {**PARAMS_FISSI, "twtDuration": ARMS[0]}
        metriche = run(
            params,
            genera_grafici=False,
            epoch_label="reset",
            cartella_padre=self.cartella_padre,
        )

        if metriche is None:
            # Fallback: osservazione neutra se ns-3 fallisce
            metriche = {
                "idle_energy_perc": MAX_IDLE_E_REF / 2,
                "avg_lat_ms":       MAX_LAT_REF / 2,
                "pktloss_perc":     0.0,
            }

        self.last_metriche = metriche
        obs  = self._metriche_to_obs(metriche)
        info = {"arm": 0, "twtDuration": ARMS[0], "metriche": metriche}
        return obs, info

    def step(self, action):
        """
        Esegue un passo dell'ambiente con l'azione scelta dall'agente.

        Parametri
        ---------
        action : int
            Indice dell'arm scelto (0..N_ARMS-1).

        Ritorna
        -------
        obs         : np.ndarray shape (3,) — stato normalizzato
        reward      : float
        terminated  : bool — sempre False (episodio infinito)
        truncated   : bool — True quando si raggiunge max_steps
        info        : dict — metriche complete per logging
        """
        self.step_count += 1
        arm_id     = int(action)
        twt_scelto = ARMS[arm_id]

        print(f"\n[ENV] Step {self.step_count}/{self.max_steps} | "
              f"Arm {arm_id} -> twtDuration={twt_scelto}")

        params   = {**PARAMS_FISSI, "twtDuration": twt_scelto}
        label    = f"step{self.step_count:02d}_arm{arm_id}"
        metriche = run(
            params,
            genera_grafici=False,
            epoch_label=label,
            cartella_padre=self.cartella_padre,
        )

        if metriche is None:
            # ns-3 ha fallito: reward negativa, osservazione dal passo precedente
            print(f"[ENV] ⚠️ Simulazione fallita allo step {self.step_count}")
            obs      = self._metriche_to_obs(self.last_metriche)
            reward   = -1.0
            info     = {"arm": arm_id, "errore": True}
        else:
            self.last_metriche = metriche
            obs    = self._metriche_to_obs(metriche)
            reward = self._calcola_reward(metriche)
            info   = {
                "arm":        arm_id,
                "twtDuration": twt_scelto,
                "metriche":   metriche,
                "reward":     reward,
            }
            print(f"[ENV] Reward: {reward:.4f} | "
                  f"Idle: {metriche['idle_energy_perc']:.1f}% | "
                  f"Lat: {metriche['avg_lat_ms']:.2f}ms")

        terminated = False
        truncated  = self.step_count >= self.max_steps

        return obs, reward, terminated, truncated, info

    def render(self):
        """Non implementato — i dati sono nei log e nei JSON per-step."""
        pass

    def close(self):
        pass