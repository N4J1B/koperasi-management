"""
widgets.py  –  Komponen UI reusable
- DatePickerWidget  : input tanggal dengan popup kalender
- PeriodeSelector   : dropdown pilih periode aktif
- MonthYearPicker   : pilih bulan & tahun
"""
import tkinter as tk
from tkinter import ttk
from datetime import date, datetime
import calendar
from helpers import BULAN_NAMA, this_year, this_month

C_ERR  = "#EF4444"
C_OK   = "#059669"

CAL_HDR    = "#1E3A5F"
CAL_TODAY  = "#2B6CB0"
CAL_SEL    = "#1E3A5F"
CAL_HOVER  = "#DBEAFE"
CAL_WK     = "#94A3B8"
CAL_WEEKEND= "#EF4444"
CAL_BG     = "#FFFFFF"
CAL_BORDER = "#E2E8F0"


class CalendarPopup(tk.Toplevel):
    """
    Popup kalender.
    - Klik tanggal        -> pilih & tutup
    - Escape              -> tutup
    - Klik di luar popup  -> tutup (via grab_set)
    - Dropdown bulan/tahun TIDAK menutup popup
    """
    def __init__(self, parent, current_date=None, on_select=None):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=CAL_BORDER)
        self._on_select = on_select
        self._alive     = True

        today = date.today()
        if current_date:
            try:
                self._cur = datetime.strptime(current_date, "%Y-%m-%d").date()
            except Exception:
                self._cur = today
        else:
            self._cur = today

        self._view_year  = self._cur.year
        self._view_month = self._cur.month
        self._today      = today

        self._main = tk.Frame(self, bg=CAL_BG, padx=1, pady=1)
        self._main.pack(fill="both", expand=True)

        self._draw()
        self.bind("<Escape>", lambda e: self._close())

    def _draw(self):
        for w in self._main.winfo_children():
            w.destroy()

        hdr = tk.Frame(self._main, bg=CAL_HDR, pady=6)
        hdr.pack(fill="x")

        tk.Button(hdr, text=chr(8249), font=("Arial", 12, "bold"),
                  bg=CAL_HDR, fg="white", bd=0, padx=8, cursor="hand2",
                  activebackground="#2D4A6E", activeforeground="white",
                  command=self._prev_month).pack(side="left", padx=4)

        month_names = [BULAN_NAMA[m] for m in range(1, 13)]
        self._mv = tk.StringVar(value=BULAN_NAMA[self._view_month])
        self._yv = tk.StringVar(value=str(self._view_year))

        cb_m = ttk.Combobox(hdr, textvariable=self._mv, values=month_names,
                             width=9, state="readonly", font=("Arial", 9, "bold"))
        cb_m.pack(side="left", padx=2)
        cb_m.bind("<<ComboboxSelected>>", self._on_month_change)

        years = [str(y) for y in range(2000, self._today.year + 10)]
        cb_y = ttk.Combobox(hdr, textvariable=self._yv, values=years,
                             width=5, state="readonly", font=("Arial", 9, "bold"))
        cb_y.pack(side="left", padx=2)
        cb_y.bind("<<ComboboxSelected>>", self._on_year_change)

        tk.Button(hdr, text=chr(8250), font=("Arial", 12, "bold"),
                  bg=CAL_HDR, fg="white", bd=0, padx=8, cursor="hand2",
                  activebackground="#2D4A6E", activeforeground="white",
                  command=self._next_month).pack(side="right", padx=4)

        tk.Button(hdr, text="Hari ini", font=("Arial", 7),
                  bg="#2B6CB0", fg="white", bd=0, padx=6, pady=1,
                  cursor="hand2", activebackground="#1A4F8A",
                  command=self._go_today).pack(side="right", padx=4)

        day_hdr = tk.Frame(self._main, bg=CAL_BG, pady=4)
        day_hdr.pack(fill="x", padx=6)
        for i, d in enumerate(["Sen","Sel","Rab","Kam","Jum","Sab","Min"]):
            fg = CAL_WEEKEND if i == 6 else CAL_WK
            tk.Label(day_hdr, text=d, font=("Arial", 8, "bold"),
                     bg=CAL_BG, fg=fg, width=3, anchor="center").pack(side="left", padx=2)

        tk.Frame(self._main, bg=CAL_BORDER, height=1).pack(fill="x", padx=6)

        grid_frame = tk.Frame(self._main, bg=CAL_BG, pady=4)
        grid_frame.pack(padx=6, pady=(2, 6))

        for row_i, week in enumerate(calendar.monthcalendar(self._view_year, self._view_month)):
            for col_i, day in enumerate(week):
                is_sunday = (col_i == 6)
                is_today  = (day == self._today.day and
                             self._view_month == self._today.month and
                             self._view_year  == self._today.year)
                is_sel    = (day == self._cur.day and
                             self._view_month == self._cur.month and
                             self._view_year  == self._cur.year)

                if day == 0:
                    tk.Label(grid_frame, text="", width=3, height=1,
                             bg=CAL_BG).grid(row=row_i, column=col_i, padx=2, pady=1)
                    continue

                if is_sel:
                    bg_c, fg_c, fnt = CAL_SEL, "white", ("Arial", 9, "bold")
                elif is_today:
                    bg_c, fg_c, fnt = CAL_TODAY, "white", ("Arial", 9, "bold")
                else:
                    bg_c = CAL_BG
                    fg_c = CAL_WEEKEND if is_sunday else "#1E293B"
                    fnt  = ("Arial", 9)

                lbl = tk.Label(grid_frame, text=str(day), font=fnt,
                               bg=bg_c, fg=fg_c, width=3, height=1,
                               cursor="hand2", relief="flat", anchor="center")
                lbl.grid(row=row_i, column=col_i, padx=2, pady=1)
                _day = day
                lbl.bind("<Enter>", lambda e, b=lbl, s=is_sel, t=is_today:
                         b.config(bg=CAL_HOVER if not (s or t) else b.cget("bg")))
                lbl.bind("<Leave>", lambda e, b=lbl, bg=bg_c: b.config(bg=bg))
                lbl.bind("<Button-1>", lambda e, d=_day: self._select(d))

    def _prev_month(self):
        if self._view_month == 1:
            self._view_month, self._view_year = 12, self._view_year - 1
        else:
            self._view_month -= 1
        self._draw()

    def _next_month(self):
        if self._view_month == 12:
            self._view_month, self._view_year = 1, self._view_year + 1
        else:
            self._view_month += 1
        self._draw()

    def _go_today(self):
        t = date.today()
        self._view_year, self._view_month, self._cur = t.year, t.month, t
        self._draw()
        if self._on_select:
            self._on_select(t)
        self._close()

    def _on_month_change(self, _=None):
        for k, v in BULAN_NAMA.items():
            if v == self._mv.get():
                self._view_month = k; break
        self._draw()

    def _on_year_change(self, _=None):
        try:
            self._view_year = int(self._yv.get())
        except ValueError:
            pass
        self._draw()

    def _select(self, day):
        sel = date(self._view_year, self._view_month, day)
        self._cur = sel
        if self._on_select:
            self._on_select(sel)
        self._close()

    def _close(self):
        if not self._alive:
            return
        self._alive = False
        try:
            self.grab_release()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass

    def position_near(self, widget):
        """Tampilkan popup di bawah widget, tangkap semua klik via grab_set."""
        self.update_idletasks()
        wx = widget.winfo_rootx()
        wy = widget.winfo_rooty() + widget.winfo_height() + 2
        sw = self.winfo_screenwidth()
        pw = self.winfo_reqwidth()
        if wx + pw > sw:
            wx = sw - pw - 4
        self.geometry(f"+{wx}+{wy}")
        self.lift()
        self.focus_set()
        # grab_set: semua event mouse masuk ke popup ini
        # sehingga klik di luar bisa dideteksi
        self.after(50, self._activate_grab)

    def _activate_grab(self):
        if not self._alive:
            return
        try:
            self.grab_set()
        except Exception:
            pass
        # Klik di popup → cek apakah di luar area kotak
        self.bind("<ButtonPress-1>", self._check_outside)

    def _check_outside(self, event):
        """Dipanggil setiap klik saat grab aktif.
        Tutup hanya jika klik di luar kotak kalender."""
        if not self._alive:
            return
        try:
            self.update_idletasks()
            # Widget mana yang diklik?
            clicked = event.widget
            # Cek apakah widget tsb ada di dalam hierarki popup ini
            w = clicked
            while w is not None:
                if str(w) == str(self):
                    return   # klik di dalam popup, biarkan
                try:
                    w = w.nametowidget(w.winfo_parent())
                except Exception:
                    break
        except Exception:
            pass
        # Sampai sini = klik di luar popup
        self._close()


