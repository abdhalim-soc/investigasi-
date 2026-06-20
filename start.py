#!/usr/bin/env python3
"""
Massive OSINT Tool – Indonesian Identity, Phone, Vehicle, Medical, and Academic Lookup.
Features: SPX tracking, name OSINT, plate lookup, student/lecturer ID, IMEI, worker info,
BPJS claim, image location, bank check, PTK, NIK->KK, NIK->Phone, NIK->Email, DB dump,
doctor search, doctor ID, teacher search, phone OSINT, e-wallet, phone comments, doxing,
full profile extraction.

This script uses a common leak database API (replace the endpoint with a real one).
All endpoints are placeholders; the tool works as soon as the correct API is provided.
Comments in English.
"""

import os
import sys
import re
import json
import argparse
import requests
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from bs4 import BeautifulSoup
from datetime import datetime

# ---------- CONFIGURATION ----------
# Central leak API endpoint – REPLACE WITH ACTUAL WORKING ENDPOINT
LEAK_DB_API = "https://api.leak-indonesia.id"
# Public APIs that do not require authentication
SPX_API = "https://api.shiptrack.id/spx"
PLATE_API = "https://api.plat-nomor.id/lookup"
IMEI_API = "https://api.imeicheck.com"
BANK_API = "https://api.rekening.id/check"
PTK_API = "https://api.ptk.kemdikbud.go.id"
DOCTOR_API = "https://api.dokter.id"
TEACHER_API = "https://api.guru.id"
EWALLET_API = "https://api.ewallet.id/name"
PHONE_COMMENT_API = "https://api.komentar-nomor.id"
BPJS_CLAIM_API = "https://api.bpjs-kesehatan.go.id/vclaim"

# Default HTTP headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-API-Key": "free-access-key"  # static for this tool
}

# ---------- UTILITY FUNCTIONS ----------
def safe_get(url, params=None, timeout=15):
    """Perform GET request and return text, or None on failure."""
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"[!] Request failed: {e}", file=sys.stderr)
        return None

def safe_post(url, data=None, timeout=15):
    """Perform POST request and return text, or None on failure."""
    try:
        resp = requests.post(url, data=data, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"[!] Request failed: {e}", file=sys.stderr)
        return None

def parse_html_table(html):
    """Parse simple HTML table into list of dicts."""
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr')
    if not rows:
        return []
    headers = [th.get_text(strip=True) for th in rows[0].find_all(['td', 'th'])]
    data = []
    for row in rows[1:]:
        cols = [td.get_text(strip=True) for td in row.find_all('td')]
        if len(cols) == len(headers):
            data.append(dict(zip(headers, cols)))
    return data

def print_json_output(data):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2, ensure_ascii=False))

# ---------- FEATURE FUNCTIONS ----------

def spx_tracking(resi):
    """Pelacakan SPX (SPX courier tracking)."""
    print(f"[*] Tracking SPX package: {resi}")
    html = safe_get(SPX_API, params={"resi": resi})
    if not html:
        return
    data = parse_html_table(html)
    print(" SPX Tracking Result ")
    for entry in data:
        print(f"Date/Time: {entry.get('waktu')}, Status: {entry.get('status')}, Location: {entry.get('lokasi')}")
    print()

def osint_name(name):
    """Osint Nama – general name lookup."""
    print(f"[*] Searching OSINT for name: {name}")
    html = safe_get(f"{LEAK_DB_API}/search/name", params={"q": name})
    if not html:
        return
    data = parse_html_table(html)
    print(f" Found {len(data)} records for name '{name}' ")
    for rec in data:
        print(f"NIK: {rec.get('nik')}, KK: {rec.get('kk')}, Alamat: {rec.get('alamat')}")
    print()

def plate_lookup(plate):
    """Lookup Plat Kendaraan (vehicle plate)."""
    print(f"[*] Looking up vehicle plate: {plate}")
    html = safe_get(PLATE_API, params={"plate": plate})
    if not html:
        return
    soup = BeautifulSoup(html, 'html.parser')
    info = soup.get_text(separator='\n')
    print(" Vehicle Plate Information ")
    print(info.strip())
    print()

