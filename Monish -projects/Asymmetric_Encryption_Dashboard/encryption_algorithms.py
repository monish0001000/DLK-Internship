"""
Asymmetric Encryption Algorithms Module
Supports RSA, ECC, ElGamal, and Rabin encryption
"""

import os
import json
import base64
from typing import Tuple, Dict, Any
from Crypto.PublicKey import RSA, ECC
from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
from Crypto.Random import get_random_bytes
from Crypto.Util.number import getPrime, inverse, GCD
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


class RSAEncryption:
    """RSA Encryption/Decryption"""
    
    @staticmethod
    def generate_keys(key_size: int = 2048) -> Tuple[str, str]:
        """Generate RSA key pair"""
        key = RSA.generate(key_size)
        public_key = key.publickey().export_key()
        private_key = key.export_key()
        return public_key.decode(), private_key.decode()
    
    @staticmethod
    def encrypt(plaintext: str, public_key_str: str) -> str:
        """Encrypt plaintext using RSA public key"""
        try:
            public_key = RSA.import_key(public_key_str)
            cipher = PKCS1_OAEP.new(public_key)
            ciphertext = cipher.encrypt(plaintext.encode())
            return base64.b64encode(ciphertext).decode()
        except Exception as e:
            raise Exception(f"RSA Encryption Error: {str(e)}")
    
    @staticmethod
    def decrypt(ciphertext_b64: str, private_key_str: str) -> str:
        """Decrypt ciphertext using RSA private key"""
        try:
            private_key = RSA.import_key(private_key_str)
            cipher = PKCS1_OAEP.new(private_key)
            ciphertext = base64.b64decode(ciphertext_b64)
            plaintext = cipher.decrypt(ciphertext)
            return plaintext.decode()
        except Exception as e:
            raise Exception(f"RSA Decryption Error: {str(e)}")


class ECCEncryption:
    """Elliptic Curve Cryptography Encryption/Decryption"""
    
    @staticmethod
    def generate_keys(curve: str = "P-256") -> Tuple[str, str]:
        """Generate ECC key pair"""
        if curve == "P-256":
            curve_obj = ec.SECP256R1()
        elif curve == "P-384":
            curve_obj = ec.SECP384R1()
        elif curve == "P-521":
            curve_obj = ec.SECP521R1()
        else:
            curve_obj = ec.SECP256R1()
        
        private_key = ec.generate_private_key(curve_obj, default_backend())
        public_key = private_key.public_key()
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return public_pem.decode(), private_pem.decode()
    
    @staticmethod
    def encrypt(plaintext: str, public_key_str: str) -> str:
        """Encrypt plaintext using ECC public key (ECIES-like)"""
        try:
            public_key = serialization.load_pem_public_key(
                public_key_str.encode(), backend=default_backend()
            )
            
            # For demonstration, using symmetric encryption with ECC
            # Generate ephemeral key pair
            ephemeral_private = ec.generate_private_key(
                ec.SECP256R1(), default_backend()
            )
            ephemeral_public = ephemeral_private.public_key()
            
            # Simple XOR-based encryption for demo (in production, use proper ECIES)
            plaintext_bytes = plaintext.encode()
            key_material = os.urandom(len(plaintext_bytes))
            ciphertext = bytes(a ^ b for a, b in zip(plaintext_bytes, key_material))
            
            ephemeral_public_bytes = ephemeral_public.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            result = base64.b64encode(ephemeral_public_bytes + key_material + ciphertext).decode()
            return result
        except Exception as e:
            raise Exception(f"ECC Encryption Error: {str(e)}")
    
    @staticmethod
    def decrypt(ciphertext_b64: str, private_key_str: str) -> str:
        """Decrypt ciphertext using ECC private key"""
        try:
            private_key = serialization.load_pem_private_key(
                private_key_str.encode(), password=None, backend=default_backend()
            )
            
            encrypted_data = base64.b64decode(ciphertext_b64)
            # Extract components (simplified for demo)
            key_material = encrypted_data[:32]  # Assuming 32 bytes
            ciphertext = encrypted_data[32:]
            
            plaintext_bytes = bytes(a ^ b for a, b in zip(ciphertext, key_material))
            return plaintext_bytes.decode()
        except Exception as e:
            raise Exception(f"ECC Decryption Error: {str(e)}")


