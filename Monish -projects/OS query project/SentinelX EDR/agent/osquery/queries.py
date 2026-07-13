QUERIES = {
    "processes": """
        SELECT pid, name, path, cmdline, state, parent, uid 
        FROM processes;
    """,
    "network": """
        SELECT pid, local_address, local_port, remote_address, remote_port, protocol, state 
        FROM process_open_sockets 
        WHERE remote_port != 0 
        LIMIT 100;
    """,
    "users": """
        SELECT user, tty, host, time 
        FROM logged_in_users;
    """,
    "startup": """
        SELECT name, path, args, type, source 
        FROM startup_items;
    """,
    "services": """
        SELECT name, display_name, status, start_type, path, user_account 
        FROM services 
        WHERE status = 'RUNNING';
    """,
    "programs": """
        SELECT name, version, install_location, install_date 
        FROM programs 
        LIMIT 100;
    """,
    "scheduled_tasks": """
        SELECT name, action, path, enabled, state, next_run_time 
        FROM scheduled_tasks;
    """
}
