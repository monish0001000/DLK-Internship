# 🔐 OdinCrypto — Enterprise Cryptographic Platform

A professional, full-featured cryptographic web application built with Python + Flask.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open in Browser
```
http://127.0.0.1:5000
```

### 4. Default Admin Account
```
Email:    admin@odincrypto.local
Password: Admin@1234
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔑 Key Management | Generate RSA-2048/4096 key pairs, download, revoke, QR share |
| 🔒 Text Encryption | AES-256, RSA-OAEP, Hybrid (AES+RSA) encryption |
| 📁 File Encryption | Encrypt/decrypt any file with AES-256-CBC |
| #️⃣ Hash Center | SHA-256, SHA-512, BLAKE2b — compute & verify |
| ✍️ Digital Signature | RSA-PSS sign and verify files/text |
| 🎲 Password Generator | Secure passwords, passphrases, PINs |
| 🗄️ Password Vault | AES-encrypted credential storage |
| 📝 Secure Notes | Encrypted personal notes |
| 🔗 Secure Sharing | Share files with password, expiry, download limits |
| 📋 Audit Logs | Complete activity tracking |
| 🛡️ Admin Panel | User management and platform statistics |

---

## 🏗️ Project Structure

```
OdinCrypto/
├── app.py                          # Flask app entry point
├── config.py                       # Configuration
├── requirements.txt
├── backend/
│   ├── api/routes.py               # All Flask routes
│   ├── authentication/auth_service.py  # Login, register, JWT
│   ├── crypto/crypto_service.py    # RSA, AES, Hybrid, Hashing, Signatures
│   ├── database/db.py              # SQLAlchemy setup
│   └── models/models.py            # Database models
├── frontend/
│   ├── templates/                  # Jinja2 HTML templates
│   └── static/
│       ├── css/main.css            # Dark theme design system
│       └── js/main.js              # Client-side JS
├── uploads/                        # Uploaded files
├── encrypted/                      # Encrypted outputs
├── decrypted/                      # Decrypted outputs
├── keys/                           # Key storage
└── database/                       # SQLite DB
```

---

## 🔐 Security Features

- **bcrypt** password hashing
- **AES-256-CBC** with PBKDF2-SHA256 key derivation (200,000 iterations)
- **RSA-OAEP** with SHA-256
- **RSA-PSS** digital signatures
- **CSRF protection** via Flask-WTF
- **Secure session cookies** (HttpOnly, SameSite)
- **SQL injection prevention** via SQLAlchemy ORM
- **Input validation** on all forms
- **No plaintext credentials** stored anywhere

---

## 🎨 UI Theme

Dark enterprise theme inspired by GitHub, Bitwarden, and Cloudflare Zero Trust.

- Colors: Black, Dark Gray, Indigo (#6366f1), Purple (#a855f7)
- Responsive sidebar layout
- Animated score ring
- Drag-and-drop file upload
- Real-time password strength meter

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask 3.0 |
| Database | SQLite (PostgreSQL-ready) |
| Crypto | `cryptography`, `pycryptodome` |
| Auth | Flask-Bcrypt, Flask-JWT-Extended |
| QR Codes | `qrcode[pil]` |
| Frontend | Bootstrap 5, Bootstrap Icons |
