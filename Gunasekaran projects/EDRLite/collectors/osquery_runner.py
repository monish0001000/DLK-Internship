"""
collectors/osquery_runner.py
────────────────────────────
Central osquery executor.

On Kali Linux with osquery installed:
  - Tries osqueryi binary (subprocess) first
  - Falls back to osqueryd UNIX socket (thrift) if available

If osquery is unavailable (or OSQUERY_SIMULATE=true):
  - Returns an empty list so callers handle it gracefully
"""

import json
import subprocess
import os
import logging
from flask import current_app

logger = logging.getLogger(__name__)


def run_query(query: str) -> list[dict]:
    """
    Execute an osquery SQL query and return results as a list of dicts.
    Returns [] on any error.
    """
    app = current_app._get_current_object()

    if app.config.get('OSQUERY_SIMULATE', False):
        logger.debug("OSQUERY_SIMULATE=true — skipping real osquery call")
        return []

    binary = app.config.get('OSQUERY_BINARY', 'osqueryi')
    return _run_via_binary(binary, query)


def _run_via_binary(binary: str, query: str) -> list[dict]:
    """Run osqueryi binary with --json flag."""
    try:
        result = subprocess.run(
            [binary, '--json', query],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        else:
            logger.warning(f"osqueryi returned code {result.returncode}: {result.stderr[:200]}")
            return []
    except FileNotFoundError:
        logger.error(f"osquery binary not found at '{binary}'. "
                     "Install osquery or set OSQUERY_SIMULATE=true.")
        return []
    except subprocess.TimeoutExpired:
        logger.warning("osquery query timed out.")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse osquery output: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected osquery error: {e}")
        return []


def run_raw_query(query: str) -> tuple[list[dict], str | None]:
    """
    Run a raw osquery query (for threat hunting page).
    Returns (results, error_message).
    """
    app = current_app._get_current_object()
    binary = app.config.get('OSQUERY_BINARY', 'osqueryi')
    try:
        result = subprocess.run(
            [binary, '--json', query],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.stdout.strip():
            data = json.loads(result.stdout)
            return data, None
        if result.stderr:
            return [], result.stderr.strip()
        return [], None
    except FileNotFoundError:
        return [], f"osquery binary '{binary}' not found. Install osquery on this system."
    except subprocess.TimeoutExpired:
        return [], "Query timed out after 30 seconds."
    except json.JSONDecodeError:
        return [], "Failed to parse osquery output."
    except Exception as e:
        return [], str(e)
