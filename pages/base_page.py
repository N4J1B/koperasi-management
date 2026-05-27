"""
base_page.py
Base class dengan widget umum yang dipakai semua halaman.
"""
import tkinter as tk
from tkinter import ttk, messagebox

C_BG    = "#F5F5F0"
C_WHITE = "white"
C_BLUE  = "#2B6CB0"
C_DARK  = "#1E293B"
C_GRAY  = "#94A3B8"
C_RED   = "#E53E3E"
C_GREEN = "#38A169"


class BasePage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=C_BG, **kwargs)

    # ── Card container ────────────────────────────────────
    def make_card(self, parent, padx=0, pady=0, **kwargs):
        f = tk.Frame(parent, bg=C_WHITE, relief="flat",
                     highlightbackground="#E2E8F0", highlightthickness=1, **kwargs)
        f.pack(fill="both", expand=True, padx=padx, pady=pady)
        return f

    # ── Section title ─────────────────────────────────────
    def section_title(self, parent, text, pady=(10, 4)):
        tk.Label(parent, text=text, font=("Arial", 10, "bold"),
                 bg=C_WHITE, fg=C_DARK).pack(anchor="w", padx=14, pady=pady)

    # ── Label + Entry row ─────────────────────────────────
    def lbl_entry(self, parent, label, row, var, width=28):
        tk.Label(parent, text=label, font=("Arial", 9),
                 bg=C_WHITE, fg=C_DARK, width=16, anchor="w").grid(
            row=row, column=0, sticky="w", padx=(12, 4), pady=4)
        e = ttk.Entry(parent, textvariable=var, width=width)
        e.grid(row=row, column=1, sticky="ew", padx=(0, 12), pady=4)
        return e

    # ── Label + Combobox row ──────────────────────────────
    def lbl_combo(self, parent, label, row, var, values, width=26):
        tk.Label(parent, text=label, font=("Arial", 9),
                 bg=C_WHITE, fg=C_DARK, width=16, anchor="w").grid(
            row=row, column=0, sticky="w", padx=(12, 4), pady=4)
        cb = ttk.Combobox(parent, textvariable=var, values=values,
                          width=width, state="readonly")
        cb.grid(row=row, column=1, sticky="ew", padx=(0, 12), pady=4)
        return cb

    # ── Tombol aksi ───────────────────────────────────────
    def btn(self, parent, text, cmd, color=C_BLUE, fg="white", padx=14, pady=5):
        b = tk.Button(parent, text=text, command=cmd,
                      bg=color, fg=fg, font=("Arial", 9, "bold"),
                      relief="flat", padx=padx, pady=pady, cursor="hand2",
                      activebackground="#1A4F8A", activeforeground="white")
        return b

    # ── Treeview builder ──────────────────────────────────
    def make_tree(self, parent, columns, show="headings", height=14):
        frame = tk.Frame(parent, bg=C_WHITE)
        frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        vsb = ttk.Scrollbar(frame, orient="vertical")
        hsb = ttk.Scrollbar(frame, orient="horizontal")
        tv = ttk.Treeview(frame, columns=columns, show=show,
                          height=height, yscrollcommand=vsb.set,
                          xscrollcommand=hsb.set)
        vsb.config(command=tv.yview)
        hsb.config(command=tv.xview)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tv.pack(fill="both", expand=True)

        # Alternating row colors
        tv.tag_configure("even", background="#EBF8FF")
        tv.tag_configure("odd",  background="white")
        return tv

    def tv_insert(self, tv, values, tags=None):
        """Insert satu baris ke treeview dengan tag ganjil/genap + tag tambahan."""
        idx      = len(tv.get_children())
        base_tag = "even" if idx % 2 == 0 else "odd"
        all_tags = (base_tag,) + (tuple(tags) if tags else ())
        tv.insert("", "end", values=values, tags=all_tags)

    def tv_clear(self, tv):
        tv.delete(*tv.get_children())

    # ── Info box ──────────────────────────────────────────
    def info_box(self, parent, label, value, bg="#EBF8FF", fg=C_BLUE):
        f = tk.Frame(parent, bg=bg, padx=14, pady=10,
                     highlightbackground="#BEE3F8", highlightthickness=1)
        tk.Label(f, text=label, font=("Arial", 8), bg=bg, fg=C_GRAY).pack(anchor="w")
        tk.Label(f, text=value, font=("Arial", 13, "bold"), bg=bg, fg=fg).pack(anchor="w")
        return f
