"""
database.py  –  Koneksi & inisialisasi SQLite
Tabel: anggota, periode, simpanan, pinjaman, angsuran
"""
import sqlite3, os

# Saat dijalankan sebagai .exe, koperasi_app.py menetapkan ATRA_DB_PATH
# agar database disimpan di folder user yang bisa ditulis.
# Saat development, fallback ke lokasi file ini (perilaku lama).
DB_FILE = os.environ.get(
    'ATRA_DB_PATH',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "koperasi.db")
)

def get_conn():
    c = sqlite3.connect(DB_FILE)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c


def _migrate(cur):
    """Tambah kolom yang belum ada (migrasi skema lama → baru)."""
    migrations = [
        ("simpanan",  "periode_id", "INTEGER"),
        ("simpanan",  "bulan",      "INTEGER"),
        ("simpanan",  "tahun",      "INTEGER"),
        ("pinjaman",  "periode_id", "INTEGER"),
        ("pinjaman",  "tahun",      "INTEGER"),
        ("angsuran",  "bulan",      "INTEGER"),
        ("angsuran",  "tahun",      "INTEGER"),
        ("angsuran",  "keterangan", "TEXT DEFAULT ''"),
        ("angsuran",  "status",     "TEXT NOT NULL DEFAULT 'lunas'"),
    ]
    for tbl, col, coltype in migrations:
        existing = [r[1] for r in cur.execute(f"PRAGMA table_info({tbl})").fetchall()]
        if col not in existing:
            try:
                cur.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} {coltype}")
            except Exception:
                pass

    # Isi kolom tahun/bulan dari tgl yang sudah ada
    try:
        cur.execute("""
            UPDATE simpanan SET
                tahun = CAST(strftime('%Y', tgl) AS INTEGER),
                bulan = CAST(strftime('%m', tgl) AS INTEGER)
            WHERE tahun IS NULL AND tgl IS NOT NULL
        """)
    except Exception: pass
    try:
        cur.execute("""
            UPDATE pinjaman SET
                tahun = CAST(strftime('%Y', tgl) AS INTEGER)
            WHERE tahun IS NULL AND tgl IS NOT NULL
        """)
    except Exception: pass
    try:
        cur.execute("""
            UPDATE angsuran SET
                tahun = CAST(strftime('%Y', tgl) AS INTEGER),
                bulan = CAST(strftime('%m', tgl) AS INTEGER)
            WHERE tahun IS NULL AND tgl IS NOT NULL
        """)
    except Exception: pass
    # Pastikan tabel periode ada
    cur.execute("""
        CREATE TABLE IF NOT EXISTS periode (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nama        TEXT NOT NULL,
            tahun       INTEGER NOT NULL,
            bulan_mulai INTEGER NOT NULL,
            bulan_akhir INTEGER NOT NULL,
            keterangan  TEXT DEFAULT '',
            status      TEXT NOT NULL DEFAULT 'aktif'
        )
    """)

