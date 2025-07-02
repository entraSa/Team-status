import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import time
import ctypes
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
from datetime import datetime

class TeamsStatusKeeperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Teams Status Keeper")
        self.running = False
        self.tray_icon = None
        self.thread = None
        self.log_entries = []

        self.start_button = tk.Button(root, text="Start", command=self.start)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.log_button = tk.Button(root, text="View Log", command=self.show_log_window)
        self.log_button.pack(pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.root.bind("<Unmap>", self.on_minimize)

    def simulate_shift_key(self):
        ctypes.windll.user32.keybd_event(0x10, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(0x10, 0, 2, 0)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_entries.append(f"Shift key pressed at {timestamp}")

    def keep_active(self):
        while self.running:
            self.simulate_shift_key()
            time.sleep(60)

    def start(self):
        if not self.running:
            self.running = True
            self.log_entries.clear()
            self.thread = threading.Thread(target=self.keep_active)
            self.thread.daemon = True
            self.thread.start()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            messagebox.showinfo("Status", "Teams activity simulation started.")

    def stop(self):
        if self.running:
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            messagebox.showinfo("Status", "Teams activity simulation stopped.")

    def show_log_window(self):
        log_window = tk.Toplevel(self.root)
        log_window.title("Activity Log")
        log_text = scrolledtext.ScrolledText(log_window, width=50, height=20)
        log_text.pack(padx=10, pady=10)
        log_text.insert(tk.END, "\n".join(self.log_entries))
        log_text.config(state=tk.DISABLED)

    def hide_window(self):
        self.root.withdraw()
        self.show_tray_icon()

    def on_minimize(self, event):
        if self.root.state() == 'iconic':
            self.hide_window()

    def show_window(self, icon=None, item=None):
        self.root.after(0, self.root.deiconify)
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def quit_app(self, icon=None, item=None):
        self.running = False
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()

    def create_image(self):
        image = Image.new('RGB', (64, 64), color='blue')
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill='white')
        return image

    def show_tray_icon(self):
        menu = (item('Show', self.show_window), item('Exit', self.quit_app))
        self.tray_icon = pystray.Icon("TeamsStatusKeeper", self.create_image(), "Teams Status Keeper", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

root = tk.Tk()
app = TeamsStatusKeeperApp(root)
root.mainloop()