class DatePickerWidget(tk.Frame):
    """
    Input tanggal dengan tombol kalender popup.
    get()  → 'YYYY-MM-DD'
    set()  → dari 'YYYY-MM-DD'
    """
    _valid = True

    def __init__(self, parent, label="Tanggal", default=None, **kw):
        bg = kw.pop("bg", parent.cget("bg"))
        super().__init__(parent, bg=bg, **kw)
        self._popup = None

        tk.Label(self, text=label, font=("Arial", 9),
                 bg=bg, fg="#64748B").grid(row=0, column=0, columnspan=6,
                                           sticky="w", pady=(2, 1))

        self._d = tk.StringVar()
        self._m = tk.StringVar()
        self._y = tk.StringVar()

        vd = (self.register(lambda v: len(v) <= 2 and (v == "" or v.isdigit())), "%P")
        vm = (self.register(lambda v: len(v) <= 2 and (v == "" or v.isdigit())), "%P")
        vy = (self.register(lambda v: len(v) <= 4 and (v == "" or v.isdigit())), "%P")

        self._ed = ttk.Entry(self, textvariable=self._d, width=3,
                             validate="key", validatecommand=vd, justify="center")
        self._em = ttk.Entry(self, textvariable=self._m, width=3,
                             validate="key", validatecommand=vm, justify="center")
        self._ey = ttk.Entry(self, textvariable=self._y, width=5,
                             validate="key", validatecommand=vy, justify="center")

        self._ed.grid(row=1, column=0, padx=(0, 1))
        tk.Label(self, text="/", bg=bg, fg="#64748B").grid(row=1, column=1)
        self._em.grid(row=1, column=2, padx=1)
        tk.Label(self, text="/", bg=bg, fg="#64748B").grid(row=1, column=3)
        self._ey.grid(row=1, column=4, padx=(1, 2))

        self._cal_btn = tk.Button(self, text="📅", font=("Arial", 10),
                                   bg="#EBF8FF", fg="#2B6CB0", bd=0,
                                   padx=4, pady=0, cursor="hand2",
                                   activebackground="#DBEAFE",
                                   command=self._open_calendar)
        self._cal_btn.grid(row=1, column=5, padx=(2, 0))

        self._lbl_err = tk.Label(self, text="", font=("Arial", 7),
                                  bg=bg, fg=C_ERR)
        self._lbl_err.grid(row=2, column=0, columnspan=6, sticky="w")

        for var in (self._d, self._m, self._y):
            var.trace_add("write", lambda *_: self._validate())

        self._ed.bind("<FocusOut>",   lambda e: (self._pad(self._d, 2), self._validate()))
        self._em.bind("<FocusOut>",   lambda e: (self._pad(self._m, 2), self._validate()))
        self._ey.bind("<FocusOut>",   lambda e: self._validate())
        self._ed.bind("<KeyRelease>", lambda e: self._auto_next(self._d, 2, self._em))
        self._em.bind("<KeyRelease>", lambda e: self._auto_next(self._m, 2, self._ey))

        if default:
            self.set(default)
        else:
            self._set_today()

    def _open_calendar(self):
        # Jika popup sudah ada dan masih hidup, tutup dulu
        if self._popup is not None:
            try:
                if self._popup._alive:
                    self._popup._close()
                    self._popup = None
                    return
            except Exception:
                pass
            self._popup = None

        popup = CalendarPopup(self, current_date=self.get() or None,
                              on_select=self._from_calendar)
        popup.position_near(self._cal_btn)
        self._popup = popup

    def _from_calendar(self, d: date):
        self._d.set(f"{d.day:02d}")
        self._m.set(f"{d.month:02d}")
        self._y.set(str(d.year))

    def _set_today(self):
        t = date.today()
        self._d.set(f"{t.day:02d}")
        self._m.set(f"{t.month:02d}")
        self._y.set(str(t.year))

    def _pad(self, var, n):
        v = var.get()
        if v and len(v) < n:
            var.set(v.zfill(n))

    def _auto_next(self, var, maxlen, nxt):
        if len(var.get()) == maxlen:
            nxt.focus()

    def _validate(self):
        d = self._d.get()
        m = self._m.get()
        y = self._y.get()
        if not d and not m and not y:
            self._lbl_err.config(text="")
            self._valid = False
            return
        try:
            _ = date(int(y), int(m), int(d))
            self._lbl_err.config(text="")
            self._valid = True
        except Exception:
            self._lbl_err.config(text="Tanggal tidak valid")
            self._valid = False

    def get(self):
        try:
            return date(int(self._y.get()), int(self._m.get()), int(self._d.get())).strftime("%Y-%m-%d")
        except Exception:
            return ""

    def set(self, date_str):
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            self._d.set(f"{dt.day:02d}")
            self._m.set(f"{dt.month:02d}")
            self._y.set(str(dt.year))
        except Exception:
            pass

    def is_valid(self):
        return self._valid


