import os
import platform
import socket
import uuid
import json
from dataclasses import dataclass, field
from typing import List

@dataclass
class AgentConfig:
    backend_url: str = "http://localhost:8000/api/v1"
    agent_id: str = None
    hostname: str = socket.gethostname()
    os_type: str = platform.system()
    os_version: str = platform.version()
    ip_address: str = socket.gethostbyname(socket.gethostname())
    uuid: str = str(uuid.uuid4())
    
    poll_interval_seconds: int = 30
    heartbeat_interval_seconds: int = 30
    
    enabled_collectors: List[str] = field(default_factory=lambda: [
        "processes", "network", "users", "startup", "services", "programs"
    ])
    
    def load_from_file(self, path: str = "agent_config.json"):
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_to_file(self, path: str = "agent_config.json"):
        try:
            with open(path, "w") as f:
                data = {
                    "backend_url": self.backend_url,
                    "agent_id": self.agent_id,
                    "poll_interval_seconds": self.poll_interval_seconds,
                    "heartbeat_interval_seconds": self.heartbeat_interval_seconds,
                    "enabled_collectors": self.enabled_collectors,
                    "uuid": self.uuid
                }
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

config = AgentConfig()
config.load_from_file()