class ElGamalEncryption:
    """ElGamal Encryption/Decryption"""
    
    @staticmethod
    def generate_keys(key_size: int = 1024) -> Tuple[str, str]:
        """Generate ElGamal key pair"""
        p = getPrime(key_size)
        g = 2
        x = int.from_bytes(get_random_bytes(key_size // 8), 'big') % (p - 1)
        h = pow(g, x, p)
        
        public_key = {"p": p, "g": g, "h": h}
        private_key = {"p": p, "g": g, "h": h, "x": x}
        
        return json.dumps(public_key), json.dumps(private_key)
    
    @staticmethod
    def encrypt(plaintext: str, public_key_str: str) -> str:
        """Encrypt plaintext using ElGamal public key"""
        try:
            public_key = json.loads(public_key_str)
            p, g, h = public_key["p"], public_key["g"], public_key["h"]
            
            plaintext_int = int.from_bytes(plaintext.encode(), 'big')
            y = int.from_bytes(get_random_bytes(16), 'big') % (p - 1)
            c1 = pow(g, y, p)
            c2 = (plaintext_int * pow(h, y, p)) % p
            
            ciphertext = json.dumps({"c1": c1, "c2": c2})
            return base64.b64encode(ciphertext.encode()).decode()
        except Exception as e:
            raise Exception(f"ElGamal Encryption Error: {str(e)}")
    
    @staticmethod
    def decrypt(ciphertext_b64: str, private_key_str: str) -> str:
        """Decrypt ciphertext using ElGamal private key"""
        try:
            private_key = json.loads(private_key_str)
            p, x = private_key["p"], private_key["x"]
            
            ciphertext = json.loads(base64.b64decode(ciphertext_b64))
            c1, c2 = ciphertext["c1"], ciphertext["c2"]
            
            plaintext_int = (c2 * pow(c1, p - 1 - x, p)) % p
            plaintext_bytes = plaintext_int.to_bytes((plaintext_int.bit_length() + 7) // 8, 'big')
            return plaintext_bytes.decode('utf-8', errors='ignore')
        except Exception as e:
            raise Exception(f"ElGamal Decryption Error: {str(e)}")


class RabinEncryption:
    """Rabin Encryption/Decryption"""
    
    @staticmethod
    def generate_keys(key_size: int = 1024) -> Tuple[str, str]:
        """Generate Rabin key pair"""
        p = getPrime(key_size // 2)
        q = getPrime(key_size // 2)
        
        # Ensure p ≡ q ≡ 3 (mod 4)
        while p % 4 != 3:
            p = getPrime(key_size // 2)
        while q % 4 != 3:
            q = getPrime(key_size // 2)
        
        n = p * q
        
        public_key = json.dumps({"n": n})
        private_key = json.dumps({"p": p, "q": q, "n": n})
        
        return public_key, private_key
    
    @staticmethod
    def encrypt(plaintext: str, public_key_str: str) -> str:
        """Encrypt plaintext using Rabin public key"""
        try:
            public_key = json.loads(public_key_str)
            n = public_key["n"]
            
            plaintext_int = int.from_bytes(plaintext.encode(), 'big')
            plaintext_int = plaintext_int % n
            ciphertext = (plaintext_int * plaintext_int) % n
            
            return base64.b64encode(json.dumps({"c": ciphertext}).encode()).decode()
        except Exception as e:
            raise Exception(f"Rabin Encryption Error: {str(e)}")
    
    @staticmethod
    def decrypt(ciphertext_b64: str, private_key_str: str) -> str:
        """Decrypt ciphertext using Rabin private key"""
        try:
            private_key = json.loads(private_key_str)
            p, q, n = private_key["p"], private_key["q"], private_key["n"]
            
            ciphertext_data = json.loads(base64.b64decode(ciphertext_b64))
            c = ciphertext_data["c"]
            
            # Find square roots mod p and q
            mp = pow(c, (p + 1) // 4, p)
            mq = pow(c, (q + 1) // 4, q)
            
            # Use CRT to combine
            invq = inverse(q, p)
            x1 = (invq * q * mp + (1 - invq * q) * p * mq) % n
            x2 = n - x1
            
            # Try to decode - return the one that makes sense
            for x in [x1, x2]:
                try:
                    result = x.to_bytes((x.bit_length() + 7) // 8, 'big')
                    decoded = result.decode('utf-8', errors='ignore')
                    if decoded and any(c.isprintable() for c in decoded):
                        return decoded
                except:
                    pass
            
            return x1.to_bytes((x1.bit_length() + 7) // 8, 'big').decode('utf-8', errors='ignore')
        except Exception as e:
            raise Exception(f"Rabin Decryption Error: {str(e)}")


class EncryptionFactory:
    """Factory class for encryption algorithms"""
    
    ALGORITHMS = {
        "RSA": RSAEncryption,
        "ECC": ECCEncryption,
        "ElGamal": ElGamalEncryption,
        "Rabin": RabinEncryption
    }
    
    @staticmethod
    def get_algorithm(algo_name: str):
        """Get encryption algorithm instance"""
        if algo_name not in EncryptionFactory.ALGORITHMS:
            raise ValueError(f"Unknown algorithm: {algo_name}")
        return EncryptionFactory.ALGORITHMS[algo_name]
    
    @staticmethod
    def list_algorithms() -> list:
        """List all available algorithms"""
        return list(EncryptionFactory.ALGORITHMS.keys())
