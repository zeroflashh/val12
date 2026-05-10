#!/usr/bin/env python3
"""Generate Pyrogram and Telethon session strings interactively."""

import sys
import os

try:
    from pyrogram import Client as PyroClient
    from pyrogram.errors import SessionPasswordNeeded as Pyro2FA
except ImportError:
    print("Installing pyrogram...")
    os.system(f"{sys.executable} -m pip install pyrogram tgcrypto")
    from pyrogram import Client as PyroClient
    from pyrogram.errors import SessionPasswordNeeded as Pyro2FA

try:
    from telethon import TelegramClient as TeleClient
    from telethon.sessions import StringSession
    from telethon.errors import SessionPasswordNeededError as Tele2FA
except ImportError:
    print("Installing telethon...")
    os.system(f"{sys.executable} -m pip install telethon")
    from telethon import TelegramClient as TeleClient
    from telethon.sessions import StringSession
    from telethon.errors import SessionPasswordNeededError as Tele2FA

print("=" * 50)
print(" Session String Generator (Pyrogram + Telethon)")
print("=" * 50)
print("1 = Pyrogram  |  2 = Telethon")

LIB_CHOICE = input("Choose library [1]: ").strip() or "1"
lib = "pyrogram" if LIB_CHOICE in ("1", "") else "telethon"

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


def gen_pyrogram(phone, session_name, idx):
    client = PyroClient(
        name=session_name,
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=phone,
    )

    # Connect and send code manually
    client.connect()
    print(f"[{idx}] Sending OTP to {phone}...")
    sent_code_info = client.send_code(phone)
    code = input(f"[{idx}] Enter OTP: ").strip()
    try:
        client.sign_in(phone, sent_code_info.phone_code_hash, code)
    except Pyro2FA:
        print(f"[{idx}] 2FA enabled. Enter password: ", end="")
        password = input().strip()
        client.check_password(password)
        client.sign_in(phone, sent_code_info.phone_code_hash, code)
    except Exception as e:
        if "SESSION_PASSWORD_NEEDED" in str(e):
            print(f"[{idx}] 2FA enabled. Enter password: ", end="")
            password = input().strip()
            client.check_password(password)
            client.sign_in(phone, sent_code_info.phone_code_hash, code)
        else:
            raise
    session_str = client.session.save()
    client.disconnect()
    return session_str


def gen_telethon(phone, session_name, idx):
    client = TeleClient(
        session=StringSession(),
        api_id=API_ID,
        api_hash=API_HASH,
    )
    client.start(phone=phone)
    print(f"[{idx}] OTP sent to {phone}")
    code = input(f"[{idx}] Enter OTP: ").strip()
    try:
        client.sign_in(phone, code)
    except Tele2FA:
        print(f"[{idx}] 2FA enabled. Enter password: ", end="")
        password = input().strip()
        client.sign_in(password=password)
    session_str = client.session.save()
    client.disconnect()
    return session_str


for i in range(1, count + 1):
    print(f"\n--- Assistant {i} ---")
    session_name = input(f"Session name [leave blank for default]: ").strip() or f"valentin_ass{i}"
    phone = input("Phone number (+country code): ").strip()

    try:
        if lib == "pyrogram":
            session_str = gen_pyrogram(phone, session_name, i)
        else:
            session_str = gen_telethon(phone, session_name, i)

        results.append((f"STRING_SESSION{i}", session_str, lib))
        print(f"[{i}] Generated ({lib}): STRING_SESSION{i} | length: {len(session_str)}")
    except Exception as e:
        print(f"[{i}] Failed: {e}")
        continue

print("\n" + "=" * 50)
print("Add these to your .env file:")
print("=" * 50)
for var, val, l in results:
    print(f'{var}="{val}"')

if results:
    print("\nDone.")
else:
    print("\nNo sessions generated.")
    sys.exit(1)
