"""
Run this ONCE on your local PC after the first successful python main.py run.
It prints the base64-encoded token.pickle that you paste into GitHub Secrets.

Usage:
    python encode_token.py
"""

import base64
from pathlib import Path

token_path = Path("token.pickle")

if not token_path.exists():
    print("❌ token.pickle not found!")
    print("   Run 'python main.py' first to generate it.")
else:
    encoded = base64.b64encode(token_path.read_bytes()).decode("utf-8")
    print("\n✅ Copy this entire string and paste it as the GOOGLE_TOKEN secret:\n")
    print(encoded)
    print("\n📋 Also copy your credentials.json content for GOOGLE_CREDENTIALS secret.")
