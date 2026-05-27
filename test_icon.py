import sys, os, tkinter as tk

# Simulasi resource_path
def resource_path(p):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), p)

root = tk.Tk()
root.title("Test Icon")
root.geometry("300x200")

ico = resource_path("atra.ico")
print("ICO path:", ico)
print("ICO exists:", os.path.exists(ico))
print("ICO size:", os.path.getsize(ico) if os.path.exists(ico) else "N/A")

# Coba iconbitmap
try:
    root.iconbitmap(ico)
    print("iconbitmap: OK")
except Exception as e:
    print("iconbitmap ERROR:", e)

tk.Label(root, text="Cek taskbar - ada logo?").pack(pady=50)
root.mainloop()