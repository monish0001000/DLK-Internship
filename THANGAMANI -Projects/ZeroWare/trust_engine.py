def calculate_trust_score(features: dict, prediction: str) -> dict:
    score = 100
    deductions = []

    if not features.get('has_signature', 0):
        score -= 20
        deductions.append('Unsigned Binary (-20)')

    entropy = features.get('max_section_entropy', 0)
    if entropy > 7.0:
        score -= 25
        deductions.append(f'Very High Entropy: {entropy:.2f} (-25)')
    elif entropy > 6.5:
        score -= 15
        deductions.append(f'High Entropy: {entropy:.2f} (-15)')

    suspicious = features.get('suspicious_api_count', 0)
    if suspicious >= 8:
        score -= 20
        deductions.append(f'{suspicious} Suspicious API Imports (-20)')
    elif suspicious >= 4:
        score -= 10
        deductions.append(f'{suspicious} Suspicious API Imports (-10)')

    if features.get('is_packed', 0):
        score -= 15
        deductions.append('Packed Executable (-15)')

    if features.get('checksum', -1) == 0:
        score -= 5
        deductions.append('Zero Checksum (-5)')

    if features.get('overlay_size', 0) > 10000:
        score -= 5
        deductions.append('Large Overlay (-5)')

    if features.get('has_ip_pattern', 0):
        score -= 5
        deductions.append('Embedded IP Strings (-5)')

    num_dlls = features.get('num_imported_dlls', 0)
    if num_dlls <= 2:
        score -= 10
        deductions.append('Suspiciously Few Imports (-10)')

    timestamp = features.get('timestamp', 0)
    if timestamp < 1000000:
        score -= 5
        deductions.append('Invalid Timestamp (-5)')

    score = max(0, score)

    if score >= 75:
        level = 'High'
        color = 'success'
    elif score >= 45:
        level = 'Medium'
        color = 'warning'
    else:
        level = 'Low'
        color = 'danger'

    return {
        'score': score,
        'level': level,
        'color': color,
        'deductions': deductions
    }


def calculate_risk_score(features: dict, malware_probability: float) -> int:
    base = malware_probability
    if features.get('has_ip_pattern', 0):
        base = min(100, base + 5)
    if features.get('is_packed', 0):
        base = min(100, base + 5)
    if features.get('suspicious_api_count', 0) >= 8:
        base = min(100, base + 5)
    return round(base)


def calculate_zeroday_probability(features: dict, top_similarity: float) -> int:
    base = 50
    if features.get('is_packed', 0):
        base += 15
    if not features.get('has_signature', 0):
        base += 10
    entropy = features.get('max_section_entropy', 0)
    if entropy > 7.5:
        base += 15
    elif entropy > 7.0:
        base += 8

    # Lower zeroday if similar to known malware
    if top_similarity > 80:
        base -= 30
    elif top_similarity > 60:
        base -= 15

    return max(5, min(95, base))
