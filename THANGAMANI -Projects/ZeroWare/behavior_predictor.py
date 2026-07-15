def predict_behavior(features: dict) -> dict:
    behaviors = {}

    # Registry Modification
    reg_prob = 20
    if features.get('has_registry_dll', 0):
        reg_prob += 40
    if features.get('suspicious_api_count', 0) >= 5:
        reg_prob += 20
    behaviors['Registry Modification'] = min(99, reg_prob)

    # Network Connection
    net_prob = 10
    if features.get('has_network_dll', 0):
        net_prob += 50
    if features.get('has_url_strings', 0):
        net_prob += 20
    if features.get('has_ip_pattern', 0):
        net_prob += 15
    behaviors['Network Connection'] = min(99, net_prob)

    # File Encryption
    enc_prob = 10
    if features.get('has_crypto_dll', 0):
        enc_prob += 40
    if features.get('max_section_entropy', 0) > 7.0:
        enc_prob += 20
    if features.get('suspicious_api_count', 0) >= 8:
        enc_prob += 15
    behaviors['File Encryption'] = min(99, enc_prob)

    # Process Injection
    inj_prob = 5
    if features.get('suspicious_api_count', 0) >= 8:
        inj_prob += 50
    elif features.get('suspicious_api_count', 0) >= 4:
        inj_prob += 25
    if features.get('is_packed', 0):
        inj_prob += 15
    behaviors['Process Injection'] = min(99, inj_prob)

    # Persistence
    per_prob = 10
    if features.get('has_registry_dll', 0):
        per_prob += 30
    if features.get('suspicious_api_count', 0) >= 5:
        per_prob += 25
    behaviors['Persistence'] = min(99, per_prob)

    # Creates DLL
    dll_prob = 15
    if features.get('num_exports', 0) > 0:
        dll_prob += 30
    if features.get('suspicious_api_count', 0) >= 6:
        dll_prob += 20
    behaviors['Creates/Drops DLL'] = min(99, dll_prob)

    return behaviors


def get_genome(features: dict) -> dict:
    def stars(prob):
        if prob >= 80:
            return 5
        elif prob >= 60:
            return 4
        elif prob >= 40:
            return 3
        elif prob >= 20:
            return 2
        else:
            return 1

    behaviors = predict_behavior(features)

    return {
        'Persistence': stars(behaviors['Persistence']),
        'Networking': stars(behaviors['Network Connection']),
        'Encryption': stars(behaviors['File Encryption']),
        'Injection': stars(behaviors['Process Injection']),
        'Stealth': stars(features.get('is_packed', 0) * 80 + features.get('suspicious_api_count', 0) * 5),
    }
