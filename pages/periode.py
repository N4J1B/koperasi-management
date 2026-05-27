"""
periode.py
Halaman manajemen periode / tahun buku koperasi.
- Tanggal Mulai & Akhir menggunakan date picker kalender (tanpa library eksternal)
- Tahun diambil otomatis dari tanggal mulai
- DB: bulan_mulai, bulan_akhir, tahun tetap diisi otomatis dari tanggal
- DB: kolom tgl_mulai, tgl_akhir (TEXT YYYY-MM-DD) ditambah via migrasi
"""
import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from datetime import date, datetime
from database import get_conn
from helpers import today_str
from pages.base_page import BasePage, C_BG, C_WHITE, C_BLUE, C_DARK, C_GRAY, C_RED, C_GREEN

BULAN_NAMES = {
    1:"Januari", 2:"Februari", 3:"Maret", 4:"April",
    5:"Mei", 6:"Juni", 7:"Juli", 8:"Agustus",
    9:"September", 10:"Oktober", 11:"November", 12:"Desember"
}


# ══════════════════════════════════════════════════════════════
#  Widget DatePicker (kalender popup pure tkinter)
# ══════════════════════════════════════════════════════════════
class DatePicker(tk.Frame):
    """
    Widget input tanggal dengan tombol kalender popup.
    Nilai diakses via .get() → str 'YYYY-MM-DD' atau '' jika kosong.
    Dipasang via .grid() seperti biasa.
    """
    def __init__(self, parent, initial_date=None, **kwargs):
        super().__init__(parent, bg=C_WHITE, **kwargs)
        today = date.today()
        if initial_date and isinstance(initial_date, str):
            try:
                d = datetime.strptime(initial_date, "%Y-%m-%d").date()
            except Exception:
                d = today
        else:
            d = initial_date if isinstance(initial_date, date) else today

        self._date = d
        self._var  = tk.StringVar(value=self._fmt_display(d))

        self._entry = ttk.Entry(self, textvariable=self._var, width=18,
                                state="readonly", font=("Arial", 9))
        self._entry.pack(side="left")

        btn = tk.Button(self, text="📅", font=("Arial", 9),
                        bg="#EBF8FF", fg=C_DARK, relief="flat", bd=0,
                        cursor="hand2", padx=4,
                        command=self._open_popup)
        btn.pack(side="left", padx=(2, 0))

    def _fmt_display(self, d):
        return f"{d.day:02d} {BULAN_NAMES[d.month]} {d.year}"

    def get(self):
        """Return tanggal sebagai string 'YYYY-MM-DD'."""
        return self._date.strftime("%Y-%m-%d") if self._date else ""

    def set_date(self, d):
        if isinstance(d, str):
            try:
                d = datetime.strptime(d, "%Y-%m-%d").date()
            except Exception:
                return
        self._date = d
        self._var.set(self._fmt_display(d))

    def _open_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Pilih Tanggal")
        popup.resizable(False, False)
        popup.grab_set()
        popup.focus_set()

        # Posisi di dekat widget
        self.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 2
        popup.geometry(f"+{x}+{y}")

        _CalendarPopup(popup, self._date, self._on_pick)

    def _on_pick(self, picked_date, popup):
        self._date = picked_date
        self._var.set(self._fmt_display(picked_date))
        popup.destroy()