def search_student_lecturer(query):
    """Cari Nama & ID Mahasiswa/Dosen."""
    print(f"[*] Searching student/lecturer: {query}")
    html = safe_get(f"{LEAK_DB_API}/academic/search", params={"q": query})
    if not html:
        return
    data = parse_html_table(html)
    print(f" Academic records for '{query}' ")
    for rec in data:
        print(f"NIM/NIDN: {rec.get('id')}, Nama: {rec.get('nama')}, Program: {rec.get('prodi')}, Universitas: {rec.get('universitas')}")
    print()

def student_lecturer_detail(id_number):
    """Lookup Detail ID Mahasiswa/Dosen."""
    print(f"[*] Detail lookup for ID: {id_number}")
    html = safe_get(f"{LEAK_DB_API}/academic/detail", params={"id": id_number})
    if not html:
        return
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator='\n')
    print(" Academic Detail ")
    print(text.strip())
    print()

def imei_lookup(imei):
    """Lookup IMEI."""
    print(f"[*] IMEI lookup: {imei}")
    html = safe_get(IMEI_API, params={"imei": imei})
    if not html:
        return
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator='\n')
    print(" IMEI Information ")
    print(text.strip())
    print()

def worker_info(nik_or_name):
    """Cari Informasi Pekerja via NIK/Nama."""
    print(f"[*] Searching worker info for: {nik_or_name}")
    html = safe_get(f"{LEAK_DB_API}/worker", params={"q": nik_or_name})
    if not html:
        return
    data = parse_html_table(html)
    print(f" Worker records for '{nik_or_name}' ")
    for rec in data:
        print(f"NIK: {rec.get('nik')}, Nama: {rec.get('nama')}, Pekerjaan: {rec.get('pekerjaan')}, Perusahaan: {rec.get('perusahaan')}")
    print()

def bpjs_vclaim(nik):
    """Lookup BPJS Vsclaim."""
    print(f"[*] BPJS claim lookup for NIK: {nik}")
    html = safe_get(BPJS_CLAIM_API, params={"nik": nik})
    if not html:
        return
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator='\n')
    print(" BPJS Claim Info ")
    print(text.strip())
    print()

def image_location_analysis(image_path):
    """Analisis Lokasi Gambar (extract GPS from EXIF)."""
    print(f"[*] Analyzing image: {image_path}")
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if not exif_data:
            print("[-] No EXIF data found.")
            return
        gps_info = {}
        for tag, value in exif_data.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                for gps_tag in value:
                    sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
                    gps_info[sub_decoded] = value[gps_tag]
        if gps_info:
            print(" GPS Information ")
            print(f"Latitude: {gps_info.get('GPSLatitude')} {gps_info.get('GPSLatitudeRef')}")
            print(f"Longitude: {gps_info.get('GPSLongitude')} {gps_info.get('GPSLongitudeRef')}")
            print(f"Altitude: {gps_info.get('GPSAltitude')}")
            print(f"Timestamp: {gps_info.get('GPSTimeStamp')}")
        else:
            print("[-] No GPS data in EXIF.")
    except Exception as e:
        print(f"[!] Error reading image: {e}")
    print()

def bank_check(account_number):
    """Cek Rekening (bank account)."""
    print(f"[*] Checking bank account: {account_number}")
    html = safe_get(BANK_API, params={"account": account_number})
    if not html:
        return
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator='\n')
    print(" Bank Account Information ")
    print(text.strip())
    print()

def ptk_check(nik):
    """Cek PTK (teacher certification)."""
    print(f"[*] PTK check for NIK: {nik}")
    html = safe_get(PTK_API, params={"nik": nik})
    if not html:
        return
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator='\n')
    print(" PTK Data ")
    print(text.strip())
    print()

def nik_to_kk(nik):
    """NIK ke KK."""
    print(f"[*] Converting NIK to KK: {nik}")
    html = safe_get(f"{LEAK_DB_API}/nik2kk", params={"nik": nik})
    if not html:
        return
    # Expected format: plain text KK number
    kk = re.search(r'\b\d{16}\b', html)
    if kk:
        print(f"[+] KK Number: {kk.group(0)}")
    else:
        print("[-] KK not found.")
    print()

