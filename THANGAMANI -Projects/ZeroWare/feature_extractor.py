import pefile
import math
import hashlib
import os
import struct


def calculate_entropy(data):
    if not data:
        return 0.0
    frequency = {}
    for byte in data:
        frequency[byte] = frequency.get(byte, 0) + 1
    entropy = 0.0
    total = len(data)
    for count in frequency.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def extract_features(file_path):
    features = {}
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()

        features['file_size'] = len(raw_data)
        features['md5'] = hashlib.md5(raw_data).hexdigest()
        features['sha256'] = hashlib.sha256(raw_data).hexdigest()
        features['overall_entropy'] = calculate_entropy(raw_data)

        pe = pefile.PE(file_path)

        # Header features
        features['machine_type'] = pe.FILE_HEADER.Machine
        features['num_sections'] = pe.FILE_HEADER.NumberOfSections
        features['timestamp'] = pe.FILE_HEADER.TimeDateStamp
        features['characteristics'] = pe.FILE_HEADER.Characteristics

        # Optional header
        features['image_base'] = pe.OPTIONAL_HEADER.ImageBase
        features['entry_point'] = pe.OPTIONAL_HEADER.AddressOfEntryPoint
        features['subsystem'] = pe.OPTIONAL_HEADER.Subsystem
        features['dll_characteristics'] = pe.OPTIONAL_HEADER.DllCharacteristics
        features['size_of_image'] = pe.OPTIONAL_HEADER.SizeOfImage
        features['size_of_headers'] = pe.OPTIONAL_HEADER.SizeOfHeaders
        features['checksum'] = pe.OPTIONAL_HEADER.CheckSum
        features['size_of_stack_reserve'] = pe.OPTIONAL_HEADER.SizeOfStackReserve
        features['size_of_heap_reserve'] = pe.OPTIONAL_HEADER.SizeOfHeapReserve

        # Section features
        section_entropies = []
        section_sizes = []
        exec_sections = 0
        write_sections = 0
        for section in pe.sections:
            sec_data = section.get_data()
            ent = calculate_entropy(sec_data)
            section_entropies.append(ent)
            section_sizes.append(section.SizeOfRawData)
            if section.Characteristics & 0x20000000:
                exec_sections += 1
            if section.Characteristics & 0x80000000:
                write_sections += 1

        features['max_section_entropy'] = max(section_entropies) if section_entropies else 0
        features['avg_section_entropy'] = sum(section_entropies) / len(section_entropies) if section_entropies else 0
        features['min_section_entropy'] = min(section_entropies) if section_entropies else 0
        features['exec_sections'] = exec_sections
        features['write_sections'] = write_sections
        features['total_section_size'] = sum(section_sizes)

        # Import features
        suspicious_apis = [
            'VirtualAlloc', 'VirtualProtect', 'WriteProcessMemory', 'CreateRemoteThread',
            'OpenProcess', 'RegSetValueEx', 'RegCreateKeyEx', 'CreateService',
            'WinExec', 'ShellExecute', 'URLDownloadToFile', 'InternetOpen',
            'CryptEncrypt', 'CryptDecrypt', 'GetProcAddress', 'LoadLibrary',
            'NtUnmapViewOfSection', 'ZwWriteVirtualMemory', 'SetWindowsHookEx'
        ]

        imported_dlls = []
        imported_apis = []
        suspicious_api_count = 0

        if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                dll_name = entry.dll.decode(errors='ignore').lower()
                imported_dlls.append(dll_name)
                for imp in entry.imports:
                    if imp.name:
                        api_name = imp.name.decode(errors='ignore')
                        imported_apis.append(api_name)
                        if api_name in suspicious_apis:
                            suspicious_api_count += 1

        features['num_imported_dlls'] = len(imported_dlls)
        features['num_imported_apis'] = len(imported_apis)
        features['suspicious_api_count'] = suspicious_api_count
        features['has_network_dll'] = 1 if any(d in ['wininet.dll', 'ws2_32.dll', 'urlmon.dll'] for d in imported_dlls) else 0
        features['has_crypto_dll'] = 1 if any(d in ['crypt32.dll', 'advapi32.dll'] for d in imported_dlls) else 0
        features['has_registry_dll'] = 1 if 'advapi32.dll' in imported_dlls else 0

        # Export features
        features['num_exports'] = 0
        if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
            features['num_exports'] = len(pe.DIRECTORY_ENTRY_EXPORT.symbols)

        # Resource features
        features['num_resources'] = 0
        if hasattr(pe, 'DIRECTORY_ENTRY_RESOURCE'):
            features['num_resources'] = len(pe.DIRECTORY_ENTRY_RESOURCE.entries)

        # Digital signature
        features['has_signature'] = 0
        if hasattr(pe, 'DIRECTORY_ENTRY_SECURITY'):
            features['has_signature'] = 1

        # Overlay
        overlay_offset = pe.get_overlay_data_start_offset()
        if overlay_offset:
            features['overlay_size'] = len(raw_data) - overlay_offset
        else:
            features['overlay_size'] = 0

        # String analysis
        strings = _extract_strings(raw_data)
        features['num_strings'] = len(strings)
        features['has_url_strings'] = 1 if any('http' in s.lower() for s in strings) else 0
        features['has_ip_pattern'] = 1 if any(_looks_like_ip(s) for s in strings) else 0

        # Packing heuristic
        features['is_packed'] = 1 if features['max_section_entropy'] > 7.0 else 0

        features['imported_dlls'] = imported_dlls
        features['imported_apis'] = imported_apis[:50]

        pe.close()
        return features

    except Exception as e:
        return {'error': str(e), 'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0}


def _extract_strings(data, min_length=4):
    strings = []
    current = ''
    for byte in data:
        if 32 <= byte <= 126:
            current += chr(byte)
        else:
            if len(current) >= min_length:
                strings.append(current)
            current = ''
    return strings[:200]


def _looks_like_ip(s):
    parts = s.split('.')
    if len(parts) == 4:
        try:
            return all(0 <= int(p) <= 255 for p in parts)
        except:
            return False
    return False
