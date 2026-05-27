"""
periode.py
Halaman manajemen periode / tahun buku koperasi.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import get_conn
from helpers import today_str
from pages.base_page import BasePage, C_BG, C_WHITE, C_BLUE, C_DARK, C_GRAY, C_RED, C_GREEN

BULAN_NAMES = {
    1:"Januari", 2:"Februari", 3:"Maret", 4:"April",
    5:"Mei", 6:"Juni", 7:"Juli", 8:"Agustus",
    9:"September", 10:"Oktober", 11:"November", 12:"Desember"
}
BULAN_LIST = [f"{k} - {v}" for k, v in BULAN_NAMES.items()]


class PeriodePage(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        self._sel_id = None
        self._build()
        self.refresh()

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
        self._v_tahun  = tk.StringVar()
        self._v_bml    = tk.StringVar(value="1 - Januari")
        self._v_bak    = tk.StringVar(value="12 - Desember")
        self._v_ket    = tk.StringVar()
        self._v_status = tk.StringVar(value="aktif")

        self.lbl_entry(form_card, "Nama Periode *",  1, self._v_nama)
        self.lbl_entry(form_card, "Tahun *",         2, self._v_tahun, width=10)
        self.lbl_combo(form_card, "Bulan Mulai *",   3, self._v_bml, BULAN_LIST, width=20)
        self.lbl_combo(form_card, "Bulan Akhir *",   4, self._v_bak, BULAN_LIST, width=20)
        self.lbl_entry(form_card, "Keterangan",      5, self._v_ket)
        self.lbl_combo(form_card, "Status",          6, self._v_status, ["aktif", "tutup"], width=10)

        btn_row = tk.Frame(form_card, bg=C_WHITE)
        btn_row.grid(row=7, column=0, columnspan=2, pady=10, padx=12, sticky="ew")

        self.btn(btn_row, "💾 Simpan",    self._save,   C_BLUE).pack(side="left", padx=(0, 4))
        self.btn(btn_row, "🗑 Hapus",     self._delete, C_RED).pack(side="left", padx=4)
        self.btn(btn_row, "✖ Bersihkan", self._clear, "#718096").pack(side="left", padx=4)

        # Tombol tutup/buka periode cepat
        quick_row = tk.Frame(form_card, bg=C_WHITE)
        quick_row.grid(row=8, column=0, columnspan=2, pady=(0, 12), padx=12, sticky="ew")
        self.btn(quick_row, "🔒 Tutup Periode", self._tutup_periode, "#C05621").pack(side="left", padx=(0, 4))
        self.btn(quick_row, "🔓 Buka Periode",  self._buka_periode,  C_GREEN).pack(side="left", padx=4)

        # ── Treeview Panel ────────────────────────────────
        tv_card = tk.Frame(top, bg=C_WHITE,
                           highlightbackground="#E2E8F0", highlightthickness=1)
        tv_card.grid(row=0, column=1, sticky="nsew")

        tk.Label(tv_card, text="Daftar Periode", font=("Arial", 10, "bold"),
                 bg=C_WHITE, fg=C_DARK).pack(anchor="w", padx=12, pady=(10, 4))

        # Filter status
        flt = tk.Frame(tv_card, bg=C_WHITE)
        flt.pack(fill="x", padx=12, pady=(0, 6))
        tk.Label(flt, text="Filter Status:", font=("Arial", 9), bg=C_WHITE).pack(side="left")
        self._v_filter = tk.StringVar(value="semua")
        for val, lbl in [("semua", "Semua"), ("aktif", "Aktif"), ("tutup", "Tutup")]:
            ttk.Radiobutton(flt, text=lbl, variable=self._v_filter, value=val,
                            command=self._filter).pack(side="left", padx=6)

        cols = ("ID", "Nama Periode", "Tahun", "Bln Mulai", "Bln Akhir", "Status", "Keterangan")
        self._tv = self.make_tree(tv_card, cols, height=16)
        widths   = [40, 200, 70, 100, 100, 70, 220]
        anchors  = ["center", "w", "center", "center", "center", "center", "w"]
        for col, w, a in zip(cols, widths, anchors):
            self._tv.heading(col, text=col)
            self._tv.column(col, width=w, anchor=a)
        self._tv.column("ID", width=0, stretch=False)   # sembunyikan ID
        self._tv.bind("<<TreeviewSelect>>", self._on_select)

        # ── Info ringkasan bawah ──────────────────────────
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
                "SELECT id,nama,tahun,bulan_mulai,bulan_akhir,status,keterangan "
                "FROM periode ORDER BY tahun DESC, bulan_mulai DESC"
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
        if f == "semua":
            rows = self._all_rows
        else:
            rows = [r for r in self._all_rows if r[5] == f]
        self._render(rows)

    def _render(self, rows):
        self.tv_clear(self._tv)
        for r in rows:
            bml_name = BULAN_NAMES.get(r[3], str(r[3]))
            bak_name = BULAN_NAMES.get(r[4], str(r[4]))
            status_icon = "🟢 aktif" if r[5] == "aktif" else "🔴 tutup"
            self.tv_insert(self._tv, (r[0], r[1], r[2], bml_name, bak_name, status_icon, r[6] or "-"))

    def _on_select(self, _=None):
        sel = self._tv.selection()
        if not sel:
            return
        vals = self._tv.item(sel[0], "values")
        self._sel_id = vals[0]
        # Cari data asli dari _all_rows berdasarkan ID
        row = next((r for r in self._all_rows if str(r[0]) == str(self._sel_id)), None)
        if not row:
            return
        self._v_nama.set(row[1])
        self._v_tahun.set(str(row[2]))
        self._v_bml.set(f"{row[3]} - {BULAN_NAMES.get(row[3], '')}")
        self._v_bak.set(f"{row[4]} - {BULAN_NAMES.get(row[4], '')}")
        self._v_status.set(row[5])
        self._v_ket.set(row[6] or "")

    # ── CRUD ──────────────────────────────────────────────
    def _cek_ada_aktif_lain(self, conn, exclude_id=None):
        """Cek apakah ada periode aktif selain exclude_id. Return row atau None."""
        if exclude_id:
            return conn.execute(
                "SELECT id, nama, tahun FROM periode WHERE status='aktif' AND id!=?",
                (exclude_id,)
            ).fetchone()
        return conn.execute(
            "SELECT id, nama, tahun FROM periode WHERE status='aktif'"
        ).fetchone()

    def _save(self):
        nama   = self._v_nama.get().strip()
        tahun  = self._v_tahun.get().strip()
        bml    = self._v_bml.get().strip()
        bak    = self._v_bak.get().strip()
        ket    = self._v_ket.get().strip()
        status = self._v_status.get()

        if not nama or not tahun or not bml or not bak:
            messagebox.showwarning("Perhatian", "Nama, Tahun, Bulan Mulai & Akhir wajib diisi!")
            return
        try:
            tahun_int = int(tahun)
        except ValueError:
            messagebox.showwarning("Perhatian", "Tahun harus berupa angka!")
            return
        try:
            bml_int = int(bml.split(" - ")[0])
            bak_int = int(bak.split(" - ")[0])
        except Exception:
            messagebox.showwarning("Perhatian", "Format bulan tidak valid!")
            return
        if bml_int > bak_int:
            messagebox.showwarning("Perhatian", "Bulan mulai tidak boleh lebih besar dari bulan akhir!")
            return

        conn = get_conn()
        try:
            if self._sel_id:
                # ── EDIT ────────────────────────────────────────
                # Jika ingin set aktif, pastikan tidak ada aktif lain
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
                    "UPDATE periode SET nama=?,tahun=?,bulan_mulai=?,bulan_akhir=?,keterangan=?,status=? "
                    "WHERE id=?",
                    (nama, tahun_int, bml_int, bak_int, ket or None, status, self._sel_id))
                messagebox.showinfo("Berhasil", "Periode berhasil diperbarui.")
            else:
                # ── TAMBAH BARU ─────────────────────────────────
                # Jika periode baru statusnya aktif, cek dulu
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
                    "INSERT INTO periode(nama,tahun,bulan_mulai,bulan_akhir,keterangan,status) "
                    "VALUES (?,?,?,?,?,?)",
                    (nama, tahun_int, bml_int, bak_int, ket or None, status))
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
        # Hitung jumlah simpanan yang akan ikut terhapus
        conn = get_conn()
        try:
            jml_simpanan = conn.execute(
                "SELECT COUNT(*) FROM simpanan WHERE periode_id=?", (self._sel_id,)
            ).fetchone()[0]
        finally:
            conn.close()

        pesan = "Yakin ingin menghapus periode ini?\n"
        if jml_simpanan > 0:
            pesan += f"\n⚠ PERHATIAN: {jml_simpanan} data simpanan yang terkait dengan periode ini\nakan IKUT TERHAPUS dan tidak dapat dikembalikan!\n"
        else:
            pesan += "\nTidak ada data simpanan yang terkait dengan periode ini.\n"

        if not messagebox.askyesno("Konfirmasi Hapus", pesan, icon="warning"):
            return

        conn = get_conn()
        try:
            # Hapus semua simpanan yang terkait terlebih dahulu
            conn.execute("DELETE FROM simpanan WHERE periode_id=?", (self._sel_id,))
            # Hapus periode
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
        # Cek apakah ada periode aktif lain
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
        self._v_tahun.set("")
        self._v_bml.set("1 - Januari")
        self._v_bak.set("12 - Desember")
        self._v_ket.set("")
        self._v_status.set("aktif")
        self._tv.selection_remove(self._tv.selection())