def nik_to_phone(nik):
    """NIK ke Nomor (phone)."""
    print(f"[*] NIK to phone number: {nik}")
    html = safe_get(f"{LEAK_DB_API}/nik2phone", params={"nik": nik})
    if not html:
        return
    phones = re.findall(r'\b08\d{8,11}\b', html)
    if phones:
        print(f"[+] Associated phone numbers: {', '.join(phones)}")
    else:
        print("[-] No phone numbers found.")
    print()

def nik_to_email(nik):
    """NIK ke Email."""
    print(f"[*] NIK to email: {nik}")
    html = safe_get(f"{LEAK_DB_API}/nik2email", params={"nik": nik})
    if not html:
        return
    emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', html)
    if emails:
        print(f"[+] Associated emails: {', '.join(emails)}")
    else:
        print("[-] No emails found.")
    print()

def dump_database(table='all'):
    """Dump DB (Eksklusif)."""
    print(f"[*] Dumping database table: {table}")
    html = safe_get(f"{LEAK_DB_API}/dump", params={"table": table})
    if not html:
        return
    # Output raw response
    print(" Database Dump ")
    print(html[:2000])  # Limit output to first 2000 chars for readability
    print("... (truncated)")

def search_doctor(name):
    """Cari Dokter via Nama."""
    print(f"[*] Searching doctor by name: {name}")
    html = safe_get(DOCTOR_API, params={"nama": name})
    if not html:
        return
    data = parse_html_table(html)
    print(f" Doctor records for '{name}' ")
    for rec in data:
        print(f"ID: {rec.get('id_dokter')}, Nama: {rec.get('nama')}, Spesialisasi: {rec.get('spesialisasi')}, RS: {rec.get('rumah_sakit')}")
    print()

def doctor_id_lookup(doctor_id):
    """Lookup ID Dokter."""
    print(f"[*] Looking up doctor ID: {doctor_id}")
    html = safe_get(f"{DOCTOR_API}/detail", params={"id": doctor_id})
    if not html:
        return
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator='\n')
    print(" Doctor Detail ")
    print(text.strip())
    print()

def search_teacher(name):
    """Cari Guru."""
    print(f"[*] Searching teacher by name: {name}")
    html = safe_get(TEACHER_API, params={"nama": name})
    if not html:
        return
    data = parse_html_table(html)
    print(f" Teacher records for '{name}' ")
    for rec in data:
        print(f"NUPTK: {rec.get('nuptk')}, Nama: {rec.get('nama')}, Sekolah: {rec.get('sekolah')}, Kota: {rec.get('kota')}")
    print()

def phone_osint(phone):
    """Osint Nomor Handphone."""
    print(f"[*] OSINT for phone number: {phone}")
    html = safe_get(f"{LEAK_DB_API}/phone/osint", params={"phone": phone})
    if not html:
        return
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator='\n')
    print(" Phone OSINT Summary ")
    print(text.strip())
    print()

def phone_analysis(phone):
    """Analisis Nomor Handphone (Pencarian)."""
    print(f"[*] Analyzing phone number: {phone}")
    # Comprehensive search: identity + location + social media
    html = safe_get(f"{LEAK_DB_API}/phone/analysis", params={"phone": phone})
    if not html:
        return
    data = parse_html_table(html)
    print(f" Full Analysis for {phone} ")
    for rec in data:
        print(f"NIK: {rec.get('nik')}, Nama: {rec.get('nama')}, Alamat: {rec.get('alamat')}, Gender: {rec.get('gender')}, TTL: {rec.get('ttl')}")
    print()

def show_victim_tags(phone):
    """Tampilkan Tag Korban: Ditambahkan (Detail Tag)."""
    print(f"[*] Showing victim tags for phone: {phone}")
    html = safe_get(f"{LEAK_DB_API}/phone/tags", params={"phone": phone})
    if not html:
        return
    tags = re.findall(r'<tag>(.*?)</tag>', html)
    if tags:
        print(f"[+] Tags: {', '.join(tags)}")
    else:
        print("[-] No tags found.")
    print()

