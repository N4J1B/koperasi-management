"""
dashboard.py
Halaman dashboard — ringkasan statistik koperasi.
"""
import tkinter as tk
from tkinter import ttk
from database import get_conn
from helpers import fmt_rp, JENIS_LABEL, JENIS_LIST
from pages.base_page import BasePage, C_BG, C_WHITE, C_BLUE, C_DARK, C_GRAY


class DashboardPage(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()
        self.refresh()

    def _build(self):
        # ── Header ───────────────────────────────────────
        hdr = tk.Frame(self, bg=C_BG)
        hdr.pack(fill="x", padx=16, pady=(16, 8))
        tk.Label(hdr, text="Selamat Datang di Sistem Koperasi Langggeng",
                 font=("Arial", 13, "bold"), bg=C_BG, fg=C_DARK).pack(anchor="w")
        tk.Label(hdr, text="Ringkasan data koperasi hari ini",
                 font=("Arial", 9), bg=C_BG, fg=C_GRAY).pack(anchor="w")

        # ── Stat cards row ───────────────────────────────
        self._card_frame = tk.Frame(self, bg=C_BG)
        self._card_frame.pack(fill="x", padx=16, pady=8)

        # ── Middle row ───────────────────────────────────
        mid = tk.Frame(self, bg=C_BG)
        mid.pack(fill="both", expand=True, padx=16, pady=4)
        mid.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=1)

        # Simpanan per jenis
        self._smp_frame = tk.Frame(mid, bg=C_WHITE,
                                   highlightbackground="#E2E8F0", highlightthickness=1)
        self._smp_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=4)

        # Pinjaman aktif
        self._pin_frame = tk.Frame(mid, bg=C_WHITE,
                                   highlightbackground="#E2E8F0", highlightthickness=1)
        self._pin_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=4)

    def refresh(self):
        conn = get_conn()
        try:
            self._rebuild_stats(conn)
            self._rebuild_simpanan(conn)
            self._rebuild_pinjaman(conn)
        finally:
            conn.close()

    def _rebuild_stats(self, conn):
        for w in self._card_frame.winfo_children():
            w.destroy()

        n_anggota = conn.execute("SELECT COUNT(*) FROM anggota").fetchone()[0]
        total_smp = conn.execute("SELECT COALESCE(SUM(jumlah),0) FROM simpanan").fetchone()[0]
        n_pinjaman_aktif = conn.execute(
            "SELECT COUNT(*) FROM pinjaman WHERE status='aktif'").fetchone()[0]
        total_pinjaman = conn.execute(
            "SELECT COALESCE(SUM(jumlah),0) FROM pinjaman WHERE status='aktif'").fetchone()[0]
        total_angsuran = conn.execute(
            "SELECT COALESCE(SUM(jumlah),0) FROM angsuran").fetchone()[0]

        stats = [
            ("👥 Total Anggota",      str(n_anggota) + " orang",  "#EBF8FF", "#2B6CB0"),
            ("💰 Total Simpanan",     fmt_rp(total_smp),           "#F0FFF4", "#276749"),
            ("📋 Pinjaman Aktif",     str(n_pinjaman_aktif) + " pinjaman", "#FFFAF0", "#C05621"),
            ("💵 Total Pinjaman",     fmt_rp(total_pinjaman),      "#FFF5F5", "#C53030"),
            ("✅ Total Angsuran",     fmt_rp(total_angsuran),      "#FAF5FF", "#6B46C1"),
        ]

        for i, (lbl, val, bg, fg) in enumerate(stats):
            f = tk.Frame(self._card_frame, bg=bg, padx=14, pady=12,
                         highlightbackground="#E2E8F0", highlightthickness=1)
            f.pack(side="left", fill="both", expand=True,
                   padx=(0 if i == 0 else 6, 0))
            tk.Label(f, text=lbl, font=("Arial", 8), bg=bg, fg=C_GRAY).pack(anchor="w")
            tk.Label(f, text=val, font=("Arial", 12, "bold"), bg=bg, fg=fg).pack(anchor="w")

    def _rebuild_simpanan(self, conn):
        for w in self._smp_frame.winfo_children():
            w.destroy()
        tk.Label(self._smp_frame, text="Simpanan per Jenis",
                 font=("Arial", 10, "bold"), bg=C_WHITE, fg=C_DARK).pack(
            anchor="w", padx=12, pady=(10, 6))

        for j in JENIS_LIST:
            total = conn.execute(
                "SELECT COALESCE(SUM(jumlah),0) FROM simpanan WHERE jenis=?", (j,)
            ).fetchone()[0]
            row = tk.Frame(self._smp_frame, bg=C_WHITE)
            row.pack(fill="x", padx=12, pady=2)
            tk.Label(row, text=JENIS_LABEL[j], font=("Arial", 9),
                     bg=C_WHITE, fg=C_DARK, width=20, anchor="w").pack(side="left")
            tk.Label(row, text=fmt_rp(total), font=("Arial", 9, "bold"),
                     bg=C_WHITE, fg=C_BLUE).pack(side="right")

        grand = conn.execute("SELECT COALESCE(SUM(jumlah),0) FROM simpanan").fetchone()[0]
        tk.Frame(self._smp_frame, bg="#E2E8F0", height=1).pack(fill="x", padx=12, pady=4)
        row = tk.Frame(self._smp_frame, bg=C_WHITE)
        row.pack(fill="x", padx=12, pady=(0, 10))
        tk.Label(row, text="TOTAL", font=("Arial", 9, "bold"),
                 bg=C_WHITE, fg=C_DARK, width=20, anchor="w").pack(side="left")
        tk.Label(row, text=fmt_rp(grand), font=("Arial", 10, "bold"),
                 bg=C_WHITE, fg="#276749").pack(side="right")

    def _rebuild_pinjaman(self, conn):
        for w in self._pin_frame.winfo_children():
            w.destroy()
        tk.Label(self._pin_frame, text="Pinjaman Aktif Terbaru",
                 font=("Arial", 10, "bold"), bg=C_WHITE, fg=C_DARK).pack(
            anchor="w", padx=12, pady=(10, 6))

        rows = conn.execute("""
            SELECT a.nama, p.jumlah, p.jangka, p.tgl
            FROM pinjaman p JOIN anggota a ON p.anggota_id=a.id
            WHERE p.status='aktif'
            ORDER BY p.tgl DESC LIMIT 8
        """).fetchall()

        cols = ("Nama", "Jumlah", "Jangka", "Tgl")
        tv = ttk.Treeview(self._pin_frame, columns=cols, show="headings", height=8)
        for col, w in zip(cols, [18, 14, 8, 12]):
            tv.heading(col, text=col)
            tv.column(col, width=w * 8, anchor="w" if col == "Nama" else "center")
        for i, r in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            tv.insert("", "end", values=(r[0], fmt_rp(r[1]), f"{r[2]} bln", r[3]), tags=(tag,))
        tv.tag_configure("even", background="#EBF8FF")
        tv.tag_configure("odd",  background="white")
        tv.pack(fill="both", expand=True, padx=8, pady=(0, 10))
