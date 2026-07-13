"""
telegram_alert.py - Telegram Notification Module
Sends instant alerts to your phone via Telegram Bot API when
predictor.py / attack_detector.py flags an anomaly.

SETUP:
1. Replace BOT_TOKEN below with your token from @BotFather
2. Replace CHAT_ID below with your chat id (from getUpdates)
3. import send_telegram_alert in predictor.py and call it in log_alert
"""

import requests
import time

# ---- CONFIG: fill these in ----
BOT_TOKEN = "PASTE_YOUR_NEW_BOT_TOKEN_HERE"
CHAT_ID = "6367364593"

TELEGRAM_API = f"https://api.telegram.org/bot8810966088:AAGcoODoSTtfG7Ml-JPY11mDz0l7LJ8yKYI/sendMessage"

# Avoid spamming Telegram - only send 1 alert per (src,dst,type) every N seconds
_last_sent = {}
COOLDOWN_SECONDS = 15


def _should_send(key):
    now = time.time()
    last = _last_sent.get(key, 0)
    if now - last >= COOLDOWN_SECONDS:
        _last_sent[key] = now
        return True
    return False


def send_telegram_alert(flow, result):
    """
    flow: dict from extractor (src_ip, dst_ip, src_port, dst_port, protocol, ...)
    result: dict from attack_detector.classify_attack()
    """
    attack_type = result["attack_type"]
    key = f"{flow['src_ip']}:{flow['dst_ip']}:{attack_type}"

    if not _should_send(key):
        return  # skip - already alerted recently for this flow+attack combo

    emoji = {
        "PORT_SCAN": "🔍",
        "DDOS_FLOOD": "🌊",
        "BRUTE_FORCE": "🔨",
        "ANOMALY": "⚠️",
    }.get(attack_type, "🚨")

    message = (
        f"{emoji} {attack_type.replace('_', ' ')} DETECTED\n\n"
        f"Severity: {result['severity']}\n"
        f"Confidence: {result['confidence']*100:.1f}%\n"
        f"Source: {flow['src_ip']}:{flow['src_port']}\n"
        f"Destination: {flow['dst_ip']}:{flow['dst_port']}\n"
        f"Protocol: {flow['protocol']}\n"
        f"Reason: {result['reason']}"
    )

    try:
        resp = requests.post(
            TELEGRAM_API,
            data={
                "chat_id": CHAT_ID,
                "text": message,
            },
            timeout=5,
        )
        if resp.status_code != 200:
            print(f"[telegram] Failed to send alert: {resp.text}")
    except requests.exceptions.RequestException as e:
        print(f"[telegram] Error sending alert: {e}")


if __name__ == "__main__":
    # Quick test
    test_flow = {
        "src_ip": "192.168.1.3", "dst_ip": "192.168.1.145",
        "src_port": 45029, "dst_port": 22, "protocol": "TCP",
    }
    test_result = {
        "attack_type": "PORT_SCAN", "severity": "HIGH",
        "confidence": 0.95, "reason": "Test alert from telegram_alert.py",
    }
    send_telegram_alert(test_flow, test_result)
    print("[telegram] Test alert sent! Check your Telegram.")