class _CalendarPopup(tk.Frame):
    """Isi kalender di dalam Toplevel popup."""
    NAV_BG   = "#2B6CB0"
    HEAD_BG  = "#EBF8FF"
    SEL_BG   = "#2B6CB0"
    SEL_FG   = "white"
    TODAY_FG = "#C05621"
    DAY_FG   = "#1E293B"
    OTHER_FG = "#CBD5E0"

    def __init__(self, popup, current_date, callback):
        super().__init__(popup, bg=C_WHITE, padx=6, pady=6)
        self.pack(fill="both", expand=True)
        self._popup    = popup
        self._callback = callback
        self._today    = date.today()
        self._sel      = current_date or self._today
        self._view_y   = self._sel.year
        self._view_m   = self._sel.month
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()

        # ── Nav bar ───────────────────────────────────────
        nav = tk.Frame(self, bg=self.NAV_BG)
        nav.pack(fill="x", pady=(0, 4))

        tk.Button(nav, text="◀", bg=self.NAV_BG, fg="white", font=("Arial", 10, "bold"),
                  relief="flat", bd=0, cursor="hand2",
                  command=self._prev_month).pack(side="left", padx=4, pady=4)

        lbl = tk.Label(nav, text=f"{BULAN_NAMES[self._view_m]} {self._view_y}",
                       font=("Arial", 10, "bold"), bg=self.NAV_BG, fg="white")
        lbl.pack(side="left", expand=True)

        tk.Button(nav, text="▶", bg=self.NAV_BG, fg="white", font=("Arial", 10, "bold"),
                  relief="flat", bd=0, cursor="hand2",
                  command=self._next_month).pack(side="right", padx=4, pady=4)

        # ── Year quick-jump ───────────────────────────────
        yf = tk.Frame(self, bg=C_WHITE)
        yf.pack(fill="x", pady=(0, 4))
        tk.Label(yf, text="Tahun:", font=("Arial", 8), bg=C_WHITE, fg=C_GRAY).pack(side="left")
        self._v_year = tk.StringVar(value=str(self._view_y))
        years = [str(y) for y in range(self._today.year - 5, self._today.year + 6)]
        cb = ttk.Combobox(yf, textvariable=self._v_year, values=years,
                          width=6, state="readonly", font=("Arial", 8))
        cb.pack(side="left", padx=4)
        cb.bind("<<ComboboxSelected>>", self._jump_year)

        # ── Day headers ───────────────────────────────────
        days_hdr = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
        hdr_f = tk.Frame(self, bg=self.HEAD_BG)
        hdr_f.pack(fill="x")
        for d in days_hdr:
            tk.Label(hdr_f, text=d, font=("Arial", 8, "bold"),
                     bg=self.HEAD_BG, fg=C_DARK, width=4,
                     anchor="center").pack(side="left", padx=1)

        # ── Day grid ──────────────────────────────────────
        grid_f = tk.Frame(self, bg=C_WHITE)
        grid_f.pack()

        cal = calendar.monthcalendar(self._view_y, self._view_m)
        for week in cal:
            row_f = tk.Frame(grid_f, bg=C_WHITE)
            row_f.pack()
            for day in week:
                if day == 0:
                    tk.Label(row_f, text="", width=4, font=("Arial", 9),
                             bg=C_WHITE).pack(side="left", padx=1, pady=1)
                else:
                    d = date(self._view_y, self._view_m, day)
                    is_sel   = (d == self._sel)
                    is_today = (d == self._today)
                    bg  = self.SEL_BG if is_sel else C_WHITE
                    fg  = self.SEL_FG if is_sel else (self.TODAY_FG if is_today else self.DAY_FG)
                    fnt = ("Arial", 9, "bold") if is_sel or is_today else ("Arial", 9)
                    btn = tk.Button(row_f, text=str(day), width=3, font=fnt,
                                    bg=bg, fg=fg, relief="flat", bd=0,
                                    cursor="hand2",
                                    command=lambda dd=d: self._pick(dd))
                    btn.pack(side="left", padx=1, pady=1)
                    if not is_sel:
                        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.HEAD_BG))
                        btn.bind("<Leave>", lambda e, b=btn: b.config(bg=C_WHITE))

        # ── Footer: Hari ini ──────────────────────────────
        tk.Button(self, text=f"📅 Hari ini: {self._fmt(self._today)}",
                  font=("Arial", 8), bg="#F0FFF4", fg=C_GREEN, relief="flat",
                  cursor="hand2",
                  command=lambda: self._pick(self._today)).pack(fill="x", pady=(6, 0))

    def _fmt(self, d):
        return f"{d.day:02d} {BULAN_NAMES[d.month]} {d.year}"

    def _prev_month(self):
        if self._view_m == 1:
            self._view_m = 12; self._view_y -= 1
        else:
            self._view_m -= 1
        self._v_year.set(str(self._view_y))
        self._build()

    def _next_month(self):
        if self._view_m == 12:
            self._view_m = 1; self._view_y += 1
        else:
            self._view_m += 1
        self._v_year.set(str(self._view_y))
        self._build()

    def _jump_year(self, _=None):
        try:
            self._view_y = int(self._v_year.get())
            self._build()
        except ValueError:
            pass

    def _pick(self, d):
        self._sel = d
        self._callback(d, self._popup)


