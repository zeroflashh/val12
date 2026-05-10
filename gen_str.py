#!/usr/bin/env python3
"""Generate Pyrogram session strings interactively."""

import sys
import os

# Check for pyrogram
try:
    from pyrogram import Client
except ImportError:
    print("Installing pyrogram...")
    os.system(f"{sys.executable} -m pip install pyrogram tgcrypto")
    from pyrogram import Client

print("=" * 50)
print(" Session String Generator")
print("=" * 50)

NUM = input("How many sessions to generate? [1-5]: ").strip() or "1"
try:
    count = max(1, min(5, int(NUM)))
except ValueError:
    count = 1

API_ID = input("API_ID: ").strip()
API_HASH = input("API_HASH: ").strip()

if not API_ID or not API_HASH:
    print("API_ID and API_HASH required!")
    sys.exit(1)

API_ID = int(API_ID)

results = []

for i in range(1, count + 1):
    print(f"\n--- Assistant {i} ---")
    session_name = input(f"Session name for assistant {i} [leave blank for default]: ").strip() or f"valentin_ass{i}"
    phone = input("Phone number (+country code): ").strip()

    print("Connecting... (this will send OTP code)")

    client = Client(
        name=session_name,
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=phone,
    )

    sent_code = client.connect()
    print(f"OTP sent to {phone}: {sent_code}")
    code = input("Enter OTP: ").strip()
    client.sign_in(phone, sent_code.phone_code_hash, code)
    session_str = client.session.save()
    client.disconnect()

    env_var = f"STRING_SESSION{i}" if i == 1 else f"STRING_SESSION{i}"
    results.append((env_var, session_str))
    print(f"Generated: {env_var}=<string length: {len(session_str)}>")

print("\n" + "=" * 50)
print("Add these to your .env file:")
print("=" * 50)
for var, val in results:
    print(f'{var}="{val}"')

print("\nDone.")
