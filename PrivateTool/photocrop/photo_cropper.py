"""
Bulk Photo Cropper - Rounded Corners
Crop many photos at once to a fixed ratio (landscape / portrait)
with smooth rounded corners like an ATM card.

Requires: pip install pillow pyinstaller
Build EXE: python -m PyInstaller --onefile --windowed --name PhotoCropper photo_cropper.py
"""
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image, ImageOps, ImageDraw

EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")

# name -> (ratio_w, ratio_h) in LANDSCAPE form
PRESETS = {
    "ATM Card (85.6 : 54)": (85.6, 54),
    "3 : 2": (3, 2),
    "4 : 3": (4, 3),
    "16 : 9": (16, 9),
    "1 : 1 (Square)": (1, 1),
    "Custom": None,
}

FOCUS = {
    "Center": (0.5, 0.5),
    "Top": (0.5, 0.0),
    "Bottom": (0.5, 1.0),
    "Left": (0.0, 0.5),
    "Right": (1.0, 0.5),
}


def rounded_mask(size, radius):
    """Anti-aliased rounded-rectangle mask (drawn 4x larger, then downscaled)."""
    w, h = size
    s = 4
    big = Image.new("L", (w * s, h * s), 0)
    ImageDraw.Draw(big).rounded_rectangle(
        (0, 0, w * s - 1, h * s - 1), radius=radius * s, fill=255
    )
    return big.resize((w, h), Image.LANCZOS)


