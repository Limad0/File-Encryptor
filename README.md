# File-Encryptor
A file encryptor that was made specifically to encrypt and decrypt your files
File Encryptor
![Version](https://img.shields.io/badge/Version-2.1-blue)
![Python](https://img.shields.io/badge/Python-3.7%2B-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Encryption](https://img.shields.io/badge/Encryption-AES--256-brightgreen)
File encryption tool with graphical interface - AES-256 encryption/decryption with advanced security features.

🚀 Features
AES-256 encryption

Two operation modes:

🔒 File replacement mode - Encrypt/decrypt files in place

📋 Copy mode - Create encrypted/decrypted copies

PBKDF2 key derivation - Secure password-based key generation

Graphical user interface - User-friendly Tkinter interface

Progress tracking - Real-time progress bar and status updates

Comprehensive logging - Detailed operation log with export capability

Multiple padding schemes - PKCS7, ISO7816, x923 support

Adjustable security - Configurable key derivation iterations

Cross-platform - Works on Windows, macOS, and Linux

Prerequisites
Python 3.7 or higher

pip package manager

STEP 1: clone or download
git clone https://github.com/yourusername/file-encryptor-pro.git
cd file-encryptor-pro

STEP 2: Install dependencies
pip install pycryptodome

Or create a virtual environment:
# Windows
python -m venv venv
venv\Scripts\activate
pip install pycryptodome

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
pip install pycryptodome

STEP 3: Run the application
python main.py
