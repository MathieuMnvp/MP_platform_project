import psutil
import threading
import time
from datetime import datetime
from typing import Optional
import os
import requests
import json

_json_lock = threading.Lock()
IP_INTERSTATE = "192.168.1.19" 

class JSON_server:
    
    def __init__(self):

        self.JSON_path = "Utils/LEDMatrix.json"
        self.update_interval = 1.0
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.process = psutil.Process(os.getpid())
        self.IP_INTERSTATE = "192.168.1.19" 

    def start(self):
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
            print(f"Monitoring des ressources démarré (mise à jour toutes les {self.update_interval}s)")
        
    def get_resources(self):
        
        system_cpu = psutil.cpu_percent(interval=0.1)
        system_ram = psutil.virtual_memory().used / (1024**3)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": round(system_cpu, 1),
                "ram_used": round(system_ram, 1),
                    },
                }
    
    def update_json(self):

        JSON_path = self.JSON_path
        with _json_lock:
            with open(JSON_path, "r") as f:
                data = json.load(f)
            
            data["resources"] = self.get_resources()
            
            with open(JSON_path, "w") as f:
                json.dump(data, f, indent=2) 

        try:
            requests.post(f"http://{self.IP_INTERSTATE}", json=data, timeout=3)
        except:
            pass
    
    def monitor_loop(self):
        while self.monitoring:
            self.update_json()
            time.sleep(self.update_interval)
    
    def stop(self):
        if self.monitoring:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=self.update_interval + 1)
            print("Monitoring des ressources arrêté")

    def json_server(self, key, value):
        fichier = "Utils/LEDMatrix.json"

        with _json_lock:
            with open(fichier, "r") as f:
                data = json.load(f)

            data[key] = value

            with open(fichier, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        try:
            requests.post(f"http://{IP_INTERSTATE}", json=data, timeout=3)
        except Exception as e:
            print(f"Interstate non connectée : {e}")
