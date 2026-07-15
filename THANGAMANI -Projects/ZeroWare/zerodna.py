import hashlib
import random
import string

KNOWN_MALWARE = [
    {'name': 'LockBit', 'profile': {'max_entropy': 7.8, 'suspicious_api': 12, 'has_network': 1, 'has_crypto': 1, 'is_packed': 1}},
    {'name': 'WannaCry', 'profile': {'max_entropy': 7.5, 'suspicious_api': 10, 'has_network': 1, 'has_crypto': 1, 'is_packed': 1}},
    {'name': 'Emotet', 'profile': {'max_entropy': 6.8, 'suspicious_api': 8, 'has_network': 1, 'has_crypto': 0, 'is_packed': 0}},
    {'name': 'AgentTesla', 'profile': {'max_entropy': 6.2, 'suspicious_api': 6, 'has_network': 1, 'has_crypto': 1, 'is_packed': 0}},
    {'name': 'Mirai', 'profile': {'max_entropy': 7.1, 'suspicious_api': 7, 'has_network': 1, 'has_crypto': 0, 'is_packed': 1}},
    {'name': 'Ryuk', 'profile': {'max_entropy': 7.6, 'suspicious_api': 11, 'has_network': 1, 'has_crypto': 1, 'is_packed': 1}},
    {'name': 'TrickBot', 'profile': {'max_entropy': 6.5, 'suspicious_api': 9, 'has_network': 1, 'has_crypto': 0, 'is_packed': 0}},
]


def generate_zerodna_id(sha256: str) -> str:
    h = sha256[:8].upper()
    part1 = h[:4]
    part2 = h[4:]
    return f"ZW-{part1}-{part2}"


def compute_similarity(features: dict, profile: dict) -> float:
    score = 0.0
    total = 0

    # Entropy similarity
    fe = features.get('max_section_entropy', 0)
    pe = profile['max_entropy']
    diff = abs(fe - pe) / 8.0
    score += max(0, 1 - diff)
    total += 1

    # API similarity
    fa = features.get('suspicious_api_count', 0)
    pa = profile['suspicious_api']
    diff = abs(fa - pa) / 15.0
    score += max(0, 1 - diff)
    total += 1

    # Boolean features
    for key, profile_key in [('has_network_dll', 'has_network'), ('has_crypto_dll', 'has_crypto'), ('is_packed', 'is_packed')]:
        if features.get(key, 0) == profile[profile_key]:
            score += 1
        total += 1

    return round((score / total) * 100, 1) if total > 0 else 0.0


def get_zerodna(features: dict, sha256: str) -> dict:
    dna_id = generate_zerodna_id(sha256)
    similarities = []

    for malware in KNOWN_MALWARE:
        sim = compute_similarity(features, malware['profile'])
        similarities.append({'name': malware['name'], 'similarity': sim})

    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    top3 = similarities[:3]

    return {
        'dna_id': dna_id,
        'similarities': top3,
        'top_match': top3[0] if top3 else None
    }
