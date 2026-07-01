import urllib.request
import urllib.error
import json
import logging
from config import config

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self):
        self.base_url = config.backend_url
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "SentinelX-OSQuery-Agent/1.0"
        }

    def _post(self, endpoint: str, data: dict) -> dict:
        url = f"{self.base_url}{endpoint}"
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'), 
            headers=self.headers, 
            method='POST'
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = response.read().decode('utf-8')
                if response_data:
                    return json.loads(response_data)
                return {}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            logger.error(f"API Request failed with {e.code}: {error_body}")
            return {}
        except urllib.error.URLError as e:
            logger.error(f"API Request failed: {e.reason}")
            return {}
        except json.JSONDecodeError:
            logger.error("Failed to decode API response.")
            return {}

    def register(self) -> bool:
        """Register the agent with the backend."""
        payload = {
            "id": config.uuid,
            "hostname": config.hostname,
            "ip_address": config.ip_address,
            "os_type": config.os_type,
            "os_version": config.os_version,
            "agent_version": "1.0.0",
            "tags": ""
        }
        
        response = self._post("/endpoints/", payload)
        if response and "id" in response:
            config.agent_id = response["id"]
            config.save_to_file()
            logger.info(f"Successfully registered. Agent ID: {config.agent_id}")
            return True
        else:
            return False

    def heartbeat(self):
        """Send a heartbeat to the backend."""
        if not config.agent_id:
            return
            
        payload = {
            "endpoint_id": config.agent_id
        }
        self._post("/endpoints/heartbeat", payload)

    def send_telemetry(self, telemetry_data: dict):
        """Send collected telemetry to the backend."""
        if not config.agent_id:
            return
            
        payload = {
            "endpoint_id": config.agent_id,
            **telemetry_data
        }
        
        response = self._post("/telemetry/ingest", payload)
        if response:
            logger.debug(f"Telemetry pushed successfully. Server responded: {response}")

api_client = APIClient()
