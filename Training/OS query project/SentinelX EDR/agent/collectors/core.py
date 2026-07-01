from typing import Dict, List, Any
from osquery.connector import connector
from osquery.queries import QUERIES

def collect_processes() -> List[Dict[str, Any]]:
    raw = connector.query(QUERIES["processes"])
    formatted = []
    for p in raw:
        formatted.append({
            "pid": int(p.get("pid", 0)),
            "name": p.get("name", ""),
            "path": p.get("path"),
            "cmdline": p.get("cmdline"),
            "parent_pid": int(p.get("parent", 0)) if p.get("parent") else None,
            "user": p.get("uid"),
            "state": p.get("state")
        })
    return formatted

def collect_network() -> List[Dict[str, Any]]:
    raw = connector.query(QUERIES["network"])
    formatted = []
    for n in raw:
        formatted.append({
            "pid": int(n.get("pid", 0)) if n.get("pid") else None,
            "local_address": n.get("local_address"),
            "local_port": int(n.get("local_port", 0)) if n.get("local_port") else None,
            "remote_address": n.get("remote_address"),
            "remote_port": int(n.get("remote_port", 0)) if n.get("remote_port") else None,
            "protocol": n.get("protocol"),
            "state": n.get("state")
        })
    return formatted

def collect_users() -> List[Dict[str, Any]]:
    raw = connector.query(QUERIES["users"])
    formatted = []
    for u in raw:
        formatted.append({
            "username": u.get("user", ""),
            "host": u.get("host"),
            "tty": u.get("tty"),
            "time": u.get("time")
        })
    return formatted

def collect_startup() -> List[Dict[str, Any]]:
    raw = connector.query(QUERIES["startup"])
    formatted = []
    for s in raw:
        formatted.append({
            "name": s.get("name", ""),
            "path": s.get("path"),
            "args": s.get("args"),
            "source": s.get("source"),
            "status": s.get("type")
        })
    return formatted

def collect_services() -> List[Dict[str, Any]]:
    raw = connector.query(QUERIES["services"])
    formatted = []
    for s in raw:
        formatted.append({
            "name": s.get("name", ""),
            "display_name": s.get("display_name"),
            "status": s.get("status"),
            "start_type": s.get("start_type"),
            "path": s.get("path"),
            "user": s.get("user_account")
        })
    return formatted

def collect_tasks() -> List[Dict[str, Any]]:
    raw = connector.query(QUERIES["scheduled_tasks"])
    formatted = []
    for t in raw:
        enabled = t.get("enabled", "0") == "1"
        formatted.append({
            "name": t.get("name", ""),
            "action": t.get("action"),
            "path": t.get("path"),
            "enabled": enabled,
            "state": t.get("state")
        })
    return formatted

def collect_all(enabled_collectors: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    data = {
        "processes": [],
        "network_connections": [],
        "user_sessions": [],
        "startup_items": [],
        "services": [],
        "scheduled_tasks": []
    }
    
    if "processes" in enabled_collectors:
        data["processes"] = collect_processes()
    if "network" in enabled_collectors:
        data["network_connections"] = collect_network()
    if "users" in enabled_collectors:
        data["user_sessions"] = collect_users()
    if "startup" in enabled_collectors:
        data["startup_items"] = collect_startup()
    if "services" in enabled_collectors:
        data["services"] = collect_services()
    if "scheduled_tasks" in enabled_collectors:
        data["scheduled_tasks"] = collect_tasks()
        
    return data
