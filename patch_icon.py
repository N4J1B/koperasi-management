"""
patch_icon.py — Inject icon ATRA langsung ke ATRA.exe via Windows API
Jalankan di Windows setelah build PyInstaller:
    python patch_icon.py

Requires: pip install pillow
"""
import sys, os, struct, ctypes, io
from pathlib import Path

def build_ico_bmp(png_path):
    """Bangun ICO dengan format BMP/DIB dari PNG source."""
    from PIL import Image
    img_src = Image.open(png_path).convert("RGBA")
    sizes = [16, 24, 32, 48, 64, 128, 256]
    bmp_list = []
    for sz in sizes:
        img = img_src.resize((sz, sz), Image.LANCZOS)
        px = img.tobytes("raw", "RGBA")
        bgra = bytearray()
        for i in range(0, len(px), 4):
            r,g,b,a = px[i],px[i+1],px[i+2],px[i+3]
            bgra.extend([b,g,r,a])
        dib = struct.pack("<IiiHHIIiiII",
            40, sz, -sz, 1, 32, 0, len(bgra), 0, 0, 0, 0)
        bmp_list.append(dib + bytes(bgra))

    n = len(sizes)
    hdr = struct.pack("<HHH", 0, 1, n)
    dir_size = 6 + n*16
    off = dir_size
    dirs = b""
    for sz, bmp in zip(sizes, bmp_list):
        w = sz if sz < 256 else 0
        dirs += struct.pack("<BBBBHHII", w, w, 0, 0, 1, 32, len(bmp), off)
        off += len(bmp)
    ico = hdr + dirs + b"".join(bmp_list)
    return ico

def inject_icon_windows(exe_path, ico_data):
    """Inject ICO ke EXE menggunakan Windows UpdateResource API."""
    import struct

    RT_ICON       = 3
    RT_GROUP_ICON = 14

    # Parse ICO
    reserved, img_type, count = struct.unpack_from("<HHH", ico_data, 0)
    entries = []
    for i in range(count):
        off = 6 + i*16
        w,h,cc,res,pl,bpp,size,img_off = struct.unpack_from("<BBBBHHII", ico_data, off)
        entries.append((w,h,cc,res,pl,bpp,size,img_off))

    k32 = ctypes.windll.kernel32
    LOAD_LIBRARY_AS_DATAFILE = 0x00000002

    # Buka handle untuk update resource
    h = k32.BeginUpdateResourceW(exe_path, False)
    if not h:
        raise RuntimeError(f"BeginUpdateResourceW gagal, error: {k32.GetLastError()}")

    ok = True
    # Tulis setiap icon sebagai RT_ICON
    grp_entries = b""
    for idx, (w,h_,cc,res,pl,bpp,size,img_off) in enumerate(entries, start=1):
        icon_data = ico_data[img_off:img_off+size]
        buf = ctypes.create_string_buffer(icon_data)
        ret = k32.UpdateResourceW(h, RT_ICON, idx, 0x0409,
                                   buf, len(icon_data))
        if not ret:
            print(f"  WARN: UpdateResource RT_ICON {idx} gagal: {k32.GetLastError()}")
            ok = False
        actual_w = w if w > 0 else 256
        actual_h = h_ if h_ > 0 else 256
        # GRPICONENTRY
        grp_entries += struct.pack("<BBBBHHHI",
            actual_w, actual_h, cc, res, pl, bpp, size, idx)

    # Tulis GRPICONDIR (RT_GROUP_ICON)
    grp_hdr = struct.pack("<HHH", 0, 1, len(entries))
    grp_data = grp_hdr + grp_entries
    buf_grp = ctypes.create_string_buffer(grp_data)
    ret = k32.UpdateResourceW(h, RT_GROUP_ICON, 1, 0x0409,
                               buf_grp, len(grp_data))
    if not ret:
        print(f"  WARN: UpdateResource RT_GROUP_ICON gagal: {k32.GetLastError()}")
        ok = False

    if not k32.EndUpdateResourceW(h, False):
        raise RuntimeError(f"EndUpdateResourceW gagal: {k32.GetLastError()}")

    return ok

def clear_icon_cache():
    """Bersihkan icon cache Windows."""
    import subprocess
    try:
        cache = os.path.join(os.environ.get("LOCALAPPDATA",""),
                             "Microsoft","Windows","Explorer")
        for f in Path(cache).glob("iconcache*"):
            try: f.unlink()
            except: pass
        for f in Path(cache).glob("thumbcache*"):
            try: f.unlink()
            except: pass
        print("Icon cache dibersihkan.")
    except Exception as e:
        print(f"Cache: {e}")

def main():
    here = Path(__file__).parent
    exe  = here / "dist" / "ATRA" / "ATRA.exe"
    png  = here / "atra.png"

    if not exe.exists():
        print(f"ERROR: {exe} tidak ditemukan.")
        print("Jalankan dulu: pyinstaller koperasi.spec --clean --noconfirm")
        input("Tekan Enter untuk keluar...")
        return

    if not png.exists():
        print(f"ERROR: {png} tidak ditemukan.")
        input("Tekan Enter untuk keluar...")
        return

    print(f"Source PNG : {png}")
    print(f"Target EXE : {exe}")
    print()

    print("Membangun ICO dari PNG...")
    ico = build_ico_bmp(str(png))
    print(f"ICO size: {len(ico)} bytes")

    if sys.platform != "win32":
        # Di non-Windows, simpan saja ICO-nya
        out_ico = here / "atra.ico"
        with open(out_ico, "wb") as f:
            f.write(ico)
        print(f"Bukan Windows — ICO disimpan ke {out_ico}")
        print("Jalankan script ini di Windows untuk inject ke EXE.")
        return

    print("Meng-inject icon ke EXE...")
    try:
        ok = inject_icon_windows(str(exe), ico)
        if ok:
            print("✓ Icon berhasil di-inject!")
        else:
            print("⚠ Inject selesai tapi ada warning (lihat di atas)")
    except Exception as e:
        print(f"✗ Gagal inject: {e}")
        input("Tekan Enter untuk keluar...")
        return

    print()
    print("Membersihkan icon cache Windows...")
    clear_icon_cache()

    print()
    print("=" * 50)
    print("SELESAI!")
    print("Langkah selanjutnya:")
    print("1. Tutup dan buka ulang File Explorer")
    print("2. Hapus shortcut lama, buat shortcut baru dari ATRA.exe")
    print("=" * 50)
    input("Tekan Enter untuk keluar...")

if __name__ == "__main__":
    main()
