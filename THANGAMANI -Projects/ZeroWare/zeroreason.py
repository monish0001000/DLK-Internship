def get_reasons(features: dict, prediction: str) -> list:
    reasons = []

    entropy = features.get('max_section_entropy', 0)
    if entropy > 7.0:
        reasons.append({'icon': '🔴', 'text': f'Very High Section Entropy ({entropy:.2f}) — Likely Packed/Encrypted'})
    elif entropy > 6.5:
        reasons.append({'icon': '🟠', 'text': f'High Section Entropy ({entropy:.2f}) — Possible Packing'})
    elif entropy < 3.5:
        reasons.append({'icon': '🟢', 'text': f'Low Entropy ({entropy:.2f}) — Appears Uncompressed'})

    if features.get('is_packed', 0):
        reasons.append({'icon': '🔴', 'text': 'Packed Executable Detected — Obfuscation Suspected'})

    suspicious = features.get('suspicious_api_count', 0)
    if suspicious >= 8:
        reasons.append({'icon': '🔴', 'text': f'{suspicious} Suspicious API Imports (VirtualAlloc, WriteProcessMemory, etc.)'})
    elif suspicious >= 4:
        reasons.append({'icon': '🟠', 'text': f'{suspicious} Potentially Suspicious API Imports'})
    elif suspicious == 0:
        reasons.append({'icon': '🟢', 'text': 'No Suspicious API Imports Found'})

    if features.get('has_signature', 0) == 0:
        reasons.append({'icon': '🔴', 'text': 'Missing Digital Signature — Unsigned Binary'})
    else:
        reasons.append({'icon': '🟢', 'text': 'Valid Digital Signature Present'})

    checksum = features.get('checksum', -1)
    if checksum == 0:
        reasons.append({'icon': '🟠', 'text': 'Checksum is Zero — PE Header Anomaly'})

    if features.get('has_network_dll', 0):
        reasons.append({'icon': '🟠', 'text': 'Network DLL Imports (WinInet / WS2_32) — May Connect to Internet'})

    if features.get('has_crypto_dll', 0):
        reasons.append({'icon': '🟠', 'text': 'Crypto DLL Imports — May Encrypt/Decrypt Data'})

    if features.get('has_ip_pattern', 0):
        reasons.append({'icon': '🔴', 'text': 'Embedded IP Address Pattern Found in Strings'})

    if features.get('has_url_strings', 0):
        reasons.append({'icon': '🟠', 'text': 'Embedded URL Strings Found'})

    num_dlls = features.get('num_imported_dlls', 0)
    if num_dlls <= 2 and features.get('num_imported_apis', 0) <= 10:
        reasons.append({'icon': '🔴', 'text': 'Very Few Imports — Strongly Suggests Runtime API Resolution (Packing)'})

    overlay = features.get('overlay_size', 0)
    if overlay > 10000:
        reasons.append({'icon': '🟠', 'text': f'Large Overlay Section ({overlay} bytes) — Possible Appended Payload'})

    num_sections = features.get('num_sections', 0)
    if num_sections <= 1:
        reasons.append({'icon': '🔴', 'text': f'Only {num_sections} PE Section(s) — Abnormal Structure'})
    elif num_sections > 10:
        reasons.append({'icon': '🟠', 'text': f'{num_sections} Sections — Unusually High Section Count'})

    timestamp = features.get('timestamp', 0)
    if timestamp < 1000000:
        reasons.append({'icon': '🔴', 'text': 'Invalid/Zero Compile Timestamp — Header Manipulation Suspected'})

    if not reasons:
        reasons.append({'icon': '🟢', 'text': 'No Suspicious Characteristics Detected'})

    return reasons
