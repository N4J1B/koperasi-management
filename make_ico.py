"""
make_ico.py — Generate atra.ico dari atra.png sebelum build PyInstaller.
Jalankan: python make_ico.py
"""
import struct, io, os, sys
from PIL import Image

SRC_PNG = os.path.join(os.path.dirname(__file__), 'atra.png')
OUT_ICO = os.path.join(os.path.dirname(__file__), 'atra.ico')

def make_ico(png_path, ico_path):
    src = Image.open(png_path).convert('RGBA')
    sizes = [16, 24, 32, 48, 64, 128, 256]
    bmp_chunks = []

    for sz in sizes:
        img = src.resize((sz, sz), Image.LANCZOS)

        # Simpan via Pillow sebagai BMP lalu ambil DIB-nya (tanpa 14-byte file header)
        buf = io.BytesIO()
        img.save(buf, format='BMP')
        dib = buf.getvalue()[14:]

        # ICO spec: biHeight harus 2x ukuran (ruang untuk XOR + AND mask)
        dib = dib[:8] + struct.pack('<i', sz * 2) + dib[12:]

        # AND mask: semua 0 = pixel fully visible (alpha dari channel A)
        row_bytes = ((sz + 31) // 32) * 4
        and_mask = b'\x00' * (row_bytes * sz)

        bmp_chunks.append(dib + and_mask)

    # Susun ICO
    n   = len(sizes)
    hdr = struct.pack('<HHH', 0, 1, n)
    off = 6 + n * 16
    dirs = b''
    for sz, chunk in zip(sizes, bmp_chunks):
        w = sz if sz < 256 else 0
        dirs += struct.pack('<BBBBHHII', w, w, 0, 0, 1, 32, len(chunk), off)
        off  += len(chunk)

    ico = hdr + dirs + b''.join(bmp_chunks)
    with open(ico_path, 'wb') as f:
        f.write(ico)

    print(f"[make_ico] Berhasil: {ico_path}")
    print(f"           {n} ukuran: {sizes}")
    print(f"           Total: {len(ico):,} bytes  Format: BMP/DIB")
    return ico_path

if __name__ == '__main__':
    make_ico(SRC_PNG, OUT_ICO)
