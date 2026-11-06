"""
EPUB Tool - batch rename, remove words inside EPUB content, and extract covers.

Folder layout (created automatically next to the app):
    raw/      -> put your original EPUB files here
    results/  -> cleaned + renamed EPUB files
    cover/    -> cover images (jpg/png) named the same as the files in results/

Uses only the Python standard library (no pip install needed).
"""
import os
import re
import sys
import shutil
import threading
import queue
import zipfile
import posixpath
import subprocess
import xml.etree.ElementTree as ET
from urllib.parse import unquote
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

TEXT_EXT = (".xhtml", ".html", ".htm", ".xml", ".ncx", ".opf")
SUBFOLDERS = ("raw", "results", "cover")
IMG_EXT = {"image/jpeg": ".jpg", "image/jpg": ".jpg", "image/png": ".png",
           "image/gif": ".gif", "image/webp": ".webp", "image/svg+xml": ".svg"}


# ---------------------------------------------------------------- helpers
def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def ensure_folders(base):
    for name in SUBFOLDERS:
        os.makedirs(os.path.join(base, name), exist_ok=True)


def clean_filename(name, prefix, use_regex, words, apply_words):
    base, ext = os.path.splitext(name)
    if prefix:
        pattern = prefix if use_regex else re.escape(prefix)
        base = re.sub(r"^(?:" + pattern + r")", "", base, count=1, flags=re.I)
    if apply_words:
        for w in words:
            base = re.sub(re.escape(w), "", base, flags=re.I)
    base = re.sub(r"\s{2,}", " ", base).strip(" -_.")
    return (base or "untitled") + ext


def unique_name(folder, name):
    """Return a filename that does not exist yet in folder."""
    base, ext = os.path.splitext(name)
    candidate, i = name, 1
    while os.path.exists(os.path.join(folder, candidate)):
        candidate = f"{base} ({i}){ext}"
        i += 1
    return candidate


# ---------------------------------------------------------------- content cleaning
def clean_text(text, words, remove_para):
    """Remove words only in text nodes (not inside tags/attributes) so links stay intact."""
    total = 0
    pats = [re.compile(re.escape(w), re.I) for w in words]

    if remove_para:
        def para_fn(m):
            nonlocal total
            plain = re.sub(r"<[^>]+>", "", m.group(0))
            if any(p.search(plain) for p in pats):
                total += 1
                return ""
            return m.group(0)
        text = re.sub(r"<p\b[^>]*>.*?</p>", para_fn, text, flags=re.S | re.I)

    parts = re.split(r"(<[^>]+>)", text)
    for i in range(0, len(parts), 2):  # even indexes = plain text
        for p in pats:
            parts[i], n = p.subn("", parts[i])
            total += n
    return "".join(parts), total


def clean_epub(src, dst, words, remove_para):
    total = 0
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.lower().endswith(TEXT_EXT):
                try:
                    text = data.decode("utf-8")
                    text, n = clean_text(text, words, remove_para)
                    total += n
                    data = text.encode("utf-8")
                except UnicodeDecodeError:
                    pass
            # mimetype must be stored uncompressed (EPUB requirement)
            comp = zipfile.ZIP_STORED if item.filename == "mimetype" else zipfile.ZIP_DEFLATED
            zout.writestr(item.filename, data, compress_type=comp)
    return total


# ---------------------------------------------------------------- cover extraction
def _local(tag):
    return tag.rsplit("}", 1)[-1]


