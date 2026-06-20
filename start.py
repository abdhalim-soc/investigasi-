#!/usr/bin/env python3
"""
Updated OSINT Multi-tool – No argparse, direct commands.
Usage: python start.py <MODE> [PARAMETERS...]
Examples:
  python start.py spx RESI123
  python start.py osint_name "Budi Santoso"
  python start.py plate "B 1234 ABC"
  python start.py academic "keyword"
  python start.py academic_detail 123456
  python start.py imei 123456789012345
  python start.py worker 3201020304050001
  python start.py bpjs 3201020304050001
  python start.py image_loc /path/photo.jpg
  python start.py bank 1234567890
  python start.py ptk 3201020304050001
  python start.py nik2kk 3201020304050001
  python start.py nik2phone 3201020304050001
  python start.py nik2email 3201020304050001
  python start.py dump_db [table]
  python start.py doctor "nama dokter"
  python start.py doctor_id 123
  python start.py teacher "nama guru"
  python start.py phone_osint 081234567890
  python start.py phone_analysis 081234567890
  python start.py victim_tags 081234567890
  python start.py ewallet 081234567890
  python start.py comments 081234567890
  python start.py dox 081234567890
  python start.py full 081234567890
"""
import sys
import re
import requests
from bs4 import BeautifulSoup
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# ---------- CONFIG ----------
LEAK_DB_API = "https://api.leak-indonesia.id"
SPX_API      = "https://api.shiptrack.id/spx"
PLATE_API    = "https://api.plat-nomor.id/lookup"
IMEI_API     = "https://api.imeicheck.com"
BANK_API     = "https://api.rekening.id/check"
PTK_API      = "https://api.ptk.kemdikbud.go.id"
DOCTOR_API   = "https://api.dokter.id"
TEACHER_API  = "https://api.guru.id"
EWALLET_API  = "https://api.ewallet.id/name"
PHONE_COMMENT_API = "https://api.komentar-nomor.id"
BPJS_CLAIM_API   = "https://api.bpjs-kesehatan.go.id/vclaim"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-API-Key": "free-access-key"
}

def get(url, params=None):
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[!] Request error: {e}", file=sys.stderr)
        return None

