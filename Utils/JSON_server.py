from __future__ import annotations
import json
import logging
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import psutil
import requests

logger = logging.getLogger(__name__)

IP_INTERSTATE = "192.168.1.15"
INTERSTATE_URL = f"http://{IP_INTERSTATE}"
REQUEST_TIMEOUT = 3.0  # s

# Chemin absolu, indépendant du répertoire de lancement
DEFAULT_JSON_PATH = Path(__file__).resolve().parent / "LEDMatrix.json"

# Verrou partagé par toutes les instances (le fichier JSON est unique)
_json_lock = threading.Lock()

class JSON_server:
    def __init__(self, json_path: Path | str = DEFAULT_JSON_PATH,
                 update_interval: float = 1.0) -> None:
        self.json_path = Path(json_path)
        self.update_interval = update_interval

        self._stop_event = threading.Event()
        self._monitor_thread: Optional[threading.Thread] = None
        self._session = requests.Session()
        self._interstate_available = True  # évite de répéter le même avertissement

        self.process = psutil.Process(os.getpid())

    # ------------------------------------------------------------------ #
    # Propriétés
    # ------------------------------------------------------------------ #
    @property
    def monitoring(self) -> bool:
        return self._monitor_thread is not None and self._monitor_thread.is_alive()

    # ------------------------------------------------------------------ #
    # Accès au fichier JSON
    # ------------------------------------------------------------------ #
    def _read_json(self) -> dict[str, Any]:
        try:
            with self.json_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Fichier %s introuvable, il sera créé", self.json_path)
        except json.JSONDecodeError as e:
            logger.error("Fichier %s corrompu (%s), il sera réinitialisé", self.json_path, e)
        return {}

    def _write_json(self, data: dict[str, Any]) -> None:
        tmp_path = self.json_path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, self.json_path)

    def _update_and_send(self, updates: dict[str, Any]) -> None:
        with _json_lock:
            data = self._read_json()
            data.update(updates)
            self._write_json(data)
        self._send(data)

    # ------------------------------------------------------------------ #
    # Communication réseau
    # ------------------------------------------------------------------ #
    def _send(self, data: dict[str, Any]) -> None:
        try:
            response = self._session.post(INTERSTATE_URL, json=data, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as e:
            if self._interstate_available:
                logger.warning("Interstate non joignable (%s) : %s", INTERSTATE_URL, e)
                self._interstate_available = False
            return

        if not self._interstate_available:
            logger.info("Connexion à l'Interstate rétablie")
            self._interstate_available = True

    # ------------------------------------------------------------------ #
    # API publique
    # ------------------------------------------------------------------ #
    def json_server(self, key: str, value: Any) -> None:
        logger.debug("Mise à jour JSON : %s = %r", key, value)
        self._update_and_send({key: value})

    @staticmethod
    def get_resources() -> dict[str, Any]:
        return {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "system": {
                "cpu_percent": round(psutil.cpu_percent(interval=0.1), 1),
                "ram_used": round(psutil.virtual_memory().used / 1024**3, 1),
            },
        }

    def update_json(self) -> None:
        self._update_and_send({"resources": self.get_resources()})

    def start(self) -> None:
        if self.monitoring:
            logger.debug("Monitoring déjà actif")
            return

        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, name="ResourceMonitor", daemon=True
        )
        self._monitor_thread.start()
        logger.info("Monitoring des ressources démarré (mise à jour toutes les %.1f s)",
                    self.update_interval)

    def stop(self) -> None:
        if not self.monitoring:
            return

        self._stop_event.set()
        self._monitor_thread.join(timeout=self.update_interval + REQUEST_TIMEOUT + 1)
        self._monitor_thread = None
        logger.info("Monitoring des ressources arrêté")

    # ------------------------------------------------------------------ #
    # Boucle de monitoring
    # ------------------------------------------------------------------ #
    def _monitor_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.update_json()
            except Exception:
                # Une erreur ne doit pas tuer le thread silencieusement
                logger.exception("Erreur pendant la mise à jour des ressources")
            # wait() plutôt que sleep() : stop() est pris en compte immédiatement
            self._stop_event.wait(self.update_interval)

    # ------------------------------------------------------------------ #
    # Gestionnaire de contexte
    # ------------------------------------------------------------------ #
    def __enter__(self) -> "JSON_server":
        self.start()
        return self

    def __exit__(self, *exc) -> None:
        self.stop()
        self._session.close()