"""
Asymmetric Encryption Dashboard
A comprehensive web-based dashboard for encryption and decryption
"""

import streamlit as st
import json
from encryption_algorithms import EncryptionFactory, RSAEncryption, ECCEncryption, ElGamalEncryption, RabinEncryption

# Page configuration
st.set_page_config(
    page_title="🔐 Asymmetric Encryption Dashboard",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .main {
            padding-top: 2rem;
        }
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 16px;
            font-weight: 600;
        }
        .algorithm-info {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .rsa-info {
            background-color: #FFE5E5;
            border-left: 4px solid #FF6B6B;
        }
        .ecc-info {
            background-color: #E5F3FF;
            border-left: 4px solid #3399FF;
        }
        .elgamal-info {
            background-color: #E5FFE5;
            border-left: 4px solid #4CAF50;
        }
        .rabin-info {
            background-color: #FFE5F5;
            border-left: 4px solid #FF1493;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🔐 Encryption Dashboard")
st.sidebar.markdown("---")

# Initialize session state
if 'generated_keys' not in st.session_state:
    st.session_state.generated_keys = {}

def show_algorithm_info(algorithm: str):
    """Display algorithm information"""
    info_dict = {
        "RSA": {
            "name": "RSA (Rivest-Shamir-Adleman)",
            "description": "One of the most widely used asymmetric cryptosystems.",
            "use_cases": "Digital signatures, SSL/TLS, key exchange",
            "security": "Based on difficulty of factoring large integers",
            "info_class": "rsa-info"
        },
        "ECC": {
            "name": "ECC (Elliptic Curve Cryptography)",
            "description": "Modern encryption using elliptic curve mathematics.",
            "use_cases": "HTTPS, Bitcoin, mobile devices",
            "security": "Based on elliptic curve discrete logarithm problem",
            "info_class": "ecc-info"
        },
        "ElGamal": {
            "name": "ElGamal Encryption",
            "description": "Asymmetric encryption based on Diffie-Hellman key exchange.",
            "use_cases": "Historical importance, educational purposes",
            "security": "Based on discrete logarithm problem",
            "info_class": "elgamal-info"
        },
        "Rabin": {
            "name": "Rabin Cryptosystem",
            "description": "Encryption system whose security is equivalent to factoring.",
            "use_cases": "Educational, theoretical cryptography",
            "security": "Based on integer factorization problem",
            "info_class": "rabin-info"
        }
    }
    
    info = info_dict.get(algorithm, {})
    html = f"""
    <div class="algorithm-info {info.get('info_class', '')}">
        <h3>{info.get('name', algorithm)}</h3>
        <p><strong>Description:</strong> {info.get('description', '')}</p>
        <p><strong>Use Cases:</strong> {info.get('use_cases', '')}</p>
        <p><strong>Security Basis:</strong> {info.get('security', '')}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# Main header
st.title("🔐 Asymmetric Encryption Dashboard")
st.markdown("Encrypt and decrypt data using various asymmetric cryptography algorithms")
st.markdown("---")

# Main tabs
tab1, tab2, tab3 = st.tabs(["🚀 Encrypt/Decrypt", "🔑 Key Management", "📚 Learn More"])

with tab1:
    st.header("Encrypt & Decrypt")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Encryption")
        
        # Algorithm selection
        algorithm = st.selectbox(
            "Select Algorithm",
            EncryptionFactory.list_algorithms(),
            key="encrypt_algo"
        )
        
        show_algorithm_info(algorithm)
        
        # Public key input
        public_key = st.text_area(
            "Public Key",
            key=f"public_key_{algorithm}",
            height=150,
            help="Paste your public key here"
        )
        
        # Plaintext input
        plaintext = st.text_area(
            "Plaintext",
            placeholder="Enter the message to encrypt...",
            height=100,
            key=f"plaintext_{algorithm}"
        )
        
        # Encrypt button
        if st.button("🔒 Encrypt", key=f"encrypt_btn_{algorithm}"):
            if not public_key or not plaintext:
                st.error("Please provide both public key and plaintext!")
            else:
                try:
                    algo_class = EncryptionFactory.get_algorithm(algorithm)
                    ciphertext = algo_class.encrypt(plaintext, public_key)
                    st.session_state.ciphertext = ciphertext
                    st.success("✅ Encryption successful!")
                    st.text_area(
                        "Ciphertext (Base64 encoded)",
                        value=ciphertext,
                        height=150,
                        disabled=True
                    )
                    st.download_button(
                        "📥 Download Ciphertext",
                        data=ciphertext,
                        file_name=f"ciphertext_{algorithm}.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"❌ Encryption failed: {str(e)}")
    
    with col2:
        st.subheader("Decryption")
        
        # Algorithm selection for decryption
        dec_algorithm = st.selectbox(
            "Select Algorithm",
            EncryptionFactory.list_algorithms(),
            key="decrypt_algo"
        )
        
        # Private key input
        private_key = st.text_area(
            "Private Key",
            key=f"private_key_{dec_algorithm}",
            height=150,
            help="Paste your private key here"
        )
        
        # Ciphertext input
        ciphertext = st.text_area(
            "Ciphertext (Base64 encoded)",
            placeholder="Enter the encrypted message...",
            height=100,
            key=f"ciphertext_{dec_algorithm}"
        )
        
        # Decrypt button
        if st.button("🔓 Decrypt", key=f"decrypt_btn_{dec_algorithm}"):
            if not private_key or not ciphertext:
                st.error("Please provide both private key and ciphertext!")
            else:
                try:
                    algo_class = EncryptionFactory.get_algorithm(dec_algorithm)
                    plaintext_decrypted = algo_class.decrypt(ciphertext, private_key)
                    st.success("✅ Decryption successful!")
                    st.text_area(
                        "Decrypted Plaintext",
                        value=plaintext_decrypted,
                        height=150,
                        disabled=True
                    )
                except Exception as e:
                    st.error(f"❌ Decryption failed: {str(e)}")

with tab2:
    st.header("Key Management")
    
    # Key generation section
    st.subheader("Generate Keys")
    
    algo_for_keygen = st.selectbox(
        "Select Algorithm for Key Generation",
        EncryptionFactory.list_algorithms(),
        key="keygen_algo"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if algo_for_keygen == "RSA":
            key_size = st.slider("Key Size (bits)", 1024, 4096, 2048, 512)
        elif algo_for_keygen == "ElGamal":
            key_size = st.slider("Key Size (bits)", 512, 2048, 1024, 256)
        elif algo_for_keygen == "Rabin":
            key_size = st.slider("Key Size (bits)", 512, 2048, 1024, 256)
        else:
            key_size = 256  # ECC
    
    with col2:
        if st.button("🔑 Generate Keys", key=f"gen_btn_{algo_for_keygen}"):
            with st.spinner(f"Generating {algo_for_keygen} keys..."):
                try:
                    algo_class = EncryptionFactory.get_algorithm(algo_for_keygen)
                    
                    if algo_for_keygen == "RSA":
                        public_key, private_key = algo_class.generate_keys(key_size)
                    elif algo_for_keygen == "ECC":
                        public_key, private_key = algo_class.generate_keys()
                    else:
                        public_key, private_key = algo_class.generate_keys(key_size)
                    
                    st.session_state.generated_keys[algo_for_keygen] = {
                        "public": public_key,
                        "private": private_key
                    }
                    st.success("✅ Keys generated successfully!")
                except Exception as e:
                    st.error(f"❌ Key generation failed: {str(e)}")
    
    # Display generated keys
    if algo_for_keygen in st.session_state.generated_keys:
        st.divider()
        st.subheader(f"{algo_for_keygen} Keys")
        
        keys = st.session_state.generated_keys[algo_for_keygen]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_area(
                "Public Key",
                value=keys["public"],
                height=200,
                disabled=True,
                key=f"display_pub_{algo_for_keygen}"
            )
            st.download_button(
                "📥 Download Public Key",
                data=keys["public"],
                file_name=f"public_key_{algo_for_keygen}.pem",
                mime="text/plain",
                key=f"download_pub_{algo_for_keygen}"
            )
        
        with col2:
            st.text_area(
                "Private Key",
                value=keys["private"],
                height=200,
                disabled=True,
                key=f"display_priv_{algo_for_keygen}"
            )
            st.download_button(
                "📥 Download Private Key",
                data=keys["private"],
                file_name=f"private_key_{algo_for_keygen}.pem",
                mime="text/plain",
                key=f"download_priv_{algo_for_keygen}"
            )

with tab3:
    st.header("📚 Learn More About Asymmetric Encryption")
    
    st.markdown("""
    ## What is Asymmetric Encryption?
    
    Asymmetric encryption (public-key cryptography) uses a pair of keys:
    - **Public Key**: Can be shared with anyone, used for encryption
    - **Private Key**: Must be kept secret, used for decryption
    
    ### Key Advantages:
    - ✅ No need for secure key exchange
    - ✅ Digital signatures and authentication
    - ✅ Scalable for many-to-one communication
    - ✅ Foundation of modern internet security
    
    ### Key Disadvantages:
    - ❌ Slower than symmetric encryption
    - ❌ Requires larger key sizes for equivalent security
    - ❌ More computationally intensive
    
    ---
    """)
    
    # Algorithm details
    for algo in EncryptionFactory.list_algorithms():
        with st.expander(f"📖 Learn about {algo}", expanded=False):
            show_algorithm_info(algo)
            
            details = {
                "RSA": """
                **RSA Algorithm Overview:**
                
                1. **Key Generation:**
                   - Select two large prime numbers p and q
                   - Calculate n = p × q
                   - Calculate φ(n) = (p-1) × (q-1)
                   - Select e such that gcd(e, φ(n)) = 1
                   - Calculate d such that (e × d) mod φ(n) = 1
                   - Public key: (e, n)
                   - Private key: (d, n)
                
                2. **Encryption:** C = M^e mod n
                3. **Decryption:** M = C^d mod n
                
                **Security:** Based on the computational difficulty of factoring large integers.
                """,
                "ECC": """
                **Elliptic Curve Cryptography Overview:**
                
                1. **Uses elliptic curves:** y² = x³ + ax + b
                2. **Key Generation:**
                   - Select a random private key d
                   - Public key Q = d × G (G is generator point)
                
                3. **Advantages:**
                   - Shorter keys for equivalent security (256-bit ECC ≈ 3072-bit RSA)
                   - Faster operations
                   - Lower bandwidth requirements
                
                **Common Curves:** SECP256R1, SECP384R1, SECP521R1
                """,
                "ElGamal": """
                **ElGamal Encryption Overview:**
                
                1. **Key Generation:**
                   - Select large prime p and generator g
                   - Private key: x
                   - Public key: h = g^x mod p
                
                2. **Encryption:**
                   - Generate random y
                   - C1 = g^y mod p
                   - C2 = M × h^y mod p
                
                3. **Decryption:**
                   - M = C2 × (C1^x)^(-1) mod p
                
                **Security:** Based on discrete logarithm problem.
                """,
                "Rabin": """
                **Rabin Cryptosystem Overview:**
                
                1. **Key Generation:**
                   - Select two large primes p and q where p ≡ q ≡ 3 (mod 4)
                   - Public key: n = p × q
                   - Private key: p and q
                
                2. **Encryption:**
                   - C = M² mod n
                
                3. **Decryption:**
                   - Uses Chinese Remainder Theorem
                   - Produces 4 possible plaintexts
                
                **Security:** As hard as integer factorization.
                """
            }
            
            st.markdown(details.get(algo, ""))
    
    st.divider()
    st.markdown("""
    ### Use Cases by Algorithm:
    
    | Algorithm | Best For | Key Size | Speed |
    |-----------|----------|----------|-------|
    | RSA | General purpose encryption, TLS | 2048-4096 bits | Moderate |
    | ECC | Modern systems, mobile, blockchain | 256-521 bits | Fast |
    | ElGamal | Historical, educational | 1024+ bits | Slow |
    | Rabin | Theoretical, research | 1024-2048 bits | Moderate |
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; margin-top: 2rem;">
    <p>🔐 Asymmetric Encryption Dashboard | Built with Streamlit</p>
    <p>For educational and demonstration purposes</p>
</div>
""", unsafe_allow_html=True)
