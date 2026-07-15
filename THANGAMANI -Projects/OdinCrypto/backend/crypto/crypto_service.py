"""
OdinCrypto - Crypto Service (cryptography stdlib + PIL QR, no pycryptodome)
"""
import os, base64, hashlib, json, secrets, string
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

class CryptoService:

    # ─── RSA KEYS ────────────────────────────────────────────────────────────

    @staticmethod
    def generate_rsa_keypair(key_size=2048):
        priv = rsa.generate_private_key(public_exponent=65537, key_size=key_size, backend=default_backend())
        pub  = priv.public_key()
        priv_pem = priv.private_bytes(serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
        pub_pem  = pub.public_bytes(serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        return {'private_key': priv_pem, 'public_key': pub_pem}

    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt,
                         iterations=200000, backend=default_backend())
        return kdf.derive(password.encode())

    @staticmethod
    def encrypt_private_key_with_password(priv_pem: str, password: str) -> str:
        salt = os.urandom(16); iv = os.urandom(16)
        key  = CryptoService._derive_key(password, salt)
        c    = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        e    = c.encryptor()
        data = priv_pem.encode()
        pad  = 16 - len(data) % 16
        data += bytes([pad]*pad)
        ct   = e.update(data) + e.finalize()
        return base64.b64encode(salt+iv+ct).decode()

    @staticmethod
    def decrypt_private_key_with_password(enc_b64: str, password: str) -> str:
        raw  = base64.b64decode(enc_b64)
        salt, iv, ct = raw[:16], raw[16:32], raw[32:]
        key  = CryptoService._derive_key(password, salt)
        c    = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        d    = c.decryptor()
        data = d.update(ct) + d.finalize()
        return data[:-data[-1]].decode()

    # ─── AES ─────────────────────────────────────────────────────────────────

    @staticmethod
    def aes_encrypt(data: bytes, password: str) -> dict:
        salt = os.urandom(16); iv = os.urandom(16)
        key  = CryptoService._derive_key(password, salt)
        c    = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        e    = c.encryptor()
        pad  = 16 - len(data) % 16
        data += bytes([pad]*pad)
        ct   = e.update(data) + e.finalize()
        return {'ciphertext': base64.b64encode(ct).decode(),
                'salt': base64.b64encode(salt).decode(),
                'iv':   base64.b64encode(iv).decode()}

    @staticmethod
    def aes_decrypt(ct_b64: str, salt_b64: str, iv_b64: str, password: str) -> bytes:
        salt = base64.b64decode(salt_b64)
        iv   = base64.b64decode(iv_b64)
        ct   = base64.b64decode(ct_b64)
        key  = CryptoService._derive_key(password, salt)
        c    = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        d    = c.decryptor()
        data = d.update(ct) + d.finalize()
        return data[:-data[-1]]

    # ─── RSA ─────────────────────────────────────────────────────────────────

    @staticmethod
    def rsa_encrypt(data: bytes, pub_pem: str) -> str:
        pub = serialization.load_pem_public_key(pub_pem.encode(), backend=default_backend())
        ct  = pub.encrypt(data, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),
                                              algorithm=hashes.SHA256(), label=None))
        return base64.b64encode(ct).decode()

    @staticmethod
    def rsa_decrypt(ct_b64: str, priv_pem: str) -> bytes:
        priv = serialization.load_pem_private_key(priv_pem.encode(), password=None, backend=default_backend())
        return priv.decrypt(base64.b64decode(ct_b64),
                            padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),
                                         algorithm=hashes.SHA256(), label=None))

    # ─── HYBRID ──────────────────────────────────────────────────────────────

    @staticmethod
    def hybrid_encrypt(data: bytes, pub_pem: str) -> dict:
        aes_key = os.urandom(32); iv = os.urandom(16)
        c = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        e = c.encryptor()
        pad = 16 - len(data) % 16
        enc_data = e.update(data + bytes([pad]*pad)) + e.finalize()
        pub = serialization.load_pem_public_key(pub_pem.encode(), backend=default_backend())
        enc_key = pub.encrypt(aes_key, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),
                                                      algorithm=hashes.SHA256(), label=None))
        return {'encrypted_data': base64.b64encode(enc_data).decode(),
                'encrypted_aes_key': base64.b64encode(enc_key).decode(),
                'iv': base64.b64encode(iv).decode(),
                'data_hash': hashlib.sha256(data).hexdigest(),
                'algorithm': 'AES-256-CBC + RSA-OAEP',
                'timestamp': datetime.utcnow().isoformat()}

    @staticmethod
    def hybrid_decrypt(pkg: dict, priv_pem: str) -> bytes:
        priv = serialization.load_pem_private_key(priv_pem.encode(), password=None, backend=default_backend())
        aes_key = priv.decrypt(base64.b64decode(pkg['encrypted_aes_key']),
                               padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),
                                            algorithm=hashes.SHA256(), label=None))
        iv = base64.b64decode(pkg['iv']); ct = base64.b64decode(pkg['encrypted_data'])
        c  = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        d  = c.decryptor()
        data = d.update(ct) + d.finalize()
        result = data[:-data[-1]]
        if hashlib.sha256(result).hexdigest() != pkg.get('data_hash'):
            raise ValueError("Integrity check failed — data hash mismatch!")
        return result

    # ─── SIGNATURES ──────────────────────────────────────────────────────────

    @staticmethod
    def sign_data(data: bytes, priv_pem: str) -> str:
        priv = serialization.load_pem_private_key(priv_pem.encode(), password=None, backend=default_backend())
        sig  = priv.sign(data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                            salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
        return base64.b64encode(sig).decode()

    @staticmethod
    def verify_signature(data: bytes, sig_b64: str, pub_pem: str) -> bool:
        try:
            pub = serialization.load_pem_public_key(pub_pem.encode(), backend=default_backend())
            pub.verify(base64.b64decode(sig_b64), data,
                       padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                       hashes.SHA256())
            return True
        except Exception:
            return False

    # ─── HASHING ─────────────────────────────────────────────────────────────

    @staticmethod
    def compute_hash(data: bytes, algorithm='sha256') -> str:
        algos = {'sha256': hashlib.sha256, 'sha512': hashlib.sha512, 'blake2b': hashlib.blake2b}
        fn = algos.get(algorithm)
        if not fn: raise ValueError(f"Unknown algorithm: {algorithm}")
        return fn(data).hexdigest()

    # ─── QR CODE (PIL only, no qrcode lib) ───────────────────────────────────

    @staticmethod
    def make_qr(data: str):
        """Generate a simple QR-style image using PIL showing the public key text."""
        from PIL import Image, ImageDraw, ImageFont
        img  = Image.new('RGB', (600, 600), color=(10, 11, 15))
        draw = ImageDraw.Draw(img)
        # Draw border
        draw.rectangle([10,10,589,589], outline=(99,102,241), width=3)
        # Title
        draw.rectangle([30,30,570,70], fill=(22,24,31))
        draw.text((300,50), "OdinCrypto — Public Key", fill=(99,102,241), anchor='mm')
        # Draw key text chunked
        lines = []
        for i in range(0, len(data), 55):
            lines.append(data[i:i+55])
        y = 90
        for line in lines[:18]:
            draw.text((30, y), line, fill=(148,163,184))
            y += 28
        if len(lines) > 18:
            draw.text((30, y), '... (truncated — download full key)', fill=(71,85,105))
        # Footer
        draw.rectangle([30,540,570,570], fill=(22,24,31))
        draw.text((300,555), "Scan or copy public key above", fill=(71,85,105), anchor='mm')
        return img

    # ─── PASSWORD GENERATOR ──────────────────────────────────────────────────

    @staticmethod
    def generate_password(length=16, use_upper=True, use_lower=True, use_digits=True, use_symbols=True) -> str:
        chars = ''; required = []
        if use_upper:   chars += string.ascii_uppercase;  required.append(secrets.choice(string.ascii_uppercase))
        if use_lower:   chars += string.ascii_lowercase;  required.append(secrets.choice(string.ascii_lowercase))
        if use_digits:  chars += string.digits;           required.append(secrets.choice(string.digits))
        if use_symbols:
            sym = '!@#$%^&*()_+-=[]{}|;:,.<>?'
            chars += sym; required.append(secrets.choice(sym))
        if not chars: chars = string.ascii_letters + string.digits
        rest = [secrets.choice(chars) for _ in range(length - len(required))]
        pw   = required + rest
        secrets.SystemRandom().shuffle(pw)
        return ''.join(pw)

    @staticmethod
    def generate_passphrase(word_count=4) -> str:
        words = ['apple','bridge','castle','dragon','eagle','forest','galaxy','harbor','island',
                 'jungle','knight','lantern','mountain','nebula','ocean','phoenix','quantum',
                 'river','shadow','thunder','umbrella','valley','winter','zenith','aurora','cipher']
        return '-'.join(secrets.choice(words) for _ in range(word_count)) + f'-{secrets.randbelow(9999)}'

    @staticmethod
    def generate_pin(length=6) -> str:
        return ''.join(str(secrets.randbelow(10)) for _ in range(length))

    # ─── VAULT ITEM ENCRYPTION ───────────────────────────────────────────────

    @staticmethod
    def encrypt_vault_item(data: str, master_key: str) -> str:
        return json.dumps(CryptoService.aes_encrypt(data.encode(), master_key))

    @staticmethod
    def decrypt_vault_item(enc_json: str, master_key: str) -> str:
        pkg = json.loads(enc_json)
        return CryptoService.aes_decrypt(pkg['ciphertext'], pkg['salt'], pkg['iv'], master_key).decode()
