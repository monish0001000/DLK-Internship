# PDF Threat Analyzer

A Python-based utility to analyze PDF files for potential security threats, malicious scripts, embedded Javascript, and suspicious metadata.

## Features

- **Metadata Analysis**: Extraction and analysis of PDF metadata (Author, Producer, Creation Date, etc.) to look for anomalies.
- **Structure Analysis**: Checks for suspicious elements like `/JavaScript`, `/OpenAction`, `/Launch`, `/EmbeddedFile`, and `/URI`.
- **Payload Extraction**: Inspects compressed streams for obfuscated shellcode or script payloads.
- **Report Generation**: Outputs a comprehensive threat analysis report.

## Getting Started

### Prerequisites

- Python 3.8+

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Gunasekaran20050831/pdf_threat_analyzer.git
   cd pdf_threat_analyzer
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install requirements (once dependencies are defined):
   ```bash
   pip install -r requirements.txt
   ```

## Usage

*(To be implemented)*
