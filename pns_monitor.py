import requests
from bs4 import BeautifulSoup
import random
import telebot
from datetime import datetime
import json
import os # Library untuk mengakses environment variables

# ==========================================================
# KONFIGURASI
# ==========================================================
BKN_URL = "https://sscasn.bkn.go.id/"
BSSN_URL = "https://bssn.go.id/karir"

# Mengambil informasi rahasia dari Environment Variables (lebih aman)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Lokasi file status disederhanakan agar berjalan di direktori yang sama
STATUS_FILE = "last_status.json" 

# ==========================================================
# FUNGSI-FUNGSI (Tidak ada perubahan logika)
# ==========================================================
# Hentikan skrip jika token atau ID tidak ditemukan
if not TELEGRAM_TOKEN or not CHAT_ID:
    print("Error: Pastikan TELEGRAM_TOKEN dan CHAT_ID sudah diatur di Environment Variables.")
    exit()

bot = telebot.TeleBot(TELEGRAM_TOKEN)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15"
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com"
    }

def check_bkn():
    try:
        response = requests.get(BKN_URL, headers=get_random_headers(), timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        registration_button = soup.find("a", {"class": "btn-daftar"})
        if registration_button and "Daftar" in registration_button.text:
            return "Pendaftaran CASN dibuka! Segera akses: " + BKN_URL
        return None
    except Exception as e:
        print(f"[ERROR BKN] {e}")
        return None

def check_bssn():
    try:
        response = requests.get(BSSN_URL, headers=get_random_headers(), timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        karir = soup.find("div", {"class": "post-content"})
        if karir and "lowongan" in karir.text.lower():
            return "Lowongan BSSN tersedia! Cek: " + BSSN_URL
        return None
    except Exception as e:
        print(f"[ERROR BSSN] {e}")
        return None

def send_telegram(msg):
    bot.send_message(CHAT_ID, msg)

# ==========================================================
# FUNGSI UTAMA
# ==========================================================
def main():
    try:
        with open(STATUS_FILE, 'r') as f:
            last_statuses = json.load(f)
    except (IOError, ValueError):
        last_statuses = {}
    
    last_bkn = last_statuses.get('bkn')
    last_bssn = last_statuses.get('bssn')

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{now}] Scanning...")

    bkn_status = check_bkn()
    if bkn_status and bkn_status != last_bkn:
        send_telegram(f"🚨 BKN UPDATE: {bkn_status}")
        last_statuses['bkn'] = bkn_status

    bssn_status = check_bssn()
    if bssn_status and bssn_status != last_bssn:
        send_telegram(f"🚨 BSSN UPDATE: {bssn_status}")
        last_statuses['bssn'] = bssn_status

    with open(STATUS_FILE, 'w') as f:
        json.dump(last_statuses, f)
    
    print(f"[{now}] Scan complete.")

if __name__ == "__main__":
    main()
