# 🔐 Asymmetric Encryption Dashboard

A comprehensive, user-friendly web-based dashboard for encrypting and decrypting data using various asymmetric cryptography algorithms.

## Features

### ✨ Supported Algorithms

1. **RSA (Rivest-Shamir-Adleman)**
   - Most widely used asymmetric cryptosystem
   - Configurable key sizes (1024-4096 bits)
   - PKCS1-OAEP padding for security
   - Perfect for TLS/SSL, digital signatures

2. **ECC (Elliptic Curve Cryptography)**
   - Modern encryption based on elliptic curves
   - Multiple curve support (P-256, P-384, P-521)
   - Superior key size to security ratio
   - Used in Bitcoin, HTTPS, and mobile devices

3. **ElGamal**
   - Based on Diffie-Hellman key exchange
   - Educational and historical significance
   - Suitable for learning cryptography concepts

4. **Rabin Cryptosystem**
   - Security equivalent to integer factorization
   - Theoretical and research applications
   - Demonstrative implementation

### 🎯 Main Features

- **Encrypt/Decrypt Tab**: Encrypt plaintext and decrypt ciphertext
- **Key Management Tab**: Generate, display, and download keys
- **Educational Resources**: Learn about each algorithm with detailed explanations
- **Base64 Encoding**: Safe transmission of binary ciphertext
- **Download Support**: Export keys and ciphertexts
- **Real-time Processing**: Instant encryption/decryption
- **Error Handling**: Comprehensive error messages

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Navigate to the project directory:**
```bash
cd d:\project\DLK\Training\Asymmetric_Encryption_Dashboard
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Usage

### Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your default browser at `http://localhost:8501`

### Basic Workflow

#### 1. Generate Keys
1. Go to the **Key Management** tab
2. Select your desired algorithm
3. Adjust key size if needed
4. Click "Generate Keys"
5. Download and save both public and private keys

#### 2. Encrypt a Message
1. Go to the **Encrypt/Decrypt** tab
2. Select the same algorithm used for key generation
3. Paste your public key
4. Enter the plaintext message
5. Click "Encrypt"
6. Copy or download the ciphertext

#### 3. Decrypt a Message
1. In the Decrypt section
2. Select the same algorithm
3. Paste your private key
4. Paste the ciphertext
5. Click "Decrypt"
6. View the recovered plaintext

## Algorithm Details

### RSA
- **Key Size**: 2048-4096 bits (configurable)
- **Complexity**: Based on difficulty of factoring large numbers
- **Use**: General-purpose encryption, digital signatures
- **Speed**: Moderate

### ECC
- **Key Size**: 256-521 bits (equivalent to 2048-15360 bits RSA)
- **Complexity**: Based on elliptic curve discrete logarithm problem
- **Use**: Modern systems, mobile, blockchain
- **Speed**: Fast

### ElGamal
- **Key Size**: 1024+ bits
- **Complexity**: Based on discrete logarithm problem
- **Use**: Educational and historical purposes
- **Speed**: Slow

### Rabin
- **Key Size**: 1024-2048 bits
- **Complexity**: Based on integer factorization (equivalent to RSA)
- **Use**: Theoretical research
- **Speed**: Moderate

## Project Structure

```
Asymmetric_Encryption_Dashboard/
├── app.py                      # Main Streamlit application
├── encryption_algorithms.py    # Encryption algorithm implementations
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Dependencies

- **streamlit**: Web application framework
- **pycryptodome**: Cryptographic primitives (RSA, ECC, ElGamal)
- **cryptography**: Modern cryptography library
- **pyopenssl**: OpenSSL bindings
- **numpy**: Numerical operations
- **pillow**: Image processing

## Security Notes

### ⚠️ Important Disclaimers

1. **Educational Purpose**: This application is designed for educational and demonstration purposes.

2. **Production Use**: For production use, always use established cryptographic libraries and follow security best practices.

3. **Key Protection**: 
   - Never share your private key
   - Store private keys securely
   - Use hardware security modules (HSMs) for critical applications

4. **Plaintext Size Limitations**:
   - RSA can encrypt up to (key_size - padding_size) bytes
   - For longer messages, use hybrid encryption (RSA + AES)

5. **Randomness**: Uses Python's `Crypto.Random` for cryptographic randomness

## Example Usage

### Python Script Usage

```python
from encryption_algorithms import RSAEncryption

# Generate keys
public_key, private_key = RSAEncryption.generate_keys(2048)

# Encrypt
plaintext = "Hello, World!"
ciphertext = RSAEncryption.encrypt(plaintext, public_key)

# Decrypt
decrypted = RSAEncryption.decrypt(ciphertext, private_key)
print(decrypted)  # Output: Hello, World!
```

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'streamlit'"
**Solution**: Install requirements
```bash
pip install -r requirements.txt
```

### Issue: Encryption/Decryption fails with invalid keys
**Solution**: Ensure you're using the correct key format and matching algorithm

### Issue: "ValueError: Unknown algorithm"
**Solution**: Select from the available algorithms: RSA, ECC, ElGamal, Rabin

## Learning Resources

### Online References
- [NIST Cryptographic Toolkit](https://csrc.nist.gov/)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [Cryptography Stack Exchange](https://crypto.stackexchange.com/)

### Books
- "Understanding Cryptography" by Paar & Pelzl
- "Introduction to Modern Cryptography" by Katz & Lindell

## Future Enhancements

- [ ] Add digital signature support
- [ ] Implement hybrid encryption (RSA + AES)
- [ ] Add key validation and verification
- [ ] Support for larger plaintext with chunking
- [ ] Export/import keys in different formats (JWK, PKCS#12)
- [ ] Performance benchmarking tools
- [ ] Multi-language support
- [ ] Mobile app version

## License

This project is provided for educational purposes. Use at your own risk.

## Disclaimer

This is an educational tool. For production encryption needs, use well-established cryptographic libraries and follow industry best practices.

## Support

For issues or questions:
1. Check the README and algorithm documentation
2. Review the error messages in the dashboard
3. Test with the learning resources provided

---

**Last Updated**: 2024  
**Version**: 1.0.0  
**Author**: Cryptography Learning Platform