def process_image(path, out_dir, size, radius, fmt, centering, bg_color):
    w, h = size
    img = Image.open(path)
    img = ImageOps.exif_transpose(img).convert("RGB")
    img = ImageOps.fit(img, (w, h), Image.LANCZOS, centering=centering)
    mask = rounded_mask((w, h), radius)

    base = os.path.splitext(os.path.basename(path))[0]
    if fmt == "PNG (transparent corners)":
        img.putalpha(mask)
        ext, save_kwargs, out = ".png", {}, img
    else:
        canvas = Image.new("RGB", (w, h), bg_color)
        canvas.paste(img, (0, 0), mask)
        out = canvas
        if fmt == "JPG (solid corners)":
            ext, save_kwargs = ".jpg", {"quality": 95, "subsampling": 0}
        else:
            ext, save_kwargs = ".webp", {"quality": 95}

    out_path = os.path.join(out_dir, f"{base}_rounded{ext}")
    n = 1
    while os.path.exists(out_path):
        out_path = os.path.join(out_dir, f"{base}_rounded_{n}{ext}")
        n += 1
    out.save(out_path, **save_kwargs)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bulk Photo Cropper - Rounded Corners")
        self.geometry("640x700")
        self.minsize(600, 660)
        self.files = []

        pad = {"padx": 10, "pady": 5}

        # ---- File list ----
        f1 = ttk.LabelFrame(self, text="1. Photos")
        f1.pack(fill="both", expand=True, **pad)
        btns = ttk.Frame(f1)
        btns.pack(fill="x", padx=5, pady=5)
        ttk.Button(btns, text="Add Photos", command=self.add_files).pack(side="left", padx=2)
        ttk.Button(btns, text="Add Folder", command=self.add_folder).pack(side="left", padx=2)
        ttk.Button(btns, text="Remove Selected", command=self.remove_selected).pack(side="left", padx=2)
        ttk.Button(btns, text="Clear All", command=self.clear_all).pack(side="left", padx=2)
        self.count_lbl = ttk.Label(btns, text="0 photos")
        self.count_lbl.pack(side="right")

        lf = ttk.Frame(f1)
        lf.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        self.listbox = tk.Listbox(lf, selectmode="extended", height=8)
        sb = ttk.Scrollbar(lf, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=sb.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # ---- Crop settings ----
        f2 = ttk.LabelFrame(self, text="2. Crop settings")
        f2.pack(fill="x", **pad)
        f2.columnconfigure(1, weight=1)

        ttk.Label(f2, text="Orientation:").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.orient = tk.StringVar(value="Landscape")
        of = ttk.Frame(f2)
        of.grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(of, text="Landscape (horizontal)", variable=self.orient, value="Landscape").pack(side="left", padx=(0, 10))
        ttk.Radiobutton(of, text="Portrait (vertical)", variable=self.orient, value="Portrait").pack(side="left")

        ttk.Label(f2, text="Aspect ratio:").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.preset = tk.StringVar(value=list(PRESETS)[0])
        cb = ttk.Combobox(f2, textvariable=self.preset, values=list(PRESETS), state="readonly", width=24)
        cb.grid(row=1, column=1, sticky="w")
        cb.bind("<<ComboboxSelected>>", lambda e: self.toggle_custom())

        ttk.Label(f2, text="Custom ratio (W : H):").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        cf = ttk.Frame(f2)
        cf.grid(row=2, column=1, sticky="w")
        self.cw = tk.StringVar(value="3")
        self.ch = tk.StringVar(value="2")
        self.cw_e = ttk.Entry(cf, textvariable=self.cw, width=6, state="disabled")
        self.cw_e.pack(side="left")
        ttk.Label(cf, text=" : ").pack(side="left")
        self.ch_e = ttk.Entry(cf, textvariable=self.ch, width=6, state="disabled")
        self.ch_e.pack(side="left")

        ttk.Label(f2, text="Long side (pixels):").grid(row=3, column=0, sticky="w", padx=8, pady=4)
        self.long_side = tk.StringVar(value="1600")
        ttk.Entry(f2, textvariable=self.long_side, width=10).grid(row=3, column=1, sticky="w")

        ttk.Label(f2, text="Crop focus:").grid(row=4, column=0, sticky="w", padx=8, pady=4)
        self.focus = tk.StringVar(value="Center")
        ttk.Combobox(f2, textvariable=self.focus, values=list(FOCUS), state="readonly", width=24).grid(row=4, column=1, sticky="w")

        # ---- Corner settings ----
        f3 = ttk.LabelFrame(self, text="3. Rounded corners")
        f3.pack(fill="x", **pad)
        f3.columnconfigure(1, weight=1)

        ttk.Label(f3, text="Corner radius:").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.radius = tk.DoubleVar(value=6.0)
        ttk.Scale(f3, from_=0, to=50, variable=self.radius, command=lambda v: self.update_radius_lbl()).grid(row=0, column=1, sticky="ew", padx=5)
        self.radius_lbl = ttk.Label(f3, text="6% (ATM card ≈ 6%)", width=22)
        self.radius_lbl.grid(row=0, column=2, padx=5)

        ttk.Label(f3, text="Output format:").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.fmt = tk.StringVar(value="PNG (transparent corners)")
        ttk.Combobox(
            f3, textvariable=self.fmt, state="readonly", width=26,
            values=["PNG (transparent corners)", "JPG (solid corners)", "WEBP (solid corners)"],
        ).grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(f3, text="Corner color (JPG/WEBP):").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        self.bg = tk.StringVar(value="#FFFFFF")
        ttk.Entry(f3, textvariable=self.bg, width=10).grid(row=2, column=1, sticky="w", padx=5)

        # ---- Output ----
        f4 = ttk.LabelFrame(self, text="4. Output folder")
        f4.pack(fill="x", **pad)
        self.out_dir = tk.StringVar()
        ttk.Entry(f4, textvariable=self.out_dir).pack(side="left", fill="x", expand=True, padx=8, pady=8)
        ttk.Button(f4, text="Browse...", command=self.pick_out).pack(side="right", padx=8)

        # ---- Run ----
        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=(8, 2))
        self.status = ttk.Label(self, text="Ready")
        self.status.pack(anchor="w", padx=10)
        self.run_btn = ttk.Button(self, text="Start Cropping", command=self.start)
        self.run_btn.pack(pady=10, ipadx=20, ipady=4)

    # ---------- UI helpers ----------
    def toggle_custom(self):
        state = "normal" if self.preset.get() == "Custom" else "disabled"
        self.cw_e.config(state=state)
        self.ch_e.config(state=state)

    def update_radius_lbl(self):
        self.radius_lbl.config(text=f"{self.radius.get():.0f}% of short side")

    def refresh_count(self):
        self.count_lbl.config(text=f"{len(self.files)} photos")

    def add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select photos",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff")],
        )
        self._add(paths)

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select folder")
        if folder:
            paths = [os.path.join(folder, f) for f in sorted(os.listdir(folder))
                     if f.lower().endswith(EXTS)]
            self._add(paths)

    def _add(self, paths):
        for p in paths:
            if p not in self.files:
                self.files.append(p)
                self.listbox.insert("end", os.path.basename(p))
        self.refresh_count()

    def remove_selected(self):
        for i in reversed(self.listbox.curselection()):
            self.listbox.delete(i)
            del self.files[i]
        self.refresh_count()

    def clear_all(self):
        self.listbox.delete(0, "end")
        self.files.clear()
        self.refresh_count()

    def pick_out(self):
        d = filedialog.askdirectory(title="Select output folder")
        if d:
            self.out_dir.set(d)

    # ---------- Processing ----------
    def get_ratio(self):
        if self.preset.get() == "Custom":
            rw, rh = float(self.cw.get()), float(self.ch.get())
        else:
            rw, rh = PRESETS[self.preset.get()]
        if rw <= 0 or rh <= 0:
            raise ValueError("Ratio must be positive")
        # normalise to landscape (long / short)
        long_r, short_r = max(rw, rh), min(rw, rh)
        return long_r, short_r

    def start(self):
        if not self.files:
            messagebox.showwarning("No photos", "Please add some photos first.")
            return
        if not self.out_dir.get():
            messagebox.showwarning("No output folder", "Please choose an output folder.")
            return
        try:
            long_r, short_r = self.get_ratio()
            long_px = int(self.long_side.get())
            if long_px < 50:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid input", "Check the ratio and the long side value.")
            return

        short_px = round(long_px * short_r / long_r)
        size = (long_px, short_px) if self.orient.get() == "Landscape" else (short_px, long_px)
        radius = round(min(size) * self.radius.get() / 100)
        bg = self.bg.get() or "#FFFFFF"

        try:
            Image.new("RGB", (1, 1), bg)
        except Exception:
            messagebox.showerror("Invalid color", "Use a color like #FFFFFF or white.")
            return

        os.makedirs(self.out_dir.get(), exist_ok=True)
        self.run_btn.config(state="disabled")
        self.progress.config(maximum=len(self.files), value=0)

        args = (list(self.files), self.out_dir.get(), size, radius,
                self.fmt.get(), FOCUS[self.focus.get()], bg)
        threading.Thread(target=self.worker, args=args, daemon=True).start()

    def worker(self, files, out_dir, size, radius, fmt, centering, bg):
        errors = []
        for i, path in enumerate(files, 1):
            try:
                process_image(path, out_dir, size, radius, fmt, centering, bg)
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {e}")
            self.after(0, self.set_progress, i, len(files))
        self.after(0, self.finish, len(files) - len(errors), errors, out_dir)

    def set_progress(self, i, total):
        self.progress.config(value=i)
        self.status.config(text=f"Processing {i} / {total}")

    def finish(self, ok, errors, out_dir):
        self.run_btn.config(state="normal")
        self.status.config(text=f"Done: {ok} saved, {len(errors)} failed")
        msg = f"{ok} photos saved to:\n{out_dir}"
        if errors:
            msg += "\n\nFailed:\n" + "\n".join(errors[:10])
        messagebox.showinfo("Finished", msg)


if __name__ == "__main__":
    App().mainloop()
