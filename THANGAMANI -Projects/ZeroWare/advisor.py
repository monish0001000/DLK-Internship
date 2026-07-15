def get_recommendations(prediction: str, features: dict, behaviors: dict) -> list:
    recs = []

    if prediction == 'Malware':
        recs.append('🚨 Quarantine this file immediately — do NOT execute it')
        recs.append('🔌 Disconnect from the network if this file was executed')
        recs.append('🔒 Block file hash in your endpoint security solution')
        recs.append('🔍 Perform a full system scan with updated definitions')
        recs.append('📋 Monitor startup entries and scheduled tasks for persistence')
        recs.append('📤 Submit sample to VirusTotal for multi-engine verification')

    elif prediction == 'Suspicious':
        recs.append('⚠️ Do NOT execute this file without sandbox analysis')
        recs.append('🧪 Submit to a sandbox (Any.run / Cuckoo) for dynamic analysis')
        recs.append('🔍 Verify file source and publisher before proceeding')
        recs.append('📋 Check file digital signature and certificate chain')

    else:
        recs.append('✅ File appears safe — standard precautions still advised')
        recs.append('🔄 Keep your security software up to date')

    # Behavior-based additional recs
    if behaviors.get('Network Connection', 0) > 70:
        recs.append('🌐 Monitor network traffic — this file may contact external servers')
    if behaviors.get('File Encryption', 0) > 70:
        recs.append('💾 Back up important data immediately — ransomware behavior detected')
    if behaviors.get('Process Injection', 0) > 70:
        recs.append('🛡️ Enable process protection in your EDR solution')
    if behaviors.get('Persistence', 0) > 70:
        recs.append('🔑 Audit registry Run keys and startup folders')

    return recs


def generate_analyst_summary(prediction: str, features: dict, reasons: list, zerodna: dict) -> str:
    label = prediction
    entropy = features.get('max_section_entropy', 0)
    is_packed = features.get('is_packed', 0)
    suspicious_apis = features.get('suspicious_api_count', 0)
    has_sig = features.get('has_signature', 0)
    top_match = zerodna.get('top_match', {})

    parts = []

    if label == 'Malware':
        parts.append(
            "This executable exhibits multiple high-confidence malware indicators."
        )
        if is_packed:
            parts.append(
                f"The file is packed with unusually high section entropy ({entropy:.2f}), "
                "a technique commonly used to evade static detection."
            )
        if suspicious_apis >= 6:
            parts.append(
                f"It imports {suspicious_apis} suspicious APIs including memory manipulation "
                "and process injection functions."
            )
        if not has_sig:
            parts.append("The binary is unsigned, with no valid digital certificate present.")
        if top_match and top_match.get('similarity', 0) > 60:
            parts.append(
                f"ZeroDNA analysis indicates {top_match['similarity']}% similarity to "
                f"{top_match['name']} — a known malware family."
            )
        parts.append("Recommendation: Quarantine immediately and isolate the affected system.")

    elif label == 'Suspicious':
        parts.append(
            "This file contains several characteristics that warrant further investigation."
        )
        if entropy > 6.5:
            parts.append(f"Section entropy is elevated ({entropy:.2f}), which may indicate packing.")
        if suspicious_apis > 0:
            parts.append(f"Found {suspicious_apis} potentially suspicious API imports.")
        parts.append(
            "Recommendation: Do not execute. Submit to sandbox analysis before taking action."
        )

    else:
        parts.append(
            "This file does not exhibit significant malware characteristics based on static analysis."
        )
        parts.append(
            "Standard security practices still apply — verify the source and keep software updated."
        )

    return " ".join(parts)
