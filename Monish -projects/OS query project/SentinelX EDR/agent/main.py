import time
import logging
from config import config
from sender.api_client import api_client
from collectors.core import collect_all

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SentinelX-Agent")

def main():
    logger.info(f"Starting SentinelX Agent (v1.0.0) on {config.hostname}")
    
    # Registration Loop
    registered = False
    while not registered:
        logger.info("Attempting to register with backend...")
        registered = api_client.register()
        if not registered:
            logger.warning("Registration failed. Retrying in 10 seconds...")
            time.sleep(10)

    last_heartbeat = 0
    last_poll = 0
    
    logger.info("Entering main collection loop.")
    while True:
        current_time = time.time()
        
        # Heartbeat
        if current_time - last_heartbeat >= config.heartbeat_interval_seconds:
            api_client.heartbeat()
            last_heartbeat = current_time
            
        # Telemetry Polling
        if current_time - last_poll >= config.poll_interval_seconds:
            logger.info("Collecting telemetry...")
            data = collect_all(config.enabled_collectors)
            api_client.send_telemetry(data)
            last_poll = current_time
            
        time.sleep(1)

if __name__ == "__main__":
    main()