def init_db():
    c = get_conn(); cur = c.cursor()
    _migrate(cur)  # migrasi skema lama
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS anggota (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        no_anggota TEXT NOT NULL UNIQUE,
        nama       TEXT NOT NULL,
        alamat     TEXT DEFAULT '',
        no_hp      TEXT DEFAULT '',
        tgl_masuk  TEXT NOT NULL DEFAULT (date('now'))
    );
    CREATE TABLE IF NOT EXISTS periode (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        nama        TEXT NOT NULL,
        tahun       INTEGER NOT NULL,
        bulan_mulai INTEGER NOT NULL,
        bulan_akhir INTEGER NOT NULL,
        keterangan  TEXT DEFAULT '',
        status      TEXT NOT NULL DEFAULT 'aktif' CHECK(status IN ('aktif','tutup'))
    );
    CREATE TABLE IF NOT EXISTS simpanan (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        periode_id INTEGER,
        anggota_id INTEGER NOT NULL,
        jenis      TEXT NOT NULL CHECK(jenis IN ('pokok','wajib','sukarela','khusus','hariraya')),
        jumlah     REAL NOT NULL CHECK(jumlah > 0),
        tgl        TEXT NOT NULL,
        bulan      INTEGER,
        tahun      INTEGER,
        keterangan TEXT DEFAULT '',
        FOREIGN KEY (anggota_id) REFERENCES anggota(id) ON DELETE RESTRICT,
        FOREIGN KEY (periode_id) REFERENCES periode(id) ON DELETE SET NULL
    );
    CREATE TABLE IF NOT EXISTS pinjaman (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        periode_id INTEGER,
        anggota_id INTEGER NOT NULL,
        jumlah     REAL NOT NULL CHECK(jumlah > 0),
        jangka     INTEGER NOT NULL CHECK(jangka > 0),
        bunga      REAL NOT NULL DEFAULT 1.5,
        tgl        TEXT NOT NULL,
        tahun      INTEGER,
        keterangan TEXT DEFAULT '',
        status     TEXT NOT NULL DEFAULT 'aktif' CHECK(status IN ('aktif','lunas')),
        FOREIGN KEY (anggota_id) REFERENCES anggota(id) ON DELETE RESTRICT,
        FOREIGN KEY (periode_id) REFERENCES periode(id) ON DELETE SET NULL
    );
    CREATE TABLE IF NOT EXISTS angsuran (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        pinjaman_id INTEGER NOT NULL,
        ke          INTEGER NOT NULL,
        jumlah      REAL NOT NULL CHECK(jumlah > 0),
        tgl         TEXT NOT NULL,
        bulan       INTEGER,
        tahun       INTEGER,
        keterangan  TEXT DEFAULT '',
        status      TEXT NOT NULL DEFAULT 'lunas',
        FOREIGN KEY (pinjaman_id) REFERENCES pinjaman(id) ON DELETE RESTRICT
    );
    """)
    if cur.execute("SELECT COUNT(*) FROM anggota").fetchone()[0] == 0:
        _seed(cur)
    c.commit(); c.close()

def _seed(cur):
    cur.executemany(
        "INSERT INTO anggota(no_anggota,nama,alamat,no_hp,tgl_masuk) VALUES(?,?,?,?,?)",
        [('KOP-001','Budi Santoso','Jl. Mawar No.5','081234567890','2024-01-15'),
         ('KOP-002','Siti Rahayu','Jl. Melati No.12','082345678901','2024-02-01'),
         ('KOP-003','Ahmad Fauzi','Jl. Dahlia No.8','083456789012','2024-03-10'),
         ('KOP-004','Dewi Lestari','Jl. Kenanga No.3','084567890123','2024-04-05'),
         ('KOP-005','Rizal Pratama','Jl. Anggrek No.7','085678901234','2024-01-20')])
    # Periode
    cur.execute("INSERT INTO periode(nama,tahun,bulan_mulai,bulan_akhir,keterangan,status)"
                " VALUES(?,?,?,?,?,?)",('Periode 2024',2024,1,12,'Tahun Buku 2024','aktif'))
    pid = cur.lastrowid
    # Simpanan pokok semua anggota
    for aid in range(1,6):
        cur.execute("INSERT INTO simpanan(periode_id,anggota_id,jenis,jumlah,tgl,bulan,tahun,keterangan)"
                    " VALUES(?,?,?,?,?,?,?,?)",
                    (pid,aid,'pokok',500000,f'2024-01-{14+aid}',1,2024,'Simpanan pokok awal'))
    # Simpanan wajib Jan–Apr
    for bulan in range(1,5):
        for aid in range(1,6):
            from calendar import monthrange
            hari = monthrange(2024,bulan)[1]
            cur.execute("INSERT INTO simpanan(periode_id,anggota_id,jenis,jumlah,tgl,bulan,tahun,keterangan)"
                        " VALUES(?,?,?,?,?,?,?,?)",
                        (pid,aid,'wajib',100000,f'2024-{bulan:02d}-{hari}',bulan,2024,f'Wajib {bulan}/2024'))
    # Sukarela
    extras = [(1,'sukarela',200000,'2024-03-15',3),(2,'hariraya',150000,'2024-03-20',3),
              (1,'khusus',300000,'2024-04-10',4),(3,'sukarela',75000,'2024-04-22',4),
              (4,'hariraya',200000,'2024-03-25',3),(5,'khusus',125000,'2024-02-14',2)]
    for aid,jenis,jml,tgl,bln in extras:
        cur.execute("INSERT INTO simpanan(periode_id,anggota_id,jenis,jumlah,tgl,bulan,tahun,keterangan)"
                    " VALUES(?,?,?,?,?,?,?,?)",(pid,aid,jenis,jml,tgl,bln,2024,f'{jenis.title()}'))
    # Pinjaman
    cur.execute("INSERT INTO pinjaman(periode_id,anggota_id,jumlah,jangka,bunga,tgl,keterangan,status)"
                " VALUES(?,?,?,?,?,?,?,?)",(pid,1,5000000,12,1.5,'2024-02-01','Modal usaha','aktif'))
    p1 = cur.lastrowid
    cur.execute("INSERT INTO pinjaman(periode_id,anggota_id,jumlah,jangka,bunga,tgl,keterangan,status)"
                " VALUES(?,?,?,?,?,?,?,?)",(pid,2,3000000,6,1.5,'2024-03-01','Kebutuhan keluarga','aktif'))
    p2 = cur.lastrowid
    cur.execute("INSERT INTO pinjaman(periode_id,anggota_id,jumlah,jangka,bunga,tgl,keterangan,status)"
                " VALUES(?,?,?,?,?,?,?,?)",(pid,3,2000000,6,1.5,'2024-01-15','Biaya pendidikan','lunas'))
    p3 = cur.lastrowid
    # Angsuran
    for ke,bln,tgl in [(1,3,'2024-03-01'),(2,4,'2024-04-01'),(3,5,'2024-05-01')]:
        cur.execute("INSERT INTO angsuran(pinjaman_id,ke,jumlah,tgl,bulan,tahun)"
                    " VALUES(?,?,?,?,?,?)",(p1,ke,457083,tgl,bln,2024))
    for ke,bln,tgl in [(1,4,'2024-04-01'),(2,5,'2024-05-01')]:
        cur.execute("INSERT INTO angsuran(pinjaman_id,ke,jumlah,tgl,bulan,tahun)"
                    " VALUES(?,?,?,?,?,?)",(p2,ke,528000,tgl,bln,2024))
    for ke,bln,tgl in [(1,2,'2024-02-15'),(2,3,'2024-03-15'),(3,4,'2024-04-15'),
                       (4,5,'2024-05-15'),(5,6,'2024-06-15'),(6,7,'2024-07-15')]:
        cur.execute("INSERT INTO angsuran(pinjaman_id,ke,jumlah,tgl,bulan,tahun)"
                    " VALUES(?,?,?,?,?,?)",(p3,ke,376667,tgl,bln,2024))
    cur.execute("UPDATE pinjaman SET status='lunas' WHERE id=?",(p3,))