def check_ewallet(phone):
    """Cek Nama E-Wallet (GoPay, OVO, etc.)."""
    print(f"[*] Checking e-wallet name for: {phone}")
    html = safe_get(EWALLET_API, params={"phone": phone})
    if not html:
        return
    name = re.search(r'Nama:\s*(.+)', html, re.IGNORECASE)
    if name:
        print(f"[+] E-wallet registered name: {name.group(1)}")
    else:
        print("[-] No e-wallet name found.")
    print()

def phone_comments(phone):
    """Cek Komentar pada Nomor Handphone."""
    print(f"[*] Fetching comments for phone: {phone}")
    html = safe_get(PHONE_COMMENT_API, params={"phone": phone})
    if not html:
        return
    comments = re.findall(r'<comment>(.*?)</comment>', html, re.DOTALL)
    if comments:
        print(f"[+] Comments ({len(comments)}):")
        for c in comments:
            print(f"  - {c.strip()}")
    else:
        print("[-] No comments.")
    print()

def doxing_phone(phone):
    """Doxing Nomor – all info from phone number."""
    print(f"[*] Doxing phone number: {phone}")
    # Aggregates results from multiple endpoints
    html = safe_get(f"{LEAK_DB_API}/phone/dox", params={"phone": phone})
    if not html:
        return
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator='\n')
    print(" DOXING REPORT ")
    print(text)
    print()

def full_profile(phone):
    """Menampilkan Informasi Lokasi terdekat, Nama lengkap, Gender, tanggal lahir, bpjs, dll."""
    print(f"[*] Full profile extraction for: {phone}")
    html = safe_get(f"{LEAK_DB_API}/phone/full", params={"phone": phone})
    if not html:
        return
    soup = BeautifulSoup(html, 'html.parser')
    data = {}
    for row in soup.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) == 2:
            key = cols[0].get_text(strip=True)
            value = cols[1].get_text(strip=True)
            data[key] = value
    print(" FULL PROFILE ")
    for k, v in data.items():
        print(f"{k}: {v}")
    print()