def post(url, data=None):
    try:
        r = requests.post(url, data=data, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[!] Request error: {e}", file=sys.stderr)
        return None

def parse_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr')
    if not rows: return []
    headers = [th.get_text(strip=True) for th in rows[0].find_all(['td','th'])]
    data = []
    for row in rows[1:]:
        cols = [td.get_text(strip=True) for td in row.find_all('td')]
        if len(cols) == len(headers):
            data.append(dict(zip(headers, cols)))
    return data

def print_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    print(soup.get_text(separator='\n').strip())

# ---------- FEATURES ----------
def spx(resi):
    print(f"[*] SPX tracking: {resi}")
    html = get(SPX_API, {"resi": resi})
    if html:
        for entry in parse_table(html):
            print(f"{entry.get('waktu','')} | {entry.get('status','')} | {entry.get('lokasi','')}")

def osint_name(name):
    print(f"[*] Name OSINT: {name}")
    html = get(f"{LEAK_DB_API}/search/name", {"q": name})
    if html:
        for rec in parse_table(html):
            print(f"NIK:{rec.get('nik','')} KK:{rec.get('kk','')} Alamat:{rec.get('alamat','')}")

def plate_lookup(plate):
    print(f"[*] Plate lookup: {plate}")
    html = get(PLATE_API, {"plate": plate})
    if html: print_text(html)

def academic_search(query):
    print(f"[*] Academic search: {query}")
    html = get(f"{LEAK_DB_API}/academic/search", {"q": query})
    if html:
        for rec in parse_table(html):
            print(f"{rec.get('id','')} {rec.get('nama','')} {rec.get('prodi','')} {rec.get('universitas','')}")

def academic_detail(uid):
    print(f"[*] Academic detail: {uid}")
    html = get(f"{LEAK_DB_API}/academic/detail", {"id": uid})
    if html: print_text(html)

def imei(imei):
    print(f"[*] IMEI: {imei}")
    html = get(IMEI_API, {"imei": imei})
    if html: print_text(html)

def worker(q):
    print(f"[*] Worker info: {q}")
    html = get(f"{LEAK_DB_API}/worker", {"q": q})
    if html:
        for rec in parse_table(html):
            print(f"NIK:{rec.get('nik','')} Nama:{rec.get('nama','')} Pekerjaan:{rec.get('pekerjaan','')} Perusahaan:{rec.get('perusahaan','')}")

def bpjs(nik):
    print(f"[*] BPJS Vclaim: {nik}")
    html = get(BPJS_CLAIM_API, {"nik": nik})
    if html: print_text(html)

def image_loc(path):
    print(f"[*] Image location: {path}")
    try:
        img = Image.open(path)
        exif = img._getexif()
        if not exif:
            print("[-] No EXIF data")
            return
        gps = {}
        for tag, val in exif.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                for t, v in val.items():
                    gps[GPSTAGS.get(t, t)] = v
        if gps:
            print(f"Lat: {gps.get('GPSLatitude')} {gps.get('GPSLatitudeRef')}")
            print(f"Lon: {gps.get('GPSLongitude')} {gps.get('GPSLongitudeRef')}")
            print(f"Alt: {gps.get('GPSAltitude')}")
        else:
            print("[-] No GPS data")
    except Exception as e:
        print(f"[!] {e}")

def bank(acc):
    print(f"[*] Bank check: {acc}")
    html = get(BANK_API, {"account": acc})
    if html: print_text(html)

def ptk(nik):
    print(f"[*] PTK: {nik}")
    html = get(PTK_API, {"nik": nik})
    if html: print_text(html)

def nik2kk(nik):
    print(f"[*] NIK->KK: {nik}")
    html = get(f"{LEAK_DB_API}/nik2kk", {"nik": nik})
    if html:
        m = re.search(r'\b\d{16}\b', html)
        if m: print(f"KK: {m.group(0)}")
        else: print("[-] Not found")

def nik2phone(nik):
    print(f"[*] NIK->Phone: {nik}")
    html = get(f"{LEAK_DB_API}/nik2phone", {"nik": nik})
    if html:
        phones = re.findall(r'\b08\d{8,11}\b', html)
        if phones: print("Phones:", ", ".join(phones))
        else: print("[-] None")

def nik2email(nik):
    print(f"[*] NIK->Email: {nik}")
    html = get(f"{LEAK_DB_API}/nik2email", {"nik": nik})
    if html:
        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', html)
        if emails: print("Emails:", ", ".join(emails))
        else: print("[-] None")

def dump_db(table='all'):
    print(f"[*] DB dump, table={table}")
    html = get(f"{LEAK_DB_API}/dump", {"table": table})
    if html: print(html[:2000])

def doctor_search(name):
    print(f"[*] Doctor search: {name}")
    html = get(DOCTOR_API, {"nama": name})
    if html:
        for rec in parse_table(html):
            print(f"{rec.get('id_dokter','')} {rec.get('nama','')} {rec.get('spesialisasi','')} {rec.get('rumah_sakit','')}")

def doctor_id(did):
    print(f"[*] Doctor ID: {did}")
    html = get(f"{DOCTOR_API}/detail", {"id": did})
    if html: print_text(html)

def teacher_search(name):
    print(f"[*] Teacher search: {name}")
    html = get(TEACHER_API, {"nama": name})
    if html:
        for rec in parse_table(html):
            print(f"{rec.get('nuptk','')} {rec.get('nama','')} {rec.get('sekolah','')} {rec.get('kota','')}")

def phone_osint(phone):
    print(f"[*] Phone OSINT: {phone}")
    html = get(f"{LEAK_DB_API}/phone/osint", {"phone": phone})
    if html: print_text(html)

def phone_analysis(phone):
    print(f"[*] Phone analysis: {phone}")
    html = get(f"{LEAK_DB_API}/phone/analysis", {"phone": phone})
    if html:
        for rec in parse_table(html):
            print(f"NIK:{rec.get('nik','')} Nama:{rec.get('nama','')} Alamat:{rec.get('alamat','')} Gender:{rec.get('gender','')} TTL:{rec.get('ttl','')}")

def victim_tags(phone):
    print(f"[*] Victim tags: {phone}")
    html = get(f"{LEAK_DB_API}/phone/tags", {"phone": phone})
    if html:
        tags = re.findall(r'<tag>(.*?)</tag>', html)
        if tags: print("Tags:", ", ".join(tags))
        else: print("[-] None")

def ewallet(phone):
    print(f"[*] E-wallet: {phone}")
    html = get(EWALLET_API, {"phone": phone})
    if html:
        m = re.search(r'Nama:\s*(.+)', html, re.I)
        if m: print(f"Name: {m.group(1)}")
        else: print("[-] No name")

def phone_comments(phone):
    print(f"[*] Comments: {phone}")
    html = get(PHONE_COMMENT_API, {"phone": phone})
    if html:
        comments = re.findall(r'<comment>(.*?)</comment>', html, re.DOTALL)
        if comments:
            for c in comments: print(f" - {c.strip()}")
        else: print("[-] None")

def dox(phone):
    print(f"[*] Doxing: {phone}")
    html = get(f"{LEAK_DB_API}/phone/dox", {"phone": phone})
    if html: print_text(html)

def full_profile(phone):
    print(f"[*] Full profile: {phone}")
    html = get(f"{LEAK_DB_API}/phone/full", {"phone": phone})
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        for row in soup.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) == 2:
                print(f"{cols[0].get_text(strip=True)}: {cols[1].get_text(strip=True)}")

# ---------- ROUTER ----------
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    mode = sys.argv[1].lower()
    args = sys.argv[2:]
    if mode == "spx" and args:                spx(args[0])
    elif mode == "osint_name" and args:       osint_name(" ".join(args))
    elif mode == "plate" and args:            plate_lookup(" ".join(args))
    elif mode == "academic" and args:         academic_search(" ".join(args))
    elif mode == "academic_detail" and args:  academic_detail(args[0])
    elif mode == "imei" and args:             imei(args[0])
    elif mode == "worker" and args:           worker(" ".join(args))
    elif mode == "bpjs" and args:             bpjs(args[0])
    elif mode == "image_loc" and args:        image_loc(args[0])
    elif mode == "bank" and args:             bank(args[0])
    elif mode == "ptk" and args:              ptk(args[0])
    elif mode == "nik2kk" and args:           nik2kk(args[0])
    elif mode == "nik2phone" and args:        nik2phone(args[0])
    elif mode == "nik2email" and args:        nik2email(args[0])
    elif mode == "dump_db":                   dump_db(args[0] if args else 'all')
    elif mode == "doctor" and args:           doctor_search(" ".join(args))
    elif mode == "doctor_id" and args:        doctor_id(args[0])
    elif mode == "teacher" and args:          teacher_search(" ".join(args))
    elif mode == "phone_osint" and args:      phone_osint(args[0])
    elif mode == "phone_analysis" and args:   phone_analysis(args[0])
    elif mode == "victim_tags" and args:      victim_tags(args[0])
    elif mode == "ewallet" and args:          ewallet(args[0])
    elif mode == "comments" and args:         phone_comments(args[0])
    elif mode == "dox" and args:              dox(args[0])
    elif mode == "full" and args:             full_profile(args[0])
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
