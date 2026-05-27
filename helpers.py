"""helpers.py – Konstanta & fungsi utilitas"""
from datetime import date

JENIS_LIST  = ['pokok','wajib','sukarela','khusus','hariraya']
JENIS_LABEL = {'pokok':'Simpanan Pokok','wajib':'Simpanan Wajib',
               'sukarela':'Simpanan Sukarela','khusus':'Simpanan Khusus',
               'hariraya':'Simpanan Hari Raya'}
BULAN_NAMA  = {1:'Januari',2:'Februari',3:'Maret',4:'April',5:'Mei',6:'Juni',
               7:'Juli',8:'Agustus',9:'September',10:'Oktober',11:'November',12:'Desember'}
BULAN_SHORT = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'Mei',6:'Jun',
               7:'Jul',8:'Agu',9:'Sep',10:'Okt',11:'Nov',12:'Des'}

def fmt_rp(n):
    try:   return f"Rp {int(round(float(n or 0))):,}".replace(",",".")
    except: return "Rp 0"

def hitung_angsuran(jumlah, jangka, bunga):
    return (jumlah / jangka) + (jumlah * bunga / 100)

def today_str():  return str(date.today())
def this_year():  return date.today().year
def this_month(): return date.today().month

def get_periode_aktif():
    """Return periode aktif tunggal dari DB. Return None jika tidak ada."""
    try:
        from database import get_conn
        conn = get_conn()
        row = conn.execute(
            "SELECT id, nama, tahun FROM periode WHERE status='aktif' ORDER BY tahun DESC LIMIT 1"
        ).fetchone()
        conn.close()
        return row  # None jika tidak ada
    except Exception:
        return None

def cek_periode_aktif():
    """Return True jika ada periode aktif."""
    return get_periode_aktif() is not None
