# DLK Internship Portfolio

## Overview
This repository (`DLK-Internship`) contains a comprehensive collection of advanced cybersecurity, penetration testing, and machine learning projects developed during the DLK Internship program. It showcases a diverse array of enterprise-grade security tools, ranging from endpoint detection systems to network anomaly detectors.

## Projects

### 1. SentinelX EDR (Enterprise Detection & Response)
**Location:** `Training/OS query project/SentinelX EDR`
An AI-powered Endpoint Detection and Response (EDR) platform built for modern Security Operations Centers (SOCs). 
- **Features:** It leverages OSQuery to treat the operating system as a high-performance relational database, ingesting rich endpoint telemetry in real-time. It uses WebSockets for instant alerting and integrates with Large Language Models (LLMs) to automatically investigate and summarize alerts for analysts.
- **Tech Stack:** FastAPI, React, OSQuery, SQLite/PostgreSQL, WebSockets.

### 2. Network Traffic Anomaly Detector
**Location:** `Training/Network Traffic anomaly Detector`
A machine learning-based system designed to monitor and analyze network traffic streams to detect anomalous patterns indicative of cyber attacks or unauthorized access.
- **Features:** Ingests PCAP or live network data and applies anomaly detection algorithms (such as Isolation Forests or Autoencoders) to flag suspicious activity that evades traditional signature-based IDS/IPS solutions.

### 3. Malware Detector
**Location:** `Training/Malware Detector`
An automated malware analysis and detection tool that evaluates static and dynamic file characteristics.
- **Features:** Analyzes PE (Portable Executable) headers, extracts features (like API calls and strings), and uses a trained classification model to determine whether a given binary is benign or malicious.

### 4. Asymmetric Encryption Dashboard
**Location:** `Training/Asymmetric_Encryption_Dashboard`
A cryptographic utility and educational dashboard for visualizing and managing asymmetric encryption workflows.
- **Features:** Demonstrates key pair generation (RSA/ECC), public key distribution, and secure message encryption/decryption, helping users understand the core mechanics of Public Key Infrastructure (PKI).

### 5. DLK Pentest (AI Pentesting Copilots)
**Location:** `Training/DLK pentest`
A collection of AI-assisted penetration testing tools, notably including integrations with `PentestGPT` and `pentest-copilot`.
- **Features:** Automates the reconnaissance, scanning, and exploitation phases of a penetration test. It reads context, suggests commands, and iteratively analyzes outputs from tools like Nmap and Metasploit, effectively acting as an intelligent copilot for ethical hackers.

## Repository Architecture

```text
DLK/
├── README.md                  # Quick overview
├── explain.md                 # Detailed project breakdowns
└── Training/                  # Main internship projects directory
    ├── Asymmetric_Encryption_Dashboard/
    ├── DLK pentest/           # PentestGPT & Copilot
    ├── Malware Detector/
    ├── Network Traffic anomaly Detector/
    └── OS query project/      # SentinelX EDR
```

## Conclusion
This repository demonstrates a deep, practical understanding of modern cybersecurity domains including Endpoint Security, Network Defense, Cryptography, Machine Learning applied to threat detection, and Offensive Security automation.