# ══════════════════════════════════════════════════════════════
#  Halaman Periode
# ══════════════════════════════════════════════════════════════
class PeriodePage(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        self._sel_id = None
        self._ensure_tgl_cols()
        self._build()
        self.refresh()

    def _ensure_tgl_cols(self):
        """Migrasi: tambah kolom tgl_mulai & tgl_akhir jika belum ada."""
        conn = get_conn()
        try:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(periode)").fetchall()]
            for col, default in [("tgl_mulai", "TEXT DEFAULT ''"),
                                  ("tgl_akhir",  "TEXT DEFAULT ''")]:
                if col not in cols:
                    conn.execute(f"ALTER TABLE periode ADD COLUMN {col} {default}")
            # Isi tgl_mulai/tgl_akhir dari bulan_mulai/bulan_akhir untuk data lama
            conn.execute("""
                UPDATE periode
                SET tgl_mulai = printf('%04d-%02d-01', tahun, bulan_mulai)
                WHERE (tgl_mulai IS NULL OR tgl_mulai = '')
                  AND bulan_mulai IS NOT NULL AND tahun IS NOT NULL
            """)
            conn.execute("""
                UPDATE periode
                SET tgl_akhir = date(
                    printf('%04d-%02d-01', tahun, bulan_akhir), '+1 month', '-1 day')
                WHERE (tgl_akhir IS NULL OR tgl_akhir = '')
                  AND bulan_akhir IS NOT NULL AND tahun IS NOT NULL
            """)
            conn.commit()
        finally:
            conn.close()

    def _build(self):
        top = tk.Frame(self, bg=C_BG)
        top.pack(fill="both", expand=True, padx=12, pady=8)
        top.columnconfigure(1, weight=1)

        # ── Form Panel ────────────────────────────────────
        form_card = tk.Frame(top, bg=C_WHITE,
                             highlightbackground="#E2E8F0", highlightthickness=1)
        form_card.grid(row=0, column=0, sticky="ns", padx=(0, 8))
        form_card.columnconfigure(1, weight=1)

        tk.Label(form_card, text="Form Periode", font=("Arial", 10, "bold"),
                 bg=C_WHITE, fg=C_DARK).grid(row=0, column=0, columnspan=2,
                                              sticky="w", padx=12, pady=(12, 6))

        self._v_nama   = tk.StringVar()
        self._v_ket    = tk.StringVar()
        self._v_status = tk.StringVar(value="aktif")

        # Nama Periode
        self.lbl_entry(form_card, "Nama Periode *", 1, self._v_nama)

        # Tanggal Mulai (date picker)
        tk.Label(form_card, text="Tanggal Mulai *", font=("Arial", 9),
                 bg=C_WHITE, fg=C_DARK, width=16, anchor="w").grid(
            row=2, column=0, sticky="w", padx=(12, 4), pady=4)
        today = date.today()
        default_mulai = date(today.year, 1, 1)
        self._dp_mulai = DatePicker(form_card, initial_date=default_mulai)
        self._dp_mulai.grid(row=2, column=1, sticky="w", padx=(0, 12), pady=4)

        # Tanggal Akhir (date picker)
        tk.Label(form_card, text="Tanggal Akhir *", font=("Arial", 9),
                 bg=C_WHITE, fg=C_DARK, width=16, anchor="w").grid(
            row=3, column=0, sticky="w", padx=(12, 4), pady=4)
        default_akhir = date(today.year, 12, 31)
        self._dp_akhir = DatePicker(form_card, initial_date=default_akhir)
        self._dp_akhir.grid(row=3, column=1, sticky="w", padx=(0, 12), pady=4)

        # Keterangan & Status
        self.lbl_entry(form_card, "Keterangan", 4, self._v_ket)
        self.lbl_combo(form_card, "Status", 5, self._v_status, ["aktif", "tutup"], width=10)

        btn_row = tk.Frame(form_card, bg=C_WHITE)
        btn_row.grid(row=6, column=0, columnspan=2, pady=10, padx=12, sticky="ew")
        self.btn(btn_row, "💾 Simpan",    self._save,   C_BLUE).pack(side="left", padx=(0, 4))
        self.btn(btn_row, "🗑 Hapus",     self._delete, C_RED).pack(side="left", padx=4)
        self.btn(btn_row, "✖ Bersihkan", self._clear, "#718096").pack(side="left", padx=4)

        quick_row = tk.Frame(form_card, bg=C_WHITE)
        quick_row.grid(row=7, column=0, columnspan=2, pady=(0, 12), padx=12, sticky="ew")
        self.btn(quick_row, "🔒 Tutup Periode", self._tutup_periode, "#C05621").pack(side="left", padx=(0, 4))
        self.btn(quick_row, "🔓 Buka Periode",  self._buka_periode,  C_GREEN).pack(side="left", padx=4)

        # ── Treeview Panel ────────────────────────────────
        tv_card = tk.Frame(top, bg=C_WHITE,
                           highlightbackground="#E2E8F0", highlightthickness=1)
        tv_card.grid(row=0, column=1, sticky="nsew")

        tk.Label(tv_card, text="Daftar Periode", font=("Arial", 10, "bold"),
                 bg=C_WHITE, fg=C_DARK).pack(anchor="w", padx=12, pady=(10, 4))

        flt = tk.Frame(tv_card, bg=C_WHITE)
        flt.pack(fill="x", padx=12, pady=(0, 6))
        tk.Label(flt, text="Filter Status:", font=("Arial", 9), bg=C_WHITE).pack(side="left")
        self._v_filter = tk.StringVar(value="semua")
        for val, lbl in [("semua", "Semua"), ("aktif", "Aktif"), ("tutup", "Tutup")]:
            ttk.Radiobutton(flt, text=lbl, variable=self._v_filter, value=val,
                            command=self._filter).pack(side="left", padx=6)

        cols = ("ID", "Nama Periode", "Tgl Mulai", "Tgl Akhir", "Tahun", "Status", "Keterangan")
        self._tv = self.make_tree(tv_card, cols, height=16)
        widths  = [40, 180, 130, 130, 60, 80, 180]
        anchors = ["center", "w", "center", "center", "center", "center", "w"]
        for col, w, a in zip(cols, widths, anchors):
            self._tv.heading(col, text=col)
            self._tv.column(col, width=w, anchor=a)
        self._tv.column("ID", width=0, stretch=False)
        self._tv.bind("<<TreeviewSelect>>", self._on_select)

        info_bar = tk.Frame(self, bg=C_BG)
        info_bar.pack(fill="x", padx=12, pady=(0, 8))
        self._lbl_info = tk.Label(info_bar, text="", font=("Arial", 8),
                                  bg=C_BG, fg=C_GRAY)
        self._lbl_info.pack(anchor="w")

    # ── Data ──────────────────────────────────────────────
    def refresh(self):
        self._all_rows = []
        conn = get_conn()
        try:
            rows = conn.execute(
                "SELECT id, nama, tahun, bulan_mulai, bulan_akhir, status, keterangan, "
                "       tgl_mulai, tgl_akhir "
                "FROM periode ORDER BY tahun DESC, tgl_mulai DESC"
            ).fetchall()
            self._all_rows = [tuple(r) for r in rows]
            total = len(self._all_rows)
            aktif = sum(1 for r in self._all_rows if r[5] == "aktif")
            self._lbl_info.config(
                text=f"Total: {total} periode  |  Aktif: {aktif}  |  Tutup: {total - aktif}"
            )
        finally:
            conn.close()
        self._filter()

    def _filter(self):
        f = self._v_filter.get()
        rows = self._all_rows if f == "semua" else [r for r in self._all_rows if r[5] == f]
        self._render(rows)

    def _fmt_tgl(self, tgl_str):
        """'YYYY-MM-DD' → 'DD Nama_Bulan YYYY'"""
        if not tgl_str:
            return "-"
        try:
            d = datetime.strptime(tgl_str, "%Y-%m-%d").date()
            return f"{d.day:02d} {BULAN_NAMES[d.month]} {d.year}"
        except Exception:
            return tgl_str

    def _render(self, rows):
        self.tv_clear(self._tv)
        for r in rows:
            # r: (id, nama, tahun, bulan_mulai, bulan_akhir, status, keterangan, tgl_mulai, tgl_akhir)
            status_icon = "🟢 aktif" if r[5] == "aktif" else "🔴 tutup"
            tgl_m = self._fmt_tgl(r[7]) if len(r) > 7 else BULAN_NAMES.get(r[3], "-")
            tgl_a = self._fmt_tgl(r[8]) if len(r) > 8 else BULAN_NAMES.get(r[4], "-")
            self.tv_insert(self._tv, (r[0], r[1], tgl_m, tgl_a, r[2], status_icon, r[6] or "-"))

    def _on_select(self, _=None):
        sel = self._tv.selection()
        if not sel:
            return
        vals = self._tv.item(sel[0], "values")
        self._sel_id = vals[0]
        row = next((r for r in self._all_rows if str(r[0]) == str(self._sel_id)), None)
        if not row:
            return
        # row: (id, nama, tahun, bulan_mulai, bulan_akhir, status, keterangan, tgl_mulai, tgl_akhir)
        self._v_nama.set(row[1])
        tgl_m = row[7] if len(row) > 7 and row[7] else f"{row[2]}-{row[3]:02d}-01"
        tgl_a = row[8] if len(row) > 8 and row[8] else None
        if not tgl_a:
            last = calendar.monthrange(row[2], row[4])[1]
            tgl_a = f"{row[2]}-{row[4]:02d}-{last:02d}"
        self._dp_mulai.set_date(tgl_m)
        self._dp_akhir.set_date(tgl_a)
        self._v_status.set(row[5])
        self._v_ket.set(row[6] or "")

    # ── CRUD ──────────────────────────────────────────────
    def _cek_ada_aktif_lain(self, conn, exclude_id=None):
        if exclude_id:
            return conn.execute(
                "SELECT id, nama, tahun FROM periode WHERE status='aktif' AND id!=?",
                (exclude_id,)
            ).fetchone()
        return conn.execute(
            "SELECT id, nama, tahun FROM periode WHERE status='aktif'"
        ).fetchone()

    def _parse_save(self):
        """Validasi & return (nama, tgl_mulai_str, tgl_akhir_str, ket, status) atau None."""
        nama   = self._v_nama.get().strip()
        tgl_m  = self._dp_mulai.get()
        tgl_a  = self._dp_akhir.get()
        ket    = self._v_ket.get().strip()
        status = self._v_status.get()

        if not nama:
            messagebox.showwarning("Perhatian", "Nama Periode wajib diisi!")
            return None
        if not tgl_m or not tgl_a:
            messagebox.showwarning("Perhatian", "Tanggal Mulai & Akhir wajib diisi!")
            return None
        try:
            d_m = datetime.strptime(tgl_m, "%Y-%m-%d").date()
            d_a = datetime.strptime(tgl_a, "%Y-%m-%d").date()
        except Exception:
            messagebox.showwarning("Perhatian", "Format tanggal tidak valid!")
            return None
        if d_m > d_a:
            messagebox.showwarning("Perhatian", "Tanggal Mulai tidak boleh lebih besar dari Tanggal Akhir!")
            return None
        return nama, d_m, d_a, ket, status

    def _save(self):
        parsed = self._parse_save()
        if parsed is None:
            return
        nama, d_m, d_a, ket, status = parsed

        tahun    = d_m.year
        bml      = d_m.month
        bak      = d_a.month
        tgl_m_s  = d_m.strftime("%Y-%m-%d")
        tgl_a_s  = d_a.strftime("%Y-%m-%d")

        conn = get_conn()
        try:
            if self._sel_id:
                if status == "aktif":
                    ada = self._cek_ada_aktif_lain(conn, exclude_id=self._sel_id)
                    if ada:
                        messagebox.showwarning(
                            "Tidak Dapat Mengaktifkan",
                            f"Sistem hanya boleh memiliki SATU periode aktif.\n\n"
                            f"Periode yang sedang aktif:\n"
                            f"▶ {ada[1]} (Tahun {ada[2]})\n\n"
                            f"Tutup periode tersebut terlebih dahulu."
                        )
                        return
                conn.execute(
                    "UPDATE periode SET nama=?, tahun=?, bulan_mulai=?, bulan_akhir=?, "
                    "tgl_mulai=?, tgl_akhir=?, keterangan=?, status=? WHERE id=?",
                    (nama, tahun, bml, bak, tgl_m_s, tgl_a_s, ket or None, status, self._sel_id))
                messagebox.showinfo("Berhasil", "Periode berhasil diperbarui.")
            else:
                if status == "aktif":
                    ada = self._cek_ada_aktif_lain(conn)
                    if ada:
                        messagebox.showwarning(
                            "Tidak Dapat Menambah Periode Baru",
                            f"Sistem hanya boleh memiliki SATU periode aktif.\n\n"
                            f"Periode yang belum ditutup:\n"
                            f"▶ {ada[1]} (Tahun {ada[2]})\n\n"
                            f"Tutup periode tersebut terlebih dahulu sebelum membuat periode baru."
                        )
                        return
                conn.execute(
                    "INSERT INTO periode(nama, tahun, bulan_mulai, bulan_akhir, "
                    "tgl_mulai, tgl_akhir, keterangan, status) VALUES (?,?,?,?,?,?,?,?)",
                    (nama, tahun, bml, bak, tgl_m_s, tgl_a_s, ket or None, status))
                messagebox.showinfo("Berhasil", "Periode baru berhasil ditambahkan.")
            conn.commit()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()
        self._clear()
        self.refresh()

    def _delete(self):
        if not self._sel_id:
            messagebox.showwarning("Perhatian", "Pilih periode yang ingin dihapus!")
            return
        conn = get_conn()
        try:
            jml_simpanan = conn.execute(
                "SELECT COUNT(*) FROM simpanan WHERE periode_id=?", (self._sel_id,)
            ).fetchone()[0]
        finally:
            conn.close()

        pesan = "Yakin ingin menghapus periode ini?\n"
        if jml_simpanan > 0:
            pesan += (f"\n⚠ PERHATIAN: {jml_simpanan} data simpanan yang terkait dengan periode ini\n"
                      f"akan IKUT TERHAPUS dan tidak dapat dikembalikan!\n")
        else:
            pesan += "\nTidak ada data simpanan yang terkait dengan periode ini.\n"
        if not messagebox.askyesno("Konfirmasi Hapus", pesan, icon="warning"):
            return

        conn = get_conn()
        try:
            conn.execute("DELETE FROM simpanan WHERE periode_id=?", (self._sel_id,))
            conn.execute("DELETE FROM periode WHERE id=?", (self._sel_id,))
            conn.commit()
            if jml_simpanan > 0:
                messagebox.showinfo("Berhasil",
                    f"Periode berhasil dihapus.\n{jml_simpanan} data simpanan terkait juga telah dihapus.")
            else:
                messagebox.showinfo("Berhasil", "Periode berhasil dihapus.")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal hapus:\n{e}")
        finally:
            conn.close()
        self._clear()
        self.refresh()

    def _tutup_periode(self):
        if not self._sel_id:
            messagebox.showwarning("Perhatian", "Pilih periode yang ingin ditutup!")
            return
        if not messagebox.askyesno("Konfirmasi", "Tutup periode ini?"):
            return
        conn = get_conn()
        try:
            conn.execute("UPDATE periode SET status='tutup' WHERE id=?", (self._sel_id,))
            conn.commit()
            messagebox.showinfo("Berhasil", "Periode berhasil ditutup.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()
        self._clear()
        self.refresh()

    def _buka_periode(self):
        if not self._sel_id:
            messagebox.showwarning("Perhatian", "Pilih periode yang ingin dibuka!")
            return
        conn = get_conn()
        try:
            aktif_lain = conn.execute(
                "SELECT id, nama, tahun FROM periode WHERE status='aktif' AND id!=?",
                (self._sel_id,)
            ).fetchone()
        finally:
            conn.close()
        if aktif_lain:
            messagebox.showwarning(
                "Tidak Dapat Membuka Periode",
                f"Sistem hanya boleh memiliki SATU periode aktif.\n\n"
                f"Periode yang sedang aktif:\n"
                f"▶ {aktif_lain[1]} (Tahun {aktif_lain[2]})\n\n"
                f"Tutup periode tersebut terlebih dahulu sebelum membuka periode lain."
            )
            return
        if not messagebox.askyesno("Konfirmasi", "Buka kembali periode ini?"):
            return
        conn = get_conn()
        try:
            conn.execute("UPDATE periode SET status='aktif' WHERE id=?", (self._sel_id,))
            conn.commit()
            messagebox.showinfo("Berhasil", "Periode berhasil dibuka kembali.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()
        self._clear()
        self.refresh()

    def _clear(self):
        self._sel_id = None
        self._v_nama.set("")
        today = date.today()
        self._dp_mulai.set_date(date(today.year, 1, 1))
        self._dp_akhir.set_date(date(today.year, 12, 31))
        self._v_ket.set("")
        self._v_status.set("aktif")
        self._tv.selection_remove(self._tv.selection())