def find_cover(z):
    """Return (path_inside_zip, extension) of the cover image, or None."""
    container = ET.fromstring(z.read("META-INF/container.xml"))
    opf_path = None
    for el in container.iter():
        if _local(el.tag) == "rootfile":
            opf_path = el.get("full-path")
            break
    if not opf_path:
        return None
    opf = ET.fromstring(z.read(opf_path))

    items, cover_id = [], None
    for el in opf.iter():
        name = _local(el.tag)
        if name == "item":
            items.append({"id": el.get("id", ""), "href": el.get("href", ""),
                          "media": el.get("media-type", ""),
                          "props": el.get("properties", "")})
        elif name == "meta" and el.get("name") == "cover":
            cover_id = el.get("content")

    images = [i for i in items if i["media"].startswith("image/")]
    chosen = None
    for i in images:                                   # EPUB3
        if "cover-image" in i["props"].split():
            chosen = i
            break
    if not chosen and cover_id:                        # EPUB2
        chosen = next((i for i in images if i["id"] == cover_id), None)
    if not chosen:                                     # fallback by name
        chosen = next((i for i in images
                       if "cover" in i["id"].lower() or "cover" in i["href"].lower()), None)
    if not chosen:
        return None

    path = posixpath.normpath(posixpath.join(posixpath.dirname(opf_path), unquote(chosen["href"])))
    ext = IMG_EXT.get(chosen["media"].lower()) or os.path.splitext(path)[1].lower() or ".jpg"
    return path, ext


def extract_cover(epub_path, cover_dir, base_name):
    with zipfile.ZipFile(epub_path) as z:
        found = find_cover(z)
        if not found:
            return None
        path, ext = found
        out = os.path.join(cover_dir, unique_name(cover_dir, base_name + ext))
        with open(out, "wb") as f:
            f.write(z.read(path))
        return os.path.basename(out)


# ---------------------------------------------------------------- main process
def process(base, prefix, use_regex, words, remove_para,
            apply_words_name, do_covers, delete_raw, log):
    ensure_folders(base)
    raw, res, cov = (os.path.join(base, n) for n in SUBFOLDERS)
    files = sorted(f for f in os.listdir(raw) if f.lower().endswith(".epub"))
    if not files:
        log(f"No .epub files found in:\n{raw}")
        return
    log(f"Found {len(files)} EPUB file(s).\n")

    ok = 0
    for f in files:
        src = os.path.join(raw, f)
        new_name = unique_name(res, clean_filename(f, prefix, use_regex, words, apply_words_name))
        dst = os.path.join(res, new_name)
        try:
            removed = 0
            if words:
                removed = clean_epub(src, dst, words, remove_para)
            else:
                shutil.copy2(src, dst)
            msg = f"OK  {f}\n    -> {new_name}  ({removed} removed)"

            if do_covers:
                try:
                    c = extract_cover(dst, cov, os.path.splitext(new_name)[0])
                    msg += f"\n    cover: {c}" if c else "\n    cover: not found"
                except Exception as e:
                    msg += f"\n    cover failed: {e}"

            if delete_raw:
                os.remove(src)
            log(msg)
            ok += 1
        except Exception as e:
            if os.path.exists(dst):
                os.remove(dst)
            log(f"FAILED {f}: {e}")
    log(f"\nDone. {ok}/{len(files)} processed.")