# ---------- MAIN MENU ----------
def main():
    parser = argparse.ArgumentParser(description="Indonesian OSINT Multi-tool")
    sub = parser.add_subparsers(dest="command", required=True, help="Available modules")

    # SPX
    p_spx = sub.add_parser("spx", help="Pelacakan SPX")
    p_spx.add_argument("resi", help="Nomor resi SPX")

    # OSINT Nama
    p_name = sub.add_parser("osint_name", help="Osint Nama")
    p_name.add_argument("name", help="Nama lengkap")

    # Plat
    p_plate = sub.add_parser("plate", help="Lookup Plat Kendaraan")
    p_plate.add_argument("plate", help="Nomor plat (contoh: B 1234 ABC)")

    # Mahasiswa/Dosen search
    p_academic = sub.add_parser("academic", help="Cari Nama & ID Mahasiswa/Dosen")
    p_academic.add_argument("query", help="Nama atau kata kunci")

    # Mahasiswa/Dosen detail
    p_academic_detail = sub.add_parser("academic_detail", help="Lookup Detail ID Mahasiswa/Dosen")
    p_academic_detail.add_argument("id", help="NIM atau NIDN")

    # IMEI
    p_imei = sub.add_parser("imei", help="Lookup IMEI")
    p_imei.add_argument("imei", help="Nomor IMEI")

    # Worker info
    p_worker = sub.add_parser("worker", help="Cari Informasi Pekerja via NIK/Nama")
    p_worker.add_argument("nik_or_name", help="NIK atau nama")

    # BPJS Vclaim
    p_bpjs = sub.add_parser("bpjs", help="Lookup BPJS Vsclaim")
    p_bpjs.add_argument("nik", help="NIK")

    # Image location
    p_image = sub.add_parser("image_loc", help="Analisis Lokasi Gambar")
    p_image.add_argument("path", help="Path ke file gambar")

    # Bank check
    p_bank = sub.add_parser("bank", help="Cek Rekening")
    p_bank.add_argument("account", help="Nomor rekening")

    # PTK
    p_ptk = sub.add_parser("ptk", help="Cek PTK")
    p_ptk.add_argument("nik", help="NIK")

    # NIK to KK
    p_nik2kk = sub.add_parser("nik2kk", help="NIK ke KK")
    p_nik2kk.add_argument("nik", help="NIK")

    # NIK to phone
    p_nik2phone = sub.add_parser("nik2phone", help="NIK ke Nomor")
    p_nik2phone.add_argument("nik", help="NIK")

    # NIK to email
    p_nik2email = sub.add_parser("nik2email", help="NIK ke Email")
    p_nik2email.add_argument("nik", help="NIK")

    # DB dump
    p_dump = sub.add_parser("dump_db", help="Dump DB (Eksklusif)")
    p_dump.add_argument("table", nargs="?", default="all", help="Nama tabel (default: all)")

    # Doctor search
    p_doc = sub.add_parser("doctor", help="Cari Dokter via Nama")
    p_doc.add_argument("name", help="Nama dokter")

    # Doctor ID
    p_doc_id = sub.add_parser("doctor_id", help="Lookup ID Dokter")
    p_doc_id.add_argument("id", help="ID Dokter")

    # Teacher search
    p_teacher = sub.add_parser("teacher", help="Cari Guru")
    p_teacher.add_argument("name", help="Nama guru")

    # Phone OSINT
    p_phone_osint = sub.add_parser("phone_osint", help="Osint Nomor Handphone")
    p_phone_osint.add_argument("phone", help="Nomor HP")

    # Phone analysis
    p_phone_analysis = sub.add_parser("phone_analysis", help="Analisis Nomor Handphone (Pencarian)")
    p_phone_analysis.add_argument("phone", help="Nomor HP")

    # Victim tags
    p_tags = sub.add_parser("victim_tags", help="Tampilkan Tag Korban")
    p_tags.add_argument("phone", help="Nomor HP")

    # E-wallet
    p_ewallet = sub.add_parser("ewallet", help="Cek Nama E-Wallet")
    p_ewallet.add_argument("phone", help="Nomor HP")

    # Phone comments
    p_comments = sub.add_parser("comments", help="Cek Komentar pada Nomor Handphone")
    p_comments.add_argument("phone", help="Nomor HP")

    # Doxing
    p_dox = sub.add_parser("dox", help="Doxing Nomor")
    p_dox.add_argument("phone", help="Nomor HP")

    # Full profile
    p_full = sub.add_parser("full", help="Full Profile (Lokasi, Nama, Gender, TTL, BPJS)")
    p_full.add_argument("phone", help="Nomor HP")

    args = parser.parse_args()
    cmd = args.command

    # Dispatch
    if cmd == "spx":
        spx_tracking(args.resi)
    elif cmd == "osint_name":
        osint_name(args.name)
    elif cmd == "plate":
        plate_lookup(args.plate)
    elif cmd == "academic":
        search_student_lecturer(args.query)
    elif cmd == "academic_detail":
        student_lecturer_detail(args.id)
    elif cmd == "imei":
        imei_lookup(args.imei)
    elif cmd == "worker":
        worker_info(args.nik_or_name)
    elif cmd == "bpjs":
        bpjs_vclaim(args.nik)
    elif cmd == "image_loc":
        image_location_analysis(args.path)
    elif cmd == "bank":
        bank_check(args.account)
    elif cmd == "ptk":
        ptk_check(args.nik)
    elif cmd == "nik2kk":
        nik_to_kk(args.nik)
    elif cmd == "nik2phone":
        nik_to_phone(args.nik)
    elif cmd == "nik2email":
        nik_to_email(args.nik)
    elif cmd == "dump_db":
        dump_database(args.table)
    elif cmd == "doctor":
        search_doctor(args.name)
    elif cmd == "doctor_id":
        doctor_id_lookup(args.id)
    elif cmd == "teacher":
        search_teacher(args.name)
    elif cmd == "phone_osint":
        phone_osint(args.phone)
    elif cmd == "phone_analysis":
        phone_analysis(args.phone)
    elif cmd == "victim_tags":
        show_victim_tags(args.phone)
    elif cmd == "ewallet":
        check_ewallet(args.phone)
    elif cmd == "comments":
        phone_comments(args.phone)
    elif cmd == "dox":
        doxing_phone(args.phone)
    elif cmd == "full":
        full_profile(args.phone)

if __name__ == "__main__":
    main()
