import subprocess
import json
import logging

logger = logging.getLogger(__name__)

class OSQueryConnector:
    def __init__(self, binary_path="C:\\Program Files\\osquery\\osqueryi.exe"):
        self.binary_path = binary_path

    def query(self, sql: str) -> list:
        """Executes an OSQuery SQL statement and returns a list of dicts."""
        try:
            # We use subprocess to run osqueryi in JSON mode
            cmd = [self.binary_path, "--json", sql]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = result.stdout.strip()
            
            if not output:
                return []
            
            # Parse the JSON output
            data = json.loads(output)
            return data
            
        except subprocess.CalledProcessError as e:
            logger.error(f"OSQuery execution failed: {e.stderr}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OSQuery output: {e}")
            return []
        except FileNotFoundError:
            logger.error(f"osqueryi binary not found at {self.binary_path}. Is OSQuery installed?")
            return []

connector = OSQueryConnector()