# ---------------------------------------------------------------- GUI
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EPUB Tool")
        self.geometry("720x700")
        self.q = queue.Queue()

        pad = {"padx": 10, "pady": 4}
        self.base = tk.StringVar(value=app_dir())
        self.prefix = tk.StringVar()
        self.use_regex = tk.BooleanVar(value=False)
        self.remove_para = tk.BooleanVar(value=False)
        self.apply_name = tk.BooleanVar(value=True)
        self.do_covers = tk.BooleanVar(value=True)
        self.delete_raw = tk.BooleanVar(value=False)

        ttk.Label(self, text="Working folder (contains raw / results / cover):").pack(anchor="w", **pad)
        row = ttk.Frame(self)
        row.pack(fill="x", **pad)
        ttk.Entry(row, textvariable=self.base).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse...", command=self.pick).pack(side="left", padx=(6, 0))
        ttk.Button(row, text="Open raw", command=lambda: self.open_sub("raw")).pack(side="left", padx=(6, 0))
        ttk.Button(row, text="Open results", command=lambda: self.open_sub("results")).pack(side="left", padx=(6, 0))
        ttk.Button(row, text="Open cover", command=lambda: self.open_sub("cover")).pack(side="left", padx=(6, 0))

        ttk.Label(self, text="Text at the start of the filename to remove (e.g. [Novel] ):").pack(anchor="w", **pad)
        ttk.Entry(self, textvariable=self.prefix).pack(fill="x", **pad)
        ttk.Checkbutton(self, text="Use regex (e.g. \\d+\\s*-\\s* for '123 - ')",
                        variable=self.use_regex).pack(anchor="w", **pad)

        ttk.Label(self, text="Words to remove from EPUB content (one per line, leave empty to skip):").pack(anchor="w", **pad)
        self.words = scrolledtext.ScrolledText(self, height=5)
        self.words.pack(fill="x", **pad)
        self.words.insert("1.0", "kucingterbang")

        ttk.Checkbutton(self, text="Remove the whole <p> paragraph containing these words (good for one-line watermarks)",
                        variable=self.remove_para).pack(anchor="w", **pad)
        ttk.Checkbutton(self, text="Also remove these words from the filename",
                        variable=self.apply_name).pack(anchor="w", **pad)
        ttk.Checkbutton(self, text="Extract cover image to cover/ (same name as the result EPUB)",
                        variable=self.do_covers).pack(anchor="w", **pad)
        ttk.Checkbutton(self, text="Delete the original from raw/ after it is processed",
                        variable=self.delete_raw).pack(anchor="w", **pad)

        row2 = ttk.Frame(self)
        row2.pack(fill="x", **pad)
        ttk.Button(row2, text="Preview Names", command=self.preview).pack(side="left")
        self.run_btn = ttk.Button(row2, text="Start", command=self.run)
        self.run_btn.pack(side="left", padx=6)

        self.log_box = scrolledtext.ScrolledText(self, state="disabled", height=14)
        self.log_box.pack(fill="both", expand=True, **pad)

        try:
            ensure_folders(self.base.get())
        except OSError:
            pass
        self.after(100, self.drain)

    # --- helpers
    def pick(self):
        d = filedialog.askdirectory()
        if d:
            self.base.set(d)
            ensure_folders(d)

    def open_sub(self, name):
        base = self.base.get()
        ensure_folders(base)
        path = os.path.join(base, name)
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def get_words(self):
        return [w.strip() for w in self.words.get("1.0", "end").splitlines() if w.strip()]

    def log(self, msg):
        self.q.put(msg)

    def drain(self):
        try:
            while True:
                msg = self.q.get_nowait()
                self.log_box.config(state="normal")
                self.log_box.insert("end", msg + "\n")
                self.log_box.see("end")
                self.log_box.config(state="disabled")
        except queue.Empty:
            pass
        self.after(100, self.drain)

    def check_base(self):
        b = self.base.get()
        if not os.path.isdir(b):
            messagebox.showwarning("EPUB Tool", "Please choose a valid working folder first.")
            return None
        ensure_folders(b)
        return b

    def preview(self):
        b = self.check_base()
        if not b:
            return
        try:
            words = self.get_words()
            raw = os.path.join(b, "raw")
            names = sorted(x for x in os.listdir(raw) if x.lower().endswith(".epub"))
            if not names:
                self.log(f"No .epub files found in:\n{raw}")
            for name in names:
                new = clean_filename(name, self.prefix.get(), self.use_regex.get(),
                                     words, self.apply_name.get())
                self.log(f"{name}\n  -> {new}")
        except re.error as e:
            messagebox.showerror("Invalid regex", str(e))

    def run(self):
        b = self.check_base()
        if not b:
            return
        if self.delete_raw.get() and not messagebox.askyesno(
                "Confirm", "Originals in raw/ will be DELETED after processing. Continue?"):
            return
        try:
            re.compile(self.prefix.get() if self.use_regex.get() else "")
        except re.error as e:
            messagebox.showerror("Invalid regex", str(e))
            return
        args = (b, self.prefix.get(), self.use_regex.get(), self.get_words(),
                self.remove_para.get(), self.apply_name.get(),
                self.do_covers.get(), self.delete_raw.get(), self.log)
        self.run_btn.config(state="disabled")

        def work():
            try:
                process(*args)
            except Exception as e:
                self.log(f"ERROR: {e}")
            finally:
                self.after(0, lambda: self.run_btn.config(state="normal"))

        threading.Thread(target=work, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()