class MonthYearPicker(tk.Frame):
    def __init__(self, parent, label="Periode", default_year=None,
                 default_month=None, show_all=True, **kw):
        bg = kw.pop("bg", parent.cget("bg"))
        super().__init__(parent, bg=bg, **kw)
        tk.Label(self, text=label, font=("Arial", 9), bg=bg,
                 fg="#64748B").grid(row=0, column=0, columnspan=2, sticky="w", pady=(2, 1))

        months = (["Semua Bulan"] if show_all else []) + [BULAN_NAMA[i] for i in range(1, 13)]
        years  = [str(y) for y in range(2020, this_year() + 3)]

        self._mv = tk.StringVar()
        self._yv = tk.StringVar()

        self._cm = ttk.Combobox(self, textvariable=self._mv, values=months, width=14, state="readonly")
        self._cy = ttk.Combobox(self, textvariable=self._yv, values=years,  width=6,  state="readonly")
        self._cm.grid(row=1, column=0, padx=(0, 6))
        self._cy.grid(row=1, column=1)

        m = default_month or this_month()
        y = default_year  or this_year()
        self._mv.set("Semua Bulan" if show_all else BULAN_NAMA[m])
        self._yv.set(str(y))

    def get_bulan(self):
        v = self._mv.get()
        for k, n in BULAN_NAMA.items():
            if n == v:
                return k
        return None

    def get_tahun(self):
        try:
            return int(self._yv.get())
        except Exception:
            return this_year()

    def set(self, bulan, tahun):
        self._yv.set(str(tahun))
        self._mv.set(BULAN_NAMA.get(bulan, "Semua Bulan"))


class PeriodeSelector(tk.Frame):
    def __init__(self, parent, conn, label="Periode", include_all=True, **kw):
        bg = kw.pop("bg", parent.cget("bg"))
        super().__init__(parent, bg=bg, **kw)
        tk.Label(self, text=label, font=("Arial", 9), bg=bg,
                 fg="#64748B").grid(row=0, column=0, sticky="w", pady=(2, 1))
        self._var = tk.StringVar()
        self._map = {}
        rows = conn.execute("SELECT id,nama,tahun FROM periode ORDER BY tahun DESC,id DESC").fetchall()
        opts = (["— Semua Periode —"] if include_all else []) + \
               [f"{r['nama']} ({r['tahun']})" for r in rows]
        for r in rows:
            self._map[f"{r['nama']} ({r['tahun']})"] = r["id"]
        self._cb = ttk.Combobox(self, textvariable=self._var, values=opts,
                                width=22, state="readonly")
        self._cb.grid(row=1, column=0)
        if opts:
            self._cb.current(0)

    def get_id(self):
        return self._map.get(self._var.get(), None)

    def bind_change(self, fn):
        self._var.trace_add("write", lambda *_: fn())
