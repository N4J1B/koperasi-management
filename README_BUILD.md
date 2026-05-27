# README - Build ATRA Koperasi

## Perbaikan Icon (EXE + Shortcut)

### Masalah yang diperbaiki
- Icon di `ATRA.exe` menampilkan logo folder/Python, bukan logo ATRA
- Icon di shortcut `ATRA.exe - Shortcut` ikut salah

### Root Cause
1. **Format ICO salah**: ICO yang berisi PNG-in-ICO tidak selalu bisa di-embed ke PE (EXE) dengan benar oleh PyInstaller. ICO harus dalam format **BMP/DIB**
2. **UPX merusak icon resource**: UPX compression di PyInstaller kadang mengacak resource icon di PE header
3. **Windows icon cache lama**: Shortcut dan Explorer menyimpan cache icon lama

### Perbaikan yang diterapkan
- `atra.ico` → di-rebuild ulang dengan format **BMP/DIB** (7 ukuran: 16,24,32,48,64,128,256px)
- `koperasi.spec` → `upx=False` pada EXE dan COLLECT
- `koperasi_app.py` → `iconphoto()` + `SetCurrentProcessExplicitAppUserModelID`

---

## Cara Build EXE

### Prasyarat
```
pip install pyinstaller pillow openpyxl
```

### Build (jalankan di CMD/PowerShell dari folder koperasi_patched)
```bash
pyinstaller koperasi.spec --clean --noconfirm
```

Output ada di: `dist\ATRA\ATRA.exe`

---

## Setelah Build: Fix Icon Shortcut

Icon shortcut butuh 2 langkah:

### Langkah 1 — Bersihkan icon cache Windows
Klik dua kali file `clear_icon_cache.bat` yang ada di folder ini.
*(Explorer akan restart sebentar, ini normal)*

### Langkah 2 — Buat ulang shortcut
Hapus shortcut lama, lalu buat shortcut baru:
- Klik kanan `ATRA.exe` → **Send to** → **Desktop (create shortcut)**

Atau klik kanan → **Create shortcut**

---

## Cara Jalankan Langsung (tanpa build)
```bash
python koperasi_app.py
```
